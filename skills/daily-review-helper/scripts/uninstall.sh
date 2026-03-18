#!/bin/bash
# =============================================================================
# 卸载脚本 v1.1
# =============================================================================
set -e

_SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$_SKILL_ROOT/scripts/lib/config.sh"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  定时回顾更新助手 v${CFG_VERSION} - 卸载向导                ║"
echo "╚════════════════════════════════════════════════════════╝"

# 删除定时任务
echo "⏰ 删除定时任务..."
crontab -l 2>/dev/null | grep -v "$CFG_CRON_ID" | crontab - 2>/dev/null && echo "  ✅ 定时任务已删除" || echo "  ℹ️  定时任务不存在"

# 清理日志
[ -d "$LOG_DIR" ] && rm -rf "$LOG_DIR" && echo "✅ 日志已清理"

# 清理 config.json（保留 example）
[ -f "$_SKILL_ROOT/config/config.json" ] && rm -f "$_SKILL_ROOT/config/config.json" && echo "✅ 配置文件已清理"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  卸载完成！                                            ║"
echo "╚════════════════════════════════════════════════════════╝"
