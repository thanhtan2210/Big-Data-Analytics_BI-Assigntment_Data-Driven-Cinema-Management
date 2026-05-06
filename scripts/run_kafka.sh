#!/bin/bash
set -e

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
source "$PROJECT_ROOT/scripts/activate.sh"

KAFKA_DIR="$PROJECT_ROOT/runtime/kafka"
KAFKA_DATA_DIR="$PROJECT_ROOT/runtime/kafka-data"
KRAFT_CONFIG="$KAFKA_DIR/config/kraft/server.properties"

if [ ! -d "$KAFKA_DIR" ]; then
    echo "Kafka chưa được cài đặt. Vui lòng chạy ./scripts/install_kafka.sh trước."
    exit 1
fi

# Format storage directory if not already formatted
if [ ! -f "$KAFKA_DATA_DIR/meta.properties" ]; then
    echo "Đang format Kafka KRaft storage..."
    CLUSTER_ID=$("$KAFKA_DIR/bin/kafka-storage.sh" random-uuid)
    "$KAFKA_DIR/bin/kafka-storage.sh" format -t $CLUSTER_ID -c "$KRAFT_CONFIG"
fi

echo "============================================================"
echo "    Đang khởi động Kafka (KRaft mode)..."
echo "    Nhấn Ctrl+C để dừng."
echo "============================================================"

"$KAFKA_DIR/bin/kafka-server-start.sh" "$KRAFT_CONFIG"
