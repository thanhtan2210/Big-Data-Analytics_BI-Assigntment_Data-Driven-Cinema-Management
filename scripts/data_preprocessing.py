import os
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, mean, stddev, to_timestamp
from dotenv import load_dotenv

def main():
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    hdfs_host = os.getenv("HDFS_HOST", "localhost")
    hdfs_port = os.getenv("HDFS_PORT", "9000")
    hdfs_base = f"hdfs://{hdfs_host}:{hdfs_port}"

    movielens_path = os.getenv("PROJECT_HDFS_RAW_MOVIELENS", "/project/cinema/raw/movielens")
    tmdb_path = os.getenv("PROJECT_HDFS_RAW_TMDB", "/project/cinema/raw/tmdb")

    mongo_uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
    mongo_db = os.getenv("MONGO_DB", "cinema_dw")

    spark = (
        SparkSession.builder
        .appName("DataPreprocessing_CinemaDW")
        .config("spark.mongodb.write.connection.uri", mongo_uri)
        .config("spark.sql.ansi.enabled", "false")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    print("=====================================================")
    print("        Starting Data Preprocessing Pipeline")
    print("=====================================================")

    print(f"Loading MovieLens data from {hdfs_base}{movielens_path} ...")
    movies_df = spark.read.csv(f"{hdfs_base}{movielens_path}/movies.csv", header=True, inferSchema=True)
    ratings_df = spark.read.csv(f"{hdfs_base}{movielens_path}/ratings.csv", header=True, inferSchema=True)
    links_df = spark.read.csv(f"{hdfs_base}{movielens_path}/links.csv", header=True, inferSchema=True)
    tags_df = spark.read.csv(f"{hdfs_base}{movielens_path}/tags.csv", header=True, inferSchema=True)

    print(f"Loading TMDB data from {hdfs_base}{tmdb_path} ...")
    has_tmdb = False
    tmdb_movies_df = None
    for name in ["tmdb_movies.csv", "tmdb_5000_movies.csv"]:
        try:
            tmdb_movies_df = spark.read.csv(f"{hdfs_base}{tmdb_path}/{name}", header=True, inferSchema=True)
            print(f"TMDB file found: {name}")
            has_tmdb = True
            break
        except Exception:
            pass

    print(f"Loading TMDB Revenue data ...")
    has_revenue = False
    revenue_df = None
    try:
        # Assuming the user put it in the same tmdb_path on HDFS
        revenue_df = spark.read.csv(f"{hdfs_base}{tmdb_path}/tmdb_revenue.csv", header=True, inferSchema=True)
        print("TMDB Revenue file found: tmdb_revenue.csv")
        has_revenue = True
    except Exception:
        pass

    print("Cleaning data ...")
    movies_df = movies_df.dropna(subset=["movieId", "title"]).fillna({"genres": "Unknown"})
    ratings_df = ratings_df.dropna(subset=["userId", "movieId", "rating"])
    links_df = links_df.dropna(subset=["movieId"])
    ratings_df = ratings_df.withColumn("timestamp_dt", to_timestamp(col("timestamp")))

    print("Removing outliers ...")
    ratings_df = ratings_df.filter((col("rating") >= 0.5) & (col("rating") <= 5.0))

    user_counts = ratings_df.groupBy("userId").agg(count("movieId").alias("rating_count"))
    stats = user_counts.select(
        mean("rating_count").alias("mean_count"),
        stddev("rating_count").alias("std_count")
    ).collect()[0]

    if stats["std_count"] is not None:
        upper_limit = stats["mean_count"] + (3 * stats["std_count"])
        valid_users = user_counts.filter(col("rating_count") <= upper_limit).select("userId")
        ratings_df = ratings_df.join(valid_users, on="userId", how="inner")

    print("Merging MovieLens and TMDB ...")
    movies_linked = movies_df.join(links_df, on="movieId", how="left")

    if has_tmdb:
        if "id" in tmdb_movies_df.columns:
            tmdb_movies_df = tmdb_movies_df.withColumnRenamed("id", "tmdbId")
        final_movies_df = movies_linked.join(tmdb_movies_df, on="tmdbId", how="left")
    else:
        final_movies_df = movies_linked

    avg_ratings = ratings_df.groupBy("movieId").agg(
        mean("rating").alias("ml_avg_rating"),
        count("rating").alias("ml_rating_count")
    )
    final_movies_df = final_movies_df.join(avg_ratings, on="movieId", how="left")

    print("Pushing cleaned data to MongoDB ...")

    if has_revenue and revenue_df is not None:
        from pyspark.sql.functions import col as _col, regexp_replace
        # movies_metadata.csv has many malformed rows with non-numeric values.
        # Use regexp_replace to strip all non-numeric chars and cast safely.
        revenue_clean = revenue_df \
            .withColumn("tmdbId", regexp_replace(_col("id"), "[^0-9]", "").cast("long")) \
            .withColumn("revenue_val", regexp_replace(_col("revenue"), "[^0-9.]", "").cast("double")) \
            .dropna(subset=["tmdbId", "revenue_val"]) \
            .filter(_col("revenue_val") > 0)

        # Join with links to get MovieLens movieId
        links_cast = links_df.select(
            _col("movieId").cast("integer"),
            _col("tmdbId").cast("long")
        ).dropna()

        revenue_joined = revenue_clean.join(links_cast, on="tmdbId", how="inner")

        revenue_final = revenue_joined.select(
            _col("movieId").cast("integer"),
            _col("tmdbId"),
            _col("title"),
            _col("release_date"),
            _col("revenue_val").alias("revenue"),
            regexp_replace(_col("vote_average"), "[^0-9.]", "").cast("double").alias("vote_average"),
            regexp_replace(_col("vote_count"), "[^0-9]", "").cast("integer").alias("vote_count"),
            _col("genres")
        ).withColumn("release_date_temp", to_timestamp(_col("release_date"), "yyyy-MM-dd")) \
         .dropna(subset=["movieId", "revenue", "release_date_temp"]) \
         .drop("release_date_temp")

        revenue_final.write.format("mongodb") \
            .mode("overwrite") \
            .option("database", mongo_db) \
            .option("collection", "revenue") \
            .save()
        print("Revenue collection saved successfully.")

    final_movies_df.write.format("mongodb") \
        .mode("overwrite") \
        .option("database", mongo_db) \
        .option("collection", "movies") \
        .save()

    ratings_df.write.format("mongodb") \
        .mode("overwrite") \
        .option("database", mongo_db) \
        .option("collection", "ratings") \
        .save()

    tags_df.write.format("mongodb") \
        .mode("overwrite") \
        .option("database", mongo_db) \
        .option("collection", "tags") \
        .save()

    print("=====================================================")
    print("      Data Preprocessing Pipeline Completed!")
    print("=====================================================")

    spark.stop()

if __name__ == "__main__":
    main()
