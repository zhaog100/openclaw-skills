#!/bin/bash
# agent-b-dev-skill - 安装脚本
# 版权声明：MIT License | Copyright (c) 2026 米粒儿 (miliger)

set -e

echo "🚀 安装 agent-b-dev-skill v1.0.0..."

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 未安装"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python版本: $PYTHON_VERSION"

# 安装依赖
echo "📦 安装依赖..."
pip3 install -q lark-oapi 2>/dev/null || pip install -q lark-oapi

# 设置权限
chmod +x skill.sh

# 测试安装
echo "🧪 测试安装..."
if python3 -c "import lark_oapi" 2>/dev/null; then
    echo "✅ lark-oapi 安装成功"
else
    echo "❌ lark-oapi 安装失败"
    exit 1
fi

echo "✅ agent-b-dev-skill 安装完成！"
echo ""
echo "📖 使用方法："
echo "    ./skill.sh help"
