# Data Preprocessing Summary

## 1. Final Output (Terminal Logs)
Đây là output cuối cùng của quá trình preprocessing (PySpark):

```text
Loading TMDB Revenue data ...
TMDB Revenue file found: tmdb_revenue.csv
Cleaning data ...
Removing outliers ...
Merging MovieLens and TMDB ...
Pushing cleaned data to MongoDB ...
=====================================================
      Data Preprocessing Pipeline Completed!
=====================================================
============================================================
    Hoàn tất script runner.
============================================================
```

## 2. Số bản ghi của các bảng (MongoDB Collections)
Dữ liệu đã được merge, làm sạch và lưu trữ vào database `cinema_dw` trên MongoDB. Số lượng bản ghi cho các bảng như sau:

- **movies**: `62,423` bản ghi
- **revenue**: `62,423` bản ghi
- **ratings**: `20,555,215` bản ghi
- **tags**: `1,093,360` bản ghi

## 3. Command đã sử dụng
Chạy lệnh shell để bắt đầu pipeline:
```bash
./scripts/run_preprocessing.sh
```

Trong file script này, thực chất lệnh đã gọi `spark-submit` với thông số cấu hình sau:
```bash
spark-submit \
  --master local[*] \
  --packages org.mongodb.spark:mongo-spark-connector_2.13:11.0.1 \
  "$PROJECT_ROOT/scripts/data_preprocessing.py"
```

## 4. Configuration đã sử dụng
Data Preprocessing job đã lấy thông tin cấu hình từ biến môi trường (file `.env` hoặc giá trị mặc định) như sau:

- **HDFS Environment**:
  - `HDFS_HOST`: `localhost`
  - `HDFS_PORT`: `9000`
  - `PROJECT_HDFS_RAW_MOVIELENS`: `/project/cinema/raw/movielens`
  - `PROJECT_HDFS_RAW_TMDB`: `/project/cinema/raw/tmdb`
  
- **MongoDB Environment**:
  - `MONGO_URI`: `mongodb://127.0.0.1:27017/`
  - `MONGO_DB`: `cinema_dw`
