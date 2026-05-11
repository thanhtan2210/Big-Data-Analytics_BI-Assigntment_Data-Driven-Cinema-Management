# Docker Screenshot Guide

Hướng dẫn dựng toàn bộ môi trường (MongoDB + Hadoop + Spark) bằng Docker
Compose để có thể **chụp lại đầy đủ các bằng chứng (evidence) cần thiết cho
báo cáo**: HDFS Web UI, DataNode Web UI, Spark UI, MongoDB shell, log của
pipeline tiền xử lý, v.v.

> Mục tiêu: bất kỳ máy nào (macOS / Linux / Windows + WSL2) có Docker và
> Docker Compose là chạy được, không cần cài Hadoop / Spark thủ công.

---

## 1. Yêu cầu phần mềm

| Phần mềm        | Phiên bản tối thiểu | Ghi chú                                              |
| --------------- | ------------------- | ---------------------------------------------------- |
| Docker          | 24.x                | bật BuildKit nếu có                                  |
| Docker Compose  | v2 (tích hợp trong Docker Desktop) | dùng lệnh `docker compose` (không phải `docker-compose`) |
| RAM khả dụng    | >= 8 GB             | Hadoop + Spark + Mongo nên cần tối thiểu 6 GB free   |
| Ổ đĩa trống     | >= 10 GB            | MovieLens 25M giải nén ~1.2 GB, thêm volume HDFS     |

**Cài đặt nhanh:**
- macOS / Windows: tải **Docker Desktop** từ <https://www.docker.com/products/docker-desktop>.
- Linux (Ubuntu): `curl -fsSL https://get.docker.com | sh` rồi thêm user vào nhóm `docker`.

Kiểm tra:
```bash
docker version
docker compose version
```

---

## 2. Cấu hình môi trường

Tại thư mục gốc dự án, sao chép file mẫu thành `.env`:

```bash
cp .env.example .env
```

Mở `.env` và chỉnh nếu cần (mặc định đã chạy được với docker compose).

Các biến quan trọng:

| Biến                          | Mặc định                                   | Ý nghĩa                                            |
| ----------------------------- | ------------------------------------------ | -------------------------------------------------- |
| `HDFS_HOST`                   | `localhost` (host) / `namenode` (Spark)    | endpoint HDFS                                      |
| `HDFS_PORT`                   | `9000`                                     | cổng RPC của NameNode                              |
| `PROJECT_HDFS_RAW_MOVIELENS`  | `/project/cinema/raw/movielens`            | nơi chứa MovieLens trên HDFS                       |
| `PROJECT_HDFS_RAW_TMDB`       | `/project/cinema/raw/tmdb`                 | nơi chứa TMDB trên HDFS                            |
| `MONGO_URI`                   | `mongodb://mongodb:27017/`                 | URI MongoDB (dùng tên service)                     |
| `MONGO_DB`                    | `cinema_dw`                                | tên database đích                                  |

---

## 3. Khởi động toàn bộ stack

Từ thư mục gốc dự án:

```bash
docker compose up -d
docker compose ps
```

Khi tất cả service ở trạng thái `Up` / `running`, các endpoint sau sẽ sẵn sàng:

| Service              | URL / cổng                    |
| -------------------- | ----------------------------- |
| HDFS NameNode Web UI | <http://localhost:9870>       |
| HDFS NameNode RPC    | `hdfs://localhost:9000`       |
| HDFS DataNode Web UI | <http://localhost:9864>       |
| Spark Master Web UI  | <http://localhost:8080>       |
| Spark App Web UI     | <http://localhost:4040> (khi job đang chạy) |
| MongoDB              | `mongodb://localhost:27017`   |

Theo dõi log:
```bash
docker compose logs -f namenode
docker compose logs -f datanode
docker compose logs -f spark
docker compose logs -f mongodb
```

---

## 4. Tải dữ liệu MovieLens & upload lên HDFS

```bash
# Bước 1: tải MovieLens 25M về data/raw/ml-25m/
bash scripts/download_movielens.sh

# Bước 2: đẩy dữ liệu lên HDFS thông qua container namenode
bash scripts/upload_to_hdfs.sh
```

Kiểm tra trực tiếp trong container:
```bash
docker exec -it cinema-namenode hdfs dfs -ls /project/cinema/raw/movielens
```

---

## 5. Chạy pipeline tiền xử lý PySpark

```bash
bash scripts/run_preprocessing_docker.sh
```

Sau khi job kết thúc, kiểm tra các collection được nạp vào MongoDB:

```bash
docker exec -it cinema-mongodb mongosh --quiet \
  --eval 'use cinema_dw; show collections; db.movies.countDocuments(); db.ratings.countDocuments()'
```

---

