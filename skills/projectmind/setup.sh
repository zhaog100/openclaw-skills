#!/bin/bash
# ProjectMind - 安装脚本
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# GitHub: https://github.com/zhaog100/openclaw-skills

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔧 ProjectMind 安装中..."

# 检查 Node.js
if ! command -v node &>/dev/null; then
    echo "❌ 需要 Node.js >= 18"
    exit 1
fi

NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js 版本过低（需要 >= 18），当前: $(node -v)"
    exit 1
fi
echo "✅ Node.js $(node -v)"

# npm install
echo "📦 安装依赖..."
npm install --production 2>&1 | tail -3

# 验证 better-sqlite3
node -e "require('better-sqlite3')" 2>/dev/null && echo "✅ better-sqlite3 编译成功" || echo "❌ better-sqlite3 编译失败，请检查 gcc/python3-make"

# 创建 data 目录
mkdir -p data
echo "✅ data/ 目录已创建"

echo ""
echo "🎉 ProjectMind 安装完成！"
echo "💡 通知功能默认关闭，编辑 config.json 启用"
