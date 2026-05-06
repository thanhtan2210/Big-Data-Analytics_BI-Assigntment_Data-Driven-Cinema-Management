# Big Data Analytics & BI Assignment
## 🎬 Data-Driven Cinema Management

Kho lưu trữ này chứa toàn bộ mã nguồn, cấu hình và tài liệu cho dự án **Phân tích Dữ liệu Rạp Phim (Cinema Analytics)**. Dự án xây dựng một hệ thống Business Intelligence (BI) hoàn chỉnh, kết hợp xử lý dữ liệu lô (Batch Processing) và dữ liệu thời gian thực (Streaming) trên tập dữ liệu **MovieLens 25M + TMDB**.

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────┐
│                     DATA SOURCES                        │
│  MovieLens 25M (ratings.csv, movies.csv)                │
│  TMDB (movies_metadata.csv - Revenue & Genre)           │
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
     │                       │  + Stream-Static Join│
     │                       └────────┬─────────────┘
     │                                │
     └──────────────┬─────────────────┘
                    ▼
           ┌────────────────┐
           │   MongoDB      │  ← cinema_dw: movies, ratings,
           │   (Serving DB) │      revenue, live_metrics
           └────────┬───────┘
                    │
           ┌────────▼───────┐
           │   Streamlit    │  → http://localhost:8501
           │  BI Dashboard  │
           └────────────────┘
```

---

## 📊 Các Chỉ Số BI Được Phân Tích

| Dashboard | Chỉ Số | Mô Tả |
|:---|:---|:---|
| **Batch** | Global Avg Rating | Điểm trung bình toàn bộ bộ phim |
| **Batch** | Genre Distribution | Biểu đồ Donut phân bổ thể loại phim |
| **Batch** | Rating Distribution | Histogram mật độ phân bố điểm số |
| **Batch** | Engagement vs Quality | Scatter Plot: Lượt đánh giá ↔ Điểm TB |
| **Streaming** | Total Streaming Ratings | Tổng số lượng đánh giá lũy kế |
| **Streaming** | Cumulative Revenue | Tổng doanh thu phim trending lũy kế |
| **Streaming** | Window Revenue | Doanh thu trong cửa sổ 30 giây gần nhất |
| **Streaming** | Peak Traffic | Lưu lượng đỉnh điểm trong 30 phút qua |

---

## 🛠️ Cài Đặt Môi Trường (Setup)

**Yêu cầu hệ thống:** macOS, Java 17, Python 3.11+

**1. Khởi tạo môi trường Python**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Cài đặt các ứng dụng phụ trợ (chỉ cần làm 1 lần)**
```bash
# Cài đặt Java 17 (nếu chưa có)
brew install openjdk@17

# Cài đặt Hadoop (HDFS)
brew install hadoop

# Cài đặt MongoDB
brew tap mongodb/brew
brew install mongodb-community
```

---

## 🚀 Hướng Dẫn Chạy Demo Toàn Bộ Dự Án (End-to-End)

Để hệ thống hoạt động từ A-Z, hãy làm theo đúng thứ tự 4 Giai đoạn. **Mở 5 cửa sổ Terminal riêng biệt** (Terminal 1 → 5) theo hướng dẫn bên dưới.

---

### 📦 Giai đoạn 1: Khởi động Hạ tầng (Terminal 1)

Đây là nền tảng cần thiết cho toàn bộ hệ thống.

```bash
# 1a. Kích hoạt biến môi trường và bật HDFS
source scripts/activate.sh
hdfs --daemon start namenode
hdfs --daemon start datanode

# 1b. Bật MongoDB
brew services start mongodb-community

# 1c. Cài đặt Kafka (chỉ chạy 1 lần đầu tiên)
./scripts/install_kafka.sh

# 1d. Bật Kafka Server (giữ Terminal này mở)
./scripts/run_kafka.sh
```

> ⚠️ **Kiểm tra HDFS đã bật thành công:** Chạy lệnh `jps` — phải thấy cả `NameNode` lẫn `DataNode` trong danh sách.

---

### 📂 Giai đoạn 2: Nạp Dữ Liệu & Xử Lý Batch (Terminal 2)

Giai đoạn này đọc dữ liệu thô từ HDFS, làm sạch và chuyển đổi bằng PySpark, lưu vào MongoDB.

```bash
# 2a. Kích hoạt môi trường
source scripts/activate.sh
source venv/bin/activate

