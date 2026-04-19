#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"
source scripts/activate.sh

echo "=== MovieLens RAW on HDFS ==="
hdfs dfs -ls /project/cinema/raw/movielens
hdfs dfs -du -h /project/cinema/raw/movielens

echo
echo "=== TMDB RAW on HDFS ==="
hdfs dfs -ls /project/cinema/raw/tmdb
hdfs dfs -du -h /project/cinema/raw/tmdb
