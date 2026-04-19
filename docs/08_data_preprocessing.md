# 8. Data Preprocessing

## 8.1 Giới thiệu
Mục tiêu của giai đoạn này là dọn dẹp dữ liệu (Clean data) và chuẩn bị Data Warehouse để phục vụ cho phân tích mô hình (Analytical models) cũng như cung cấp dữ liệu cho BI Dashboards.

## 8.2 Quy trình xử lý với PySpark (Preprocessing Jobs)
Quá trình xử lý dữ liệu được thực hiện tự động bằng Apache Spark (PySpark), thông qua script `scripts/data_preprocessing.py`.

### A. Tải dữ liệu từ HDFS
- Đọc các tệp tin CSV thô từ Hadoop Distributed File System (HDFS).
- Dữ liệu MovieLens: `movies.csv`, `ratings.csv`, `links.csv`, `tags.csv`.
- Dữ liệu TMDB (nếu có, qua `PROJECT_HDFS_RAW_TMDB`).

### B. Xử lý giá trị bị thiếu (Missing Values)
- **movies**: Các bộ phim thiếu `movieId` hoặc `title` bị loại bỏ. Các bộ phim không có thể loại được gán nhãn `Unknown`.
- **ratings**: Các đánh giá thiếu thông tin về người dùng, bộ phim, hoặc điểm số bị loại bỏ.
- **links**: Các mục không chứa `movieId` không được giữ lại (vì không thể nối với Movies/TMDB). 

### C. Xử lý Outliers (Dữ liệu ngoại lai)
- **Khoảng điểm hợp lệ**: Lọc các rating nằm ngoài khoảng điểm chuẩn của MovieLens là 0.5 đến 5.0.
- **Số lượng rating quá bất thường**: Dựa vào thống kê trung bình (mean) và độ lệch chuẩn (standard deviation) của số lượng rating theo mỗi user. Nếu user có số lượng review vượt quá `(mean + 3*std)`, user đó có thể được coi là bot/scraper và bị loại trừ.

### D. Ghép nối dữ liệu (Merge Information)
- Liên kết dữ liệu `movies` với `links` để lấy ra `tmdbId`.
- Nếu có dữ liệu mở rộng từ TMDB, tiến hành join qua khoá `tmdbId` để lấy thông tin phụ trợ (như kinh phí, doanh thu, thời lượng,...).
- Tiến hành thực hiện gom nhóm từ `ratings` theo phim (aggregation) để lấy điểm đánh giá trung bình.

## 8.3 Serving Layer Storage (MongoDB)
Để tối ưu hóa số lần và tốc độ đọc cho các truy vấn BI Dashboard sau này, toàn bộ dữ liệu đã làm sạch được đưa từ phân tán sang MongoDB đóng vai trò như kho lưu trữ phân tích (Serving Layer). 

Cấu trúc DB: `cinema_dw`.  
Các Collections chính:
- `movies`: Danh sách phim (để hiện dashboard tổng quan), chứa metadata MovieLens và TMDB.
- `ratings`: Dữ liệu phân tích chi tiết.
- `tags`: Dữ liệu về keywords của phim.

Sử dụng Spark Connector cho MongoDB giúp cho việc Pipeline Data từ PySpark sang MongoDB trở nên song song và bảo đảm tốc độ ghi hiệu quả.
