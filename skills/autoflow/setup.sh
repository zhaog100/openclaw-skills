#!/bin/bash
# AutoFlow - AI自动化服务平台 安装脚本
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# GitHub: https://github.com/zhaog100/autoflow

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="${SCRIPT_DIR}/api"
DATA_DIR="${API_DIR}/data"

echo "=== AutoFlow 安装 ==="

# 1. Python依赖
echo "[1/4] 安装Python依赖..."
pip install -q fastapi uvicorn httpx python-jose pydantic aiosqlite matplotlib 2>/dev/null || \
  pip3 install -q fastapi uvicorn httpx python-jose pydantic aiosqlite matplotlib

# 2. 数据目录
echo "[2/4] 创建数据目录..."
mkdir -p "${DATA_DIR}"

# 3. 配置文件（如果不存在）
echo "[3/4] 检查配置..."
if [ ! -f "${API_DIR}/config.json" ]; then
  if [ -f "${API_DIR}/config.example.json" ]; then
    cp "${API_DIR}/config.example.json" "${API_DIR}/config.json"
    echo "  已创建 config.json（从模板复制）"
  fi
fi

# 4. 环境变量检查
echo "[4/4] 环境变量检查..."
if [ -z "${AF_JWT_SECRET}" ]; then
  echo "  ⚠️  AF_JWT_SECRET 未设置，使用默认值（生产环境请设置！）"
else
  echo "  ✅ AF_JWT_SECRET 已设置"
fi

echo ""
echo "=== 安装完成 ==="
echo "启动命令："
echo "  cd ${API_DIR} && AF_JWT_SECRET=\${AF_JWT_SECRET:-change-me} python -m uvicorn main:app --host 0.0.0.0 --port 8000"
