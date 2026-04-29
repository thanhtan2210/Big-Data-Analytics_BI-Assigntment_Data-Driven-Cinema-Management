# 7. Danh Sách Kiểm Tra Minh Chứng

## 7.1 Mục đích

Danh sách này dùng để xác nhận Mục 1 đã hoàn tất cả về kỹ thuật lẫn tài liệu.

## 7.2 Minh chứng dữ liệu MovieLens

- [x] dữ liệu raw MovieLens có trong `data/raw/`
- [x] các file đã có:
  - `ratings.csv`
  - `movies.csv`
  - `tags.csv`
  - `links.csv`
  - `genome-scores.csv`
  - `genome-tags.csv`
  - `README.txt`

## 7.3 Minh chứng dữ liệu TMDB

- [x] dữ liệu raw TMDB có trong `data/raw/tmdb/extracted/`
- [x] các file đã có:
  - `movies_metadata.csv`
  - `credits.csv`
  - `keywords.csv`

## 7.4 Minh chứng môi trường

- [x] project chạy trong **WSL Ubuntu**
- [x] Java local được lưu trong `runtime/java`
- [x] Hadoop local được lưu trong `runtime/hadoop`
- [x] HDFS local được lưu trong `runtime/hdfs-store`
- [x] môi trường được kích hoạt bằng `source scripts/activate.sh`

## 7.5 Minh chứng runtime

- [x] `java -version`
- [x] `hadoop version`
- [x] `hdfs version`
- [x] `jps`

## 7.6 Minh chứng HDFS cho MovieLens

- [x] `hdfs dfs -ls /project/cinema/raw/movielens`
- [x] `hdfs dfs -du -h /project/cinema/raw/movielens`

## 7.7 Minh chứng HDFS cho TMDB

- [x] `hdfs dfs -ls /project/cinema/raw/tmdb`
- [x] `hdfs dfs -du -h /project/cinema/raw/tmdb`

## 7.8 Log cần lưu giữ

Trong `artifacts/terminal_logs/` cần có:
- [x] `hdfs_format.txt`
- [x] `hdfs_movielens_ls.txt`
- [x] `hdfs_movielens_du.txt`
- [x] `hdfs_tmdb_ls.txt`
- [x] `hdfs_tmdb_du.txt`
- [x] `jps_after_start.txt`

## 7.9 Ảnh chụp màn hình cần lưu giữ

Trong `artifacts/screenshots/` nên có:
- [x] ảnh `java -version`
- [x] ảnh `hadoop version`
- [x] ảnh `jps`
- [x] ảnh `hdfs dfs -ls /project/cinema/raw/movielens`
- [x] ảnh `hdfs dfs -du -h /project/cinema/raw/movielens`
- [x] ảnh `hdfs dfs -ls /project/cinema/raw/tmdb`
- [x] ảnh `hdfs dfs -du -h /project/cinema/raw/tmdb`

## 7.10 Điều kiện hoàn thành Mục 1

Mục 1 được xem là hoàn thành khi:

- [x] MovieLens raw đã được thu thập
- [x] TMDB raw đã được thu thập
- [x] cấu trúc dữ liệu đã được mô tả
- [x] chiến lược join đã được xác định
- [x] Hadoop/HDFS local đã được cấu hình
- [x] MovieLens raw đã được nạp lên HDFS
- [x] TMDB raw đã được nạp lên HDFS
- [x] log và screenshot đã được lưu giữ

## 7.11 Kết luận

Mục 1 hiện đã hoàn thành đầy đủ phần:
- data collection
- data understanding
- raw data storage in HDFS
