#!/bin/bash
set -e
echo "=== SolFoundry Sync 测试套件 ==="
python -m pytest tests/ -v --tb=short
echo "=== 测试完成 ==="
