#!/bin/bash
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
NAM_TMBD="$REPO_ROOT/nam/data/raw/tmdb"
THANH_TMBD="$REPO_ROOT/thanh/data/raw/tmdb"

if [[ ! -d "$NAM_TMBD" || ! -d "$THANH_TMBD" ]]; then
  echo "[FAIL] Missing TMDB folder(s)."
  echo "- nam path: $NAM_TMBD"
  echo "- thanh path: $THANH_TMBD"
  exit 1
fi

echo "============================================================"
echo "TMDB DUAL-SOURCE VERIFICATION"
echo "============================================================"
echo "nam   : $NAM_TMBD"
echo "thanh : $THANH_TMBD"
echo

status=0
for f in "$NAM_TMBD"/*.csv; do
  base=$(basename "$f")
  f2="$THANH_TMBD/$base"

  if [[ ! -f "$f2" ]]; then
    echo "[MISS] $base does not exist in thanh folder"
    status=1
    continue
  fi

  h1=$(shasum -a 256 "$f" | awk '{print $1}')
  h2=$(shasum -a 256 "$f2" | awk '{print $1}')
  n1=$(wc -l < "$f" | tr -d ' ')
  n2=$(wc -l < "$f2" | tr -d ' ')

  if [[ "$h1" == "$h2" ]]; then
    echo "[SAME] $base | lines: nam=$n1, thanh=$n2 | sha256=$h1"
  else
    echo "[DIFF] $base | lines: nam=$n1, thanh=$n2"
    echo "       nam   sha256=$h1"
    echo "       thanh sha256=$h2"
    status=1
  fi
done

echo
if [[ $status -eq 0 ]]; then
  echo "[PASS] Both TMDB folders are identical. Using one means using both datasets."
else
  echo "[WARN] There are differences between two TMDB folders."
fi

exit $status
