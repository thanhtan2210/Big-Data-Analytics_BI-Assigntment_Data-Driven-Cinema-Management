# 1. Tổng Quan Bộ Dữ Liệu

## 1.1 Mục đích của bộ dữ liệu trong dự án

Dự án này sử dụng hai nguồn dữ liệu thô chính trong Mục 1:

- **MovieLens 25M**: nguồn dữ liệu hành vi người dùng, bao gồm đánh giá và gắn thẻ phim
- **TMDB-side dataset từ Kaggle**: nguồn metadata phim phục vụ các thuộc tính như ngân sách, doanh thu và thông tin phim mở rộng

Mục tiêu của Mục 1 là thu thập, hiểu dữ liệu, tài liệu hóa cấu trúc và nạp dữ liệu thô vào HDFS.

## 1.2 Tóm tắt bộ dữ liệu MovieLens 25M

MovieLens 25M là bộ dữ liệu gợi ý phim công khai, bao gồm:

- 25,000,095 lượt đánh giá
- 1,093,360 lượt gắn thẻ
- 62,423 bộ phim
- 162,541 người dùng

Các tệp raw local của MovieLens hiện nằm trong:

```text
data/raw/
```

Bao gồm:
- `ratings.csv`
- `movies.csv`
- `tags.csv`
- `links.csv`
- `genome-scores.csv`
- `genome-tags.csv`
- `README.txt`

## 1.3 Tóm tắt dữ liệu TMDB-side

Dự án sử dụng thêm một bộ dữ liệu metadata phim từ Kaggle để phục vụ các thuộc tính như doanh thu và ngân sách.

Các tệp raw local hiện nằm trong:

```text
data/raw/tmdb/extracted/
```

Bao gồm:
- `movies_metadata.csv`
- `credits.csv`
- `keywords.csv`

Trong đó:
- `movies_metadata.csv` là tệp quan trọng nhất cho các trường như `budget`, `revenue`, `id`, `genres`, `release_date`
- `credits.csv` chứa thông tin cast và crew
- `keywords.csv` chứa từ khóa mô tả nội dung phim

## 1.4 Vai trò của từng nguồn dữ liệu

### MovieLens
Dùng cho:
- phân tích hành vi đánh giá phim
- xây dựng recommendation model
- theo dõi xu hướng rating

### TMDB-side dataset
Dùng cho:
- bổ sung metadata phim
- phân tích doanh thu và ngân sách
- làm giàu dữ liệu ở các mục sau

## 1.5 Kết quả sau Mục 1

Sau khi hoàn thành Mục 1:
- dữ liệu MovieLens raw đã được nạp lên HDFS tại `/project/cinema/raw/movielens`
- dữ liệu TMDB raw đã được nạp lên HDFS tại `/project/cinema/raw/tmdb`
