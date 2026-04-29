#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"
source scripts/activate.sh

hdfs --daemon start namenode
hdfs --daemon start datanode

sleep 5
hdfs dfsadmin -safemode leave || true

echo "=== Safe mode status ==="
hdfs dfsadmin -safemode get || true

echo "=== JPS ==="
jps