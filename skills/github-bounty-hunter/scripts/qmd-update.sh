#!/bin/bash
# QMD 索引更新脚本
# 功能：更新 QMD 向量化索引

set -e

WORKSPACE="$HOME/.openclaw/workspace"
cd "$WORKSPACE"

echo "🔍 检查 QMD 安装..."
if ! command -v qmd &> /dev/null; then
    echo "❌ QMD 未安装，请先安装：pipx install qmd"
    exit 1
fi

echo "📊 QMD 版本:"
qmd --version || echo "未知版本"

echo "🔄 更新 QMD 索引..."
qmd update

echo "📊 检查索引状态..."
qmd status

echo "✅ QMD 索引更新完成！"
