#!/bin/bash
# 监控守护脚本 - 自动检查和重启监控进程
# 版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/bounty-guardian.log"
PID_FILE="/tmp/bounty-monitor.pid"
EXPECTED_SCRIPT="algora_monitor.py"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_and_restart() {
    log "=== 检查监控进程 ==="
    
    # 检查进程是否存在
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log "✅ 监控进程运行中 (PID: $PID)"
            return 0
        else
            log "❌ 进程文件存在但进程已停止 (PID: $PID)"
            rm -f "$PID_FILE"
        fi
    else
        log "❌ 未找到 PID 文件"
    fi
    
    # 检查是否有同名进程
    if pgrep -f "$EXPECTED_SCRIPT" > /dev/null 2>&1; then
        EXISTING_PID=$(pgrep -f "$EXPECTED_SCRIPT" | head -1)
        log "⚠️  发现残留进程 (PID: $EXISTING_PID)，清理中..."
        kill "$EXISTING_PID" 2>/dev/null
        sleep 2
    fi
    
    # 重启监控
    log "🔄 启动监控进程..."
    
    # 从配置文件加载环境变量（如果存在）
    if [ -f "$SCRIPT_DIR/.env" ]; then
        source "$SCRIPT_DIR/.env"
    fi
    
    # 如果仍未配置，使用系统环境变量
    if [ -z "$GITHUB_TOKEN" ]; then
        log "⚠️  警告：GITHUB_TOKEN 未配置"
    fi
    
    cd "$SCRIPT_DIR" && nohup python3 algora_monitor.py > /tmp/bounty-monitor.log 2>&1 &
    NEW_PID=$!
    echo "$NEW_PID" > "$PID_FILE"
    
    sleep 3
    if ps -p "$NEW_PID" > /dev/null 2>&1; then
        log "✅ 监控进程已启动 (PID: $NEW_PID)"
        return 0
    else
        log "❌ 启动失败"
        return 1
    fi
}

# 主逻辑
log "🦞 Bounty Guardian 启动"
check_and_restart
log "=== 检查完成 ==="
log ""
