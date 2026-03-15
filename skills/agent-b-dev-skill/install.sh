#!/bin/bash
# agent-b-dev-skill - 安装脚本
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

set -e

echo "🚀 安装 agent-b-dev-skill v1.0.0..."

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 未安装"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python版本: $PYTHON_VERSION"

# 设置权限
chmod +x skill.sh

# 可选：安装依赖（跳过如果失败）
echo "📦 检查依赖..."
if python3 -c "import lark_oapi" 2>/dev/null; then
    echo "✅ lark-oapi 已安装"
else
    echo "⚠️  lark-oapi 未安装（可选依赖，基础功能可用）"
    echo "   如需飞书集成，请手动安装：pip3 install --break-system-packages lark-oapi"
fi

echo "✅ agent-b-dev-skill 安装完成！"
echo ""
echo "📖 使用方法："
echo "    ./skill.sh help"
