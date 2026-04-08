# 5. Hướng Dẫn Chạy

## 5.1 Mục đích

Tài liệu này mô tả chính xác các bước chạy môi trường Java, Hadoop và HDFS cục bộ cho Mục 1.

**Tất cả lệnh đều chạy trong WSL Ubuntu.**

## 5.2 Mở dự án trong WSL

```bash
cd /mnt/d/Daihoc/Nam3/AnalysisBigdata/BTL/Big-Data-Analytics_BI-Assigntment_Data-Driven-Cinema-Management
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

## 5.5 Giải nén Java nếu chưa có

```bash
mkdir -p runtime/java

tar -xzf runtime/downloads/OpenJDK11U-jdk_x64_linux_hotspot_*.tar.gz -C runtime/java --strip-components=1
```

## 5.6 Giải nén Hadoop nếu chưa có

```bash
mkdir -p runtime/hadoop

tar -xzf runtime/downloads/hadoop-3.4.3.tar.gz -C runtime/hadoop --strip-components=1
```

## 5.7 Format HDFS (chỉ cho lần đầu)

```bash
hdfs namenode -format
```

Lưu ý:

- chỉ chạy một lần cho lần khởi tạo đầu tiên
- không chạy lại khi NameNode đang hoạt động

## 5.8 Khởi động HDFS local

```bash
hdfs --daemon start namenode
hdfs --daemon start datanode
jps
```

Kết quả kỳ vọng:

- `NameNode`
- `DataNode`

## 5.9 Tạo thư mục HDFS cho dự án

```bash
hdfs dfs -mkdir -p /project/cinema/raw/movielens
hdfs dfs -mkdir -p /project/cinema/raw/tmdb
```

## 5.10 Tải dữ liệu MovieLens raw lên HDFS

Nếu dữ liệu đã nằm trong `data/raw/`:

```bash
hdfs dfs -put data/raw/* /project/cinema/raw/movielens/
```

## 5.11 Kiểm tra dữ liệu đã nạp lên

```bash
hdfs dfs -ls /project/cinema/raw/movielens
hdfs dfs -du -h /project/cinema/raw/movielens
```

## 5.12 Lưu log minh chứng

```bash
mkdir -p artifacts/terminal_logs
hdfs dfs -ls /project/cinema/raw/movielens > artifacts/terminal_logs/hdfs_movielens_ls.txt 2>&1
hdfs dfs -du -h /project/cinema/raw/movielens > artifacts/terminal_logs/hdfs_movielens_du.txt 2>&1
jps > artifacts/terminal_logs/jps_after_start.txt
```

## 5.13 Dừng HDFS sau khi sử dụng

```bash
hdfs --daemon stop datanode
hdfs --daemon stop namenode
jps
```

## 5.14 Tóm tắt workflow chuẩn

- mở WSL Ubuntu
- vào thư mục dự án
- chạy `source scripts/activate.sh`
- kiểm tra Java và Hadoop
- format HDFS nếu là lần đầu
- khởi động HDFS
- nạp dữ liệu raw lên HDFS
- kiểm tra dữ liệu và lưu log
- dừng HDFS khi hoàn tất
