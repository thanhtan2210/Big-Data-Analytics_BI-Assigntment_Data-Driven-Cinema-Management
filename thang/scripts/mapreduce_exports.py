import os
from pathlib import Path

from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def _resolve_column_name(df, candidates):
    lower_map = {col_name.lower(): col_name for col_name in df.columns}
    for candidate in candidates:
        found = lower_map.get(candidate.lower())
        if found:
            return found
    return None


def _write_single_csv(df, output_dir):
    local_uri = Path(output_dir).resolve().as_uri()
    (
        df.coalesce(1)
        .write.mode("overwrite")
        .option("header", True)
        .csv(local_uri)
    )


def main():
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env")

    mongo_uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
    mongo_db = os.getenv("MONGO_DB", "cinema_dw")

    out_root = project_root / "visual" / "exports" / "mapreduce"
    out_root.mkdir(parents=True, exist_ok=True)

    spark = (
        SparkSession.builder.appName("Task3_MapReduce_Exports")
        .config("spark.mongodb.read.connection.uri", mongo_uri)
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    movies_df = (
        spark.read.format("mongodb")
        .option("database", mongo_db)
        .option("collection", "movies_enriched")
        .load()
    )
    ratings_df = (
        spark.read.format("mongodb")
        .option("database", mongo_db)
        .option("collection", "ratings")
        .load()
    )

    movie_col = _resolve_column_name(ratings_df, ["movieId", "movie_id", "movieid"])
    rating_col = _resolve_column_name(ratings_df, ["rating", "score"])
    ts_col = _resolve_column_name(ratings_df, ["timestamp", "createdAt", "created_at"])

    if not movie_col or not rating_col:
        raise RuntimeError(
            "ratings collection schema is incompatible. "
            f"Found columns: {ratings_df.columns}. "
            "Need movieId and rating (or accepted aliases)."
        )

    rating_select = [
        F.col(movie_col).cast("int").alias("movieId"),
        F.col(rating_col).cast("double").alias("rating"),
    ]
    if ts_col:
        rating_select.append(F.col(ts_col).cast("long").alias("timestamp"))
    else:
        rating_select.append(F.lit(None).cast("long").alias("timestamp"))

    ratings_df = ratings_df.select(*rating_select)

    genres_col = F.coalesce(F.col("genres"), F.lit("Unknown"))
    parsed_genres_col = F.split(genres_col, r"\|")
    final_genres_array = (
        F.when(
            F.col("genres_array").isNull()
            | (F.size(F.col("genres_array")) == 0)
            | F.array_contains(F.col("genres_array"), "|"),
            parsed_genres_col,
        ).otherwise(F.col("genres_array"))
    )

    genre_movie_df = movies_df.select(
        F.col("movieId").cast("int").alias("movieId"),
        F.explode_outer(final_genres_array).alias("genre"),
        F.col("revenue").cast("double").alias("revenue"),
        F.col("decade").cast("int").alias("decade"),
    )

    rating_by_movie_df = ratings_df.groupBy("movieId").agg(
        F.count("rating").alias("rating_count"),
        F.sum("rating").alias("rating_sum"),
    )

    joined = rating_by_movie_df.join(genre_movie_df, on="movieId", how="inner")

    genre_stats_mr_df = (
        joined.groupBy("genre")
        .agg(
            F.sum("rating_count").alias("rating_count"),
            F.sum("rating_sum").alias("rating_sum"),
        )
        .withColumn(
            "avg_rating",
            F.when(F.col("rating_count") > 0, F.col("rating_sum") / F.col("rating_count")).otherwise(F.lit(None)),
        )
        .select("genre", "rating_count", "avg_rating")
        .orderBy(F.desc("rating_count"))
    )

    decade_genre_mr_df = (
        joined.groupBy("decade", "genre")
        .agg(
            F.sum("rating_count").alias("rating_count"),
            F.sum("rating_sum").alias("rating_sum"),
            F.avg("revenue").alias("avg_revenue"),
        )
        .withColumn(
            "avg_rating",
            F.when(F.col("rating_count") > 0, F.col("rating_sum") / F.col("rating_count")).otherwise(F.lit(None)),
        )
        .select("decade", "genre", "rating_count", "avg_rating", "avg_revenue")
        .orderBy("decade", F.desc("rating_count"))
    )

    rating_dist_mr_df = (
        ratings_df.groupBy("rating")
        .agg(F.count("rating").alias("frequency"))
        .orderBy("rating")
    )

    _write_single_csv(genre_stats_mr_df, str(out_root / "mr_genre_rating"))
    _write_single_csv(decade_genre_mr_df, str(out_root / "mr_decade_genre_heatmap"))
    _write_single_csv(rating_dist_mr_df, str(out_root / "mr_rating_distribution"))

    print("MapReduce exports completed:")
    print(f"- {out_root / 'mr_genre_rating'}")
    print(f"- {out_root / 'mr_decade_genre_heatmap'}")
    print(f"- {out_root / 'mr_rating_distribution'}")

    spark.stop()


if __name__ == "__main__":
    main()
