# BI Dashboards — Mô tả Chart & Mục tiêu

> **BI Tool:** Power BI Desktop  
> **Dữ liệu đầu vào:** MongoDB collections (output của PySpark pipeline)  
> **Cách import:** xem [CONNECTION_GUIDE.md](CONNECTION_GUIDE.md)

---

## Dashboard 1 — Revenue & Genre Intelligence

**Câu hỏi kinh doanh:** _Genre nào mang lại doanh thu cao nhất? Nên ưu tiên chiếu phim gì vào cuối tuần và dịp lễ?_

**MongoDB collection chính:** `genre_stats`, `movies_enriched`, `decade_stats`

---

### KPI Cards

| Card                       | Giá trị                      | Mục đích                    |
| -------------------------- | ---------------------------- | --------------------------- |
| Tổng doanh thu (TMDB)      | SUM(revenue)                 | Tổng quan quy mô thị trường |
| ROI trung bình toàn ngành  | AVG(roi)                     | Hiệu quả đầu tư trung bình  |
| Số phim có lợi nhuận dương | COUNT(revenue > budget)      | Tỷ lệ phim thành công       |
| Genre doanh thu cao nhất   | TOP 1 genre by total_revenue | Nhanh identify cơ hội       |

---

### Chart 1.1 — Horizontal Bar: Doanh thu theo Genre

```
Trục Y  : genre
Trục X  : total_revenue (triệu USD)
Màu sắc : gradient từ thấp → cao
Sắp xếp : descending by total_revenue
```

**Collection:** `genre_stats`  
**Cột dùng:** `genre`, `total_revenue`, `movie_count`

**Mục tiêu:** Xác định ngay top 3–5 genre doanh thu cao nhất → ưu tiên đặt lịch chiếu cho các khung giờ vàng (thứ 6–7–CN, dịp lễ Tết). Genre thấp → chỉ chiếu thứ 2–4.

---

### Chart 1.2 — Scatter Plot: Budget vs Revenue (Bubble Chart)

```
Trục X      : avg_budget (triệu USD) — log scale
Trục Y      : avg_revenue (triệu USD) — log scale
Kích thước bubble : rating_count (popularity)
Màu bubble  : genre
Đường tham chiếu : y = x (breakeven line — revenue = budget)
```

**Collection:** `genre_stats`  
**Cột dùng:** `genre`, `avg_budget`, `avg_revenue`, `avg_roi`, `rating_count`

**Mục tiêu:** Phân tích rủi ro-lợi nhuận theo genre. Bubble nằm trên đường y=x là có lợi nhuận. Bubble lớn + cao = genre vừa được yêu thích vừa sinh lời — top priority cho rạp.

---

### Chart 1.3 — Line Chart: Doanh thu trung bình theo Thập kỷ

```
Trục X  : decade (1950, 1960, ..., 2010, 2020)
Trục Y  : avg_revenue (triệu USD)
Series  : mỗi genre là một đường màu riêng
Filter  : top 5 genre theo tổng doanh thu (cắt bớt nhiễu)
```

**Collection:** `decade_stats`  
**Cột dùng:** `decade`, `genre`, `avg_revenue`

**Mục tiêu:** Xem xu hướng dài hạn — genre nào đang "lên" theo thời gian (Action, Sci-Fi) vs đang "xuống" (Western, Musical) → chiến lược danh mục phim dài hạn cho rạp.

---

### Chart 1.4 — Treemap: Phân bổ doanh thu theo Genre

```
Nhóm cha    : genre
Kích thước ô : total_revenue
Màu sắc     : avg_roi (xanh = ROI cao, đỏ = ROI thấp)
Tooltip     : movie_count, avg_revenue, avg_budget
```

**Collection:** `genre_stats`  
**Cột dùng:** `genre`, `total_revenue`, `avg_roi`, `movie_count`

