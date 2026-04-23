# 11. Runbook va Handoff cho Task 4 (BI)

## 11.1 Thu tu chay de on dinh

1. Hoan thanh Muc 2 (`movies`, `ratings`, `tags` da co trong MongoDB).
2. Chay Task 3 pipeline:

```bash
./thang/scripts/run_task3_pipeline.sh
```

3. Export CSV cho Power BI:

```bash
./thang/scripts/run_phase4_export.sh
```

4. Neu can bang mapreduce theo yeu cau BI:

```bash
./thang/scripts/run_mapreduce_export.sh
```

## 11.2 Noi BI lay du lieu

Dashboard chinh nen dung file trong `visual/exports/`:

- `movies_enriched.csv`
- `genre_stats.csv`
- `decade_genre_heatmap.csv`
- `year_stats.csv`
- `rating_distribution.csv`
- `user_segments.csv`
- `segment_genre_preference.csv`
- `tag_stats.csv`
- `segment_recommendations.csv`

## 11.3 Mapping nhanh theo dashboard

1. Revenue Dashboard:

- `genre_stats.csv`
- `decade_genre_heatmap.csv`

2. Customer Rating Trend Dashboard:

- `year_stats.csv`
- `rating_distribution.csv`

3. Recommendation Dashboard:

- `user_segments.csv`
- `segment_genre_preference.csv`
- `segment_recommendations.csv`
- `movies_enriched.csv`

## 11.4 Checklist truoc khi ban giao

- ALS metrics da duoc luu tai `thang/artifacts/metrics/als_metrics.json`.
- Tat ca collection analytics da co data.
- CSV export khong rong va dung ten file.
- Segment recommendations da co rank 1..N theo tung segment.
- BI ben Task 4 import duoc va refresh khong loi.
