#!/bin/bash
set -e

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
source "$PROJECT_ROOT/scripts/activate.sh"

echo "============================================================"
echo "    Bắt đầu chạy PySpark Structured Streaming Job"
echo "============================================================"

if [ -d "$PROJECT_ROOT/.venv" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
elif [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
else
    echo "Không tìm thấy môi trường ảo venv. Vui lòng cài đặt trước."
    exit 1
fi

python "$PROJECT_ROOT/scripts/streaming_processor.py"
