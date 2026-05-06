# 13. Hướng dẫn trường dữ liệu và MapReduce cho Task 3

Tài liệu này là handoff kỹ thuật để thành viên làm Task 3 thực hiện đúng data contract cho BI, và biết rõ phần nào cần ưu tiên MapReduce khi xử lý dataset lớn (MovieLens 25M + TMDB).

## 13.1 Mục tiêu

Task 3 cần đảm bảo 3 đầu ra:

1. Tạo bộ bảng analytics/recommendation đúng schema cho Task 4.
2. Tính toán ổn định trên dữ liệu lớn (ratings ~25M) bằng xử lý phân tán.
3. Có bộ kết quả đối chiếu MapReduce cho nhóm chart rating.

## 13.2 Input data contract (bắt buộc)

### A. Collection `movies` (hoặc bảng đầu vào tương đương)

| Trường    | Kiểu dữ liệu | Bắt buộc    | Ghi chú sử dụng                              |
| --------- | ------------ | ----------- | -------------------------------------------- |
| `movieId` | int          | Có          | Khóa join chính với ratings                  |
| `title`   | string       | Có          | Tách `title_clean`, `year`, `decade`         |
| `genres`  | string       | Có          | Tách thành `genres_array` bởi delimiter `\|` |
| `revenue` | double       | Khuyến nghị | Tính doanh thu theo genre/decade             |
| `budget`  | double       | Khuyến nghị | Tính ROI                                     |
| `imdbId`  | string       | Không       | Metadata thêm                                |
| `tmdbId`  | string       | Không       | Metadata thêm                                |

Chấp nhận alias cho revenue/budget nếu schema khác:

- `revenue | tmdb_revenue | box_office | gross_revenue`
- `budget | tmdb_budget | production_budget`

### B. Collection `ratings`

| Trường      | Kiểu dữ liệu | Bắt buộc    | Ghi chú sử dụng              |
| ----------- | ------------ | ----------- | ---------------------------- |
| `userId`    | int          | Có          | Phân khúc user, active users |
| `movieId`   | int          | Có          | Join với movies              |
| `rating`    | double       | Có          | Toàn bộ KPI/chất lượng/ALS   |
| `timestamp` | long (unix)  | Khuyến nghị | Tính `year_stats` theo năm   |

Chấp nhận alias schema:

- `movieId | movie_id | movieid`
- `rating | score`
- `timestamp | createdAt | created_at`

### C. Collection `tags`

| Trường    | Kiểu dữ liệu | Bắt buộc | Ghi chú sử dụng               |
| --------- | ------------ | -------- | ----------------------------- |
| `tag`     | string       | Có       | Tạo `tag_stats`               |
| `movieId` | int          | Không    | Có thể dùng cho phân tích sau |
| `userId`  | int          | Không    | Có thể dùng cho phân tích sau |

## 13.3 Output data contract cho BI (bắt buộc)

Task 3 phải tạo đúng 9 bảng sau (schema chi tiết tại `thang/docs/10_data_contracts_task3.md`):

- `movies_enriched`
- `genre_stats`
- `decade_stats`
- `year_stats`
- `rating_dist`
- `user_segments`
- `segment_genre_preference`
- `tag_stats`
- `segment_recommendations`

Sau đó export CSV cho Task 4 trong `visual/exports/`.

## 13.4 Các thông tin BẮT BUỘC ưu tiên MapReduce với dataset lớn

Lưu ý: ở Spark, `groupBy + agg` trên dữ liệu lớn chính là map-shuffle-reduce pattern. Các phép dưới đây nên chạy theo hướng này để tránh nghẽn bộ nhớ khi ratings rất lớn.

### 13.4.1 Rating aggregate theo phim (nên dùng MapReduce)

- Input: `ratings(userId, movieId, rating)`
- Map key: `movieId`
- Map value: `(rating, 1, rating^2)`
- Reduce: `sum(rating), sum(count), sum(rating^2)`
- Output dùng cho: `movies_enriched.avg_rating`, `rating_count`, `rating_stddev`

Lý do cần MapReduce: ratings là bảng lớn nhất, groupBy theo movieId là phép tính cốt lõi cho nhiều bảng khác.

### 13.4.2 Rating và revenue theo genre (nên dùng MapReduce)

