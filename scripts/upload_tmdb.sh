#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"
source scripts/activate.sh

LOCAL_TMDB_DIR="data/raw/tmdb/extracted"
[ -f "$LOCAL_TMDB_DIR/movies_metadata.csv" ] || { echo "Thiếu movies_metadata.csv"; exit 1; }
[ -f "$LOCAL_TMDB_DIR/credits.csv" ] || { echo "Thiếu credits.csv"; exit 1; }
[ -f "$LOCAL_TMDB_DIR/keywords.csv" ] || { echo "Thiếu keywords.csv"; exit 1; }

HDFS_TMDB_DIR="/project/cinema/raw/tmdb"

echo "=== Checking local TMDB files ==="
ls -lh "$LOCAL_TMDB_DIR"

echo "=== Creating HDFS TMDB directory ==="
hdfs dfs -mkdir -p "$HDFS_TMDB_DIR"

echo "=== Uploading movies_metadata.csv ==="
hdfs dfs -put -f "$LOCAL_TMDB_DIR/movies_metadata.csv" "$HDFS_TMDB_DIR/"

echo "=== Uploading credits.csv ==="
hdfs dfs -put -f "$LOCAL_TMDB_DIR/credits.csv" "$HDFS_TMDB_DIR/"

echo "=== Uploading keywords.csv ==="
hdfs dfs -put -f "$LOCAL_TMDB_DIR/keywords.csv" "$HDFS_TMDB_DIR/"

mkdir -p artifacts/terminal_logs

echo "=== HDFS LS ==="
hdfs dfs -ls "$HDFS_TMDB_DIR" | tee artifacts/terminal_logs/hdfs_tmdb_ls.txt

echo "=== HDFS DU ==="
hdfs dfs -du -h "$HDFS_TMDB_DIR" | tee artifacts/terminal_logs/hdfs_tmdb_du.txt

echo "=== Upload TMDB completed ==="
