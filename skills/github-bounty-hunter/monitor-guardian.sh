#!/bin/bash
# GitHub Bounty Hunter - Crontab 守护脚本
# 每 10 分钟检查监控进程，确保持续运行
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
PID_FILE="$SCRIPT_DIR/monitor.pid"
LOG_FILE="$LOG_DIR/monitor-guardian.log"

# 创建日志目录
mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "=== Guardian 检查启动 ==="

# 检查监控进程
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        log "✅ 监控进程运行中 (PID: $PID)"
    else
        log "⚠️ 监控进程已停止，重新启动..."
        cd "$SCRIPT_DIR"
        export GITHUB_TOKEN
        nohup python3 scripts/monitor.py > "$LOG_DIR/monitor.log" 2>&1 &
        echo $! > "$PID_FILE"
        log "✅ 监控进程已重启 (PID: $!)"
    fi
else
    log "⚠️ 未找到 PID 文件，启动监控进程..."
    cd "$SCRIPT_DIR"
    export GITHUB_TOKEN
    nohup python3 scripts/monitor.py > "$LOG_DIR/monitor.log" 2>&1 &
    echo $! > "$PID_FILE"
    log "✅ 监控进程已启动 (PID: $!)"
fi

log "=== Guardian 检查完成 ==="
