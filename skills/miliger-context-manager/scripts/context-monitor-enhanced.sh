#!/bin/bash
# 上下文监控脚本（增强版 - 带错误重试机制）
# 创建时间：2026-03-04
# 更新时间：2026-03-18
# 功能：通过OpenClaw API监控真实上下文使用率，带重试机制和错误处理

# 环境修复（cron）
export HOME="${HOME:-/root}"
export PATH="$HOME/.npm-global/bin:$PATH"

# 加载配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config-loader.sh"

# 加载错误处理库（可选）
if [ -f "$ERROR_HANDLER" ]; then
    source "$ERROR_HANDLER"
fi

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$MONITOR_LOG"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$ERROR_LOG"
    log "❌ 错误: $1"
}

# 检查冷却期
is_in_cooldown() {
    if [ -f "$COOLDOWN_FILE" ]; then
        local last_notification=$(cat "$COOLDOWN_FILE" 2>/dev/null || echo "0")
        local current_time=$(date +%s)
        local elapsed=$((current_time - last_notification))
        if [ "$elapsed" -lt "$NOTIFICATION_COOLDOWN" ]; then
            log "⏸️ 冷却期中（距上次通知${elapsed}秒，需${NOTIFICATION_COOLDOWN}秒）"
            return 0
        fi
    fi
    return 1
}

set_cooldown() {
    date +%s > "$COOLDOWN_FILE"
    log "🔒 设置通知冷却期（$((NOTIFICATION_COOLDOWN / 60))分钟）"
}

record_error() {
    local error_type="$1"
    local current_hour=$(date +%Y%m%d%H)
    local error_file="${ERROR_COUNT_PREFIX}${current_hour}"

    if [ -f "$error_file" ]; then
        local count=$(cat "$error_file")
        count=$((count + 1))
    else
        count=1
    fi
    echo "$count" > "$error_file"
    log_error "$error_type (第${count}次)"

    if [ "$count" -ge "$ERROR_THRESHOLD" ]; then
        log "🚨 错误达到阈值（${count}次/${ERROR_THRESHOLD}次）"
        send_feishu_notification "🚨 上下文监控异常\n\n错误类型：$error_type\n错误次数：${count}次/小时\n阈值：${ERROR_THRESHOLD}次/小时\n\n建议检查系统状态！"
    fi
}

# 发送飞书通知（带重试）
send_feishu_notification() {
    local message="$1"
    local retry_count=0
    local success=false

    log "📤 发送飞书通知: $message"

    while [ $retry_count -lt $MAX_RETRIES ]; do
        retry_count=$((retry_count + 1))
        log "尝试 ${retry_count}/${MAX_RETRIES}..."

        timeout "$API_TIMEOUT" openclaw message send --channel "$FEISHU_CHANNEL" --account "$FEISHU_ACCOUNT" --target "$FEISHU_TARGET" --message "$message" 2>&1 >> "$MONITOR_LOG"
        local exit_code=$?

        if [ $exit_code -eq 0 ]; then
            log "✅ 通知发送成功"
            success=true
            break
        elif [ $exit_code -eq 124 ]; then
            log_error "通知发送超时（${API_TIMEOUT}秒）"
            record_error "通知超时"
        else
            log_error "通知发送失败（退出码：$exit_code）"
            record_error "通知失败"
        fi

        if [ $retry_count -lt $MAX_RETRIES ]; then
            sleep "$RETRY_DELAY"
        fi
    done

    if [ "$success" = true ]; then
        set_cooldown
        return 0
    else
        log_error "通知发送失败，已达最大重试次数"
        return 1
    fi
}

# 获取真实上下文使用率（带重试）
get_context_usage() {
    local retry_count=0

    while [ $retry_count -lt $MAX_RETRIES ]; do
        retry_count=$((retry_count + 1))
        log_info "📊 调用 OpenClaw API 获取会话信息（尝试 ${retry_count}/${MAX_RETRIES}）..."

        local sessions_json
        sessions_json=$(timeout "$API_TIMEOUT" openclaw sessions --active "$ACTIVE_SESSION_WINDOW" --json 2>&1)

        if [ -n "$sessions_json" ] && [ "$sessions_json" != "{}" ]; then
            local session_info=$(echo "$sessions_json" | jq '.sessions[0]' 2>/dev/null)

            if [ $? -eq 0 ] && [ "$session_info" != "null" ]; then
                local total_tokens=$(echo "$session_info" | jq -r '.totalTokens // 0')
                local context_tokens=$(echo "$session_info" | jq -r '.contextTokens // 202752')
                local session_key=$(echo "$session_info" | jq -r '.key // "unknown"')
                local model=$(echo "$session_info" | jq -r '.model // "unknown"')

                log "📝 会话: $session_key"
                log "🤖 模型: $model"
                log "📊 当前Tokens: $total_tokens / $context_tokens"

                if [ "$context_tokens" -gt 0 ]; then
                    local usage=$((total_tokens * 100 / context_tokens))
                    log "✅ 上下文使用率: ${usage}%"
                    echo "$usage"
                    return 0
                else
                    log "⚠️ 上下文大小为0，使用默认值"
                    echo "0"
                    return 1
                fi
            else
                log_error "JSON解析失败"
                record_error "JSON解析失败"
            fi
        fi

        if [ $retry_count -lt $MAX_RETRIES ]; then
            log "等待 ${RETRY_DELAY} 秒后重试..."
            sleep "$RETRY_DELAY"
        fi
    done

    log_error "获取上下文使用率失败，已达最大重试次数"
    echo "0"
    return 1
}

# 检查上下文使用率
check_context() {
    local usage=$(get_context_usage)
    local status=$?

    if [ $status -ne 0 ]; then
        log "⚠️ 无法获取上下文使用率"
        return 1
    fi

    log "📊 当前上下文使用率: ${usage}%"

    if [ "$usage" -ge "$THRESHOLD" ]; then
        log "🚨 上下文使用率达到阈值（${usage}% >= ${THRESHOLD}%）"
        if ! is_in_cooldown; then
            send_feishu_notification "⚠️ 上下文使用率警告\n\n当前使用率：${usage}%\n阈值：${THRESHOLD}%\n剩余空间：$((100 - usage))%\n\n建议准备切换会话或清理上下文。"
        fi
        return 2
    fi

    return 0
}

# 主函数
main() {
    log "========================================="
    log "🚀 开始上下文监控检查（增强版 v2.2.3）"
    log "========================================="

    check_context
    local status=$?

    case $status in
        0) log "✅ 上下文使用率正常" ;;
        1) log "❌ 检查失败" ;;
        2) log "⚠️ 上下文使用率过高，已发送通知" ;;
    esac

    log "========================================="
    log "✅ 检查完成"
    log "========================================="

    return $status
}

main
