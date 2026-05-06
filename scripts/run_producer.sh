#!/bin/bash
set -e

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
source "$PROJECT_ROOT/scripts/activate.sh"

if [ -d "$PROJECT_ROOT/.venv" ]; then
    VENV_DIR="$PROJECT_ROOT/.venv"
elif [ -d "$PROJECT_ROOT/venv" ]; then
    VENV_DIR="$PROJECT_ROOT/venv"
else
    echo "Không tìm thấy môi trường ảo (virtual environment) tại $PROJECT_ROOT/.venv hoặc $PROJECT_ROOT/venv"
    echo "Vui lòng tạo venv và cài đặt dependencies:"
    echo "python3 -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

source "$VENV_DIR/bin/activate"

echo "============================================================"
echo "    Bắt đầu chạy Kafka Producer (Giả lập Streaming)"
echo "============================================================"

python "$PROJECT_ROOT/scripts/kafka_producer.py"
