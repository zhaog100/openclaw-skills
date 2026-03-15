#!/bin/bash
# 上下文监控脚本（增强版 - 带错误重试机制）
# 创建时间：2026-03-04
# 更新时间：2026-03-14 18:05
# 功能：通过OpenClaw API监控真实上下文使用率，带重试机制和错误处理

# ⭐ 修复cron环境问题（2026-03-06）
export HOME="/home/zhaog"
export PATH="/home/zhaog/.npm-global/bin:$PATH"

# 配置参数
THRESHOLD=60  # v2.2.2优化：85% → 60%
LOG_FILE="$HOME/.openclaw/workspace/logs/context-monitor.log"
ERROR_LOG="$HOME/.openclaw/workspace/logs/context-errors.log"
FEISHU_TARGET="user:ou_64e8948aedd09549e512218c96702830"
NOTIFICATION_COOLDOWN=3600  # 1小时冷却期（秒）
COOLDOWN_FILE="/tmp/context-notification-cooldown"
ERROR_THRESHOLD_FILE="/tmp/context-error-count"
ERROR_THRESHOLD=5  # 错误阈值（5次/小时）

# 重试配置
MAX_RETRIES=3
RETRY_DELAY=5  # 秒
TIMEOUT=30  # 超时时间（秒）

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$(dirname "$ERROR_LOG")"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 记录错误日志
log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$ERROR_LOG"
    # 同时记录到主日志
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
            return 0  # 在冷却期
        fi
    fi
    return 1  # 不在冷却期
}

# 设置冷却期
set_cooldown() {
    date +%s > "$COOLDOWN_FILE"
    log "🔒 设置通知冷却期（1小时）"
}

# 记录错误计数
record_error() {
    local error_type="$1"
    local current_hour=$(date +%Y%m%d%H)
    local error_file="${ERROR_THRESHOLD_FILE}_${current_hour}"
    
    # 增加错误计数
    if [ -f "$error_file" ]; then
        local count=$(cat "$error_file")
        count=$((count + 1))
    else
        count=1
    fi
    
    echo "$count" > "$error_file"
    log_error "$error_type (第${count}次)"
    
    # 检查是否达到阈值
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
        
        # 使用openclaw message tool发送通知（带超时）
        timeout $TIMEOUT openclaw message send --channel feishu --account main --target "$FEISHU_TARGET" --message "$message" 2>&1 >> "$LOG_FILE"
        
        local exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            log "✅ 通知发送成功"
            success=true
            break
        elif [ $exit_code -eq 124 ]; then
            log_error "通知发送超时（${TIMEOUT}秒）"
            record_error "通知超时"
        else
            log_error "通知发送失败（退出码：$exit_code）"
            record_error "通知失败"
        fi
        
        # 如果不是最后一次尝试，等待后重试
        if [ $retry_count -lt $MAX_RETRIES ]; then
            log "等待 ${RETRY_DELAY} 秒后重试..."
            sleep $RETRY_DELAY
        fi
    done
    
    if [ "$success" = true ]; then
        # 设置冷却期
        set_cooldown
        return 0
    else
        log_error "通知发送失败，已达最大重试次数"
        return 1
    fi
}

# 获取真实上下文使用率（通过OpenClaw API，带重试）
get_context_usage() {
    local retry_count=0
    local success=false
    
    log "📊 调用OpenClaw API获取会话信息..."
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        retry_count=$((retry_count + 1))
        log "尝试 ${retry_count}/${MAX_RETRIES}..."
        
        # 获取最近2小时的活跃会话（带超时）
        local sessions_json
        sessions_json=$(timeout $TIMEOUT openclaw sessions --active 120 --json 2>&1)
        
        local exit_code=$?
        
        if [ $exit_code -eq 124 ]; then
            log_error "API调用超时（${TIMEOUT}秒）"
            record_error "API超时"
        elif [ $exit_code -ne 0 ]; then
            log_error "API调用失败（退出码：$exit_code）"
            record_error "API失败"
        else
            # 解析JSON
            local session_info=$(echo "$sessions_json" | jq '.sessions[0]' 2>/dev/null)
            
            if [ $? -eq 0 ] && [ "$session_info" != "null" ]; then
                local total_tokens=$(echo "$session_info" | jq -r '.totalTokens // 0')
                local context_tokens=$(echo "$session_info" | jq -r '.contextTokens // 202752')
                local session_key=$(echo "$session_info" | jq -r '.key // "unknown"')
                local model=$(echo "$session_info" | jq -r '.model // "unknown"')
                
                log "📝 会话: $session_key"
                log "🤖 模型: $model"
                log "📊 当前Tokens: $total_tokens / $context_tokens"
                
                # 计算使用率
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
        
        # 如果不是最后一次尝试，等待后重试
        if [ $retry_count -lt $MAX_RETRIES ]; then
            log "等待 ${RETRY_DELAY} 秒后重试..."
            sleep $RETRY_DELAY
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
    
    # 检查是否超过阈值
    if [ "$usage" -ge "$THRESHOLD" ]; then
        log "🚨 上下文使用率达到阈值（${usage}% >= ${THRESHOLD}%）"
        
        # 检查冷却期
        if ! is_in_cooldown; then
            send_feishu_notification "⚠️ 上下文使用率警告\n\n当前使用率：${usage}%\n阈值：${THRESHOLD}%\n剩余空间：$((100 - usage))%\n\n建议准备切换会话或清理上下文。"
        fi
        
        return 2  # 返回2表示超过阈值
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
        0)
            log "✅ 上下文使用率正常"
            ;;
        1)
            log "❌ 检查失败"
            ;;
        2)
            log "⚠️ 上下文使用率过高，已发送通知"
            ;;
    esac
    
    log "========================================="
    log "✅ 检查完成"
    log "========================================="
    
    return $status
}

# 执行主函数
main
