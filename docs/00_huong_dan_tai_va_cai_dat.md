# 0. Hướng Dẫn Tải File, Giải Nén và Cài Đặt Cho Mục 1 (macOS)

Tài liệu này tổng hợp **toàn bộ link tải chính thức** và hướng dẫn thao tác chi tiết để chuẩn bị môi trường cho Mục 1 trên **macOS**.

## 0.1 Các thành phần cần thiết

### 1) Bộ dữ liệu MovieLens 25M

- Trang chính thức: https://grouplens.org/datasets/movielens/25m/
- File nén: https://files.grouplens.org/datasets/movielens/ml-25m.zip

### 2) Java và Hadoop cho macOS

Sử dụng **Homebrew** để cài đặt Java và Hadoop:

```bash
brew install openjdk@17
brew install hadoop
```

## 0.2 Vị trí lưu file dữ liệu trong project

### MovieLens

- File zip: `data/raw/ml-25m.zip`
- File giải nén: `data/raw/`

## 0.3 Cách giải nén MovieLens

Nếu đã tải file `ml-25m.zip` vào thư mục dự án `data/raw/`:

```bash
cd /Users/truongnhatthanh/Downloads/Big-Data-Analytics_BI-Assigntment_Data-Driven-Cinema-Management
unzip -q data/raw/ml-25m.zip -d data/raw/
```

Nếu sau khi giải nén xuất hiện thư mục con `ml-25m/`, di chuyển dữ liệu ra ngoài:

```bash
mv data/raw/ml-25m/* data/raw/
rmdir data/raw/ml-25m
```

## 0.4 Kích hoạt môi trường local

Kích hoạt các biến môi trường để trỏ Hadoop/Java vào config cục bộ của project:

```bash
source scripts/activate.sh
```

Kiểm tra:

```bash
java -version
hadoop version
```

## 0.5 Trình tự khuyến nghị từ đầu đến cuối

1. tải MovieLens zip
2. cài đặt Java và Hadoop qua `brew install openjdk@17 hadoop`
3. giải nén MovieLens vào `data/raw/` bằng lệnh unzip
4. chạy `source scripts/activate.sh`
5. kiểm tra `java -version`, `hadoop version`, `hdfs version`
6. format HDFS nếu là lần đầu thiết lập
7. khởi động HDFS và nạp dữ liệu raw vào hệ thống HDFS
