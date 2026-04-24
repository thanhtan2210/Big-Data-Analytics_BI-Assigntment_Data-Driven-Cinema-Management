# visual/ — Phase 4: BI Visualization

Thư mục này chứa toàn bộ sản phẩm của **Phase 4 — Business Intelligence & Visualization**:
Streamlit dashboard prototype, dữ liệu export từ pipeline Task 3, và tài liệu kỹ thuật.

---

## Cấu trúc thư mục

```
visual/
├── README.md                  ← file này
├── DASHBOARDS.md              ← đặc tả 3 dashboard, 15 charts (spec gốc)
│
├── streamlit_app/             ← ứng dụng Streamlit prototype
│   ├── app.py                 ← entry point: toàn bộ UI + chart logic (~650 dòng)
│   ├── data.py                ← data loaders: đọc từ exports/*.csv (9 hàm)
│   └── README.md              ← hướng dẫn cài đặt và chạy
│
├── exports/                   ← CSV output từ pipeline Task 3 (serving layer)
│   ├── genre_stats.csv            → Charts 1.1, 1.2, 1.4, 2.1, 2.5
│   ├── movies_enriched.csv        → Chart 1.5 (Top 20 movies table)
│   ├── decade_genre_heatmap.csv   → Chart 1.3, 2.4  ⚠️ avg_revenue = 0 (chờ Task 3)
│   ├── year_stats.csv             → Chart 2.3 (dual-axis timeline)
│   ├── rating_distribution.csv    → Chart 2.2 (histogram)
│   ├── user_segments.csv          → Charts 3.1, 3.5  ⚠️ thiếu cột, chỉ 1 segment
│   ├── segment_genre_preference.csv → Chart 3.2      ⚠️ chỉ có segment Heavy
│   ├── segment_recommendations.csv  → Chart 3.4      ⚠️ predicted_rating = 5.0
│   ├── tag_stats.csv              → Chart 3.3 (tag bar)
│   └── mapreduce/                 ← raw output từ MapReduce jobs
│       ├── mr_genre_rating/
│       ├── mr_rating_distribution/
│       └── mr_decade_genre_heatmap/
│
├── docs/                      ← tài liệu kỹ thuật Phase 4
│   ├── 12_suggested_table.md          ← bảng dữ liệu dự kiến theo DASHBOARDS.md
│   ├── 13_task3_data_fields_and_mapreduce.md ← schema chi tiết các bảng export
│   ├── 14_task3_results.md            ← kết quả pipeline Task 3 hiện tại
│   ├── 15_dashboard_data_mapping_task3.md   ← mapping chart → collection → cột
│   ├── 16_streamlit_run_guide.md      ← hướng dẫn chạy Streamlit (Windows)
│   └── 17_task3_data_requirements_for_bi.md ← yêu cầu bổ sung dữ liệu gửi Task 3
│
└── img/                       ← screenshots / hình ảnh cho báo cáo
```

---

## 3 Dashboards

| Dashboard                     | Câu hỏi kinh doanh                                                       | Charts                                                              |
| ----------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| **1 — Revenue & Genre**       | Genre nào sinh lời cao nhất? Ưu tiên lịch chiếu ngày lễ thế nào?         | 1.1 Bar, 1.2 Bubble, 1.3 Line, 1.4 Treemap, 1.5 Table               |
| **2 — Audience Engagement**   | Xu hướng đánh giá theo thời gian? Genre nào vừa phổ biến vừa chất lượng? | 2.1 Bar, 2.2 Histogram, 2.3 Dual-axis, 2.4 Heatmap, 2.5 Combo       |
| **3 — Customer Segmentation** | Phân khúc khách hàng ra sao? Gợi ý phim nào cho từng nhóm?               | 3.1 Donut, 3.2 Grouped bar, 3.3 Tag bar, 3.4 Rec table, 3.5 Scatter |

Mô tả chi tiết từng chart: [`DASHBOARDS.md`](DASHBOARDS.md)

---

## Chạy nhanh

```powershell
# từ root project
.\.venv\Scripts\activate
.\.venv\Scripts\streamlit.exe run visual/streamlit_app/app.py
```

Mở trình duyệt tại **http://localhost:8501**

Hướng dẫn đầy đủ: [`docs/16_streamlit_run_guide.md`](docs/16_streamlit_run_guide.md)

---

## Trạng thái dữ liệu

| File                           | Trạng thái                             | Ảnh hưởng                                           |
| ------------------------------ | -------------------------------------- | --------------------------------------------------- |
| `genre_stats.csv`              | ✅ Đầy đủ                              | Charts 1.1, 1.2, 1.4, 2.1, 2.5 hiển thị bình thường |
| `movies_enriched.csv`          | ✅ Đầy đủ                              | Chart 1.5 hiển thị bình thường                      |
| `year_stats.csv`               | ✅ Đầy đủ                              | Chart 2.3 hiển thị bình thường                      |
| `rating_distribution.csv`      | ✅ Đầy đủ                              | Chart 2.2 hiển thị bình thường                      |
| `tag_stats.csv`                | ✅ Đầy đủ                              | Chart 3.3 hiển thị bình thường                      |
| `decade_genre_heatmap.csv`     | ⚠️ avg_revenue = 0, rating_count < 100 | Charts 1.3, 2.4 hiển thị thông báo chờ              |
| `user_segments.csv`            | ⚠️ chỉ 1 segment, thiếu cột            | Charts 3.1, 3.5 bị giới hạn                         |
| `segment_genre_preference.csv` | ⚠️ chỉ Heavy                           | Chart 3.2 bị giới hạn                               |
| `segment_recommendations.csv`  | ⚠️ predicted = 5.0                     | Chart 3.4 hiển thị nhưng không chính xác            |

Yêu cầu bổ sung gửi Task 3: [`docs/17_task3_data_requirements_for_bi.md`](docs/17_task3_data_requirements_for_bi.md)
