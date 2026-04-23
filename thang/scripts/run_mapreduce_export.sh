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

spark-submit \
  --master 'local[2]' \
  --driver-memory 6g \
  --executor-memory 6g \
  --conf spark.local.dir="$SPARK_LOCAL_TMP" \
  --conf spark.sql.shuffle.partitions=24 \
  --packages org.mongodb.spark:mongo-spark-connector_2.13:11.0.1 \
  "$REPO_ROOT/thang/scripts/mapreduce_exports.py"