**Mục tiêu:** Nhìn tổng thể tỷ trọng doanh thu của từng genre trong toàn bộ thị trường + tô màu ROI → phát hiện genre chiếm thị phần lớn nhưng ROI thấp (warning sign).

---

### Chart 1.5 — Table: Top 20 Phim Doanh Thu Cao Nhất

| Cột           | Mô tả                         |
| ------------- | ----------------------------- |
| Tên phim      | title_clean                   |
| Genre         | genres_array (join bằng "\|") |
| Năm           | year                          |
| Doanh thu     | revenue (format: $M)          |
| Budget        | budget (format: $M)           |
| ROI           | roi (format: %)               |
| Rating TB     | avg_rating (★ format)         |
| Lượt đánh giá | rating_count (format: K)      |

**Collection:** `movies_enriched`  
**Filter:** TOP 20 by revenue, revenue > 0

**Mục tiêu:** Danh sách phim cụ thể để rạp cân nhắc tái chiếu (re-run) hoặc chiếu khi có sự kiện đặc biệt. Kết hợp rating cao + doanh thu cao = ứng viên phù hợp nhất.

---

---

## Dashboard 2 — Audience Engagement & Rating Trends

**Câu hỏi kinh doanh:** _Khán giả đang xem thể loại gì và đánh giá ra sao? Xu hướng thay đổi theo thời gian như thế nào?_

**MongoDB collection chính:** `genre_stats`, `year_stats`, `decade_stats`, `rating_dist`

---

### KPI Cards

| Card                            | Giá trị                     | Mục đích                     |
| ------------------------------- | --------------------------- | ---------------------------- |
| Tổng số ratings                 | 25,000,095                  | Quy mô dữ liệu               |
| Rating trung bình toàn hệ thống | AVG(rating) toàn bộ         | Baseline để so sánh          |
| Genre được đánh giá nhiều nhất  | TOP 1 genre by rating_count | Genre phổ biến nhất hiện tại |
| Active users (3 năm gần nhất)   | COUNT DISTINCT userId       | Xu hướng giữ chân khách hàng |

---

### Chart 2.1 — Bar Chart: Rating Trung Bình theo Genre

```
Trục X  : genre
Trục Y  : avg_rating (0 → 5)
Màu     : encoding độ lệch so với avg toàn hệ thống (xanh = trên TB, đỏ = dưới)
Đường tham chiếu : avg rating toàn hệ thống
Sắp xếp : descending by avg_rating
```

**Collection:** `genre_stats`  
**Cột dùng:** `genre`, `avg_rating`, `rating_count`

**Mục tiêu:** Genre nào được khán giả đánh giá cao nhất không hẳn là phổ biến nhất → kết hợp với Chart 2.5 để lọc "hidden gem genre" — chất lượng cao nhưng ít người biết.

---

### Chart 2.2 — Histogram: Phân Phối Rating

```
Trục X  : rating (0.5, 1.0, 1.5, ..., 5.0 — 10 bins)
Trục Y  : frequency (số lượt rating)
Màu     : đơn sắc
Tooltip : % trong tổng số ratings
```

**Collection:** `rating_dist`  
**Cột dùng:** `rating`, `frequency`

**Mục tiêu:** Hiểu hành vi khán giả — khán giả có xu hướng rate cao (lenient) hay khắt khe? Phân phối lệch phải (positively skewed) cho thấy khán giả nhìn chung hài lòng. Thông tin này ảnh hưởng đến ngưỡng rating để đánh giá "phim tốt".

---

### Chart 2.3 — Line Chart: Hoạt Động Rating theo Năm

```
Trục X  : rating_year (1995 → 2019)
Trục Y trái  : rating_count (số lượt đánh giá)
Trục Y phải : active_users (số user unique)
Marker  : điểm dữ liệu từng năm
Tooltip : rating_count, active_users, avg_rating của năm đó
```

**Collection:** `year_stats`  
**Cột dùng:** `rating_year`, `rating_count`, `active_users`, `avg_rating`

