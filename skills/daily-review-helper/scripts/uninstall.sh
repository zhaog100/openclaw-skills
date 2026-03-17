#!/bin/bash
# =============================================================================
# 定时回顾更新助手 - 卸载脚本
# =============================================================================
# 版本：v1.0
# 创建时间：2026-03-16
# 创建者：思捷娅科技 (SJYKJ)
# 许可证：MIT License
# 版权：Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${WORKSPACE:-$(pwd)}"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  定时回顾更新助手 v1.0 - 卸载向导                      ║"
echo "╚════════════════════════════════════════════════════════╝"

# 删除定时任务
echo ""
echo "⏰ 删除定时任务..."

EXISTING_CRON=$(crontab -l 2>/dev/null | grep "daily-review-assistant" || true)

if [ -n "$EXISTING_CRON" ]; then
    # 删除定时任务
    crontab -l 2>/dev/null | grep -v "daily-review-assistant" | crontab -
    echo "  ✅ 定时任务已删除"
else
    echo "  ℹ️  定时任务不存在"
fi

# 清理日志文件
echo ""
echo "🧹 清理日志文件..."
if [ -d "$SCRIPT_DIR/../logs" ]; then
    rm -rf "$SCRIPT_DIR/../logs"
    echo "  ✅ 日志文件已清理"
else
    echo "  ℹ️  日志文件不存在"
fi

# 清理配置文件
echo ""
echo "🧹 清理配置文件..."
if [ -f "$SCRIPT_DIR/../config/config.json" ]; then
    rm -f "$SCRIPT_DIR/../config/config.json"
    echo "  ✅ 配置文件已清理"
else
    echo "  ℹ️  配置文件不存在"
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  卸载完成！                                            ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  已清理：                                              ║"
echo "║  ✅ 定时任务                                           ║"
echo "║  ✅ 日志文件                                           ║"
echo "║  ✅ 配置文件                                           ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  注意：技能文件未删除，如需删除请手动执行：            ║"
echo "║  rm -rf $SCRIPT_DIR/..                                  ║"
echo "╚════════════════════════════════════════════════════════╝"
