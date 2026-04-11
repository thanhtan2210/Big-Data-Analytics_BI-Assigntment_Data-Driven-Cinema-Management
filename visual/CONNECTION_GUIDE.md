# Hướng Dẫn Kết Nối Power BI với MongoDB & Spark

> Có **2 cách** để đưa dữ liệu từ pipeline vào Power BI.  
> **Khuyến nghị:** dùng Cách 2 (CSV export) — đơn giản hơn, không cần cài thêm connector.

---

## Kiến trúc tổng quan

```
dataset/ml-25m/*.csv
        │
        ▼
   [Phase 1]  HDFS Ingestion
        │
        ▼
   [Phase 2]  PySpark Preprocessing
        │         → movies_enriched        ─┐
        ▼                                   │
   [Phase 3]  Analytics + ALS              │  MongoDB (cinema_db)
        │         → genre_stats             │
        │         → decade_stats            │
        │         → year_stats             ─┘
        │         → rating_dist
        │         → user_segments
        │         → segment_genre_preference
        │         → tag_stats
        │         → segment_recommendations
        ▼
   [Phase 4]  Export  ──►  visual/exports/*.csv  ──►  Power BI
```

---

## Cách 1 — Import CSV (Đơn giản, Khuyến nghị)

### Bước 1: Chạy Phase 4 export

Sau khi MongoDB đã có dữ liệu (Phase 1–3 hoàn tất):

```bash
# Cần: pip install pymongo pandas
python pipeline/phase4_export.py
```

File CSV được tạo tại `visual/exports/`:

| File CSV                       | Collection MongoDB       | Dùng cho Dashboard |
| ------------------------------ | ------------------------ | ------------------ |
| `movies_enriched.csv`          | movies_enriched          | 1, 3               |
| `genre_stats.csv`              | genre_stats              | 1, 2               |
| `decade_genre_heatmap.csv`     | decade_stats             | 1, 2               |
| `year_stats.csv`               | year_stats               | 2                  |
| `rating_distribution.csv`      | rating_dist              | 2                  |
| `user_segments.csv`            | user_segments            | 3                  |
| `segment_genre_preference.csv` | segment_genre_preference | 3                  |
| `tag_stats.csv`                | tag_stats                | 3                  |
| `segment_recommendations.csv`  | segment_recommendations  | 3                  |

### Bước 2: Import vào Power BI

1. Mở **Power BI Desktop**
2. **Home → Get Data → Text/CSV**
3. Chọn file đầu tiên trong `visual/exports/`
4. Click **Load** (không cần Transform)
5. Lặp lại cho từng file CSV
6. Vào **Model view** → tạo relationships theo sơ đồ trong [DASHBOARDS.md](DASHBOARDS.md)

### Refresh dữ liệu

Khi pipeline chạy lại và xuất CSV mới:

- Power BI Desktop: **Home → Refresh**
- Power BI Service: cần publish lại file `.pbix` hoặc dùng Personal Gateway

---

## Cách 2 — Kết nối trực tiếp MongoDB Connector

> Yêu cầu: **Power BI Desktop** phiên bản ≥ March 2021 và MongoDB Atlas / local server đang chạy.

### Bước 1: Cài MongoDB Connector

Power BI không có MongoDB connector built-in. Hai lựa chọn:

**Option A — MongoDB Atlas SQL Interface (Production):**

