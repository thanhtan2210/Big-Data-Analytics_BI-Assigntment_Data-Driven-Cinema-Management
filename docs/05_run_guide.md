# 5. Hướng Dẫn Chạy

## 5.1 Mục đích

Tài liệu này mô tả các bước chạy đúng cho Mục 1 của project.

Tất cả lệnh đều được thực hiện trong **WSL Ubuntu**.

## 5.2 Mở project trong WSL

```bash
cd /mnt/d/Daihoc/Nam3/AnalysisBigdata/BTL/Big-Data-Analytics_BI-Assigntment_Data-Driven-Cinema-Management
```

## 5.3 Kích hoạt môi trường local

```bash
source scripts/activate.sh
```

Lưu ý: Trước khi chạy bất kỳ script nào trong thư mục `scripts/`, cần thực hiện `source scripts/activate.sh` trong terminal WSL hiện tại.

## 5.4 Kiểm tra runtime

```bash
java -version
hadoop version
hdfs version
```

## 5.5 Khởi động HDFS

```bash
bash scripts/start_hdfs.sh
```

Script này sẽ:
- kích hoạt env
- bật `NameNode`
- bật `DataNode`
- kiểm tra safe mode
- in `jps`

## 5.6 Nạp dữ liệu TMDB raw lên HDFS

Trước tiên, cần đặt 3 file trong:

```text
data/raw/tmdb/extracted/
```

Bao gồm:
- `movies_metadata.csv`
- `credits.csv`
- `keywords.csv`

Sau đó chạy:

```bash
bash scripts/upload_tmdb.sh
```

Script này sẽ:
- kiểm tra 3 file local
- tạo thư mục `/project/cinema/raw/tmdb`
- upload 3 file lên HDFS
- lưu log vào `artifacts/terminal_logs/`

## 5.7 Kiểm tra toàn bộ raw data trên HDFS

```bash
bash scripts/check_hdfs_raw.sh
```

Script này sẽ kiểm tra:
- raw MovieLens tại `/project/cinema/raw/movielens`
- raw TMDB tại `/project/cinema/raw/tmdb`

## 5.8 Dừng HDFS

```bash
bash scripts/stop_hdfs.sh
```

## 5.9 Log sinh ra

Sau khi chạy xong, project sẽ có các log như:
- `artifacts/terminal_logs/hdfs_movielens_ls.txt`
- `artifacts/terminal_logs/hdfs_movielens_du.txt`
- `artifacts/terminal_logs/hdfs_tmdb_ls.txt`
- `artifacts/terminal_logs/hdfs_tmdb_du.txt`
- `artifacts/terminal_logs/jps_after_start.txt`

## 5.10 Kết luận

Nếu chạy thành công toàn bộ các bước trên, Mục 1 sẽ hoàn thành đầy đủ phần:
- data collection
- schema understanding
- raw data ingestion into HDFS