**Mục tiêu:** Xem nền tảng phát triển hay suy giảm theo thời gian. Năm nào có spike bất thường (vd: ra mắt phim bom tấn) → học hỏi để lên lịch marketing. Nếu active_users giảm → cần chiến lược giữ chân khách hàng.

---

### Chart 2.4 — Heatmap: Genre × Thập Kỷ → Rating Trung Bình

```
Trục Y  : genre (18 genres)
Trục X  : decade (1950 → 2010)
Màu ô   : avg_rating (xanh đậm = cao, trắng = TB, đỏ = thấp)
Tooltip : avg_rating, rating_count
Filter  : chỉ ô có rating_count ≥ 100 (tránh nhiễu từ ít dữ liệu)
```

**Collection:** `decade_stats`  
**Cột dùng:** `decade`, `genre`, `avg_rating`, `rating_count`

**Mục tiêu:** Phát hiện xu hướng chất lượng theo thời gian — genre nào đang tốt lên hay tệ đi qua các thập kỷ. Ví dụ: Animation thập kỷ 2000–2010 được đánh giá cao hơn 1990s → cho thấy chất lượng sản xuất cải thiện.

---

### Chart 2.5 — Combo Bar/Line: Popularity vs Quality per Genre

```
Bar (trục Y trái)  : rating_count (popularity — số lượng đánh giá)
Line (trục Y phải) : avg_rating (quality)
Trục X             : genre
Màu quadrant       :
  High Pop + High Quality  → "Blockbuster Genre"  → ưu tiên chiếu
  High Pop + Low Quality   → "Popular but Mediocre" → cẩn thận marketing
  Low Pop + High Quality   → "Hidden Gem"          → cơ hội marketing
  Low Pop + Low Quality    → "Avoid"                → ít chiếu
```

**Collection:** `genre_stats`  
**Cột dùng:** `genre`, `avg_rating`, `rating_count`

**Mục tiêu:** Bản đồ chiến lược genre — phân loại 18 genres vào 4 quadrant để ra quyết định lịch chiếu và chiến lược marketing.

---

---

## Dashboard 3 — Customer Segmentation & Recommendations

**Câu hỏi kinh doanh:** _Khách hàng của rạp là ai? Nên gợi ý phim gì cho từng nhóm để tối ưu marketing?_

**MongoDB collection chính:** `user_segments`, `segment_genre_preference`, `tag_stats`, `segment_recommendations`

---

### KPI Cards

| Card                  | Giá trị                  | Mục đích                        |
| --------------------- | ------------------------ | ------------------------------- |
| Tổng users            | 162,541                  | Quy mô khách hàng               |
| Tỷ lệ Heavy users     | % segment = Heavy        | Tỷ lệ khách hàng trung thành    |
| Top tag phổ biến nhất | TOP 1 tag by frequency   | Nội dung khán giả quan tâm nhất |
| Avg genre/user        | AVG(unique_genres_rated) | Độ đa dạng sở thích             |

---

### Chart 3.1 — Donut Chart: Phân Khúc Khách Hàng

```
Segments:
  Heavy  : ≥ 200 ratings  (khách hàng trung thành)
  Medium : 50–199 ratings (khách hàng thường xuyên)
  Light  : 20–49 ratings  (khách hàng thỉnh thoảng)

Hiển thị:
  Phần trăm và số lượng tuyệt đối mỗi segment
  Tooltip: avg_rating, avg unique_movies_rated của segment đó
```

**Collection:** `user_segments`  
**Cột dùng:** `segment`, `userId` (count), `avg_rating`, `rating_count`

**Mục tiêu:** Heavy users là "VIP" — cần chương trình ưu đãi và gợi ý đặc biệt. Light users có tiềm năng nâng cấp → cần chiến lược engagement (push notification, email marketing phim mới).

---

### Chart 3.2 — Grouped Bar: Genre Ưa Thích theo Phân Khúc