# 2b. Tạo thư mục lưu trữ trên HDFS
hdfs dfs -mkdir -p /project/cinema/raw/movielens
hdfs dfs -mkdir -p /project/cinema/raw/tmdb

# 2c. Tải dữ liệu MovieLens lên HDFS
hdfs dfs -put data/raw/*.csv /project/cinema/raw/movielens/

# 2d. Tải dữ liệu TMDB lên HDFS (đổi tên cho code nhận diện đúng)
hdfs dfs -put data/raw/tmdb/extracted/movies_metadata.csv /project/cinema/raw/tmdb/tmdb_revenue.csv

# 2e. Chạy tiến trình PySpark Batch (mất 2-3 phút)
./scripts/run_preprocessing.sh
```

*Kết quả: MongoDB sẽ có 3 collections: `movies`, `ratings`, `revenue` trong database `cinema_dw`.*

> 💡 **Kiểm tra dữ liệu sau khi xong:** Mở `mongosh cinema_dw --eval "db.movies.countDocuments()"` — phải thấy con số lớn hơn 0.

---

### ⚡ Giai đoạn 3: Khởi chạy Luồng Dữ liệu Real-time (Terminal 3 & 4)

Mô phỏng hàng nghìn người dùng đang đánh giá phim đồng thời, xử lý real-time.

**Terminal 3 — Bật Kafka Producer (giả lập user rating):**
```bash
source venv/bin/activate
./scripts/run_producer.sh
```
*Script đọc `ratings.csv` và bắn **1.000 rating/giây** lên Kafka topic `movie_ratings_stream`.*

**Terminal 4 — Bật PySpark Streaming Processor:**
```bash
source venv/bin/activate
./scripts/run_streaming.sh
```
*PySpark lắng nghe Kafka → Thực hiện **Stream-Static Join** với dữ liệu Revenue từ MongoDB → Tổng hợp metrics theo cửa sổ 30 giây → Đổ vào MongoDB `live_metrics`.*

---

### 🖥️ Giai đoạn 4: Mở Giao Diện BI Dashboard (Terminal 5)

```bash
source venv/bin/activate
./scripts/run_dashboard.sh
```

**🌐 Truy cập:** [`http://localhost:8501`](http://localhost:8501)

Tại thanh điều hướng bên trái, chuyển đổi mượt mà giữa 2 Dashboard:
- 📊 **Batch Analytics** — Phân tích dữ liệu tổng hợp (tĩnh), tải ngay lập tức nhờ Caching.
- 🎬 **Real-time Streaming** — Biểu đồ live cập nhật mỗi 5 giây, hiển thị Traffic và Revenue phim trending.

---

## 🔧 Xử Lý Sự Cố Thường Gặp

| Lỗi | Nguyên nhân | Cách khắc phục |
|:---|:---|:---|
| `Connection refused` (HDFS) | NameNode chưa bật | Chạy `jps` để kiểm tra. Nếu không có NameNode, thử `hdfs namenode -format -force` rồi bật lại |
| `Incompatible clusterID` | DataNode không đồng bộ | Xóa dữ liệu cũ: `rm -rf runtime/hdfs-store/datanode/*` rồi `hdfs --daemon start datanode` |
| `Revenue = 0` (Dashboard) | Streaming mới khởi động | Đợi 30-60 giây để Spark thu thập đủ data cho 1 batch đầu tiên |
| Batch reload chậm | Cache chưa được dùng | Đây là lần load đầu tiên. Các lần sau sẽ tải ngay lập tức |
| Kafka `Connection refused` | Kafka chưa bật | Quay lại Terminal 1 và chạy `./scripts/run_kafka.sh` |

---

## 📁 Cấu Trúc Thư Mục Dự Án

```
.
├── config/hadoop/          # Cấu hình HDFS (core-site.xml, hdfs-site.xml)
├── data/
│   ├── raw/                # Dữ liệu MovieLens thô (ratings.csv, movies.csv...)
│   └── raw/tmdb/           # Dữ liệu TMDB (movies_metadata.csv)
├── docs/                   # Tài liệu kỹ thuật chi tiết
├── runtime/
│   ├── checkpoints/        # Spark Streaming checkpoints
│   ├── hdfs-store/         # Dữ liệu HDFS (namenode, datanode)
│   └── kafka/              # Kafka binary
├── scripts/
│   ├── activate.sh         # Script thiết lập biến môi trường
│   ├── data_preprocessing.py   # PySpark Batch Job
│   ├── kafka_producer.py   # Giả lập user rating stream
│   ├── streaming_processor.py  # PySpark Structured Streaming
│   ├── run_kafka.sh        # Bật Kafka
│   ├── run_preprocessing.sh    # Chạy Batch Job
│   ├── run_producer.sh     # Chạy Producer
│   ├── run_streaming.sh    # Chạy Streaming Job
│   └── run_dashboard.sh    # Chạy Streamlit
└── visual/
    ├── app.py              # Entrypoint Streamlit
    └── dashboards/
        ├── batch.py        # Batch Analytics Dashboard
        └── streaming.py    # Real-time Streaming Dashboard
```

---

## 📚 Tài Liệu Kỹ Thuật Chi Tiết

Các tài liệu phân tích chuyên sâu nằm trong thư mục `docs/`:

| File | Nội dung |
|:---|:---|
| `01_dataset_overview.md` | Tổng quan bộ dữ liệu MovieLens 25M & TMDB |
| `02_schema_mapping.md` | Ánh xạ lược đồ dữ liệu giữa các nguồn |
| `03_join_strategy.md` | Chiến lược kết hợp dữ liệu trong PySpark |
| `04_hadoop_hdfs_setup.md` | Cài đặt và gỡ lỗi Hadoop HDFS trên macOS |
| `05_run_guide.md` | Hướng dẫn chạy và các câu lệnh thường dùng |
| `06_usage_guide.md` | Hướng dẫn sử dụng chi tiết hệ thống |
| `07_evidence_checklist.md` | Bảng kiểm tra minh chứng kỹ thuật |
| `08_data_preprocessing.md` | Phân tích quy trình Batch Processing |

---

*Stack: **Kafka** (Message Broker) · **HDFS** (Distributed Storage) · **PySpark** (Batch & Streaming) · **MongoDB** (Serving Layer) · **Streamlit + Plotly** (BI Dashboard)*


---

## 🛠️ Cài Đặt Môi Trường (Setup)

Dự án này được tối ưu để chạy hoàn toàn trên máy tính cá nhân (Local/Project) sử dụng macOS.

**1. Khởi tạo môi trường Python**
Mở terminal tại thư mục gốc dự án và chạy:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
*(Lưu ý: PySpark yêu cầu máy bạn đã cài sẵn **Java 17**)*

**2. Cài đặt các ứng dụng phụ trợ (macOS)**
```bash
# Cài đặt Hadoop (HDFS)
brew install hadoop

# Cài đặt MongoDB
brew tap mongodb/brew
brew install mongodb-community
```

---

## 🚀 Hướng Dẫn Chạy Demo Toàn Bộ Dự Án (End-to-End)

Để hệ thống hoạt động trơn tru từ A-Z, hãy làm theo đúng thứ tự 4 Giai đoạn (Phase) dưới đây. Hãy mở 4 cửa sổ Terminal riêng biệt để dễ dàng quản lý.

### Giai đoạn 1: Khởi động Hạ tầng (Terminal 1)
Chạy các nền tảng lưu trữ và trung chuyển dữ liệu:

**1. Bật hệ thống HDFS và MongoDB:**
```bash
# Bật HDFS NameNode và DataNode
source scripts/activate.sh
hdfs --daemon start namenode
hdfs --daemon start datanode

# Bật MongoDB
brew services start mongodb-community
```

**2. Cài đặt và bật Kafka (Chỉ chạy cài đặt lần đầu):**
```bash
# Tải và cài đặt Kafka vào thư mục runtime/ (chỉ chạy 1 lần)
./scripts/install_kafka.sh

# Khởi động Kafka Server (Sẽ chạy liên tục trên terminal này)
./scripts/run_kafka.sh
```

---

### Giai đoạn 2: Xử lý Dữ liệu Tĩnh / Batch (Terminal 2)
Giai đoạn này nạp dữ liệu thô MovieLens & TMDB vào HDFS, làm sạch bằng PySpark, và lưu vào MongoDB phục vụ cho Dashboard.

**1. Tạo thư mục trên HDFS:**
```bash
source scripts/activate.sh
hdfs dfs -mkdir -p /project/cinema/raw/movielens
hdfs dfs -mkdir -p /project/cinema/raw/tmdb
```

**2. Tải dữ liệu thô lên HDFS:**
```bash
# Đẩy dữ liệu MovieLens
hdfs dfs -put data/raw/*.csv /project/cinema/raw/movielens/

# Đẩy dữ liệu TMDB và đổi tên để code nhận diện đúng file doanh thu
hdfs dfs -put data/raw/tmdb/extracted/movies_metadata.csv /project/cinema/raw/tmdb/tmdb_revenue.csv
```

**3. Chạy tiến trình xử lý tự động (PySpark Batch):**
```bash
source venv/bin/activate
./scripts/run_preprocessing.sh
```
*Đợi khoảng 2-3 phút, hệ thống sẽ gộp dữ liệu, làm sạch và tạo ra collection `movies`, `ratings`, `revenue` trong MongoDB (`cinema_dw`).*

---

### Giai đoạn 3: Chạy Luồng Dữ liệu Thời gian thực / Streaming (Terminal 3 & 4)
Để mô phỏng hàng ngàn user đang đánh giá phim cùng lúc, chúng ta cần bật Producer bắn data, và Processor để xử lý data đó.

**1. Bật bộ mô phỏng dữ liệu (Kafka Producer) - Terminal 3:**
```bash
source venv/bin/activate
./scripts/run_producer.sh
```
*Script này sẽ đọc file `ratings.csv` và gửi liên tục lên topic `movie_ratings_stream`.*

**2. Bật bộ xử lý Streaming (PySpark Streaming) - Terminal 4:**
Mở thêm một Terminal mới và chạy:
```bash
source venv/bin/activate
./scripts/run_streaming.sh
```
*Tiến trình này sẽ lắng nghe Kafka, thực hiện Stream-Static Join (kết hợp rating streaming với revenue tĩnh từ MongoDB), tính toán các thông số theo cửa sổ thời gian (30 giây) và đổ dữ liệu sống vào MongoDB `live_metrics`.*

---

### Giai đoạn 4: Mở Giao diện BI Dashboard (Terminal 5)
Bước cuối cùng là khởi động ứng dụng Web để trực quan hóa dữ liệu.

```bash
source venv/bin/activate
./scripts/run_dashboard.sh
```

**Truy cập vào trình duyệt tại:** `http://localhost:8501`

Tại thanh điều hướng (Menu) bên trái, bạn có thể chuyển đổi mượt mà giữa:
*   📊 **Batch Analytics**: Phân tích dữ liệu tổng hợp (Phân bổ thể loại, Phân phối điểm, Tương quan mức độ tương tác - chất lượng). Nhờ công nghệ Caching, tab này load siêu tốc!
*   🎬 **Real-time Streaming**: Biểu đồ trực tiếp cập nhật mỗi 5 giây, hiển thị lưu lượng traffic thời gian thực và tổng doanh thu lũy kế (Cumulative Revenue) của các bộ phim đang trending.

---

## 📂 Cấu Trúc Tài Liệu Chi Tiết

Các tài liệu kỹ thuật chuyên sâu được phân tích và lưu trữ trong thư mục `docs/`:

- `01_dataset_overview.md`: Tổng quan bộ dữ liệu MovieLens & TMDB.
- `02_schema_mapping.md`: Ánh xạ lược đồ dữ liệu giữa các nguồn.
- `03_join_strategy.md`: Chiến lược kết hợp (join) dữ liệu trong PySpark.
- `04_hadoop_hdfs_setup.md`: Hướng dẫn cài đặt và gỡ lỗi Hadoop HDFS.
- `05_run_guide.md`: Các câu lệnh và môi trường chạy.
- `06_usage_guide.md`: Hướng dẫn sử dụng chi tiết hệ thống.
- `07_evidence_checklist.md`: Bảng kiểm tra minh chứng kỹ thuật.
- `08_data_preprocessing.md`: Phân tích quy trình Batch Processing.

---
*Dự án kết hợp Kafka, HDFS, MongoDB, PySpark và Streamlit để xây dựng giải pháp Data Analytics hoàn chỉnh.*
