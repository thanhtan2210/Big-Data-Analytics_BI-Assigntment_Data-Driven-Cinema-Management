# 6. Hướng Dẫn Sử Dụng

## 6.1 Mục đích

Tài liệu này giải thích cách sử dụng lại môi trường Mục 1 sau khi đã cài đặt xong.

## 6.2 Các vị trí quan trọng

- Java local: `runtime/java`
- Hadoop local: `runtime/hadoop`
- HDFS local: `runtime/hdfs-store`
- cấu hình Hadoop: `config/hadoop`
- dữ liệu raw local: `data/raw/`
- dữ liệu raw trên HDFS: `/project/cinema/raw/movielens`

## 6.3 Mỗi lần mở terminal mới cần làm gì

### Bước 1: mở WSL và vào project

```bash
cd /mnt/d/Daihoc/Nam3/AnalysisBigdata/BTL/Big-Data-Analytics_BI-Assigntment_Data-Driven-Cinema-Management
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

- bạn đã reset HDFS
- bạn đã format lại NameNode
- thư mục `/project/cinema/raw/movielens` không còn dữ liệu

Lúc đó chạy lại:

```bash
hdfs dfs -mkdir -p /project/cinema/raw/movielens
hdfs dfs -put data/raw/* /project/cinema/raw/movielens/
```

## 6.6 Lưu ý quan trọng

- tất cả lệnh phải chạy trong WSL Ubuntu
- không dùng PowerShell để chạy lệnh Hadoop của project này
- không giải nén file `.tar.gz` bằng Windows Explorer
- nên giải nén Java và Hadoop bằng `tar -xzf ...` trong WSL
- lệnh `hdfs namenode -format` không nên chạy lại nếu không có chủ đích reset toàn bộ HDFS

## 6.7 Tóm tắt sử dụng hằng ngày

- mở WSL
- vào project
- kích hoạt local env
- khởi động HDFS nếu cần
- kiểm tra dữ liệu raw trong HDFS
- tiếp tục sang các mục sau của dự án
