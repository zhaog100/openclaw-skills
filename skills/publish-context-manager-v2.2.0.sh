#!/bin/bash
# Context Manager v2.2.0 发布脚本
# 创建时间：2026-03-05 13:43

SKILL_DIR="$HOME/.openclaw/workspace/skills/context-manager-v2"
TAR_FILE="$HOME/.openclaw/workspace/skills/context-manager-v2.2.0.tar.gz"

echo "🦞 Context Manager v2.2.0 发布准备"
echo "================================"
echo ""

# 1. 检查文件
echo "📋 检查文件..."
if [ ! -f "$TAR_FILE" ]; then
    echo "❌ 打包文件不存在: $TAR_FILE"
    exit 1
fi

echo "✅ 打包文件: $(ls -lh "$TAR_FILE" | awk '{print $5}')"
echo ""

# 2. 检查登录状态
echo "🔐 检查ClawHub登录状态..."
if ! clawhub whoami &>/dev/null; then
    echo "⚠️ 未登录ClawHub"
    echo ""
    echo "请先登录："
    echo "  clawhub login"
    echo ""
    echo "登录后重新运行此脚本"
    exit 1
fi

echo "✅ 已登录ClawHub"
echo ""

# 3. 发布
echo "📤 发布到ClawHub..."
echo ""

clawhub publish "$SKILL_DIR" \
  --slug miliger-context-manager \
  --name "Context Manager" \
  --version 2.2.0 \
  --changelog "真实API监控，修复假监控问题，1小时冷却期，详细日志记录"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 发布成功！"
    echo ""
    echo "📦 包名：miliger-context-manager"
    echo "📌 版本：2.2.0"
    echo "🌐 安装：clawhub install miliger-context-manager"
    echo ""
else
    echo ""
    echo "❌ 发布失败"
    exit 1
fi
