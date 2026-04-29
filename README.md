# Big Data Analytics & BI Assignment
## Data-Driven Cinema Management

Kho lưu trữ này hiện chứa phần triển khai và tài liệu cho **Mục 1: Khởi tạo, Thu thập dữ liệu và Hiểu dữ liệu**.

## Phạm vi Mục 1

Mục tiêu của phần này là chuẩn bị dữ liệu thô và nền tảng kỹ thuật cho các giai đoạn tiếp theo của dự án. Các công việc chính đã hoàn thành:

- thu thập bộ dữ liệu MovieLens 25M dạng thô
- tìm hiểu cấu trúc bộ dữ liệu và các tệp chính
- xác định chiến lược tích hợp sử dụng `tmdbId`
- thiết lập Java runtime và Hadoop runtime theo mô hình project-local
- cấu hình môi trường HDFS cục bộ dạng single-node
- tải các tệp MovieLens thô lên HDFS

## Môi trường thực thi

Dự án được chạy **bên trong WSL Ubuntu trên Windows**.

Đường dẫn dự án trong WSL:

```bash
/mnt/d/Daihoc/Nam3/AnalysisBigdata/BTL/Big-Data-Analytics_BI-Assigntment_Data-Driven-Cinema-Management
```

## Cấu trúc tài liệu

Các tài liệu chi tiết của Mục 1 nằm trong thư mục `docs/`:

- `01_dataset_overview.md`: tổng quan bộ dữ liệu
- `02_schema_mapping.md`: ánh xạ lược đồ dữ liệu
- `03_join_strategy.md`: chiến lược join dữ liệu
- `04_hadoop_hdfs_setup.md`: thiết lập Hadoop và HDFS
- `05_run_guide.md`: hướng dẫn chạy
- `06_usage_guide.md`: hướng dẫn sử dụng
- `07_evidence_checklist.md`: danh sách kiểm tra minh chứng

## Dữ liệu và minh chứng

- Dữ liệu thô MovieLens: `data/raw/`
- Log lệnh kỹ thuật: `artifacts/terminal_logs/`
- Ảnh chụp minh chứng: `artifacts/screenshots/`

## Kết quả đạt được của Mục 1

Sau khi hoàn tất Mục 1, dự án đã có:

- môi trường Java và Hadoop cục bộ theo dự án
- môi trường HDFS local single-node hoạt động ổn định
- dữ liệu MovieLens thô được lưu thành công vào HDFS
- tài liệu và minh chứng kỹ thuật phục vụ báo cáo

Nền tảng này sẵn sàng cho các bước tiếp theo như tiền xử lý dữ liệu, phân tích và xây dựng mô hình gợi ý.