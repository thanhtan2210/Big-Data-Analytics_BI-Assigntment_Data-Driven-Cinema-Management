# 1. Tổng Quan Bộ Dữ Liệu

## 1.1 Mục đích

Trong Mục 1, bộ dữ liệu MovieLens 25M được dùng làm **nguồn dữ liệu thô chính** cho toàn bộ dự án Data-Driven Cinema Management. Phần việc của Mục 1 tập trung vào:

- thu thập dữ liệu gốc
- hiểu cấu trúc dữ liệu
- xác định khóa liên kết với nguồn ngoài
- chuẩn bị môi trường lưu trữ HDFS cho lớp dữ liệu thô

## 1.2 Tóm tắt bộ dữ liệu

MovieLens 25M là bộ dữ liệu gợi ý phim công khai của GroupLens, bao gồm:

- 25.000.095 lượt đánh giá
- 1.093.360 lượt gắn thẻ
- 62.423 bộ phim
- 162.541 người dùng

Các tệp dữ liệu được phát hành dưới dạng CSV có header, mã hóa UTF-8.

## 1.3 Các tệp chính dùng trong Mục 1

Các tệp quan trọng nhất gồm:

- `ratings.csv`
- `movies.csv`
- `tags.csv`
- `links.csv`

Ngoài ra còn có:

- `genome-scores.csv`
- `genome-tags.csv`
- `README.txt`

Trong phạm vi Mục 1, nhóm chủ yếu tập trung vào 4 tệp cốt lõi đầu tiên để hiểu lược đồ dữ liệu và chuẩn bị cho bước tích hợp metadata ở các mục sau.

## 1.4 Ý nghĩa đối với dự án

- `ratings.csv` là đầu vào chính cho hệ gợi ý
- `movies.csv` cung cấp tên phim và thể loại
- `tags.csv` bổ sung metadata do người dùng tạo ra
- `links.csv` cung cấp `imdbId` và `tmdbId`, là cầu nối đến dữ liệu phim từ bên ngoài
