#!/bin/bash
# 定时提醒检查脚本
# 由 heartbeat 或 crontab 定期调用

REMINDERS_DIR="$HOME/.openclaw/workspace/memory/reminders"
LOG_FILE="$HOME/.openclaw/workspace/logs/reminders.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== 检查提醒 =========="

# 检查所有待处理的提醒
if [ -d "$REMINDERS_DIR" ]; then
    for reminder_file in "$REMINDERS_DIR"/*.json; do
        if [ -f "$reminder_file" ]; then
            reminder=$(cat "$reminder_file")
            id=$(echo "$reminder" | jq -r '.id')
            triggerAt=$(echo "$reminder" | jq -r '.triggerAt')
            status=$(echo "$reminder" | jq -r '.status')
            message=$(echo "$reminder" | jq -r '.message')
            
            now=$(date +%s)000
            
            # 检查是否到了触发时间
            if [ "$status" = "pending" ] && [ "$now" -ge "$triggerAt" ]; then
                log "⏰ 触发提醒: $id"
                log "   消息: $message"
                
                # 标记为已发送
                jq '.status = "sent"' "$reminder_file" > "${reminder_file}.tmp"
                mv "${reminder_file}.tmp" "$reminder_file"
                
                # TODO: 实际发送消息的逻辑
                # 这里的消息会在下一个 heartbeat 时被发送
                log "✅ 提醒已标记为待发送"
            fi
        fi
    done
fi

log "========== 检查完成 =========="
