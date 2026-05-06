# 4. Thiết Lập Hadoop và HDFS (macOS)

## 4.1 Mục tiêu

Mục tiêu của phần thiết lập này là chuẩn bị môi trường lưu trữ Big Data cục bộ theo dự án cho Mục 1. Toàn bộ vùng lưu trữ HDFS được giữ **bên trong thư mục dự án**.

Thiết lập này được chạy **trên macOS**.

## 4.2 Môi trường thực thi

- Hệ điều hành máy chủ: macOS
- Đường dẫn truy cập dự án trong terminal:

```bash
/Users/truongnhatthanh/Downloads/Big-Data-Analytics_BI-Assigntment_Data-Driven-Cinema-Management
```

Toàn bộ lệnh lệnh Java, Hadoop và HDFS được chạy trên terminal của macOS.

## 4.3 Cấu trúc runtime local theo dự án

- HDFS storage: `runtime/hdfs-store`

Các thư mục con của HDFS local:

- `runtime/hdfs-store/tmp`
- `runtime/hdfs-store/namenode`
- `runtime/hdfs-store/datanode`

## 4.4 Tải dữ liệu chính thức

### Bộ dữ liệu MovieLens 25M

- Trang dataset: https://grouplens.org/datasets/movielens/25m/
- File zip trực tiếp: https://files.grouplens.org/datasets/movielens/ml-25m.zip

Lưu file zip vào:

- file nén: `data/raw/ml-25m.zip`
- thư mục file giải nén: `data/raw/`

## 4.5 Cài đặt Java và Hadoop trên macOS

Chúng ta sử dụng trình quản lý gói `Homebrew` trên macOS để thiết lập Java và Hadoop.

Chạy các lệnh terminal sau:

```bash
brew install openjdk@17
brew install hadoop
```

## 4.6 Kích hoạt môi trường local

Project cần kết nối Java và Hadoop (từ Homebrew) với thư mục cấu hình và cấu trúc data cục bộ.
Script kích hoạt môi trường:

```bash
source scripts/activate.sh
```

Script này định cấu hình các biến chính từ `.env` hoặc hệ thống hệ điều hành (macOS), bao gồm:

- `PROJECT_ROOT`
- `JAVA_HOME`
- `HADOOP_HOME`
- `HADOOP_CONF_DIR`

## 4.7 Các tệp cấu hình Hadoop

Nằm trong:

```text
config/hadoop/
```

Các tệp chính:

- `core-site.xml`
- `hdfs-site.xml`
- `hadoop-env.sh`

## 4.8 Kết quả mong đợi

Sau khi thiết lập xong, dự án cần có:

- Java và Hadoop hoạt động tốt bằng lệnh từ hệ thống.
- HDFS local trong `runtime/hdfs-store`
- Dữ liệu MovieLens raw đã được tải và sẵn sàng sử dụng.
