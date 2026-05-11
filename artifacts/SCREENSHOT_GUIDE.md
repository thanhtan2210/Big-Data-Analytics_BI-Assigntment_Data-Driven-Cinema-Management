# Hướng dẫn chụp ảnh cho báo cáo

Tài liệu này liệt kê toàn bộ ảnh cần chụp cho báo cáo dự án **Data-Driven Cinema Management**, kèm theo:
- Mô tả nội dung từng ảnh
- Cách chụp (lệnh shell hoặc ứng dụng cần mở)
- Vị trí lưu file
- Các lưu ý quan trọng

> **Quy ước chung**
> - `PROJECT_ROOT` = thư mục gốc của repo này
> - Tất cả ảnh PNG đều lưu vào `PROJECT_ROOT/artifacts/screenshots/`
> - Các file Mermaid (`.mmd`) nằm trong `PROJECT_ROOT/artifacts/diagrams/` — dùng <https://mermaid.live/> để export sang PNG
> - Script trợ giúp: `PROJECT_ROOT/artifacts/capture_screenshots.sh`

---

## Tổng quan thư mục

```
artifacts/
├── diagrams/                 # 4 file Mermaid (.mmd) để render thành PNG
│   ├── system_architecture.mmd
│   ├── erd_movielens.mmd
│   ├── preprocessing_pipeline.mmd
│   └── analytics_pipeline.mmd
├── screenshots/              # Nơi lưu toàn bộ ảnh PNG đã chụp
├── terminal_logs/            # Log terminal đi kèm (tùy chọn)
├── capture_screenshots.sh    # Script in hướng dẫn từng bước
└── SCREENSHOT_GUIDE.md       # Tài liệu này
```

---

## NHÓM 1: Architecture & HDFS

### 1. `system_architecture.png` — Kiến trúc tổng thể hệ thống
- **Nội dung:** Sơ đồ luồng dữ liệu MovieLens + TMDB → HDFS → PySpark → MongoDB → Streamlit/Power BI.
- **Cách chụp:**
  1. Mở file `artifacts/diagrams/system_architecture.mmd`
  2. Copy toàn bộ nội dung
  3. Paste vào <https://mermaid.live/>
  4. Bấm **Actions → PNG** để export
- **Lưu:** `artifacts/screenshots/system_architecture.png`

### 2. `java_hadoop_version.png` — Phiên bản Java & Hadoop
- **Nội dung:** Kết quả `java -version` và `hadoop version` trong terminal.
- **Cách chụp:**
  ```bash
  java -version
  hadoop version
  ```
  Chụp toàn bộ terminal sau khi cả hai lệnh chạy xong.
- **Lưu:** `artifacts/screenshots/java_hadoop_version.png`

### 3. `jps_after_start.png` — HDFS daemons đang chạy
- **Nội dung:** Output `jps` cho thấy `NameNode` và `DataNode` đã start.
- **Cách chụp:**
  ```bash
  source $PROJECT_ROOT/scripts/activate.sh
  hdfs --daemon start namenode
  hdfs --daemon start datanode
  jps
  ```
- **Lưu:** `artifacts/screenshots/jps_after_start.png`

### 4. `hdfs_webui.png` — HDFS Web UI
- **Nội dung:** Trang Summary của HDFS NameNode UI.
- **Cách chụp:**
  1. Mở trình duyệt → <http://localhost:9870>
  2. Chụp phần **Summary** (Configured Capacity, Live Nodes, Used,…)
- **Lưu:** `artifacts/screenshots/hdfs_webui.png`

### 5. `hdfs_ls_du.png` — Dữ liệu raw trên HDFS
- **Nội dung:** Danh sách file MovieLens và dung lượng theo `-du -h`.
- **Cách chụp:**
  ```bash
  source $PROJECT_ROOT/scripts/activate.sh
  hdfs dfs -ls /project/cinema/raw/movielens
  hdfs dfs -du -h /project/cinema/raw/movielens
  ```
- **Lưu:** `artifacts/screenshots/hdfs_ls_du.png`

---

## NHÓM 2: Data Input

### 6. `tmdb_preview.png` — Preview file TMDB Revenue
- **Nội dung:** 5–10 dòng đầu của `data/raw/tmdb_revenue.csv` (cột `id`, `title`, `revenue`, `budget`, …).
- **Cách chụp:**
  - Mở file `data/raw/tmdb_revenue.csv` bằng Excel hoặc VS Code
  - Chụp 5–10 dòng đầu, đảm bảo nhìn rõ header
- **Lưu:** `artifacts/screenshots/tmdb_preview.png`

### 7. `erd_movielens.png` — Sơ đồ ERD MovieLens
- **Nội dung:** Quan hệ giữa `USERS`, `MOVIES`, `RATINGS`, `TAGS`, `LINKS`.
- **Cách chụp:** Render `artifacts/diagrams/erd_movielens.mmd` qua <https://mermaid.live/> → export PNG.
- **Lưu:** `artifacts/screenshots/erd_movielens.png`

---

## NHÓM 3: Preprocessing

### 8. `preprocessing_pipeline.png` — Sơ đồ pipeline preprocessing
- **Nội dung:** Các bước Load → Clean → Filter → Merge → Write to MongoDB.
- **Cách chụp:** Render `artifacts/diagrams/preprocessing_pipeline.mmd` qua <https://mermaid.live/> → export PNG.
- **Lưu:** `artifacts/screenshots/preprocessing_pipeline.png`

