# 7. Danh Sách Kiểm Tra Minh Chứng

## 7.1 Minh chứng dữ liệu

- [x] đã tải bộ dữ liệu MovieLens 25M
- [x] đã giải nén dữ liệu raw vào `data/raw/`
- [x] có các tệp:
  - `ratings.csv`
  - `movies.csv`
  - `tags.csv`
  - `links.csv`
  - `genome-scores.csv`
  - `genome-tags.csv`
  - `README.txt`

## 7.2 Minh chứng môi trường

- [x] chạy trong **WSL Ubuntu**
- [x] Java local nằm trong `runtime/java`
- [x] Hadoop local nằm trong `runtime/hadoop`
- [x] HDFS local nằm trong `runtime/hdfs-store`
- [x] môi trường được kích hoạt bằng `source scripts/activate.sh`

## 7.3 Minh chứng runtime

- [x] `java -version`
- [x] `hadoop version`
- [x] `hdfs version`
- [x] `jps`

## 7.4 Minh chứng HDFS

- [x] đã format HDFS thành công
- [x] NameNode đã chạy
- [x] DataNode đã chạy
- [x] đã tạo thư mục `/project/cinema/raw/movielens`
- [x] đã nạp dữ liệu MovieLens raw lên HDFS

## 7.5 Lệnh kiểm tra cần lưu

- [x] `hdfs dfs -ls /project/cinema/raw/movielens`
- [x] `hdfs dfs -du -h /project/cinema/raw/movielens`

## 7.6 Các file log cần có

Trong `artifacts/terminal_logs/` nên có:

- [x] `hdfs_format.txt`
- [x] `hdfs_movielens_ls.txt`
- [x] `hdfs_movielens_du.txt`
- [x] `jps_after_start.txt`

## 7.7 Ảnh chụp màn hình khuyến nghị

- [x] `java -version`
- [x] `hadoop version`
- [x] `jps`
- [x] `hdfs dfs -ls /project/cinema/raw/movielens`
- [x] `hdfs dfs -du -h /project/cinema/raw/movielens`

## 7.8 Tiêu chí hoàn thành Mục 1

Mục 1 được xem là hoàn thành khi:

- [x] bộ dữ liệu raw đã được thu thập
- [x] cấu trúc dữ liệu đã được mô tả
- [x] chiến lược join đã được tài liệu hóa
- [x] Java và Hadoop local đã được chuẩn bị
- [x] HDFS single-node local đã được cấu hình
- [x] dữ liệu raw đã được nạp thành công vào HDFS
- [x] log và ảnh chụp màn hình đã được lưu giữ
