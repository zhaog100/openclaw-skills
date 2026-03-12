#!/bin/bash
# 沟通机制定时任务脚本
# 包含：超时提醒、日报、周报、状态同步

WORKSPACE="/home/zhaog/.openclaw/workspace"
INBOX="$WORKSPACE/.mili_comm/inbox"
OUTBOX="$WORKSPACE/.mili_comm/outbox"
LOG_FILE="/tmp/communication-cron.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 检查超时（每 5 分钟执行）
check_timeout() {
    log "🔍 检查超时消息..."
    
    # 获取 outbox 中 5 分钟前发送但未回复的文件
    find "$OUTBOX" -name "*.md" -mmin +5 -mmin -10 2>/dev/null | while read file; do
        filename=$(basename "$file")
        # 检查 inbox 是否有对应回复
        if [ ! -f "$INBOX/$filename" ] && [ ! -f "$INBOX/reply-${filename}" ]; then
            log "⚠️ 发现超时文件：$filename"
            # 触发超时提醒（Issue 评论）
            # TODO: 调用 gh issue comment
        fi
    done
}

# 日报提醒（每日 17:00）
daily_report_reminder() {
    log "📋 发送日报提醒..."
    # TODO: Issue 评论提醒双方提交日报
}

# 周报提醒（每周五 17:00）
weekly_report_reminder() {
    log "📊 发送周报提醒..."
    # TODO: Issue 评论提醒双方提交周报
}

# 状态同步检查（每小时）
status_sync_check() {
    log "📊 检查状态同步..."
    # TODO: 检查双方状态是否同步
}

# 主函数
case "$1" in
    timeout)
        check_timeout
        ;;
    daily)
        daily_report_reminder
        ;;
    weekly)
        weekly_report_reminder
        ;;
    status)
        status_sync_check
        ;;
    *)
        log "未知命令：$1"
        ;;
esac
