# Yêu cầu dữ liệu từ Task 3 để hoàn thiện BI Dashboard

> **Gửi:** Thành viên phụ trách Task 3 (analytics pipeline)  
> **Từ:** Thành viên phụ trách Phase 4 (BI Visualization)  
> **Mục đích:** Liệt kê các trường dữ liệu còn thiếu / sai trong export CSV hiện tại,  
> khiến 3 chart trong Streamlit dashboard chưa hiển thị được đúng spec.

---

## Tóm tắt nhanh

| Chart   | Vấn đề                                                   | File cần sửa                   | Trường cần bổ sung                                 |
| ------- | -------------------------------------------------------- | ------------------------------ | -------------------------------------------------- |
| **1.3** | `avg_revenue = 0` cho toàn bộ 201 rows                   | `decade_genre_heatmap.csv`     | `avg_revenue` (giá trị thực, triệu USD)            |
| **2.4** | `rating_count` max = 49, filter ≥ 100 không pass         | `decade_genre_heatmap.csv`     | `rating_count` (tính trên full data, không sample) |
| **3.1** | Chỉ có segment `Heavy`, thiếu `Medium` và `Light`        | `user_segments.csv`            | Phân khúc đúng theo threshold                      |
| **3.2** | Thiếu `Medium` và `Light` trong segment_genre_preference | `segment_genre_preference.csv` | Dữ liệu 3 segments                                 |
| **3.4** | `avg_predicted_rating = 5.0` cho tất cả (fallback giả)   | `segment_recommendations.csv`  | Giá trị ALS thực, hoặc popularity hợp lý           |
| **3.5** | Cột `unique_genres_rated` chưa tồn tại                   | `user_segments.csv`            | Cột mới `unique_genres_rated`                      |

---

## Chi tiết từng file

---

### 1. `visual/exports/decade_genre_heatmap.csv`

**Dùng cho:** Chart 1.3 (line) + Chart 2.4 (heatmap)

**Schema hiện tại:**

```
decade, genre, avg_rating, rating_count, movie_count, avg_revenue
```

#### Vấn đề A — `avg_revenue = 0` cho tất cả 201 rows

**Nguyên nhân:** Script fast-mode dùng `_extract_year(title)` để trích xuất năm từ tên phim.  
Các phim từ TMDB (vd: `"Avatar"`) không có định dạng `"Tên (YYYY)"` → `year = None` → `decade = None`  
→ dòng code `if decade is not None: decade_movie_stats[decade]["total_revenue"] += revenue` bị bỏ qua hoàn toàn.

**Yêu cầu:** `avg_revenue` phải là **trung bình doanh thu thực tế (USD, dạng số nguyên)** của các phim có revenue > 0 trong từng ô (decade, genre). Giá trị mẫu kỳ vọng:

| decade | genre  | avg_revenue (USD) |
| ------ | ------ | ----------------- |
| 2010   | Action | ~150,000,000      |
| 2000   | Drama  | ~45,000,000       |

**Fix gợi ý:**

```python
year = (
    _safe_int(movie.get("release_year"))
    or _safe_int(str(movie.get("release_date", ""))[:4])
    or _extract_year(movie.get("title", ""))
)
```

---

#### Vấn đề B — `rating_count` quá thấp (max = 49)

**Nguyên nhân:** `TASK3_FAST_SAMPLE_FRACTION = 0.0005` → chỉ 12,500 ratings (~49 max per genre×decade cell).  
Dashboard cần filter `rating_count >= 100` để loại ô nhiễu (theo spec Chart 2.4). Với 49 max → toàn bộ bị lọc → heatmap trống.

**Yêu cầu:** Mỗi ô (decade, genre) cần `rating_count` là **tổng số ratings thực** của toàn bộ movies trong ô đó.  
Kỳ vọng: Drama×2000s ≥ 1,000,000 ratings; các ô nhỏ nhất ≥ 100.

**Fix gợi ý:** Tăng sample fraction hoặc dùng Spark full:

```bash
TASK3_ANALYTICS_SAMPLE_FRACTION=0.05 python analytics_modeling.py
# hoặc
TASK3_FAST_MODE=0 python analytics_modeling.py
```

---

### 2. `visual/exports/user_segments.csv`

**Dùng cho:** Chart 3.1 (donut), Chart 3.5 (scatter)

**Schema hiện tại:**

```
userId, segment, rating_count, avg_rating, unique_movies_rated
```

#### Vấn đề A — Tất cả users đều là `Heavy`

**Nguyên nhân:** Với 12,500 ratings / ~8,000 users → median = 1–2 ratings/user. Quantile-based threshold dẫn đến `q1 = q2 = 1`, mọi user đều thành "Heavy".

**Yêu cầu:** Phân khúc theo **threshold tuyệt đối** (per DASHBOARDS.md spec):

| Segment | Điều kiện      | Mô tả                   |
| ------- | -------------- | ----------------------- |
| Heavy   | ≥ 200 ratings  | Khách hàng trung thành  |
| Medium  | 50–199 ratings | Khách hàng thường xuyên |
| Light   | < 50 ratings   | Khách hàng thỉnh thoảng |

**Kết quả kỳ vọng:**

```
Heavy  : ~25–35% users  (approx 40,000–57,000 users)
Medium : ~15–25% users
Light  : ~45–55% users  (số lớn vì nhiều users chỉ rate 1–2 phim)
```

**Fix gợi ý:**

