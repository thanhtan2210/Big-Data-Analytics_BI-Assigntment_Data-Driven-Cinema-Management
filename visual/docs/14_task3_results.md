# 14. Kết quả nhận được từ Task 3

Tài liệu này tổng hợp kết quả đầu ra của Task 3 (Analytics + Recommendation Modeling) để làm đầu vào cho Task 4 (BI).

## 14.1 Đầu ra chính của Task 3

Task 3 đã tạo bộ dữ liệu analytics và recommendation gồm 9 nhóm bảng:

- `movies_enriched`
- `genre_stats`
- `decade_stats`
- `year_stats`
- `rating_dist`
- `user_segments`
- `segment_genre_preference`
- `tag_stats`
- `segment_recommendations`

Thông tin schema chi tiết đã được chốt tại: `thang/docs/10_data_contracts_task3.md`.

Repo cũng có thêm 3 output bổ sung được tổng hợp theo hướng MapReduce trong `visual/exports/mapreduce/`:

- `mr_genre_rating`
- `mr_decade_genre_heatmap`
- `mr_rating_distribution`

## 14.2 Kết quả export CSV cho BI

Dữ liệu đã được export sang folder `visual/exports/` để import vào Power BI.

| File CSV                       | Số dòng dữ liệu (không tính header) |
| ------------------------------ | ----------------------------------: |
| `movies_enriched.csv`          |                               62423 |
| `genre_stats.csv`              |                                  20 |
| `decade_genre_heatmap.csv`     |                                 264 |
| `year_stats.csv`               |                                  26 |
| `rating_distribution.csv`      |                                  10 |
| `user_segments.csv`            |                               10920 |
| `segment_genre_preference.csv` |                                  60 |
| `tag_stats.csv`                |                               65402 |
| `segment_recommendations.csv`  |                                  30 |

Nhận xét nhanh:

- Dữ liệu đã đủ số lượng cho cả 3 dashboard (Revenue, Audience, Segmentation).
- Các bảng tổng hợp (`genre_stats`, `year_stats`, `rating_distribution`) gọn nhẹ, phù hợp cho KPI/charts tổng quan.
- Các bảng chi tiết (`movies_enriched`, `tag_stats`, `user_segments`) đủ lớn để phân tích sâu hơn.

## 14.3 Kết quả export bổ sung bằng MapReduce

Ba output bổ sung hiện có:

| Thư mục                                                       | Số dòng dữ liệu | Vai trò                                           |
| ------------------------------------------------------------- | --------------: | ------------------------------------------------- |
| `visual/exports/mapreduce/mr_genre_rating/part-*.csv`         |              53 | Bổ sung tổng hợp rating theo genre                |
| `visual/exports/mapreduce/mr_decade_genre_heatmap/part-*.csv` |              53 | Bổ sung heatmap decade x genre cho rating/revenue |
| `visual/exports/mapreduce/mr_rating_distribution/part-*.csv`  |              10 | Bản MapReduce của phân bố rating                  |

Đánh giá áp dụng:

- `mr_genre_rating` không thay thế `genre_stats.csv` vì thiếu `total_revenue`, `avg_budget`, `avg_roi`, `movie_count`.
- `mr_decade_genre_heatmap` không thay thế `decade_genre_heatmap.csv` vì thiếu `movie_count` và số dòng ít hơn.
- `mr_rating_distribution` có schema trùng với `rating_distribution.csv`, có thể dùng thay thế nếu muốn nhấn mạnh nguồn tổng hợp MapReduce.

Khuyến nghị sử dụng:

- Dùng các file MapReduce như nguồn đối chiếu/xác minh cho các chart rating.
- Chỉ dùng thay thế trực tiếp với `rating_distribution.csv`.
- Với `genre_stats` và `decade_genre_heatmap`, nên giữ file export chính và xem MapReduce là nguồn phụ trợ.

## 14.4 Kết quả ALS metrics

File metrics: `thang/artifacts/metrics/als_metrics.json`

Trạng thái hiện tại:

- `best_validation.mode = fast_mongo_fallback`
- `top_n = 10`
- `als_sample_fraction = 0.0005`
- `sample_size = 12500`
- `fast_mode = true`
- `test_rmse = null`

Ý nghĩa:

- Pipeline đã tạo được recommendation output cho BI.
- Metrics đang ở chế độ fast fallback (ưu tiên tốc độ, mẫu nhỏ).
- Nếu cần báo cáo học thuật đầy đủ (có RMSE test), cần chạy lại ALS với cấu hình full train/validation/test.

## 14.5 Kiểm tra sẵn sàng cho Task 4

Checklist kết quả:

- [x] Có đủ 9 bảng analytics/recommendation theo data contract.
- [x] Có đủ 9 file CSV cho BI import.
- [x] Có thêm 3 output MapReduce phụ trợ cho nhóm chart rating.
- [x] Có metrics artifact cho ALS.
- [x] Segment recommendations đã có rank theo từng segment.

Kết luận: Task 3 đã cung cấp dữ liệu đầu vào để triển khai dashboard BI ở Task 4.
