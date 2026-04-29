# 6. Hướng Dẫn Sử Dụng

## 6.1 Mục đích

Tài liệu này giải thích cách sử dụng lại môi trường Mục 1 sau khi đã cài đặt xong.

Tất cả thao tác đều thực hiện trong **WSL Ubuntu**.

## 6.2 Các vị trí quan trọng

- Java local: `runtime/java`
- Hadoop local: `runtime/hadoop`
- HDFS local: `runtime/hdfs-store`
- cấu hình Hadoop: `config/hadoop`
- dữ liệu raw local MovieLens: `data/raw/`
- dữ liệu raw local TMDB: `data/raw/tmdb/extracted/`
- dữ liệu raw trên HDFS MovieLens: `/project/cinema/raw/movielens`
- dữ liệu raw trên HDFS TMDB: `/project/cinema/raw/tmdb`

## 6.3 Mỗi lần mở terminal mới cần làm gì

### Bước 1: mở WSL và vào project

```bash
cd /mnt/d/Daihoc/Nam3/AnalysisBigdata/BTL/Big-Data-Analytics_BI-Assigntment_Data-Driven-Cinema-Management
```

### Bước 2: kích hoạt môi trường local

```bash
source scripts/activate.sh
```

### Bước 3: kiểm tra runtime nếu cần

```bash
java -version
hadoop version
hdfs version
```

## 6.4 Khi nào cần khởi động HDFS

Cần khởi động HDFS khi bạn muốn:
- kiểm tra dữ liệu raw trên HDFS
- upload lại raw data
- chuẩn bị sang bước preprocessing ở Mục 2

Khởi động bằng:

```bash
bash scripts/start_hdfs.sh
```

## 6.5 Khi nào cần tải lại dữ liệu raw

Chỉ cần tải lại khi:
- HDFS bị reset hoặc format lại
- file trên HDFS bị xóa
- bạn muốn nạp lại dữ liệu từ local

### Upload lại TMDB raw
```bash
bash scripts/upload_tmdb.sh
```

### Kiểm tra lại toàn bộ raw data
```bash
bash scripts/check_hdfs_raw.sh
```

## 6.6 Các file TMDB local cần có

Trong thư mục:

```text
data/raw/tmdb/extracted/
```

cần có:
- `movies_metadata.csv`
- `credits.csv`
- `keywords.csv`

## 6.7 Các file log quan trọng

Lưu trong:

```text
artifacts/terminal_logs/
```

Bao gồm:
- `hdfs_format.txt`
- `hdfs_movielens_ls.txt`
- `hdfs_movielens_du.txt`
- `hdfs_tmdb_ls.txt`
- `hdfs_tmdb_du.txt`
- `jps_after_start.txt`

## 6.8 Dừng HDFS khi xong

```bash
bash scripts/stop_hdfs.sh
```

## 6.9 Kết luận

Mô hình sử dụng Mục 1 rất đơn giản:

1. mở WSL
2. vào project
3. `source scripts/activate.sh`
4. start HDFS nếu cần
5. kiểm tra hoặc upload raw data
6. stop HDFS khi hoàn tất
