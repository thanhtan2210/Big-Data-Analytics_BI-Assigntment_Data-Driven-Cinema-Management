# Big Data Analytics & BI Assignment
## Data-Driven Cinema Management

Kho lưu trữ này hiện chứa phần triển khai và tài liệu cho **Mục 1: Khởi tạo, Thu thập dữ liệu và Hiểu dữ liệu**.

## Phạm vi Mục 1

Mục tiêu của phần này là chuẩn bị dữ liệu thô và nền tảng kỹ thuật cho các giai đoạn tiếp theo của dự án. Các công việc chính đã hoàn thành:

- thu thập bộ dữ liệu MovieLens 25M dạng thô
- tìm hiểu cấu trúc bộ dữ liệu và các tệp chính
- xác định chiến lược tích hợp sử dụng `tmdbId`
- thiết lập Java runtime và Hadoop bằng Homebrew trên macOS
- cấu hình môi trường HDFS cục bộ dạng single-node
- tải các tệp MovieLens thô lên HDFS

## Môi trường thực thi

Dự án được chạy **trên macOS**.

Đường dẫn dự án:

```bash
/Users/truongnhatthanh/Downloads/Big-Data-Analytics_BI-Assigntment_Data-Driven-Cinema-Management
```

## Mục 2: Tiền xử lý dữ liệu (Data Preprocessing)

Để thực thi quá trình làm sạch và chuyển đổi dữ liệu (Mục 2), hãy làm theo các bước sau để chạy code:

**Bước 1: Cài đặt thư viện Python**
Mở terminal tại thư mục gốc dự án và cài đặt môi trường ảo (ví dụ dùng `venv`), sau đó cài đặt thư viện cần thiết:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
*(Lưu ý: PySpark yêu cầu bạn phải cài sẵn **Java 17** qua Homebrew, và file `activate.sh` trong dự án đã cấu hình sẵn JAVA_HOME)*

**Bước 2: Khởi động các dịch vụ liên quan**
Các dịch vụ này cần chạy trước khi tiền xử lý:
1. **HDFS**: Nơi chứa dữ liệu thô MovieLens (đầu vào từ Mục 1).
```bash
source scripts/activate.sh
hdfs --daemon start namenode
hdfs --daemon start datanode
```
*(Mẹo: Nếu hệ thống báo service đã chạy nhưng bạn cần khởi động/tắt lại, hãy dùng lệnh `stop` trước: `hdfs --daemon stop namenode` và `hdfs --daemon stop datanode`)*

2. **MongoDB**: Cài đặt và khởi động MongoDB trên máy ở cổng `27017` (nếu dùng macOS Homebrew):
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```
*(Mẹo: Nếu gặp lỗi "Bootstrap failed: 5" nghĩa là MongoDB đã chạy ngầm. Để dừng toàn bộ hoặc tái khởi động CSDL, hãy thay từ `start` bằng `stop` hoặc `restart`, ví dụ: `brew services stop mongodb-community`)*

**Bước 3: Chạy Data Preprocessing Pipeline**
Nằm ở thư mục gốc, hãy cấp quyền thực thi (nếu cần) và chạy script bash sau. Script này sẽ sử dụng `spark-submit` để tự động xử lý và lưu kết quả vào MongoDB:
```bash
chmod +x scripts/run_preprocessing.sh
./scripts/run_preprocessing.sh
```

**Bước 4: Kiểm tra kết quả sau khi hoàn thành**
Dùng lệnh sau để truy cập MongoDB thông qua terminal và kiểm tra các collection đã tạo:
```bash
mongosh "mongodb://localhost:27017"
```

**Bước 5: Thao tác dữ liệu thông qua lệnh MongoDB (mongosh)**
Trong Mongo shell (`mongosh`), dưới đây là một số lệnh liên quan trực tiếp tới dữ liệu của dự án (`movies`, `ratings`, `tags`):
```javascript
// Chọn cơ sở dữ liệu
use cinema_dw;

// Liệt kê danh sách các collections
show collections;

// Đếm số lượng record phim và đánh giá đã được lưu
db.movies.countDocuments();
db.ratings.countDocuments();

// Xem thử cấu trúc dữ liệu của 5 bộ phim đầu tiên
db.movies.find().limit(5).pretty();

// Tìm kiếm phim theo title (kết quả gần đúng)
db.movies.find({ title: /Toy Story/i }).limit(2).pretty();
```

## Cấu trúc tài liệu

Các tài liệu chi tiết của Mục 1 và Mục 2 nằm trong thư mục `docs/`:

- `01_dataset_overview.md`: tổng quan bộ dữ liệu
- `02_schema_mapping.md`: ánh xạ lược đồ dữ liệu
- `03_join_strategy.md`: chiến lược join dữ liệu
- `04_hadoop_hdfs_setup.md`: thiết lập Hadoop và HDFS trên macOS
- `05_run_guide.md`: hướng dẫn chạy trên macOS
- `06_usage_guide.md`: hướng dẫn sử dụng trên macOS
- `07_evidence_checklist.md`: danh sách kiểm tra minh chứng
- `08_data_preprocessing.md`: quy trình xử lý dữ liệu (Mục 2)

## Dữ liệu và minh chứng

- Dữ liệu thô MovieLens: `data/raw/`
- Log lệnh kỹ thuật: `artifacts/terminal_logs/`
- Ảnh chụp minh chứng: `artifacts/screenshots/`

## Kết quả đạt được của Mục 1

Sau khi hoàn tất Mục 1, dự án đã có:

- môi trường Java và Hadoop được cấu hình theo đường dẫn Homebrew trên macOS
- môi trường HDFS local single-node hoạt động ổn định
- dữ liệu MovieLens thô được lưu thành công vào HDFS
- tài liệu và minh chứng kỹ thuật phục vụ báo cáo

Nền tảng này sẵn sàng cho các bước tiếp theo như tiền xử lý dữ liệu, phân tích và xây dựng mô hình gợi ý.