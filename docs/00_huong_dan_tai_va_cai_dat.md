# 0. Hướng Dẫn Tải File, Giải Nén và Cài Đặt Cho Mục 1

Tài liệu này tổng hợp **toàn bộ link tải chính thức** và hướng dẫn thao tác chi tiết để chuẩn bị môi trường cho Mục 1.

## 0.1 Các thành phần cần tải

### 1) Bộ dữ liệu MovieLens 25M

- Trang chính thức: https://grouplens.org/datasets/movielens/25m/
- File nén: https://files.grouplens.org/datasets/movielens/ml-25m.zip

### 2) Java cho WSL Ubuntu

- Trang chính thức Temurin JDK 11: https://adoptium.net/en-GB/temurin/releases?version=11
- Chọn đúng gói:
  - Version: **JDK 11**
  - Operating System: **Linux**
  - Architecture: **x64**
  - Package Type: **JDK**
  - Format: **tar.gz**

### 3) Hadoop

- Trang release: https://hadoop.apache.org/release/3.4.3.html
- File tar.gz: https://archive.apache.org/dist/hadoop/common/hadoop-3.4.3/hadoop-3.4.3.tar.gz

## 0.2 Vị trí nên lưu file trong project

### MovieLens

- File zip: `data/raw/ml-25m.zip`
- File giải nén: `data/raw/`

### Java

- File tải về: `runtime/downloads/OpenJDK11U-jdk_x64_linux_hotspot_....tar.gz`
- Thư mục giải nén: `runtime/java/`

### Hadoop

- File tải về: `runtime/downloads/hadoop-3.4.3.tar.gz`
- Thư mục giải nén: `runtime/hadoop/`

## 0.3 Cách giải nén MovieLens

Nếu đã có file `ml-25m.zip` trong project:

```bash
unzip -q data/raw/ml-25m.zip -d data/raw/
```

Nếu sau khi giải nén xuất hiện thư mục con `ml-25m/`, di chuyển dữ liệu ra ngoài:

```bash
mv data/raw/ml-25m/* data/raw/
rmdir data/raw/ml-25m
```

## 0.4 Cách giải nén Java

```bash
mkdir -p runtime/java

tar -xzf runtime/downloads/OpenJDK11U-jdk_x64_linux_hotspot_*.tar.gz -C runtime/java --strip-components=1
```

Kiểm tra:

```bash
runtime/java/bin/java -version
```

## 0.5 Cách giải nén Hadoop

```bash
mkdir -p runtime/hadoop

tar -xzf runtime/downloads/hadoop-3.4.3.tar.gz -C runtime/hadoop --strip-components=1
```

Kiểm tra:

```bash
ls runtime/hadoop
hadoop version
```

## 0.6 Kích hoạt môi trường local

```bash
source scripts/activate.sh
```

## 0.7 Trình tự khuyến nghị từ đầu đến cuối

1. tải MovieLens zip
2. tải JDK 11 Linux x64 tar.gz
3. tải Hadoop 3.4.3 tar.gz
4. giải nén MovieLens vào `data/raw/`
5. giải nén Java vào `runtime/java/`
6. giải nén Hadoop vào `runtime/hadoop/`
7. chạy `source scripts/activate.sh`
8. kiểm tra `java -version`, `hadoop version`, `hdfs version`
9. format HDFS nếu là lần đầu
10. khởi động HDFS và nạp dữ liệu raw vào HDFS
