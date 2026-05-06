import os
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_timestamp, window, avg, count
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType, LongType
from dotenv import load_dotenv

def write_to_mongo(df, epoch_id, mongo_uri, mongo_db):
    """
    Function to write streaming micro-batches to MongoDB.
    """
    if df.isEmpty():
        return

    # In production, we might use upsert. Here we simply write/append to live_metrics.
    # To maintain a live view, we can write to a collection and dashboard reads the latest.
    df.write.format("mongodb") \
        .mode("append") \
        .option("spark.mongodb.write.connection.uri", mongo_uri) \
        .option("spark.mongodb.write.database", mongo_db) \
        .option("spark.mongodb.write.collection", "live_metrics") \
        .save()

import pyspark

def main():
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    kafka_broker = os.getenv("KAFKA_BROKER", "localhost:9092")
    topic_name = "movie_ratings_stream"
    mongo_uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
    mongo_db = os.getenv("MONGO_DB", "cinema_dw")

    # Dynamically match the kafka package version to the installed pyspark version
    spark_version = pyspark.__version__
    packages = f"org.apache.spark:spark-sql-kafka-0-10_2.13:{spark_version},org.mongodb.spark:mongo-spark-connector_2.13:11.0.1"

    # Initialize Spark Session with MongoDB and Kafka packages
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

    # Define schema for the incoming JSON messages
    schema = StructType([
        StructField("userId", IntegerType(), True),
        StructField("movieId", IntegerType(), True),
        StructField("rating", DoubleType(), True),
        StructField("timestamp", LongType(), True)
    ])

    # Read from Kafka topic
    df_kafka = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_broker) \
        .option("subscribe", topic_name) \
        .option("startingOffsets", "latest") \
        .load()

    # The value from Kafka is binary, cast it to string
    df_json = df_kafka.selectExpr("CAST(value AS STRING) as json_str")

    # Parse JSON string into columns
    df_parsed = df_json.select(from_json(col("json_str"), schema).alias("data")).select("data.*")

    # Add a processing time column for windowing
    df_with_time = df_parsed.withColumn("processing_time", current_timestamp())

    # Load static revenue data for Stream-Static Join
    print("Loading static revenue data from MongoDB for Stream Enrichment...")
    static_revenue_df = spark.read.format("mongodb") \
        .option("spark.mongodb.read.connection.uri", mongo_uri) \
        .option("spark.mongodb.read.database", mongo_db) \
        .option("spark.mongodb.read.collection", "revenue") \
        .load()
    
    # Keep only needed columns and cast revenue
    static_revenue_df = static_revenue_df.select(
        col("movieId").cast("integer"), 
        col("revenue").cast("double").alias("movie_revenue")
    ).dropna(subset=["movie_revenue"])
    
    # Join the stream with the static revenue DataFrame
    df_joined = df_with_time.join(static_revenue_df, on="movieId", how="left")

    # Aggregate metrics: tumbling window of 5 seconds (for near-realtime updates)
    windowed_metrics = df_joined \
        .withWatermark("processing_time", "30 seconds") \
        .groupBy(window(col("processing_time"), "5 seconds")) \
        .agg(
            count("rating").alias("total_ratings_in_window"),
            avg("rating").alias("avg_rating_in_window"),
            pyspark.sql.functions.sum("movie_revenue").alias("revenue_in_window")
        )

    # Add a flattened timestamp column for easier parsing in Streamlit
    final_df = windowed_metrics \
        .withColumn("window_start", col("window.start")) \
        .withColumn("window_end", col("window.end")) \
        .drop("window")

    print("Bắt đầu đẩy dữ liệu stream lên MongoDB...")

    # Write to MongoDB using foreachBatch
    query = final_df.writeStream \
        .foreachBatch(lambda df, epoch_id: write_to_mongo(df, epoch_id, mongo_uri, mongo_db)) \
        .outputMode("update") \
        .option("checkpointLocation", f"file://{project_root}/runtime/checkpoints/live_metrics") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
