#!/bin/bash
set -e

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)

if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
  source "$PROJECT_ROOT/.venv/bin/activate"
elif [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
  source "$PROJECT_ROOT/venv/bin/activate"
fi

python "$PROJECT_ROOT/thang/scripts/phase4_export.py"
