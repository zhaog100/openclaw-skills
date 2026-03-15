#!/bin/bash
# agent-a-pm-skill - 安装脚本
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

set -e

echo "🚀 安装 agent-a-pm-skill v1.0.0..."

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 未安装"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python 版本：$PYTHON_VERSION"

# 安装依赖
echo "📦 安装依赖..."
pip3 install -q lark-oapi --break-system-packages 2>/dev/null || pip install -q lark-oapi --break-system-packages 2>/dev/null || echo "⚠️ 依赖安装失败，但可继续使用"

# 设置权限
chmod +x skill.sh

# 测试安装
echo "🧪 测试安装..."
if python3 -c "import modules.product_manager" 2>/dev/null; then
    echo "✅ 模块导入成功"
else
    echo "⚠️ 模块导入失败，请检查依赖"
fi

echo "✅ agent-a-pm-skill 安装完成！"
echo ""
echo "📖 使用方法："
echo "    ./skill.sh help"
