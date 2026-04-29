# 4. Thiết Lập Hadoop và HDFS

## 4.1 Mục tiêu

Mục tiêu của phần này là thiết lập một môi trường lưu trữ Big Data cục bộ theo project để phục vụ Mục 1.

Thay vì dùng Java hoặc Hadoop cài đặt toàn hệ thống, project sử dụng runtime local nằm trong chính thư mục dự án.

## 4.2 Môi trường thực thi

Project được chạy trong:

- Hệ điều hành máy chủ: Windows
- Môi trường Linux: WSL Ubuntu
- Đường dẫn project trong WSL:

```bash
/mnt/d/Daihoc/Nam3/AnalysisBigdata/BTL/Big-Data-Analytics_BI-Assigntment_Data-Driven-Cinema-Management
```

Toàn bộ lệnh Java, Hadoop và HDFS đều được thực hiện từ terminal WSL.

## 4.3 Cấu trúc runtime local

### Java local
```text
runtime/java/
```

### Hadoop local
```text
runtime/hadoop/
```

### HDFS local
```text
runtime/hdfs-store/
```

Các thư mục con:
- `runtime/hdfs-store/tmp`
- `runtime/hdfs-store/namenode`
- `runtime/hdfs-store/datanode`

## 4.4 Kích hoạt môi trường

Mỗi phiên terminal mới cần chạy:

```bash
cd /mnt/d/Daihoc/Nam3/AnalysisBigdata/BTL/Big-Data-Analytics_BI-Assigntment_Data-Driven-Cinema-Management
source scripts/activate.sh
```

Sau khi kích hoạt, các biến môi trường chính sẽ được nạp:
- `PROJECT_ROOT`
- `JAVA_HOME`
- `HADOOP_HOME`
- `HADOOP_CONF_DIR`

## 4.5 Cấu hình Hadoop

Cấu hình Hadoop được lưu trong:

```text
config/hadoop/
```

Các tệp chính:
- `core-site.xml`
- `hdfs-site.xml`
- `hadoop-env.sh`

## 4.6 Script hỗ trợ HDFS

Trong project hiện có các script:

- `scripts/start_hdfs.sh`
- `scripts/stop_hdfs.sh`
- `scripts/check_hdfs_raw.sh`
- `scripts/upload_tmdb.sh`

## 4.7 Quy trình khởi tạo HDFS

1. kích hoạt môi trường local
2. khởi động `NameNode` và `DataNode`
3. thoát safe mode nếu cần
4. tạo thư mục HDFS cho raw data
5. nạp MovieLens raw và TMDB raw lên HDFS
6. kiểm tra dữ liệu trên HDFS

## 4.8 Kết quả hiện tại

Hiện tại HDFS đã có hai thư mục dữ liệu thô chính:

```text
/project/cinema/raw/movielens
/project/cinema/raw/tmdb
```

Điều này chứng minh phần cấu hình lưu trữ của Mục 1 đã hoàn tất.
