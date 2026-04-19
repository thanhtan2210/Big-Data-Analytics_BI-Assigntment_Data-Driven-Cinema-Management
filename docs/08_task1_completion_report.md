# 8. Báo Cáo Hoàn Thành Mục 1

## 8.1 Mục tiêu

Mục 1 nhằm xây dựng nền tảng dữ liệu và hạ tầng kỹ thuật ban đầu cho dự án.

Các yêu cầu chính gồm:
- tải MovieLens 25M
- tải TMDB-side dataset từ Kaggle
- mô tả cấu trúc dữ liệu
- xác định chiến lược join
- cài đặt Hadoop/HDFS local
- ingest toàn bộ raw data vào HDFS

## 8.2 Những gì đã hoàn thành

### Dữ liệu MovieLens
Đã tải và lưu local đầy đủ trong `data/raw/`.

Đã nạp lên HDFS tại:
```text
/project/cinema/raw/movielens
```

### Dữ liệu TMDB
Đã lưu local trong:
```text
data/raw/tmdb/extracted/
```

Bao gồm:
- `movies_metadata.csv`
- `credits.csv`
- `keywords.csv`

Đã nạp lên HDFS tại:
```text
/project/cinema/raw/tmdb
```

### Tài liệu dữ liệu
Đã hoàn thành:
- tổng quan dữ liệu
- ánh xạ lược đồ
- chiến lược join
- hướng dẫn cài đặt
- hướng dẫn chạy
- hướng dẫn sử dụng
- checklist minh chứng

### Môi trường kỹ thuật
Đã thiết lập:
- Java local
- Hadoop local
- HDFS local
- các script hỗ trợ thao tác HDFS

## 8.3 Minh chứng kỹ thuật

### Log
Lưu trong:
```text
artifacts/terminal_logs/
```

### Ảnh
Lưu trong:
```text
artifacts/screenshots/
```

## 8.4 Kết luận

Mục 1 của project đã hoàn thành trọn vẹn.

Kết quả cuối cùng:
- có đủ hai nguồn raw data là MovieLens và TMDB
- có mô tả rõ cấu trúc dữ liệu
- có chiến lược join giữa MovieLens và TMDB
- có môi trường Hadoop/HDFS local theo project
- toàn bộ raw data đã được nạp thành công vào HDFS
