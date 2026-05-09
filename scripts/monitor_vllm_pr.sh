#!/bin/bash
# vllm-omni PR #2080 监控脚本
# 每小时检查一次 PR 状态

PR_NUMBER=2080
REPO="vllm-project/vllm-omni"
LOG_FILE="/home/zhaog/.openclaw/workspace/logs/vllm-omni-pr-2080.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== vllm-omni PR #2080 监控 =========="

# 获取 PR 状态
PR_DATA=$(curl -s "https://api.github.com/repos/$REPO/pulls/$PR_NUMBER")

STATE=$(echo "$PR_DATA" | jq -r '.state')
MERGED=$(echo "$PR_DATA" | jq -r '.merged')
UPDATED=$(echo "$PR_DATA" | jq -r '.updated_at')
COMMENTS=$(echo "$PR_DATA" | jq -r '.comments')
REVIEW_COMMENTS=$(echo "$PR_DATA" | jq -r '.review_comments')

log "状态: $STATE"
log "合并: $MERGED"
log "最后更新: $UPDATED"
log "评论数: $COMMENTS"
log "审查评论: $REVIEW_COMMENTS"

# 检查是否有新评论
if [ "$COMMENTS" -gt 1 ] || [ "$REVIEW_COMMENTS" -gt 2 ]; then
    log "⚠️ 发现新评论！需要查看 PR"
    
    # 发送通知（如果有新评论）
    if command -v notify-send &> /dev/null; then
        notify-send "🌶️ vllm-omni PR #2080" "发现新评论，请检查！"
    fi
fi

# 检查是否已合并
if [ "$MERGED" = "true" ]; then
    log "🎉 PR 已合并！"
    
    # 创建完成标记
    echo "MERGED_AT=$(date -Iseconds)" >> /home/zhaog/.openclaw/workspace/memory/reminders/vllm-omni-pr-2080-merged.json
    
    # 发送通知
    if command -v notify-send &> /dev/null; then
        notify-send "🎉 vllm-omni PR #2080" "已合并！检查 bounty 付款流程"
    fi
fi

log "========== 监控完成 =========="
