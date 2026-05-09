#!/bin/bash
#
# error-retry.sh - 防护脚本，处理 "Something went wrong" 错误
# 功能：
# 1. 捕获错误输出
# 2. 自动重试（最多3次）
# 3. 记录错误日志
# 4. 发送通知

set -euo pipefail

# 配置
MAX_RETRIES=3
RETRY_DELAY=2
LOG_FILE="/home/zhaog/.openclaw/workspace/data/error-retry.log"
ERROR_PATTERN="Something went wrong"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# 错误处理函数
handle_error() {
    local exit_code=$1
    local command="$2"
    local retry_count=$3
    
    log "❌ 错误: 退出码 $exit_code | 命令: $command | 重试次数: $retry_count"
    
    if [ $retry_count -lt $MAX_RETRIES ]; then
        log "🔄 等待 ${RETRY_DELAY}秒后重试..."
        sleep $RETRY_DELAY
        return 0
    else
        log "💀 达到最大重试次数，放弃"
        return 1
    fi
}

# 主函数
main() {
    local command="$1"
    local retry_count=0
    
    log "🚀 开始执行: $command"
    
    while [ $retry_count -le $MAX_RETRIES ]; do
        # 执行命令并捕获输出
        if output=$(eval "$command" 2>&1); then
            # 成功
            log "✅ 执行成功"
            echo "$output"
            return 0
        else
            exit_code=$?
            
            # 检查是否包含错误模式
            if echo "$output" | grep -q "$ERROR_PATTERN"; then
                log "⚠️  检测到 '$ERROR_PATTERN' 错误"
            fi
            
            # 处理错误
            if ! handle_error $exit_code "$command" $retry_count; then
                break
            fi
            
            retry_count=$((retry_count + 1))
        fi
    done
    
    # 最终失败
    log "❌ 最终失败: $command"
    echo "$output"
    return 1
}

# 参数检查
if [ $# -eq 0 ]; then
    echo "用法: $0 <命令>"
    echo "示例: $0 'python3 script.py'"
    exit 1
fi

# 执行主函数
main "$*"
