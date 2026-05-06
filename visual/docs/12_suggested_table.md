# 12. Bảng dự kiến thực hiện dựa trên DASHBOARDS.md

Tài liệu này mô tả các bảng dữ liệu cần dùng cho bộ 3 dashboard trong `visual/DASHBOARDS.md`.

## 12.1 Danh sách bảng dự kiến

| Bảng dữ liệu               | Nguồn         | Mục đích sử dụng                                                               |
| -------------------------- | ------------- | ------------------------------------------------------------------------------ |
| `movies_enriched`          | Task 3 output | Bảng phim chi tiết: top movie table, re-run candidate, join với recommendation |
| `genre_stats`              | Task 3 output | KPI và chart theo genre: revenue, rating, budget, roi                          |
| `decade_stats`             | Task 3 output | Xu hướng theo thập kỷ: line chart, heatmap genre x decade                      |
| `year_stats`               | Task 3 output | Timeline activity theo năm: rating_count, active_users, avg_rating             |
| `rating_dist`              | Task 3 output | Histogram phân bố rating 0.5 -> 5.0                                            |
| `user_segments`            | Task 3 output | Phân khúc Heavy/Medium/Light, KPI customer base                                |
| `segment_genre_preference` | Task 3 output | Sở thích genre theo từng segment                                               |
| `tag_stats`                | Task 3 output | Top tags phù hợp marketing content                                             |
| `segment_recommendations`  | Task 3 output | Top-N gợi ý phim theo segment (ALS)                                            |

Bảng bổ sung từ nhóm export MapReduce:

| Bảng dữ liệu              | Nguồn            | Mục đích sử dụng                                   |
| ------------------------- | ---------------- | -------------------------------------------------- |
| `mr_genre_rating`         | MapReduce export | Bảng đối chiếu nhanh cho rating theo genre         |
| `mr_decade_genre_heatmap` | MapReduce export | Bảng đối chiếu cho heatmap decade x genre          |
| `mr_rating_distribution`  | MapReduce export | Bản thay thế tương đương cho `rating_distribution` |

## 12.2 Mục tiêu thiết kế theo từng nhóm bảng

1. Nhóm doanh thu và hiệu quả đầu tư:

- `genre_stats`
- `movies_enriched`
- `decade_stats`

2. Nhóm hành vi và chất lượng đánh giá:

- `genre_stats`
- `year_stats`
- `rating_dist`
- `decade_stats`
- `mr_genre_rating` (bổ sung đối chiếu)
- `mr_decade_genre_heatmap` (bổ sung đối chiếu)
- `mr_rating_distribution` (có thể dùng thay thế)

3. Nhóm phân khúc và recommendation:

- `user_segments`
- `segment_genre_preference`
- `tag_stats`
- `segment_recommendations`
- `movies_enriched` (join title/genre)

## 12.3 Trường dữ liệu cốt lõi cần ưu tiên

`movies_enriched`

- `movieId`, `title_clean`, `genres_array`, `year`, `revenue`, `budget`, `roi`, `avg_rating`, `rating_count`

`genre_stats`

- `genre`, `total_revenue`, `avg_revenue`, `avg_budget`, `avg_roi`, `avg_rating`, `rating_count`, `movie_count`

`decade_stats`

- `decade`, `genre`, `avg_revenue`, `avg_rating`, `rating_count`, `movie_count`

`year_stats`

- `rating_year`, `rating_count`, `active_users`, `avg_rating`

`rating_dist`

- `rating`, `frequency`

`user_segments`

- `userId`, `segment`, `rating_count`, `avg_rating`, `unique_movies_rated`

`segment_genre_preference`

- `segment`, `genre`, `rating_count`, `avg_rating`, `genre_rank`

`tag_stats`

- `tag`, `frequency`

`segment_recommendations`

- `segment`, `movieId`, `avg_predicted_rating`, `recommended_to_users`, `rank`, `title_clean`, `genres_array`

## 12.4 Quan hệ dự kiến trong model BI

Quan hệ ưu tiên tạo trong Power BI:

- `movies_enriched[movieId]` -> `segment_recommendations[movieId]` (many-to-one)
- `genre_stats[genre]` -> `segment_genre_preference[genre]` (one-to-many)
- `user_segments[segment]` -> `segment_genre_preference[segment]` (one-to-many)
- `user_segments[segment]` -> `segment_recommendations[segment]` (one-to-many)

Ghi chú:

- Nếu cần heatmap `genre x decade`, có thể dùng trực tiếp `decade_stats` hoặc file export đổi tên `decade_genre_heatmap.csv`.
- Nếu cần nhấn mạnh kết quả tổng hợp theo hướng MapReduce, ưu tiên áp dụng ở các chart rating thay vì chart doanh thu.
