import os
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_timestamp, window, avg, count, sum as spark_sum, lit
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType, LongType
from dotenv import load_dotenv

def write_window_metrics(df, epoch_id, mongo_uri, mongo_db):
    """Write windowed aggregate metrics to live_metrics collection."""
    if df.isEmpty():
        return
    df.write.format("mongodb") \
        .mode("append") \
        .option("spark.mongodb.write.connection.uri", mongo_uri) \
        .option("spark.mongodb.write.database", mongo_db) \
        .option("spark.mongodb.write.collection", "live_metrics") \
        .save()

def write_movie_stats(df, epoch_id, mongo_uri, mongo_db):
    """
    Write per-movie stats for each micro-batch to live_movie_stats.
    This enables the dashboard to compute Top-10 rankings in real-time.
    """
    if df.isEmpty():
        return
    movie_stats = df.groupBy("movieId").agg(
        count("rating").alias("rating_count"),
        spark_sum("rating").alias("rating_sum"),
        avg("movie_revenue").alias("movie_revenue")  # Same value per movieId from static join
    ).withColumn("epoch_id", lit(epoch_id)) \
     .withColumn("batch_time", current_timestamp())

    movie_stats.write.format("mongodb") \
        .mode("append") \
        .option("spark.mongodb.write.connection.uri", mongo_uri) \
        .option("spark.mongodb.write.database", mongo_db) \
        .option("spark.mongodb.write.collection", "live_movie_stats") \
        .save()

import pyspark

def main():
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    kafka_broker = os.getenv("KAFKA_BROKER", "localhost:9092")
    topic_name = "movie_ratings_stream"
    mongo_uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
    mongo_db = os.getenv("MONGO_DB", "cinema_dw")

    spark_version = pyspark.__version__
    packages = f"org.apache.spark:spark-sql-kafka-0-10_2.13:{spark_version},org.mongodb.spark:mongo-spark-connector_2.13:11.0.1"

    spark = (
        SparkSession.builder
        .appName("StreamingProcessor_CinemaDW")
        .config("spark.jars.packages", packages)
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    print("=====================================================")
    print("        Starting PySpark Streaming Processor")
    print("=====================================================")
    print(f"Listening to Kafka: {kafka_broker}, Topic: {topic_name}")

    schema = StructType([
        StructField("userId", IntegerType(), True),
        StructField("movieId", IntegerType(), True),
        StructField("rating", DoubleType(), True),
        StructField("timestamp", LongType(), True)
    ])

    df_kafka = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_broker) \
        .option("subscribe", topic_name) \
        .option("startingOffsets", "latest") \
        .load()

    df_json = df_kafka.selectExpr("CAST(value AS STRING) as json_str")
    df_parsed = df_json.select(from_json(col("json_str"), schema).alias("data")).select("data.*")
    df_with_time = df_parsed.withColumn("processing_time", current_timestamp())

    # Load static revenue data for Stream-Static Join
    print("Loading static revenue data from MongoDB for Stream Enrichment...")
    static_revenue_df = spark.read.format("mongodb") \
        .option("spark.mongodb.read.connection.uri", mongo_uri) \
        .option("spark.mongodb.read.database", mongo_db) \
        .option("spark.mongodb.read.collection", "revenue") \
        .load()

    static_revenue_df = static_revenue_df.select(
        col("movieId").cast("integer"),
        col("revenue").cast("double").alias("movie_revenue")
    ).dropna(subset=["movie_revenue"])

    # Stream-Static Join: enrich ratings with revenue
    df_joined = df_with_time.join(static_revenue_df, on="movieId", how="left")

    # ── Query 1: Windowed aggregate metrics (for overall traffic KPIs) ──
    windowed_metrics = df_joined \
        .withWatermark("processing_time", "30 seconds") \
        .groupBy(window(col("processing_time"), "5 seconds")) \
        .agg(
            count("rating").alias("total_ratings_in_window"),
            avg("rating").alias("avg_rating_in_window"),
            pyspark.sql.functions.sum("movie_revenue").alias("revenue_in_window")
        )

    final_df = windowed_metrics \
        .withColumn("window_start", col("window.start")) \
        .withColumn("window_end", col("window.end")) \
        .drop("window")

    print("Bắt đầu đẩy dữ liệu stream lên MongoDB...")

    query1 = final_df.writeStream \
        .foreachBatch(lambda df, epoch_id: write_window_metrics(df, epoch_id, mongo_uri, mongo_db)) \
        .outputMode("update") \
        .option("checkpointLocation", f"file://{project_root}/runtime/checkpoints/live_metrics") \
        .start()

    # ── Query 2: Per-movie stats for Top-10 BI analytics ──
    query2 = df_joined.writeStream \
        .foreachBatch(lambda df, epoch_id: write_movie_stats(df, epoch_id, mongo_uri, mongo_db)) \
        .outputMode("append") \
        .option("checkpointLocation", f"file://{project_root}/runtime/checkpoints/live_movie_stats") \
        .start()

    query1.awaitTermination()

if __name__ == "__main__":
    main()
