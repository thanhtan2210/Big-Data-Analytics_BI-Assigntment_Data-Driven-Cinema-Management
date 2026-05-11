#!/usr/bin/env bash
# =============================================================================
# Download the MovieLens 25M dataset and extract it into data/raw/.
# -----------------------------------------------------------------------------
# Usage:
#   bash scripts/download_movielens.sh
#
# Output layout (relative to the project root):
#   data/raw/ml-25m/movies.csv
#   data/raw/ml-25m/ratings.csv
#   data/raw/ml-25m/tags.csv
#   data/raw/ml-25m/links.csv
#   data/raw/ml-25m/genome-scores.csv
#   data/raw/ml-25m/genome-tags.csv
#   data/raw/ml-25m/README.txt
#
# The script is idempotent: it skips download/extraction if the destination
# already exists.
# =============================================================================
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load .env if present so callers can override the URL / filenames.
if [ -f "$PROJECT_ROOT/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$PROJECT_ROOT/.env"
  set +a
fi

MOVIELENS_URL="${MOVIELENS_URL:-https://files.grouplens.org/datasets/movielens/ml-25m.zip}"
MOVIELENS_ZIP="${MOVIELENS_ZIP:-ml-25m.zip}"
MOVIELENS_DIR="${MOVIELENS_DIR:-ml-25m}"

RAW_DIR="$PROJECT_ROOT/data/raw"
ZIP_PATH="$RAW_DIR/$MOVIELENS_ZIP"
EXTRACT_DIR="$RAW_DIR/$MOVIELENS_DIR"

mkdir -p "$RAW_DIR"

echo "[movielens] Project root : $PROJECT_ROOT"
echo "[movielens] Raw dir      : $RAW_DIR"
echo "[movielens] Source URL   : $MOVIELENS_URL"

if [ -d "$EXTRACT_DIR" ] && [ -f "$EXTRACT_DIR/movies.csv" ]; then
  echo "[movielens] Dataset already extracted at $EXTRACT_DIR (skipping)."
  exit 0
fi

if [ ! -f "$ZIP_PATH" ]; then
  echo "[movielens] Downloading $MOVIELENS_URL ..."
  if command -v curl >/dev/null 2>&1; then
    curl -L --fail --retry 3 -o "$ZIP_PATH" "$MOVIELENS_URL"
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$ZIP_PATH" "$MOVIELENS_URL"
  else
    echo "[movielens] ERROR: need either curl or wget to download the dataset." >&2
    exit 1
  fi
else
  echo "[movielens] Zip already present at $ZIP_PATH (skipping download)."
fi

echo "[movielens] Extracting $ZIP_PATH ..."
if command -v unzip >/dev/null 2>&1; then
  unzip -o "$ZIP_PATH" -d "$RAW_DIR"
elif command -v python3 >/dev/null 2>&1; then
  python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" \
    "$ZIP_PATH" "$RAW_DIR"
else
  echo "[movielens] ERROR: need either unzip or python3 to extract the archive." >&2
  exit 1
fi

if [ ! -f "$EXTRACT_DIR/movies.csv" ]; then
  echo "[movielens] ERROR: extraction did not produce $EXTRACT_DIR/movies.csv" >&2
  exit 1
fi

echo "[movielens] Done. Files available at: $EXTRACT_DIR"
ls -1 "$EXTRACT_DIR"
