# 4. Thiết Lập Hadoop và HDFS

## 4.1 Mục tiêu

Mục tiêu của phần thiết lập này là chuẩn bị môi trường lưu trữ Big Data cục bộ theo dự án cho Mục 1. Toàn bộ Java, Hadoop và vùng lưu trữ HDFS được giữ **bên trong thư mục dự án**, không phụ thuộc vào cài đặt toàn hệ thống.

Thiết lập này được chạy **bên trong WSL Ubuntu trên Windows**.

## 4.2 Môi trường thực thi

- Hệ điều hành máy chủ: Windows
- Môi trường Linux: WSL Ubuntu
- Đường dẫn truy cập dự án trong WSL:

```bash
/mnt/d/Daihoc/Nam3/AnalysisBigdata/BTL/Big-Data-Analytics_BI-Assigntment_Data-Driven-Cinema-Management
```

Toàn bộ lệnh Java, Hadoop và HDFS được chạy trong terminal WSL.

## 4.3 Cấu trúc runtime local theo dự án

- Java runtime: `runtime/java`
- Hadoop runtime: `runtime/hadoop`
- HDFS storage: `runtime/hdfs-store`

Các thư mục con của HDFS local:

- `runtime/hdfs-store/tmp`
- `runtime/hdfs-store/namenode`
- `runtime/hdfs-store/datanode`

## 4.4 Link tải chính thức

### Bộ dữ liệu MovieLens 25M

- Trang dataset: https://grouplens.org/datasets/movielens/25m/
- File zip trực tiếp: https://files.grouplens.org/datasets/movielens/ml-25m.zip

### Java cho WSL (khuyến nghị)

- Trang Temurin JDK 11: https://adoptium.net/en-GB/temurin/releases?version=11
- Khuyến nghị chọn: **JDK 11, Linux, x64, HotSpot, tar.gz**

### Hadoop

- Trang release Hadoop 3.4.3: https://hadoop.apache.org/release/3.4.3.html
- File tar.gz: https://archive.apache.org/dist/hadoop/common/hadoop-3.4.3/hadoop-3.4.3.tar.gz

## 4.5 Tải file về đúng vị trí trong project

### Tải MovieLens

Lưu file zip vào:

```text
runtime/downloads/ hoặc data/raw/
```

Khuyến nghị với project hiện tại:

- file nén: `data/raw/ml-25m.zip`
- file giải nén: `data/raw/`

### Tải Java tar.gz

Lưu vào:

```text
runtime/downloads/
```

Ví dụ:

- `runtime/downloads/OpenJDK11U-jdk_x64_linux_hotspot_....tar.gz`

### Tải Hadoop tar.gz

Lưu vào:

```text
runtime/downloads/
```

Ví dụ:

- `runtime/downloads/hadoop-3.4.3.tar.gz`

## 4.6 Cách giải nén Java trong WSL

**Không giải nén bằng Windows Explorer.**

Giải nén bằng terminal WSL:

```bash
mkdir -p runtime/java
mkdir -p runtime/downloads

tar -xzf runtime/downloads/OpenJDK11U-jdk_x64_linux_hotspot_*.tar.gz -C runtime/java --strip-components=1
```

Kiểm tra:

```bash
runtime/java/bin/java -version
```

## 4.7 Cách giải nén Hadoop trong WSL

```bash
mkdir -p runtime/hadoop

tar -xzf runtime/downloads/hadoop-3.4.3.tar.gz -C runtime/hadoop --strip-components=1
```

Kiểm tra:

```bash
ls runtime/hadoop
ls runtime/hadoop/bin | head
```

## 4.8 Kích hoạt môi trường local

Script kích hoạt môi trường:

```bash
source scripts/activate.sh
```

Script này nạp các biến chính từ `.env`, gồm:

- `PROJECT_ROOT`
- `JAVA_HOME`
- `HADOOP_HOME`
- `HADOOP_CONF_DIR`

## 4.9 Các tệp cấu hình Hadoop

Nằm trong:

```text
config/hadoop/
```

Các tệp chính:

- `core-site.xml`
- `hdfs-site.xml`
- `hadoop-env.sh`

## 4.10 Kết quả mong đợi

Sau khi thiết lập xong, dự án cần có:

- Java local trong `runtime/java`
- Hadoop local trong `runtime/hadoop`
- HDFS local trong `runtime/hdfs-store`
- dữ liệu MovieLens raw đã được nạp thành công vào HDFS
