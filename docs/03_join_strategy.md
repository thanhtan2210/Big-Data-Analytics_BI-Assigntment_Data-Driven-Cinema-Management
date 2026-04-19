# 3. Chiến Lược Join

## 3.1 Mục tiêu

Dự án cần làm giàu dữ liệu MovieLens bằng metadata phim từ nguồn ngoài như ngân sách, doanh thu, ngày phát hành, độ phổ biến hoặc thông tin chi tiết khác.

## 3.2 Đường join chính

Chiến lược join được khuyến nghị là:

`movieId` -> `links.csv` -> `tmdbId` -> metadata TMDB bên ngoài

## 3.3 Vì sao chọn chiến lược này

Chiến lược này được ưu tiên vì:

- dùng định danh rõ ràng thay vì văn bản tự do
- giảm rủi ro sai khớp tên phim
- ổn định hơn so với join theo `title`
- phù hợp cho bước làm giàu dữ liệu ở các mục sau

## 3.4 Vì sao không join theo tiêu đề

Join theo tiêu đề dễ gặp lỗi vì:

- tiêu đề có thể khác nhau về dấu câu hoặc năm phát hành
- có thể tồn tại khác biệt định dạng
- tên phim trong MovieLens có thể có lỗi hoặc không nhất quán

## 3.5 Phạm vi áp dụng trong Mục 1

Trong Mục 1, dự án chỉ **xác định và tài liệu hóa** chiến lược join. Việc lấy metadata thực tế từ TMDB có thể triển khai ở các mục tiếp theo sau khi tiền xử lý hoàn tất.