## 6. Checklist ảnh cho báo cáo

Chụp lần lượt theo thứ tự sau và lưu vào `artifacts/screenshots/` với tên tương ứng:

| #  | Tên ảnh (gợi ý)                                | Nội dung cần thấy trong ảnh                                                       |
| -- | ---------------------------------------------- | ---------------------------------------------------------------------------------- |
| 1  | `01_docker_compose_ps.png`                     | terminal: kết quả `docker compose ps` với tất cả service `Up`                       |
| 2  | `02_hdfs_web_ui_overview.png`                  | trình duyệt: <http://localhost:9870> – tab **Overview**, hiển thị cluster id, capacity |
| 3  | `03_hdfs_web_ui_datanodes.png`                 | <http://localhost:9870> – tab **Datanodes**, thấy 1 DataNode `In Service`           |
| 4  | `04_hdfs_browse_movielens.png`                 | <http://localhost:9870/explorer.html#/project/cinema/raw/movielens> – danh sách CSV |
| 5  | `05_datanode_web_ui.png`                       | <http://localhost:9864> – DataNode Web UI                                           |
| 6  | `06_download_movielens.png`                    | terminal: log `bash scripts/download_movielens.sh` chạy thành công                  |
| 7  | `07_upload_to_hdfs.png`                        | terminal: log `bash scripts/upload_to_hdfs.sh` – các dòng `-> ...csv` + `hdfs dfs -ls` cuối |
| 8  | `08_spark_master_ui.png`                       | <http://localhost:8080> – Spark Master Web UI, trạng thái `ALIVE`                   |
| 9  | `09_run_preprocessing_docker.png`              | terminal: log job preprocessing, các dòng `Loading MovieLens data ...`, `Pushing cleaned data to MongoDB ...` |
| 10 | `10_spark_app_ui.png`                          | <http://localhost:4040> – Spark application UI khi job đang chạy (Jobs / Stages)    |
| 11 | `11_mongosh_collections.png`                   | terminal: `mongosh --eval 'use cinema_dw; show collections'` thấy `movies, ratings, tags` |
| 12 | `12_mongosh_sample_movie.png`                  | terminal: `db.movies.find({ title: /Toy Story/i }).limit(2).pretty()` ra kết quả    |

> Mẹo: dùng tổ hợp phím chụp toàn cửa sổ trình duyệt / cửa sổ terminal để giữ
> được thanh URL và các tab — đây là phần giám khảo cần để xác minh.

---

## 7. Render các sơ đồ Mermaid

Bốn sơ đồ kiến trúc nằm trong `artifacts/diagrams/`:

- `system_architecture.mmd`
- `erd_movielens.mmd`
- `preprocessing_pipeline.mmd`
- `analytics_pipeline.mmd`

Cách render nhanh nhất:

1. Mở <https://mermaid.live>.
2. Dán nội dung file `.mmd` vào trình soạn thảo.
3. Bấm **Actions → PNG** (hoặc **SVG**) và lưu vào `artifacts/screenshots/`.

Hoặc dùng Mermaid CLI:

```bash
npx -y @mermaid-js/mermaid-cli -i artifacts/diagrams/system_architecture.mmd \
  -o artifacts/screenshots/system_architecture.png -b transparent
```

---

## 8. Lưu ý quan trọng

- **Dừng stack đúng cách** khi không dùng nữa:
  ```bash
  docker compose down
  # xoá luôn dữ liệu (chỉ khi muốn reset hoàn toàn):
  docker compose down -v
  ```
- Cổng `9000` (HDFS RPC) hoặc `27017` (MongoDB) có thể đã bị một service khác
  trên máy bạn chiếm. Khi đó hãy đổi port mapping trong `docker-compose.yml`
  (ví dụ `27018:27017`) và cập nhật `MONGO_URI` trong `.env` cho khớp.
- Lần đầu chạy `docker compose up -d` sẽ tốn vài phút để tải image
  (`bde2020/hadoop-namenode`, `bde2020/hadoop-datanode`, `bitnami/spark`,
  `mongo:7.0`). Hãy chuẩn bị kết nối Internet ổn định.
- Lần đầu NameNode khởi động sẽ tự `format` namespace; trên macOS Apple Silicon
  có thể mất ~30–60 giây. Nếu Web UI 9870 chưa lên, đợi thêm rồi `docker compose logs namenode`.
- `data/`, `data/raw/`, và các CSV MovieLens **không nên** được commit vào git —
  thêm chúng vào `.gitignore` nếu chưa có.
- Khi chụp ảnh, đảm bảo trên thanh URL của trình duyệt thấy `localhost:9870`,
  `localhost:9864`, `localhost:8080`, `localhost:4040` để chứng minh các service
  đang chạy.