```
Trục X  : top genres (filter top 10)
Trục Y  : rating_count (số lượt rating trong segment đó)
Màu nhóm : Heavy / Medium / Light (3 bars per genre)
Sắp xếp : by total rating_count across all segments
Tooltip : avg_rating của segment đó với genre đó
```

**Collection:** `segment_genre_preference`  
**Cột dùng:** `segment`, `genre`, `rating_count`, `avg_rating`, `genre_rank`  
**Filter:** `genre_rank ≤ 10`

**Mục tiêu:** Hiểu sự khác biệt về gu phim giữa các nhóm → thiết kế email marketing khác nhau. Ví dụ: Heavy users thích Drama & Thriller → gửi thông báo phim mới của 2 genre này trước, tối thiểu 3 ngày trước suất chiếu.

---

### Chart 3.3 — Bar Chart: Top 20 Tags Phổ Biến Nhất

```
Trục Y  : tag (lowercase)
Trục X  : frequency (số lần được gán)
Màu     : gradient intensity by frequency
Sắp xếp : descending
Tooltip : frequency, % trong tổng số tags
```

**Collection:** `tag_stats`  
**Cột dùng:** `tag`, `frequency`  
**Filter:** TOP 20 by frequency

**Mục tiêu:** Tags phản ánh ngôn ngữ của khán giả khi mô tả phim — dùng làm từ khóa cho marketing content, mô tả phim trên app, và SEO (nếu có web). Tags cao → nội dung khán giả quan tâm.

---

### Chart 3.4 — Table: Top 10 Phim Gợi Ý cho Mỗi Segment (ALS)

```
Filter  : segment = [Heavy / Medium / Light] (dùng slicer)
Cột hiển thị:
  Rank             | rank
  Tên phim         | title_clean
  Genre            | genres_array
  Predicted Rating | avg_predicted_rating (★)
  # Users gợi ý   | recommended_to_users
```

**Collection:** `segment_recommendations`  
**Cột dùng:** `segment`, `rank`, `title_clean`, `genres_array`, `avg_predicted_rating`, `recommended_to_users`

**Mục tiêu:** Danh sách cụ thể để rạp đưa vào email/push notification gửi đến từng nhóm khách hàng. Phim rank 1–5 của Heavy users → ưu tiên đặt lịch chiếu tuần tới. Đây là output trực tiếp của ALS Collaborative Filtering.

---

### Chart 3.5 — Scatter Plot: User Activity vs Genre Diversity

```
Trục X  : rating_count (tổng số bộ phim đã rating — log scale)
Trục Y  : unique_genres_rated (đếm số genre khác nhau đã xem)
Màu     : segment (Heavy=đậm, Medium=trung, Light=nhạt)
Tooltip : userId (ẩn danh), avg_rating, top genre
```

**Collection:** `user_segments`  
**Cột dùng:** `userId`, `rating_count`, `unique_movies_rated`, `segment`, `avg_rating`

**Mục tiêu:** Phát hiện pattern ẩn trong hành vi khán giả. Ví dụ: Heavy users tập trung vào 2–3 genre (chuyên biệt) hay xem đủ thể loại (omnivore)? Kết quả ảnh hưởng đến cách thiết kế recommendation engine.

---

## Liên kết giữa các Dashboard

```
[Dashboard 1] genre_stats.genre
       ↕ liên kết
[Dashboard 2] genre_stats.genre   →  segment_genre_preference.genre
                                              ↕ liên kết
                                  [Dashboard 3] segment_genre_preference

[Dashboard 1] movies_enriched.movieId
       ↕ liên kết
[Dashboard 3] segment_recommendations.movieId
```

Trong Power BI, tạo relationships:

- `movies_enriched[movieId]` → `segment_recommendations[movieId]` _(many-to-one)_
- `genre_stats[genre]` → `segment_genre_preference[genre]` _(one-to-many)_
- `user_segments[segment]` → `segment_genre_preference[segment]` _(one-to-many)_
- `user_segments[segment]` → `segment_recommendations[segment]` _(one-to-many)_
