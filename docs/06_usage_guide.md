# 6. Hướng Dẫn Sử Dụng (macOS)

## 6.1 Mục đích

Tài liệu này giải thích cách sử dụng lại môi trường Mục 1 sau khi đã cài đặt xong trên **macOS**.

## 6.2 Các vị trí quan trọng

- Môi trường cài đặt Java / Hadoop: Sử dụng Homebrew
- HDFS local storage: `runtime/hdfs-store`
- cấu hình Hadoop: `config/hadoop`
- dữ liệu raw local: `data/raw/`
- dữ liệu raw trên HDFS: `/project/cinema/raw/movielens`

## 6.3 Mỗi lần mở terminal mới cần làm gì

### Bước 1: mở Terminal và vào project

```bash
cd /Users/truongnhatthanh/Downloads/Big-Data-Analytics_BI-Assigntment_Data-Driven-Cinema-Management
```

### Bước 2: kích hoạt môi trường local

```bash
source scripts/activate.sh
```

### Bước 3: kiểm tra runtime

```bash
java -version
hadoop version
hdfs version
```

## 6.4 Cách dùng HDFS local

### Khởi động

```bash
hdfs --daemon start namenode
hdfs --daemon start datanode
jps
```

### Kiểm tra dữ liệu raw trong HDFS

```bash
hdfs dfs -ls /project/cinema/raw/movielens
hdfs dfs -du -h /project/cinema/raw/movielens
```

### Dừng HDFS

```bash
hdfs --daemon stop datanode
hdfs --daemon stop namenode
jps
```

## 6.5 Khi nào cần tải lại dữ liệu raw

Chỉ cần tải lại nếu:

- bạn đã xoá hoặc thay đổi thư mục `runtime/hdfs-store/`
- bạn đã format lại NameNode
- thư mục `/project/cinema/raw/movielens` hoặc `tmdb` không còn dữ liệu trong HDFS

Lúc đó chạy lại:

```bash
hdfs dfs -mkdir -p /project/cinema/raw/movielens
hdfs dfs -mkdir -p /project/cinema/raw/tmdb
hdfs dfs -put data/raw/movies.csv data/raw/ratings.csv data/raw/links.csv data/raw/tags.csv data/raw/genome*.csv /project/cinema/raw/movielens/
hdfs dfs -put data/raw/tmdb_*.csv /project/cinema/raw/tmdb/
```

## 6.6 Lưu ý quan trọng

- Tất cả lệnh được chuẩn hóa cho terminal của macOS.
- Nếu gặp lỗi bộ nhớ với HDFS, cân nhắc kiểm tra Java Homebrew `/opt/homebrew/`.
- Lệnh `hdfs namenode -format` không nên chạy lại nếu không có chủ đích reset toàn bộ HDFS.

## 6.7 Tóm tắt sử dụng hằng ngày

- mở Terminal
- vào thư mục project
- kích hoạt local env
- khởi động HDFS nếu cần 
- kiểm tra dữ liệu raw trong HDFS
- tiếp tục sang các mục sau của dự án (ví dụ Data Preprocessing)
