#!/bin/bash
# 智能上下文检查脚本
# 在AI回复时被调用，主动提醒用户
# 更新时间：2026-03-05 - 切换到飞书通知

LOG_FILE="$HOME/.openclaw/workspace/logs/smart-context-check.log"
FEISHU_TARGET="user:ou_64e8948aedd09549e512218c96702830"

# 阈值设置
WARNING_THRESHOLD=85
CRITICAL_THRESHOLD=95

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 发送飞书通知
send_feishu_notification() {
    local message="$1"
    log "📤 发送飞书通知: $message"
    
    # 使用openclaw message tool发送通知
    # 正确的命令格式：必须指定--account main
    openclaw message send --channel feishu --account main --target "$FEISHU_TARGET" --message "$message" 2>&1 >> "$LOG_FILE"
}

# 检查并提醒
check_and_notify() {
    # 从session_status获取当前上下文使用率
    # 这里使用估算值，实际应该从OpenClaw API获取
    CURRENT_USAGE=36  # TODO: 从OpenClaw实时获取
    
    if [ "$CURRENT_USAGE" -ge "$CRITICAL_THRESHOLD" ]; then
        log "🚨 上下文使用率已达${CURRENT_USAGE}%，接近上限！"
        
        # 发送飞书通知
        send_feishu_notification "🚨 上下文告警\n\n上下文使用率已达${CURRENT_USAGE}%，接近上限！\n\n💡 建议立即发送 /new 开始新会话\n📝 我会自动保存当前会话的重要信息到记忆中"
        
        echo "🚨 上下文使用率已达${CURRENT_USAGE}%，接近上限！"
        echo "💡 建议立即发送 /new 开始新会话"
        echo "📝 我会自动保存当前会话的重要信息到记忆中"
        
    elif [ "$CURRENT_USAGE" -ge "$WARNING_THRESHOLD" ]; then
        log "⚠️ 上下文使用率已达${CURRENT_USAGE}%，建议准备切换会话"
        
        # 发送飞书通知
        send_feishu_notification "⚠️ 上下文预警\n\n上下文使用率已达${CURRENT_USAGE}%\n\n💡 可以继续对话，但请注意适时发送 /new"
        
        echo "⚠️ 上下文使用率已达${CURRENT_USAGE}%，建议准备切换会话"
        echo "💡 可以继续对话，但请注意适时发送 /new"
    fi
}

# 主函数
main() {
    log "🔍 开始智能上下文检查"
    check_and_notify
    log "✅ 检查完成"
}

main
