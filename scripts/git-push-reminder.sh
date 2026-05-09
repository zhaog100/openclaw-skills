#!/bin/bash
# Git 定期推送提醒脚本
# 每天检查并提醒推送

WORKSPACE="$HOME/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/git-push.log"

cd "$WORKSPACE" || exit 1

# 检查未推送的提交数
UNPUSHED_XIAOMILA=$(git log --oneline HEAD..xiaomila/main 2>/dev/null | wc -l)
UNPUSHED_ORIGIN=$(git log --oneline HEAD..origin/main 2>/dev/null | wc -l)

# 记录日志
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检查推送状态" >> "$LOG_FILE"
echo "  - xiaomila 未推送: $UNPUSHED_XIAOMILA 个提交" >> "$LOG_FILE"
echo "  - origin 未推送: $UNPUSHED_ORIGIN 个提交" >> "$LOG_FILE"

# 如果有未推送的提交，发送提醒
if [ "$UNPUSHED_XIAOMILA" -gt 10 ] || [ "$UNPUSHED_ORIGIN" -gt 10 ]; then
    echo ""
    echo "⚠️  Git 推送提醒"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "检测到大量未推送的提交："
    echo "  • xiaomila: $UNPUSHED_XIAOMILA 个"
    echo "  • origin: $UNPUSHED_ORIGIN 个"
    echo ""
    echo "建议立即推送："
    echo "  cd ~/.openclaw/workspace"
    echo "  git push xiaomila main"
    echo "  git push origin main"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi
