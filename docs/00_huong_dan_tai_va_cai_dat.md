# 0. Hướng Dẫn Tải Dữ Liệu Và Cài Đặt Môi Trường

## 0.1 Mục đích

Tài liệu này mô tả cách tải bộ dữ liệu, bố trí tệp trong project, cài đặt môi trường local và chuẩn bị Hadoop/HDFS cho Mục 1 của dự án.

Toàn bộ quy trình được thực hiện trong **WSL Ubuntu**, trong khi thư mục project được lưu trên ổ `D:` của Windows.

## 0.2 Đường dẫn project

Đường dẫn project trong WSL:

```bash
/mnt/d/Daihoc/Nam3/AnalysisBigdata/BTL/Big-Data-Analytics_BI-Assigntment_Data-Driven-Cinema-Management
```

## 0.3 Các nguồn dữ liệu dùng trong Mục 1

### MovieLens 25M
Nguồn tải:
- Trang chính: https://grouplens.org/datasets/movielens/25m/
- File zip trực tiếp: https://files.grouplens.org/datasets/movielens/ml-25m.zip

### TMDB-side dataset từ Kaggle
Nguồn tải:
- The Movies Dataset: https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset

Trong Mục 1, các tệp TMDB raw được dùng là:
- `movies_metadata.csv`
- `credits.csv`
- `keywords.csv`

## 0.4 Cấu trúc thư mục dữ liệu local

### MovieLens raw
Các tệp MovieLens raw được đặt trực tiếp trong:

```text
data/raw/
```

Bao gồm:
- `ratings.csv`
- `movies.csv`
- `tags.csv`
- `links.csv`
- `genome-scores.csv`
- `genome-tags.csv`
- `README.txt`

### TMDB raw
Các tệp TMDB raw được đặt trong:

```text
data/raw/tmdb/extracted/
```

Bao gồm:
- `movies_metadata.csv`
- `credits.csv`
- `keywords.csv`

Nếu có file nén gốc, có thể lưu trong:

```text
data/raw/tmdb/zip/
```

## 0.5 Java local theo project

Java được đặt trong:

```text
runtime/java/
```

Project sử dụng Java local thay vì cài đặt toàn hệ thống.

## 0.6 Hadoop local theo project

Hadoop được đặt trong:

```text
runtime/hadoop/
```

Project sử dụng Hadoop local thay vì cài đặt toàn hệ thống.

## 0.7 HDFS local theo project

Vùng lưu trữ HDFS local được đặt trong:

```text
runtime/hdfs-store/
```

Các thư mục con:
- `runtime/hdfs-store/tmp`
- `runtime/hdfs-store/namenode`
- `runtime/hdfs-store/datanode`

## 0.8 Kích hoạt môi trường local

Mỗi lần mở terminal mới trong WSL, cần chạy:

```bash
cd /mnt/d/Daihoc/Nam3/AnalysisBigdata/BTL/Big-Data-Analytics_BI-Assigntment_Data-Driven-Cinema-Management
source scripts/activate.sh
```

## 0.9 Kiểm tra runtime

```bash
java -version
hadoop version
hdfs version
```

## 0.10 Các script hỗ trợ

Trong thư mục `scripts/` hiện có:

- `activate.sh`
- `start_hdfs.sh`
- `stop_hdfs.sh`
- `upload_tmdb.sh`
- `check_hdfs_raw.sh`

## 0.11 Quy trình tổng quát của Mục 1

1. tải MovieLens 25M
2. đặt file raw vào `data/raw/`
3. tải TMDB-side dataset
4. đặt `movies_metadata.csv`, `credits.csv`, `keywords.csv` vào `data/raw/tmdb/extracted/`
5. kích hoạt môi trường local
6. khởi động HDFS
7. nạp MovieLens raw lên HDFS
8. nạp TMDB raw lên HDFS
9. kiểm tra lại dữ liệu trên HDFS
10. lưu log và ảnh minh chứng

## 0.12 Kết quả mong đợi

Sau khi hoàn thành Mục 1, project phải có:

- dữ liệu MovieLens raw local
- dữ liệu TMDB raw local
- Java local
- Hadoop local
- HDFS local
- raw MovieLens trên HDFS
- raw TMDB trên HDFS
- docs, log và ảnh minh chứng đầy đủ
