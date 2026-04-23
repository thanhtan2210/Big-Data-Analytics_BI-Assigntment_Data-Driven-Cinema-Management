# 9. Analytics & Recommendation Modeling

## 9.1 Muc tieu

Muc 3 tap trung vao 3 ket qua chinh:

1. Phan tich xu huong doanh thu va rating tren du lieu lon bang Spark SQL.
2. Xay dung he goi y phim bang Collaborative Filtering (ALS).
3. Tao bo bang tong hop toi uu cho dashboard BI va quyet dinh kinh doanh.

## 9.2 Dau vao

Nguon du lieu duoc doc tu MongoDB sau Muc 2:

- `movies`
- `ratings`
- `tags`

Gia tri mac dinh:

- `MONGO_URI=mongodb://127.0.0.1:27017/`
- `MONGO_DB=cinema_dw`

## 9.3 Cac buoc xu ly trong pipeline

Script: `thang/scripts/analytics_modeling.py`

1. Chuan hoa movie metadata:

- Tach `title_clean`, `year`, `decade`.
- Chuan hoa `genres_array`.
- Tinh `roi = (revenue - budget) / budget`.

2. Revenue trend analysis:

- `genre_stats`: tong hop theo genre.
- `decade_stats`: tong hop theo decade x genre.
- `year_stats`: xu huong rating theo nam.
- `rating_dist`: phan bo diem rating.

3. User behavior analysis:

- Phan khuc nguoi dung thanh `Heavy`, `Medium`, `Light`.
- Tinh so lieu so thich genre theo tung segment.
- Tong hop tag pho bien (`tag_stats`).

4. Recommendation modeling (ALS):

- Chia tap train/validation/test = 80/10/10.
- Grid search tren `rank`, `regParam`, `maxIter`.
- Chon model theo RMSE validation nho nhat.
- Danh gia lai tren test set.
- Sinh `Top-N` recommendations theo tung segment.

5. Ghi ket qua:

- Ghi 9 collections analytics vao MongoDB.
- Luu metrics tuning tai `thang/artifacts/metrics/als_metrics.json`.

## 9.4 Lenh chay

```bash
cd /Users/hosythang/Downloads/BI/Big-Data-Analytics_BI-Assigntment_Data-Driven-Cinema-Management

python3 -m venv venv
source venv/bin/activate
pip install -r thang/requirements.txt

chmod +x thang/scripts/run_task3_pipeline.sh
./thang/scripts/run_task3_pipeline.sh
```

## 9.5 Bien moi truong co the tinh chinh

- `ALS_RANK_GRID` (vd: `20,40,60`)
- `ALS_REG_GRID` (vd: `0.05,0.1,0.2`)
- `ALS_MAX_ITER_GRID` (vd: `10,15,20`)
- `ALS_TOP_N` (mac dinh 10)
- `ALS_SEED` (mac dinh 42)

## 9.6 Kiem tra ket qua

```javascript
use cinema_dw;
show collections;

db.genre_stats.find().limit(5).pretty();
db.decade_stats.find().limit(5).pretty();
db.segment_recommendations.find().limit(5).pretty();
```

## 9.7 Ket qua mong doi

- Co metrics RMSE ro rang cho model ALS.
- Co bo bang aggregate day du cho dashboard doanh thu/rating/recommendation.
- Co bo recommendations theo segment de toi uu marketing.
