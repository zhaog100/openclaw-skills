#!/bin/bash
# 自动检查循环脚本 - 每 1 分钟检查一次

WORKSPACE="/home/zhaog/.openclaw/workspace"
INBOX="$WORKSPACE/.mili_comm/inbox"
OUTBOX="$WORKSPACE/.mili_comm/outbox"
LOG_FILE="/tmp/auto-check.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_new_files() {
    # 检查 inbox 新文件
    local new_inbox=$(find "$INBOX" -name "*.md" -mmin -1 2>/dev/null | wc -l)
    if [ "$new_inbox" -gt 0 ]; then
        log "⚠️ 发现 $new_inbox 个新 inbox 文件！"
        # 通知米粒儿
        echo "📬 小米粒回复了！inbox 有新文件！" > /tmp/notify_mili.txt
    fi
    
    # 检查 outbox 确认发送
    local new_outbox=$(find "$OUTBOX" -name "*.md" -mmin -1 2>/dev/null | wc -l)
    if [ "$new_outbox" -gt 0 ]; then
        log "📤 发现 $new_outbox 个新 outbox 文件"
    fi
}

# 主循环
log "🔄 自动检查循环启动（每 1 分钟）"
while true; do
    check_new_files
    sleep 60
done
