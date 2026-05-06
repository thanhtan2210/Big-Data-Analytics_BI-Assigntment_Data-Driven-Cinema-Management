#!/bin/bash
set -e

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
source "$PROJECT_ROOT/scripts/activate.sh"

KAFKA_VERSION="3.9.2"
SCALA_VERSION="2.13"
KAFKA_DIR="$PROJECT_ROOT/runtime/kafka"
DOWNLOAD_URLS=(
    "https://dlcdn.apache.org/kafka/${KAFKA_VERSION}/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz"
    "https://downloads.apache.org/kafka/${KAFKA_VERSION}/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz"
    "https://archive.apache.org/dist/kafka/${KAFKA_VERSION}/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz"
)

echo "============================================================"
echo "    Bắt đầu tải và cài đặt Kafka (Local)"
echo "============================================================"

if [ -d "$KAFKA_DIR" ]; then
    echo "Kafka đã được cài đặt tại: $KAFKA_DIR"
else
    mkdir -p "$PROJECT_ROOT/runtime"
    
    SUCCESS=0
    for URL in "${DOWNLOAD_URLS[@]}"; do
        echo "Đang thử tải Kafka từ $URL ..."
        # Use -f to fail on HTTP errors, -L to follow redirects, --connect-timeout 15 to fail fast if blocked
        if curl -f -L --connect-timeout 15 -o "$PROJECT_ROOT/runtime/kafka.tgz" "$URL"; then
            SUCCESS=1
            echo "Tải thành công từ $URL"
            break
        else
            echo "Tải thất bại từ $URL. Đang thử link khác..."
        fi
    done
    
    if [ $SUCCESS -eq 0 ]; then
        echo "Lỗi: Không thể tải Kafka từ bất kỳ nguồn nào. Vui lòng kiểm tra lại kết nối mạng."
        exit 1
    fi
    
    echo "Đang giải nén..."
    tar -xzf "$PROJECT_ROOT/runtime/kafka.tgz" -C "$PROJECT_ROOT/runtime/"
    mv "$PROJECT_ROOT/runtime/kafka_${SCALA_VERSION}-${KAFKA_VERSION}" "$KAFKA_DIR"
    rm "$PROJECT_ROOT/runtime/kafka.tgz"
    
    echo "Kafka đã được cài đặt thành công tại $KAFKA_DIR"
fi

KAFKA_DATA_DIR="$PROJECT_ROOT/runtime/kafka-data"
if [ ! -d "$KAFKA_DATA_DIR" ]; then
    mkdir -p "$KAFKA_DATA_DIR"
    echo "Đã tạo thư mục dữ liệu Kafka tại $KAFKA_DATA_DIR"
fi

echo "Cấu hình KRaft..."
# Configure KRaft properties to use our local data dir
sed -i.bak "s|^log.dirs=.*|log.dirs=$KAFKA_DATA_DIR|g" "$KAFKA_DIR/config/kraft/server.properties"

echo "============================================================"
echo "    Hoàn tất cài đặt Kafka."
echo "============================================================"
