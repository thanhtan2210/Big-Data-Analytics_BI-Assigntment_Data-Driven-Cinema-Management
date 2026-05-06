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

echo "🧹 Đang dọn dẹp dữ liệu cũ (Checkpoints & MongoDB live collections)..."
rm -rf "$PROJECT_ROOT/runtime/checkpoints/live_metrics"
rm -rf "$PROJECT_ROOT/runtime/checkpoints/live_movie_stats"

# Xóa dữ liệu realtime cũ trong MongoDB để nạp lại từ đầu
mongosh cinema_dw --eval "db.live_metrics.drop(); db.live_movie_stats.drop();" --quiet

python "$PROJECT_ROOT/scripts/streaming_processor.py"
