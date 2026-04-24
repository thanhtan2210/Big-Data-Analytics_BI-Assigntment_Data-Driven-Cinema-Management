# 15. Mapping Dashboard và dữ liệu sử dụng từ Task 3

Tài liệu này chỉ rõ mỗi dashboard trong `visual/DASHBOARDS.md` đang dùng dữ liệu nào từ output Task 3.

## 15.1 Dashboard 1 - Revenue and Genre Intelligence

Collections/Bảng sử dụng:

- `genre_stats`
- `movies_enriched`
- `decade_stats`

Bảng bổ sung có thể đối chiếu:

- `mr_genre_rating` cho phần rating theo genre
- `mr_decade_genre_heatmap` cho phần decade x genre

Mapping theo chart:

- KPI Cards:
  - Tổng doanh thu: `genre_stats.total_revenue` (SUM)
  - ROI trung bình: `genre_stats.avg_roi` (AVG)
  - Số phim có lãi: `movies_enriched` với điều kiện `revenue > budget`
  - Genre doanh thu cao nhất: `genre_stats` theo `total_revenue`
- Chart 1.1 (bar): `genre_stats.genre`, `genre_stats.total_revenue`
- Chart 1.2 (bubble): `genre_stats.avg_budget`, `genre_stats.avg_revenue`, `genre_stats.rating_count`
- Chart 1.3 (line decade): `decade_stats.decade`, `decade_stats.genre`, `decade_stats.avg_revenue`
- Chart 1.4 (treemap): `genre_stats.genre`, `genre_stats.total_revenue`, `genre_stats.avg_roi`
- Chart 1.5 (top 20 table): `movies_enriched.title_clean`, `genres_array`, `year`, `revenue`, `budget`, `roi`, `avg_rating`, `rating_count`

## 15.2 Dashboard 2 - Audience Engagement and Rating Trends

Collections/Bảng sử dụng:

- `genre_stats`
- `year_stats`
- `decade_stats`
- `rating_dist`

Bảng MapReduce nên áp dụng:

- `mr_genre_rating`
- `mr_decade_genre_heatmap`
- `mr_rating_distribution`

Mapping theo chart:

- KPI Cards:
  - Tổng số ratings: tổng `genre_stats.rating_count` hoặc tổng từ bảng ratings gốc
  - Rating trung bình hệ thống: weighted avg từ `genre_stats` hoặc avg từ nguồn gốc
  - Genre được đánh giá nhiều nhất: `genre_stats` theo `rating_count`
  - Active users 3 năm gần nhất: tổng `year_stats.active_users` theo filter năm
- Chart 2.1 (bar avg rating theo genre): `genre_stats.genre`, `genre_stats.avg_rating`, `genre_stats.rating_count`
- Chart 2.2 (histogram): ưu tiên `mr_rating_distribution.rating`, `mr_rating_distribution.frequency`; nếu cần đồng bộ với export chính thì dùng `rating_dist`
- Chart 2.3 (dual-axis line): `year_stats.rating_year`, `year_stats.rating_count`, `year_stats.active_users`, `year_stats.avg_rating`
- Chart 2.4 (heatmap): ưu tiên `decade_stats.decade`, `decade_stats.genre`, `decade_stats.avg_rating`, `decade_stats.rating_count`; có thể đối chiếu với `mr_decade_genre_heatmap`
- Chart 2.5 (combo popularity vs quality): ưu tiên `genre_stats.rating_count`, `genre_stats.avg_rating`, `genre_stats.genre`; có thể đối chiếu với `mr_genre_rating`

## 15.3 Dashboard 3 - Customer Segmentation and Recommendations

Collections/Bảng sử dụng:

- `user_segments`
- `segment_genre_preference`
- `tag_stats`
- `segment_recommendations`
- `movies_enriched` (bổ sung title/genre nếu cần)

Mapping theo chart:

- KPI Cards:
  - Tổng users: count `user_segments.userId`
  - Tỉ lệ Heavy users: tỉ trọng `segment='Heavy'` trên tổng users
  - Top tag: `tag_stats` theo `frequency`
  - Avg genre/user: có thể dùng metric bổ sung (nếu chưa có thì dùng `unique_movies_rated` thay thế)
- Chart 3.1 (donut segment): `user_segments.segment`, count `userId`, avg `avg_rating`
- Chart 3.2 (grouped bar): `segment_genre_preference.segment`, `genre`, `rating_count`, `avg_rating`, `genre_rank`
- Chart 3.3 (top tag): `tag_stats.tag`, `tag_stats.frequency`
- Chart 3.4 (ALS table): `segment_recommendations.segment`, `rank`, `title_clean`, `genres_array`, `avg_predicted_rating`, `recommended_to_users`
- Chart 3.5 (scatter): `user_segments.rating_count`, `user_segments.unique_movies_rated`, `user_segments.segment`, `user_segments.avg_rating`

## 15.4 Mapping bảng export CSV (nếu dùng Power BI import CSV)

- `movies_enriched` -> `visual/exports/movies_enriched.csv`
- `genre_stats` -> `visual/exports/genre_stats.csv`
- `decade_stats` -> `visual/exports/decade_genre_heatmap.csv`
- `year_stats` -> `visual/exports/year_stats.csv`
- `rating_dist` -> `visual/exports/rating_distribution.csv`
- `user_segments` -> `visual/exports/user_segments.csv`
- `segment_genre_preference` -> `visual/exports/segment_genre_preference.csv`
- `tag_stats` -> `visual/exports/tag_stats.csv`
- `segment_recommendations` -> `visual/exports/segment_recommendations.csv`

Mapping bổ sung từ MapReduce:

- `mr_genre_rating` -> `visual/exports/mapreduce/mr_genre_rating/part-*.csv`
- `mr_decade_genre_heatmap` -> `visual/exports/mapreduce/mr_decade_genre_heatmap/part-*.csv`
- `mr_rating_distribution` -> `visual/exports/mapreduce/mr_rating_distribution/part-*.csv`

Kết luận: cả 3 dashboard đều đã có dữ liệu từ Task 3. Nhóm file MapReduce nên được áp dụng như nguồn phụ trợ cho dashboard rating, và có thể dùng thay thế trực tiếp cho `rating_distribution.csv`.
