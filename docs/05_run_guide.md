# 5. Hướng Dẫn Chạy (macOS)

## 5.1 Mục đích

Tài liệu này mô tả chính xác các bước chạy môi trường Java, Hadoop và HDFS cục bộ cho Mục 1 trên hệ điều hành **macOS**.

**Tất cả lệnh đều chạy trong terminal của macOS.**

## 5.2 Mở dự án trong Terminal

```bash
cd /Users/truongnhatthanh/Downloads/Big-Data-Analytics_BI-Assigntment_Data-Driven-Cinema-Management
```

## 5.3 Kích hoạt môi trường local

```bash
source scripts/activate.sh
```

## 5.4 Kiểm tra Java và Hadoop

```bash
java -version
hadoop version
hdfs version
```

## 5.5 Format HDFS (chỉ cho lần đầu)

```bash
hdfs namenode -format
```

Lưu ý:

- chỉ chạy một lần cho lần khởi tạo đầu tiên (hoặc khi cần dọn sạch HDFS)
- không chạy lại khi NameNode đang hoạt động và đang lưu dữ liệu.

## 5.6 Khởi động HDFS local

```bash
hdfs --daemon start namenode
hdfs --daemon start datanode
jps
```

Kết quả kỳ vọng khi chạy lệnh jps:

- `NameNode`
- `DataNode`

## 5.7 Tạo thư mục HDFS cho dự án

```bash
hdfs dfs -mkdir -p /project/cinema/raw/movielens
hdfs dfs -mkdir -p /project/cinema/raw/tmdb
```

## 5.8 Tải dữ liệu MovieLens và TMDB raw lên HDFS

Nếu dữ liệu đã nằm trong `data/raw/`:

```bash
hdfs dfs -put data/raw/movies.csv data/raw/ratings.csv data/raw/links.csv data/raw/tags.csv data/raw/genome*.csv /project/cinema/raw/movielens/
hdfs dfs -put data/raw/tmdb_*.csv /project/cinema/raw/tmdb/
```

## 5.9 Kiểm tra dữ liệu đã nạp lên

```bash
hdfs dfs -ls /project/cinema/raw/movielens
hdfs dfs -du -h /project/cinema/raw/movielens
```

## 5.10 Lưu log minh chứng

```bash
mkdir -p artifacts/terminal_logs
hdfs dfs -ls /project/cinema/raw/movielens > artifacts/terminal_logs/hdfs_movielens_ls.txt 2>&1
hdfs dfs -du -h /project/cinema/raw/movielens > artifacts/terminal_logs/hdfs_movielens_du.txt 2>&1
jps > artifacts/terminal_logs/jps_after_start.txt
```

## 5.11 Dừng HDFS sau khi sử dụng

```bash
hdfs --daemon stop datanode
hdfs --daemon stop namenode
jps
```

## 5.12 Tóm tắt workflow chuẩn

- mở Terminal macOS
- vào thư mục dự án
- chạy `source scripts/activate.sh`
- kiểm tra Java và Hadoop
- format HDFS nếu là lần đầu thiết lập
- khởi động HDFS
- nạp dữ liệu raw lên HDFS
- kiểm tra dữ liệu và lưu log minh chứng
- dừng HDFS khi hoàn tất thao tác ngày hôm đó
