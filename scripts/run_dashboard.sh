#!/bin/bash
set -e

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
source "$PROJECT_ROOT/scripts/activate.sh"

if [ -d "$PROJECT_ROOT/.venv" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
elif [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

echo "============================================================"
echo "    Đang khởi động Cinema Live Streaming Dashboard"
echo "============================================================"

streamlit run "$PROJECT_ROOT/visual/app.py"
