#!/bin/bash
# 夜间持续监控脚本（23:00 - 07:00）
# 每 30 分钟检查一次新任务

LOG_FILE="/home/zhaog/.openclaw/workspace/skills/github-bounty-hunter/logs/night_monitor.log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== 夜间监控启动 ==="
log "监控时间：$(date) 到 明天 07:00"
log "监控间隔：30 分钟"

# 循环监控直到早上 7 点
while true; do
    current_hour=$(date +%H)
    
    # 如果到了早上 7 点，退出
    if [ "$current_hour" -ge "07" ]; then
        log "=== 夜间监控结束（已到达 07:00）==="
        break
    fi
    
    log "=== 执行监控检查 ==="
    
    # 运行 Algora 监控
    cd "$SCRIPT_DIR"
    python3 algora_monitor.py >> "$LOG_FILE" 2>&1
    
    log "=== 本次检查完成 ==="
    
    # 等待 30 分钟
    log "等待 30 分钟后下次检查..."
    sleep 1800
done

log "=== 夜间监控脚本退出 ==="
