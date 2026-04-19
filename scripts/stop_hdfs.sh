#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"
source scripts/activate.sh

hdfs --daemon stop datanode
hdfs --daemon stop namenode

echo "=== JPS ==="
jps
