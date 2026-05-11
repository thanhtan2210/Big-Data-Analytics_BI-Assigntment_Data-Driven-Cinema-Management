#!/usr/bin/env bash
# =============================================================================
# Run the data preprocessing PySpark job inside the `spark` container.
# -----------------------------------------------------------------------------
# Usage:
#   bash scripts/run_preprocessing_docker.sh
#
# Prerequisites:
#   - `docker compose up -d` is running.
#   - MovieLens data has been uploaded to HDFS via:
#       bash scripts/download_movielens.sh
#       bash scripts/upload_to_hdfs.sh
#
# What it does:
#   1. Installs python-dotenv inside the Spark container (idempotent, only
#      pulls the wheel the first time).
#   2. Submits scripts/data_preprocessing.py to spark-submit running in
#      local[*] mode, with the official MongoDB Spark connector loaded via
#      --packages. The job writes the cleaned movies/ratings/tags
#      collections to the `cinema_dw` database on the mongodb service.
#
# The project root is bind-mounted at /workspace inside the container, so
# the script reads from /workspace/scripts/data_preprocessing.py.
# =============================================================================
set -euo pipefail

SPARK_CONTAINER="${SPARK_CONTAINER:-cinema-spark}"

if ! docker ps --format '{{.Names}}' | grep -q "^${SPARK_CONTAINER}$"; then
  echo "[spark] ERROR: container '$SPARK_CONTAINER' is not running." >&2
  echo "        Start the stack first with: docker compose up -d" >&2
  exit 1
fi

echo "[spark] Installing python-dotenv inside the container (if needed) ..."
docker exec "$SPARK_CONTAINER" bash -c "pip install --quiet python-dotenv >/dev/null 2>&1 || pip install python-dotenv"

echo "[spark] Submitting data_preprocessing.py to spark-submit ..."
docker exec \
  -e HDFS_HOST=namenode \
  -e HDFS_PORT=9000 \
  -e MONGO_URI=mongodb://mongodb:27017/ \
  -e MONGO_DB=cinema_dw \
  -e PROJECT_HDFS_RAW_MOVIELENS=/project/cinema/raw/movielens \
  -e PROJECT_HDFS_RAW_TMDB=/project/cinema/raw/tmdb \
  "$SPARK_CONTAINER" bash -c '
    cd /workspace && \
    spark-submit \
      --master "local[*]" \
      --packages org.mongodb.spark:mongo-spark-connector_2.13:11.0.1 \
      /workspace/scripts/data_preprocessing.py
  '

echo "[spark] Preprocessing job finished."
echo "[spark] Verify with:"
echo "    docker exec -it cinema-mongodb mongosh --eval \"use cinema_dw; show collections;\""