```python
def _segment(count):
    if count >= 200: return "Heavy"
    elif count >= 50: return "Medium"
    else:            return "Light"
user_df["segment"] = user_df["rating_count"].apply(_segment)
```

---

#### Vấn đề B — Thiếu cột `unique_genres_rated`

**Nguyên nhân:** Cột này chưa được tính trong pipeline hiện tại.

**Yêu cầu:** Thêm cột `unique_genres_rated` = **số lượng genre khác nhau mà user đã rate ít nhất 1 phim**.

**Cách tính:**

```python
# ratings.csv + movies.csv (explode genres)
user_genre_counts = (
    ratings
    .merge(movies[["movieId","genres"]], on="movieId")
    .assign(genre=lambda df: df["genres"].str.split("|"))
    .explode("genre")
    .groupby("userId")["genre"]
    .nunique()
    .rename("unique_genres_rated")
    .reset_index()
)
user_df = user_df.merge(user_genre_counts, on="userId", how="left")
user_df["unique_genres_rated"] = user_df["unique_genres_rated"].fillna(0).astype(int)
```

**Schema mong đợi sau khi sửa:**

```
userId, segment, rating_count, avg_rating, unique_movies_rated, unique_genres_rated
```

---

### 3. `visual/exports/segment_genre_preference.csv`

**Dùng cho:** Chart 3.2 (grouped bar)

**Schema hiện tại:**

```
segment, genre, rating_count, avg_rating, genre_rank
```

**Vấn đề:** Chỉ có rows với `segment = "Heavy"`. Không có `Medium` và `Light`.

**Nguyên nhân:** Hệ quả trực tiếp của vấn đề segmentation ở trên — tất cả users đều là "Heavy" → không có users "Medium"/"Light" để tính preference.

**Yêu cầu:** Sau khi sửa `user_segments.csv`, chạy lại pipeline export để có đủ 3 segments.

**Kết quả kỳ vọng (mẫu):**

| segment | genre  | rating_count | avg_rating | genre_rank |
| ------- | ------ | ------------ | ---------- | ---------- |
| Heavy   | Drama  | 5,806        | 3.68       | 1          |
| Medium  | Drama  | ~1,200       | ~3.6       | 1          |
| Light   | Comedy | ~300         | ~3.4       | 1          |

---

### 4. `visual/exports/segment_recommendations.csv`

**Dùng cho:** Chart 3.4 (recommendation table)

**Schema hiện tại:**

```
segment, movieId, avg_predicted_rating, recommended_to_users, rank, title_clean, genres_array, avg_rating
```

**Vấn đề:** `avg_predicted_rating = 5.0` cho tất cả (popularity-based fallback, không phải ALS).

**Yêu cầu theo spec:** Giá trị `avg_predicted_rating` phải là **giá trị dự đoán từ ALS model**, không phải 5.0 cứng.

**Nếu ALS không thể chạy** (giới hạn resource), dùng fallback hợp lý:

```python
# Dùng avg_rating làm proxy — KHÔNG hardcode 5.0
avg_predicted_rating = movie["avg_rating"]  # Giá trị thực từ MovieLens
```

**Kết quả kỳ vọng (mẫu):**

| segment | rank | title_clean              | avg_predicted_rating | recommended_to_users |
| ------- | ---- | ------------------------ | -------------------- | -------------------- |
| Heavy   | 1    | The Shawshank Redemption | 4.43                 | 10,920               |
| Medium  | 1    | Schindler's List         | 4.31                 | 4,200                |
| Light   | 1    | Forrest Gump             | 4.12                 | 6,800                |

---

## Thứ tự ưu tiên

```
Priority 1 — Blocking nhiều chart nhất:
  → Sửa user segmentation (Heavy/Medium/Light đúng threshold)
    File: user_segments.csv + segment_genre_preference.csv

Priority 2 — Blocking Chart 1.3 + 2.4:
  → Sửa avg_revenue và rating_count trong decade_genre_heatmap.csv

Priority 3 — Hoàn thiện Chart 3.5:
  → Thêm cột unique_genres_rated vào user_segments.csv

Priority 4 — Cải thiện chất lượng:
  → Sửa avg_predicted_rating trong segment_recommendations.csv
```

---

## Kiểm tra sau khi sửa

```python
import pandas as pd

# 1. decade_genre_heatmap.csv
df = pd.read_csv("visual/exports/decade_genre_heatmap.csv")
print("avg_revenue non-zero:", (df.avg_revenue > 0).sum(), "/", len(df))   # Kỳ vọng: > 150
print("rating_count max:", df.rating_count.max())                          # Kỳ vọng: > 100,000

# 2. user_segments.csv
df2 = pd.read_csv("visual/exports/user_segments.csv")
print("Segments:", df2.segment.value_counts().to_dict())                    # Kỳ vọng: 3 segments
print("Has unique_genres_rated:", "unique_genres_rated" in df2.columns)    # Kỳ vọng: True

# 3. segment_genre_preference.csv
df3 = pd.read_csv("visual/exports/segment_genre_preference.csv")
print("Segments in preference:", df3.segment.unique().tolist())             # Kỳ vọng: ['Heavy','Medium','Light']

# 4. segment_recommendations.csv
df4 = pd.read_csv("visual/exports/segment_recommendations.csv")
print("Max predicted rating:", df4.avg_predicted_rating.max())             # Kỳ vọng: < 5.0
print("Segments in recs:", df4.segment.unique().tolist())                   # Kỳ vọng: 3 segments
```