- Input: `movies_enriched` sau khi explode `genres_array`
- Map key: `genre`
- Map value: `(rating_count, rating_sum, revenue, budget, roi, movie_count)`
- Reduce: tổng hợp các metric theo `genre`
- Output dùng cho: `genre_stats`

Lý do cần MapReduce: cần tổng hợp trên tập genre xuất phát từ millions ratings + join movies.

### 13.4.3 Heatmap decade x genre (nên dùng MapReduce)

- Input: `movies_enriched` + ratings aggregate
- Map key: `(decade, genre)`
- Map value: `(rating_count, rating_sum, revenue, movie_count)`
- Reduce: tổng hợp theo cặp khóa
- Output dùng cho: `decade_stats` và `decade_genre_heatmap.csv`

Lý do cần MapReduce: key kết hợp (decade, genre) để tạo heatmap trên tập lớn.

### 13.4.4 Phân bố rating (nên dùng MapReduce)

- Input: `ratings.rating`
- Map key: `rating` (0.5..5.0)
- Map value: `1`
- Reduce: count frequency theo từng bin
- Output dùng cho: `rating_dist` và `rating_distribution.csv`

Lý do cần MapReduce: bài toán đếm tần suất có khối lượng record rất lớn, để tối ưu quá trình count.

### 13.4.5 Hoạt động theo năm (nên dùng MapReduce)

- Input: `ratings(timestamp, rating, userId)`
- Map key: `rating_year`
- Map value: `(rating, 1, userId)`
- Reduce: `rating_count`, `avg_rating`, `active_users`
- Output dùng cho: `year_stats`

Lý do cần MapReduce: gom nhóm theo năm trên toàn bộ ratings, cần tối ưu distinct user.

### 13.4.6 Tag frequency (nên dùng MapReduce)

- Input: `tags.tag`
- Map key: `tag_normalized`
- Map value: `1`
- Reduce: count
- Output dùng cho: `tag_stats`

Lý do cần MapReduce: tags có cardinality lớn, cần đếm tần suất trên toàn bộ tập tags.

## 13.5 Các thông tin KHÔNG bắt buộc MapReduce trực tiếp

Những phần dưới đây có thể dùng Spark SQL/Window/ML pipeline, không cần ép thành bài toán reduce thủ công:

- Tách `title_clean`, `year`, `decade` từ `title`.
- Tính `roi = (revenue - budget)/budget` theo từng phim.
- Phân khúc user `Heavy/Medium/Light` (quantile/window).
- Rank genre trong từng segment (`segment_genre_preference.genre_rank`).
- ALS Collaborative Filtering (`segment_recommendations`).

Ghi chú: ALS vẫn là xử lý phân tán trên Spark, nhưng không nằm trong nhóm map/reduce aggregate cổ điển.

## 13.6 Bộ kết quả MapReduce đối chiếu cần tạo

Ngoài 9 bảng chính, nên tạo thêm bộ file đối chiếu trong `visual/exports/mapreduce/`:

- `mr_genre_rating/part-*.csv`
- `mr_decade_genre_heatmap/part-*.csv`
- `mr_rating_distribution/part-*.csv`

Mục đích:

- Xác minh nhóm chart rating trên BI.
- Dùng thay thế trực tiếp cho `rating_distribution.csv` khi cần.
- Không thay thế hoàn toàn `genre_stats.csv` và `decade_genre_heatmap.csv` vì thiếu một số cột kinh doanh.

## 13.7 Checklist thực thi cho thành viên Task 3

- [ ] Input schema đủ 3 collection `movies`, `ratings`, `tags` (hoặc alias hợp lệ).
- [ ] Hoàn thành 6 nhóm aggregate ưu tiên MapReduce ở mục 13.4.
- [ ] Tạo đủ 9 output collections theo data contract.
- [ ] Export đủ 9 file CSV sang `visual/exports/`.
- [ ] Tạo thêm 3 output MapReduce đối chiếu trong `visual/exports/mapreduce/`.
- [ ] Lưu metrics ALS tại `thang/artifacts/metrics/als_metrics.json`.

Nếu đạt đủ checklist trên, Task 4 có thể vào Power BI và dùng dashboard ngay mà không cần sửa lại schema.
