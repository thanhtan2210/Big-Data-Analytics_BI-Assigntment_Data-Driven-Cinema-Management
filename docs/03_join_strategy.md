# 3. Chiến Lược Join

## 3.1 Mục tiêu

Dự án cần tích hợp dữ liệu hành vi người dùng từ MovieLens với metadata phim mở rộng từ TMDB-side dataset.

Để làm điều này một cách ổn định, cần xác định rõ đường join ngay từ Mục 1.

## 3.2 Đường join chính

Chiến lược được dùng trong dự án là:

```text
MovieLens movieId
-> links.csv
-> tmdbId
-> TMDB id
-> movies_metadata.csv / credits.csv / keywords.csv
```

## 3.3 Vì sao chọn chiến lược này

Chiến lược này được ưu tiên vì:

- dùng định danh rõ ràng thay vì tên phim dạng văn bản
- giảm rủi ro sai khớp tiêu đề
- phù hợp với quy trình dữ liệu lớn
- dễ dùng cho bước preprocessing và merge ở Mục 2

## 3.4 Vì sao không join theo title

Join theo tên phim không ổn định vì:

- tên phim có thể khác nhau về định dạng
- năm phát hành có thể được ghi khác nhau
- dữ liệu text dễ có lỗi chính tả và thiếu nhất quán
- tên phim không phải là khóa kỹ thuật tốt cho pipeline dữ liệu lớn

## 3.5 Phạm vi áp dụng trong Mục 1

Trong Mục 1, dự án chỉ:
- xác định chiến lược join
- chuẩn bị sẵn hai nguồn dữ liệu raw
- nạp raw data vào HDFS

Việc ép kiểu, chuẩn hóa cột khóa và merge thực tế sẽ thực hiện ở Mục 2.
