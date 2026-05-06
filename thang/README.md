# Task 3 - Analytics & Recommendation Modeling (Thang)

Thu muc nay chua toan bo code va tai lieu cho **Nhiem vu 3** trong project:

- Revenue Trend Analysis (Spark SQL)
- Collaborative Filtering (ALS - Spark MLlib)
- Hyperparameter tuning + RMSE evaluation
- Segment-level recommendations
- Export du lieu cho BI dashboard (Power BI)
- MapReduce-style exports de ban giao cho Task 4

## Cau truc

- `scripts/analytics_modeling.py`: Pipeline phan tich va mo hinh goi y chinh (ghi vao MongoDB)
- `scripts/phase4_export.py`: Export cac collection analytics sang CSV
- `scripts/mapreduce_exports.py`: Export bang tong hop theo map-reduce style
- `scripts/run_task3_pipeline.sh`: Runner cho Task 3
- `scripts/run_phase4_export.sh`: Runner export CSV
- `scripts/run_mapreduce_export.sh`: Runner mapreduce export
- `docs/09_analytics_modeling.md`: Huong dan chi tiet cho phan 3
- `docs/10_data_contracts_task3.md`: Data contracts cho cac bang dau ra
- `docs/11_runbook_and_handoff.md`: Runbook va handoff cho BI

## Dau ra chinh cho BI

Pipeline se tao cac collections sau trong MongoDB (`cinema_dw`):

- `movies_enriched`
- `genre_stats`
- `decade_stats`
- `year_stats`
- `rating_dist`
- `user_segments`
- `segment_genre_preference`
- `tag_stats`
- `segment_recommendations`

CSV export cho Power BI duoc luu tai:

- `visual/exports/*.csv`

MapReduce-style CSV duoc luu tai:

- `visual/exports/mapreduce/*`
