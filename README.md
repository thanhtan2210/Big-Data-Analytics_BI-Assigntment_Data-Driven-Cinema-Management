# Big Data Analytics & BI Assignment
## 🎬 Data-Driven Cinema Management

Dự án xây dựng hệ thống Business Intelligence (BI) hoàn chỉnh cho rạp chiếu phim, kết hợp xử lý dữ liệu lô (Batch) và luồng (Streaming) trên tập dữ liệu **MovieLens 25M + TMDB**.

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────┐
│                     DATA SOURCES                        │
│  MovieLens 25M (ratings, movies) + TMDB (Revenue)       │
└────────────────────┬────────────────────────────────────┘
                     │
          ┌──────────▼──────────┐
          │    HDFS Storage     │  ← Nơi lưu trữ dữ liệu thô
          └──────────┬──────────┘
                     │
      ┌───────────────┴────────────────┐
      │                                │
┌────▼────────────┐          ┌────────▼─────────────┐
│  PySpark Batch  │          │   Kafka Producer     │
│  (Preprocessing)│          │  (Giả lập User Rate) │
└────┬────────────┘          └────────┬─────────────┘
     │                                │
     │                       ┌────────▼─────────────┐
     │                       │  PySpark Streaming   │
     │                       │  (Dual-Query Stats)  │
     │                       └────────┬─────────────┘
     │                                │
     └──────────────┬─────────────────┘
                    ▼
           ┌────────────────┐
           │   MongoDB      │  ← cinema_dw: movies, ratings,
           │   (Serving DB) │      revenue, live_movie_stats
           └────────┬───────┘
                    │
           ┌────────▼───────┐
           │   Streamlit    │  → http://localhost:8501
           │  BI Dashboard  │
           └────────────────┘
```

---

## 📊 Business Intelligence Insights

### 1. 🎬 Real-time Streaming (Quyết định tức thì)
Dashboard cập nhật mỗi **5 giây** giúp rạp chiếu phim ứng biến nhanh với thị hiếu:
- **Top 10 Phim Doanh Thu Cao**: Blockbuster nào đang "hot" nhất.
- **Top 10 Thể Loại Doanh Thu Cao**: Thể loại phim nào đang hái ra tiền.
- **Top 10 Phim Rating Cao**: Phim nào đang được khán giả đánh giá cao nhất.
- **Top 10 Thể Loại Rating Cao**: Gu phim của khán giả hiện tại.

### 2. 📊 Historical Batch (Chiến lược dài hạn)
Phân tích xu hướng qua các **Thập kỷ (Decades)** từ 1900 đến nay:
- **Doanh thu mỗi Thập kỷ**: Sự phát triển quy mô thị trường điện ảnh.
- **Xu hướng Quan tâm & Chất lượng**: Lượng traffic và điểm số trung bình qua từng thời kỳ.
- **Sự tiến hóa Thể loại**: Theo dõi sự thay đổi thị hiếu thể loại phim qua hơn 100 năm.

---

## 🚀 Hướng Dẫn Chạy Demo (End-to-End)

### Giai đoạn 1: Hạ tầng (Terminal 1)
```bash
# Bật HDFS & MongoDB
source scripts/activate.sh
hdfs --daemon start namenode
hdfs --daemon start datanode
brew services start mongodb-community

# Bật Kafka
./scripts/install_kafka.sh # (chỉ chạy 1 lần đầu)
./scripts/run_kafka.sh
```

### Giai đoạn 2: Xử lý Batch (Terminal 2)
```bash
source scripts/activate.sh && source venv/bin/activate
# Nạp HDFS (Cần có data/raw/movies.csv, ratings.csv, links.csv và movies_metadata.csv)
hdfs dfs -mkdir -p /project/cinema/raw/movielens
hdfs dfs -mkdir -p /project/cinema/raw/tmdb
hdfs dfs -put data/raw/*.csv /project/cinema/raw/movielens/
hdfs dfs -put data/raw/tmdb/extracted/movies_metadata.csv /project/cinema/raw/tmdb/tmdb_revenue.csv

# Chạy Preprocessing (2-3 phút)
./scripts/run_preprocessing.sh
```

### Giai đoạn 3: Real-time (Terminal 3 & 4)
```bash
# Terminal 3: Producer (Bắn 1000 rating/s)
./scripts/run_producer.sh

# Terminal 4: Streaming Processor (Tự động xóa dữ liệu cũ và chạy)
./scripts/run_streaming.sh
```

### Giai đoạn 5: Dashboard (Terminal 5)
```bash
./scripts/run_dashboard.sh
```
Truy cập: [`http://localhost:8501`](http://localhost:8501)

---

## 🛠️ Xử Lý Sự Cố
- **Dữ liệu không nhảy**: Kiểm tra Spark Streaming terminal có báo lỗi không. Xóa `runtime/checkpoints/*` và restart.
- **Revenue bằng 0**: Đảm bảo giai đoạn 2 đã hoàn thành và collection `revenue` trong MongoDB đã có dữ liệu.
- **HDFS Lỗi**: Chạy `jps` để kiểm tra NameNode/DataNode.

---
*Stack: Kafka · HDFS · PySpark · MongoDB · Streamlit · Plotly*