1. Đăng ký [MongoDB Atlas](https://www.mongodb.com/atlas) (free tier 512MB)
2. Tạo cluster → import data
3. Trong Atlas: **Data API** → enable Atlas SQL
4. Trong Power BI: **Get Data → ODBC** → dùng Atlas ODBC driver

**Option B — Local MongoDB qua Web Data Connector (Dev):**

MongoDB có thể export sang JSON endpoint qua script Python đơn giản:

```python
# Chạy: python pipeline/phase4_export.py
# Hoặc expose REST API tạm thời:
from flask import Flask, jsonify
from pymongo import MongoClient
import config

app = Flask(__name__)
client = MongoClient(config.MONGO_URI)
db = client[config.MONGO_DB]

@app.route("/api/<collection>")
def get_collection(collection):
    docs = list(db[collection].find({}, {"_id": 0}))
    return jsonify(docs)

if __name__ == "__main__":
    app.run(port=5000)
```

Sau đó trong Power BI: **Get Data → Web → http://localhost:5000/api/genre_stats**

> ⚠️ REST API này chỉ dùng trong môi trường local phát triển, không expose ra internet.

### Bước 2: Kết nối trong Power BI

```
Get Data
  → Other
    → ODBC
      → DSN: MongoDB Atlas ODBC
        → Database: cinema_db
          → Select tables (collections):
              ☑ genre_stats
              ☑ movies_enriched
              ☑ decade_stats
              ...
```

---

## Cách 3 — Kết nối PySpark qua JDBC/ODBC

> Dùng khi cần query trực tiếp HDFS (không qua MongoDB).

### Yêu cầu

- Apache Spark đang chạy (local hoặc Docker)
- Spark Thrift Server đang bật (cung cấp JDBC endpoint)

### Bật Spark Thrift Server

```bash
# Trong container spark-master hoặc local Spark:
$SPARK_HOME/sbin/start-thriftserver.sh \
  --hiveconf hive.server2.thrift.port=10000 \
  --master local[*]
```

### Kết nối Power BI

1. Power BI → **Get Data → More → Spark** (hoặc **Hive LLAP**)
2. Server: `localhost:10000`
3. Protocol: `HTTP`
4. Nhập Spark SQL query:

```sql
-- Ví dụ lấy genre_stats từ Spark SQL view
SELECT genre, avg_rating, total_revenue, rating_count
FROM genre_stats
ORDER BY total_revenue DESC
```

---

## Schemas của các collection MongoDB

### `movies_enriched`

| Cột           | Kiểu   | Mô tả                         |
| ------------- | ------ | ----------------------------- |
| movieId       | int    | MovieLens ID                  |
| title         | string | Tên gốc (có năm)              |
| title_clean   | string | Tên đã bỏ năm                 |
| year          | int    | Năm phát hành                 |
| decade        | int    | Thập kỷ (1990, 2000...)       |
| genres        | string | Pipe-separated genres         |
| genres_array  | array  | ["Action", "Drama", ...]      |
| avg_rating    | float  | Trung bình rating (MovieLens) |
| rating_count  | int    | Số lượt đánh giá              |
| rating_stddev | float  | Độ lệch chuẩn rating          |
| imdbId        | string | IMDB ID                       |
| tmdbId        | string | TMDB ID                       |
| revenue       | float  | Doanh thu (USD, từ TMDB)      |
| budget        | float  | Ngân sách (USD, từ TMDB)      |
| roi           | float  | (revenue-budget)/budget       |

### `genre_stats`

| Cột           | Kiểu   | Mô tả                |
| ------------- | ------ | -------------------- |
| genre         | string | Tên genre            |
| avg_rating    | float  | Rating trung bình    |
| rating_count  | long   | Tổng số lượt rating  |
| movie_count   | long   | Số phim thuộc genre  |
| total_revenue | double | Tổng doanh thu TMDB  |
| avg_revenue   | double | Doanh thu trung bình |
| avg_budget    | double | Budget trung bình    |
| avg_roi       | double | ROI trung bình       |

### `decade_stats`

| Cột          | Kiểu   | Mô tả               |
| ------------ | ------ | ------------------- |
| decade       | int    | Thập kỷ             |
| genre        | string | Tên genre           |
| avg_rating   | float  | Rating trung bình   |
| rating_count | long   | Số lượt rating      |
| avg_revenue  | double | Doanh thu TB (TMDB) |
| movie_count  | long   | Số phim             |

### `year_stats`

| Cột          | Kiểu  | Mô tả                    |
| ------------ | ----- | ------------------------ |
| rating_year  | int   | Năm rating               |
| rating_count | long  | Số lượt rating trong năm |
| avg_rating   | float | Rating TB trong năm      |
| active_users | long  | Số user unique trong năm |

### `rating_dist`

| Cột       | Kiểu  | Mô tả                      |
| --------- | ----- | -------------------------- |
| rating    | float | Giá trị rating (0.5 → 5.0) |
| frequency | long  | Số lần xuất hiện           |

### `user_segments`

| Cột                 | Kiểu   | Mô tả                        |
| ------------------- | ------ | ---------------------------- |
| userId              | int    | User ID (ẩn danh)            |
| segment             | string | "Heavy" / "Medium" / "Light" |
| rating_count        | long   | Tổng số phim đã rating       |
| avg_rating          | float  | Rating TB của user           |
| unique_movies_rated | long   | Số phim unique đã xem        |

### `segment_genre_preference`

| Cột          | Kiểu   | Mô tả                        |
| ------------ | ------ | ---------------------------- |
| segment      | string | Heavy / Medium / Light       |
| genre        | string | Tên genre                    |
| rating_count | long   | Lượt rating trong segment    |
| avg_rating   | float  | Rating TB segment × genre    |
| genre_rank   | int    | Xếp hạng genre trong segment |

### `tag_stats`

| Cột       | Kiểu   | Mô tả           |
| --------- | ------ | --------------- |
| tag       | string | Tag (lowercase) |
| frequency | long   | Số lần được gán |

### `segment_recommendations`

| Cột                  | Kiểu   | Mô tả                            |
| -------------------- | ------ | -------------------------------- |
| segment              | string | Heavy / Medium / Light           |
| movieId              | int    | MovieLens ID                     |
| avg_predicted_rating | float  | Rating dự đoán TB trong segment  |
| recommended_to_users | long   | Số user trong segment được gợi ý |
| rank                 | int    | Thứ hạng trong segment (1–10)    |
| title_clean          | string | Tên phim                         |
| genres_array         | array  | Genres của phim                  |
| avg_rating           | float  | Rating thực tế trung bình        |

---

## Troubleshooting

| Vấn đề                           | Nguyên nhân                           | Giải pháp                                                      |
| -------------------------------- | ------------------------------------- | -------------------------------------------------------------- |
| CSV trống                        | Phase 3 chưa chạy xong                | Kiểm tra MongoDB collection có data chưa                       |
| `genres_array` là string "[...]" | pandas không flatten được             | Dùng `\|` delimiter — cột `genres` (không phải `genres_array`) |
| revenue = null                   | TMDB CSV chưa đặt vào `dataset/tmdb/` | Đặt file Kaggle TMDB tại đúng path                             |
| Power BI refresh lỗi             | CSV path thay đổi                     | Data Source Settings → update path                             |
| MongoDB connection refused       | MongoDB chưa chạy                     | `docker compose up -d mongodb`                                 |