### 9. `analytics_pipeline.png` — Sơ đồ pipeline analytics
- **Nội dung:** MongoDB → Spark Analytics → 9 Collections + ALS Model.
- **Cách chụp:** Render `artifacts/diagrams/analytics_pipeline.mmd` qua <https://mermaid.live/> → export PNG.
- **Lưu:** `artifacts/screenshots/analytics_pipeline.png`

### 10. `preprocessing_output.png` — Output Spark preprocessing
- **Nội dung:** Output cuối của job preprocessing, kết thúc bằng `Data Preprocessing Pipeline Completed!`.
- **Cách chụp:**
  ```bash
  chmod +x $PROJECT_ROOT/scripts/run_preprocessing.sh
  $PROJECT_ROOT/scripts/run_preprocessing.sh
  ```
  Chụp các dòng cuối của terminal (đảm bảo thấy dòng "Completed").
- **Lưu:** `artifacts/screenshots/preprocessing_output.png`

### 11. `mongodb_count.png` — Số document trong MongoDB
- **Nội dung:** Kết quả `countDocuments()` cho `movies`, `ratings`, `tags`.
- **Cách chụp:**
  ```bash
  mongosh "mongodb://localhost:27017"
  ```
  Trong mongosh:
  ```javascript
  use cinema_dw
  db.movies.countDocuments()
  db.ratings.countDocuments()
  db.tags.countDocuments()
  ```
- **Lưu:** `artifacts/screenshots/mongodb_count.png`

### 12. `mongodb_compass_overview.png` — MongoDB Compass overview
- **Nội dung:** Tab **Databases** trong Compass, thấy rõ database `cinema_dw` và danh sách collections.
- **Cách chụp:**
  1. Mở MongoDB Compass
  2. Kết nối: `mongodb://localhost:27017`
  3. Chọn database `cinema_dw`
  4. Chụp tab Databases / Collections
- **Lưu:** `artifacts/screenshots/mongodb_compass_overview.png`

---

## NHÓM 4: Analytics & Dashboard

### 13. `analytics_collections.png` — 9 collections phân tích (tùy chọn)
- **Nội dung:** Danh sách collections sau khi chạy analytics (`genre_stats`, `movies_enriched`, `decade_genre_heatmap`, …).
- **Cách chụp:**
  ```bash
  mongosh "mongodb://localhost:27017"
  ```
  ```javascript
  use cinema_dw
  show collections
  ```
- **Lưu:** `artifacts/screenshots/analytics_collections.png`

### 14. `streamlit_dashboard_full.png` — Streamlit dashboard
- **Nội dung:** Toàn màn hình dashboard Streamlit (charts, KPIs, filters).
- **Cách chụp:**
  ```bash
  source $PROJECT_ROOT/scripts/activate.sh
  streamlit run $PROJECT_ROOT/visual/streamlit_app/app.py
  ```
  Mở <http://localhost:8501> → chụp toàn màn hình.
- **Lưu:** `artifacts/screenshots/streamlit_dashboard_full.png`

---

## Cách render các file Mermaid sang PNG

Bạn có hai lựa chọn:

### Cách 1: Dùng web (khuyến nghị, không cần cài thêm gì)
1. Truy cập <https://mermaid.live/>
2. Mở file `.mmd` cần render, copy toàn bộ nội dung
3. Paste vào ô **Code** ở bên trái
4. Bấm **Actions → PNG** (hoặc SVG) để tải về
5. Đổi tên file đúng quy ước trong tài liệu này, rồi đặt vào `artifacts/screenshots/`

### Cách 2: Dùng Mermaid CLI (offline)
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i artifacts/diagrams/system_architecture.mmd -o artifacts/screenshots/system_architecture.png
mmdc -i artifacts/diagrams/erd_movielens.mmd -o artifacts/screenshots/erd_movielens.png
mmdc -i artifacts/diagrams/preprocessing_pipeline.mmd -o artifacts/screenshots/preprocessing_pipeline.png
mmdc -i artifacts/diagrams/analytics_pipeline.mmd -o artifacts/screenshots/analytics_pipeline.png
```

---

## Lưu ý quan trọng

- **Khởi động dịch vụ trước khi chụp:**
  - HDFS NameNode + DataNode phải đang chạy (kiểm tra bằng `jps`).
  - MongoDB phải đang lắng nghe ở `localhost:27017`.
  - Streamlit (port 8501) chạy sau khi dữ liệu đã được nạp vào MongoDB.
- **Dữ liệu đầu vào:**
  - File `tmdb_revenue.csv` cần tải về và đặt vào `data/raw/` trước khi chạy preprocessing.
  - Dataset MovieLens 25M cần được upload lên HDFS tại `/project/cinema/raw/movielens` (xem `scripts/`).
- **Đặt tên file:** giữ nguyên tên đã quy định trong tài liệu này để báo cáo dễ tham chiếu.
- **Độ phân giải:** chụp ở chế độ cửa sổ full HD trở lên để chữ rõ nét khi in.
- **Script hỗ trợ:** chạy `bash artifacts/capture_screenshots.sh` để in hướng dẫn từng bước ra terminal.

---

## Checklist

- [ ] `system_architecture.png`
- [ ] `java_hadoop_version.png`
- [ ] `jps_after_start.png`
- [ ] `hdfs_webui.png`
- [ ] `hdfs_ls_du.png`
- [ ] `tmdb_preview.png`
- [ ] `erd_movielens.png`
- [ ] `preprocessing_pipeline.png`
- [ ] `analytics_pipeline.png`
- [ ] `preprocessing_output.png`
- [ ] `mongodb_count.png`
- [ ] `mongodb_compass_overview.png`
- [ ] `analytics_collections.png` *(tùy chọn)*
- [ ] `streamlit_dashboard_full.png`
