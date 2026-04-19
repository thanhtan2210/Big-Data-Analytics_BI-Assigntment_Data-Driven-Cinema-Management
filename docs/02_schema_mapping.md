# 2. Ánh Xạ Lược Đồ

## 2.1 Tổng quan

Bộ dữ liệu của dự án hiện gồm hai nhóm:

- nhóm dữ liệu MovieLens raw
- nhóm dữ liệu TMDB raw

Trong đó, `userId`, `movieId`, `tmdbId` và `id` là các khóa quan trọng cho việc tích hợp ở các bước sau.

## 2.2 Lược đồ MovieLens

### ratings.csv
Lưu điểm đánh giá phim của người dùng.

Các cột chính:
- `userId`
- `movieId`
- `rating`
- `timestamp`

### tags.csv
Lưu các thẻ do người dùng gán.

Các cột chính:
- `userId`
- `movieId`
- `tag`
- `timestamp`

### movies.csv
Lưu thông tin cơ bản của phim.

Các cột chính:
- `movieId`
- `title`
- `genres`

### links.csv
Lưu khóa đối sánh ra hệ thống ngoài.

Các cột chính:
- `movieId`
- `imdbId`
- `tmdbId`

### genome-scores.csv
Lưu mức độ liên quan giữa phim và tag.

Các cột chính:
- `movieId`
- `tagId`
- `relevance`

### genome-tags.csv
Ánh xạ `tagId` sang tên tag.

Các cột chính:
- `tagId`
- `tag`

## 2.3 Lược đồ TMDB-side dataset

### movies_metadata.csv
Lưu metadata phim mở rộng.

Một số cột quan trọng:
- `id`
- `budget`
- `revenue`
- `genres`
- `release_date`
- `popularity`
- `runtime`
- `title`

### credits.csv
Lưu thông tin cast và crew.

Một số cột chính:
- `id`
- `cast`
- `crew`

### keywords.csv
Lưu từ khóa liên quan đến phim.

Một số cột chính:
- `id`
- `keywords`

## 2.4 Quan hệ giữa các tệp

### Trong MovieLens
- `userId` liên kết giữa `ratings.csv` và `tags.csv`
- `movieId` liên kết giữa:
  - `ratings.csv`
  - `tags.csv`
  - `movies.csv`
  - `links.csv`

### Giữa MovieLens và TMDB-side dataset
- `links.csv` chứa `tmdbId`
- `movies_metadata.csv`, `credits.csv`, `keywords.csv` chứa `id`
- ở các bước sau, có thể nối:
  - `links.csv.tmdbId`
  - với `movies_metadata.csv.id`

## 2.5 Kết luận

Mục 1 chỉ tài liệu hóa lược đồ và chuẩn bị lớp dữ liệu thô. Việc chuẩn hóa kiểu dữ liệu và merge sâu sẽ được thực hiện ở Mục 2.
