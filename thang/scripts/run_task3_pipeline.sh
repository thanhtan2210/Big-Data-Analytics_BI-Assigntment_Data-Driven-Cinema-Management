#!/bin/bash
set -e

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
SPARK_LOCAL_TMP="$REPO_ROOT/thang/runtime/spark-local"
mkdir -p "$SPARK_LOCAL_TMP"

if [ -f "$REPO_ROOT/thanh/scripts/activate.sh" ]; then
  source "$REPO_ROOT/thanh/scripts/activate.sh"
elif [ -f "$REPO_ROOT/nam/scripts/activate.sh" ]; then
  source "$REPO_ROOT/nam/scripts/activate.sh"
fi

echo "============================================================"
echo "   TASK 3 PIPELINE: Analytics + Recommendation Modeling"
echo "============================================================"

: "${ALS_SAMPLE_FRACTION:=0.0005}"
: "${TASK3_FAST_SAMPLE_FRACTION:=0.0005}"
: "${ALS_RANK_GRID:=20}"
: "${ALS_REG_GRID:=0.1}"
: "${ALS_MAX_ITER_GRID:=10}"
: "${ALS_TOP_N:=10}"
: "${ALS_SEED:=42}"
: "${TASK3_FAST_MODE:=1}"

export ALS_SAMPLE_FRACTION
export TASK3_FAST_SAMPLE_FRACTION
export ALS_RANK_GRID
export ALS_REG_GRID
export ALS_MAX_ITER_GRID
export ALS_TOP_N
export ALS_SEED
export TASK3_FAST_MODE

spark-submit \
  --master 'local[2]' \
  --driver-memory 6g \
  --executor-memory 6g \
  --conf spark.local.dir="$SPARK_LOCAL_TMP" \
  --conf spark.sql.shuffle.partitions=24 \
  --packages org.mongodb.spark:mongo-spark-connector_2.13:11.0.1 \
  "$REPO_ROOT/thang/scripts/analytics_modeling.py"

echo "============================================================"
echo "   TASK 3 PIPELINE COMPLETED"
echo "============================================================"
