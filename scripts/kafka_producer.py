import os
import json
import time
import csv
from pathlib import Path
from kafka import KafkaProducer
from dotenv import load_dotenv

def main():
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    # Path to local ratings file
    # User's prompt: MovieLens raw local: data/raw/
    # We will check common locations
    possible_paths = [
        project_root / "data" / "raw" / "ratings.csv",
        project_root / "data" / "raw" / "movielens" / "ratings.csv",
        project_root / "data" / "raw" / "ml-latest-small" / "ratings.csv"
    ]
    
    ratings_file = None
    for p in possible_paths:
        if p.exists():
            ratings_file = p
            break
            
    if not ratings_file:
        print("Không tìm thấy file ratings.csv tại thư mục data/raw/. Vui lòng đảm bảo dữ liệu đã được tải.")
        return

    kafka_broker = os.getenv("KAFKA_BROKER", "localhost:9092")
    topic_name = "movie_ratings_stream"

    print(f"Khởi tạo Kafka Producer kết nối tới {kafka_broker}...")
    producer = KafkaProducer(
        bootstrap_servers=[kafka_broker],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print(f"Đang đọc dữ liệu từ {ratings_file} và gửi lên topic '{topic_name}'...")
    
    with open(ratings_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            # message structure
            message = {
                "userId": int(row["userId"]),
                "movieId": int(row["movieId"]),
                "rating": float(row["rating"]),
                "timestamp": int(row["timestamp"])
            }
            
            producer.send(topic_name, value=message)
            count += 1
            
            # Simulate real-time stream (send 1000 messages per second)
            if count % 1000 == 0:
                print(f"Đã gửi {count} messages...")
                producer.flush() # Force sending the batch
                time.sleep(1.0)  # Sleep 1 second for every 1000 messages

    producer.flush()
    print("Hoàn tất gửi dữ liệu stream.")

if __name__ == "__main__":
    main()
