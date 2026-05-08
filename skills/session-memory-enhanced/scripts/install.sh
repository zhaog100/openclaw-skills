#!/bin/bash
# Session Memory Enhanced - Installation Script
# Version: 2.0.0

set -e

# 加载统一配置
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$SKILL_DIR/scripts/lib/config.sh"

SCRIPT_NAME="session-memory-enhanced-v4.sh"

echo "🚀 安装 Session Memory Enhanced v2.0.0"
echo "================================"

# 1. 创建配置文件（如不存在）
if [ ! -f "$SKILL_DIR/config.json" ]; then
  if [ -f "$SKILL_DIR/config.example.json" ]; then
    cp "$SKILL_DIR/config.example.json" "$SKILL_DIR/config.json"
    echo "📝 已从模板创建配置文件：config.json"
    echo "⚠️  请根据需要编辑 $SKILL_DIR/config.json"
  fi
fi

# 2. 检查crontab
echo "⏰ 检查crontab配置..."
if crontab -l 2>/dev/null | grep -q "$SCRIPT_NAME"; then
  echo "ℹ️  Crontab已配置"
else
  echo "ℹ️  Crontab未配置"
  echo "  手动执行: crontab -e"
  echo "  添加: 0 * * * * $SKILL_DIR/scripts/$SCRIPT_NAME >> $LOG_FILE 2>&1"
fi

# 3. 显示配置状态
echo ""
echo "📊 当前配置："
echo "  - 闲置时间：${FLUSH_IDLE_SECONDS}秒"
echo "  - 消息上限：${MAX_MESSAGES_PER_PART}条"
echo "  - 结构化提取：${ENABLE_STRUCTURED_EXTRACTION}"
echo "  - 向量检索：${ENABLE_VECTOR_SEARCH}"
echo ""
echo "✅ 安装完成！"
echo "================================"
