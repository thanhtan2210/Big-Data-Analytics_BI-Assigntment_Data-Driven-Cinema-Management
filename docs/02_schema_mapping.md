# 2. Ánh Xạ Lược Đồ

## 2.1 Tổng quan

Bộ dữ liệu MovieLens 25M có cấu trúc quan hệ, được tách thành nhiều tệp CSV. Trong đó:

- `userId` là khóa liên kết ở cấp người dùng
- `movieId` là khóa liên kết ở cấp phim

## 2.2 Các tệp cốt lõi và cột dữ liệu

### ratings.csv

- `userId`: mã người dùng đã ẩn danh
- `movieId`: mã phim trong MovieLens
- `rating`: điểm đánh giá từ 0.5 đến 5.0
- `timestamp`: thời điểm đánh giá theo Unix timestamp

### tags.csv

- `userId`: mã người dùng đã ẩn danh
- `movieId`: mã phim trong MovieLens
- `tag`: thẻ do người dùng gán
- `timestamp`: thời điểm gắn thẻ

### movies.csv

- `movieId`: mã phim trong MovieLens
- `title`: tên phim, thường kèm năm phát hành
- `genres`: danh sách thể loại phân tách bởi ký tự `|`

### links.csv

- `movieId`: mã phim trong MovieLens
- `imdbId`: mã phim trên IMDb
- `tmdbId`: mã phim trên TMDB

## 2.3 Quan hệ giữa các tệp

### Liên kết theo người dùng

- `userId` nhất quán giữa `ratings.csv` và `tags.csv`

### Liên kết theo phim

- `movieId` nhất quán giữa:
  - `ratings.csv`
  - `tags.csv`
  - `movies.csv`
  - `links.csv`

## 2.4 Các tệp hỗ trợ

### genome-scores.csv

Lưu điểm mức độ liên quan giữa phim và từng tag.

### genome-tags.csv

Lưu ánh xạ giữa `tagId` và nội dung tag.

Hai tệp này hữu ích cho các phân tích nâng cao nhưng không phải trọng tâm chính của Mục 1.
