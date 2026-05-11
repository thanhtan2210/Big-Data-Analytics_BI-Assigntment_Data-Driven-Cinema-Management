#!/usr/bin/env bash
# =============================================================================
# Upload data/raw/* into HDFS via the running `namenode` container.
# -----------------------------------------------------------------------------
# Usage:
#   bash scripts/upload_to_hdfs.sh
#
# Prerequisites:
#   - `docker compose up -d` has been started successfully.
#   - `scripts/download_movielens.sh` has been executed at least once so that
#     data/raw/ml-25m/ exists.
#
# What it does:
#   1. Creates the target HDFS directories
#        /project/cinema/raw/movielens
#        /project/cinema/raw/tmdb
#   2. Copies every CSV from data/raw/ml-25m/ into the movielens HDFS path.
#   3. Copies every CSV from data/raw/tmdb/ (if present) into the tmdb HDFS
#      path. The TMDB directory is optional - the project's preprocessing
#      script already tolerates its absence.
#
# Inside the namenode container the project root is bind-mounted at /data,
# so `data/raw/...` on the host appears as `/data/raw/...` in the container.
# =============================================================================
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load .env if present so MOVIELENS_DIR / HDFS paths can be overridden.
if [ -f "$PROJECT_ROOT/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$PROJECT_ROOT/.env"
  set +a
fi

MOVIELENS_DIR="${MOVIELENS_DIR:-ml-25m}"
HDFS_RAW_MOVIELENS="${PROJECT_HDFS_RAW_MOVIELENS:-/project/cinema/raw/movielens}"
HDFS_RAW_TMDB="${PROJECT_HDFS_RAW_TMDB:-/project/cinema/raw/tmdb}"

NAMENODE_CONTAINER="${NAMENODE_CONTAINER:-cinema-namenode}"

if ! docker ps --format '{{.Names}}' | grep -q "^${NAMENODE_CONTAINER}$"; then
  echo "[hdfs] ERROR: container '$NAMENODE_CONTAINER' is not running." >&2
  echo "       Start the stack first with: docker compose up -d" >&2
  exit 1
fi

LOCAL_MOVIELENS_DIR="$PROJECT_ROOT/data/raw/$MOVIELENS_DIR"
if [ ! -d "$LOCAL_MOVIELENS_DIR" ]; then
  echo "[hdfs] ERROR: $LOCAL_MOVIELENS_DIR does not exist." >&2
  echo "       Run scripts/download_movielens.sh first." >&2
  exit 1
fi

# Inside the container the project root is mounted at /data.
CONTAINER_MOVIELENS_DIR="/data/data/raw/$MOVIELENS_DIR"
CONTAINER_TMDB_DIR="/data/data/raw/tmdb"

echo "[hdfs] Creating HDFS directories ..."
docker exec "$NAMENODE_CONTAINER" \
  hdfs dfs -mkdir -p "$HDFS_RAW_MOVIELENS" "$HDFS_RAW_TMDB"

echo "[hdfs] Uploading MovieLens CSVs from $CONTAINER_MOVIELENS_DIR ..."
docker exec "$NAMENODE_CONTAINER" bash -c "
  set -e
  for f in $CONTAINER_MOVIELENS_DIR/*.csv; do
    [ -f \"\$f\" ] || continue
    echo '  -> '\$f
    hdfs dfs -put -f \"\$f\" $HDFS_RAW_MOVIELENS/
  done
"

echo "[hdfs] Uploading TMDB CSVs (optional) ..."
docker exec "$NAMENODE_CONTAINER" bash -c "
  if [ -d $CONTAINER_TMDB_DIR ]; then
    for f in $CONTAINER_TMDB_DIR/*.csv; do
      [ -f \"\$f\" ] || continue
      echo '  -> '\$f
      hdfs dfs -put -f \"\$f\" $HDFS_RAW_TMDB/
    done
  else
    echo '  (no $CONTAINER_TMDB_DIR found, skipping)'
  fi
"

echo "[hdfs] Final HDFS listing:"
docker exec "$NAMENODE_CONTAINER" hdfs dfs -ls "$HDFS_RAW_MOVIELENS"
docker exec "$NAMENODE_CONTAINER" hdfs dfs -ls "$HDFS_RAW_TMDB" || true

echo "[hdfs] Done."
