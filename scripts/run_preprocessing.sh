#!/bin/bash
set -e

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
source "$PROJECT_ROOT/scripts/activate.sh"

echo "============================================================"
echo "    Bắt đầu chạy Data Preprocessing Pipeline (PySpark)"
echo "============================================================"

spark-submit \
  --master local[*] \
  --packages org.mongodb.spark:mongo-spark-connector_2.13:11.0.1 \
  "$PROJECT_ROOT/scripts/data_preprocessing.py"

echo "============================================================"
echo "    Hoàn tất script runner."
echo "============================================================"
