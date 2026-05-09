#!/bin/bash
# 系统健康监控脚本
# 功能：全面监控OpenClaw系统运行状态

WORKSPACE="/Users/zhaog/.openclaw/workspace"
LOG_DIR="/Users/zhaog/.openclaw/workspace/data/system-logs"
LOG_FILE="$LOG_DIR/health-monitor.log"
DATA_FILE="$LOG_DIR/health-data.csv"

mkdir -p "$LOG_DIR"

# 初始化
if [ ! -f "$DATA_FILE" ]; then
    echo "timestamp,uptime_minutes,load_avg,cpu_percent,memory_percent,disk_percent,openclaw_pid,monitor_pid,caffeinate_pid,github_status,network_latency_ms" > "$DATA_FILE"
fi

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 获取系统运行时间（分钟）
get_uptime_minutes() {
    echo $(awk '{print int($1/60)}' /proc/uptime 2>/dev/null || echo "0")
}

# 获取系统负载（1分钟平均）
get_load_avg() {
    uptime | awk -F'load averages:' '{print $2}' | awk '{print $1}' | tr -d ','
}

# 获取CPU占用率
get_cpu_percent() {
    ps -A -o %cpu 2>/dev/null | awk '{s+=$1} END {printf "%.1f", s}' || echo "0"
}

# 获取内存占用率
get_memory_percent() {
    vm_stat 2>/dev/null | perl -ne 'print $2*4096,' || top -l 1 | grep "PhysMem" | awk '{print $2}' | sed 's/[^0-9]//g'
}

# 获取磁盘占用率
get_disk_percent() {
    df -h / | tail -1 | awk '{print $5}' | tr -d '%'
}

# 检查OpenClaw Gateway进程
check_openclaw_pid() {
    pgrep -f "openclaw-gateway" | head -1 || echo "0"
}

# 检查功耗监控进程
check_monitor_pid() {
    pgrep -f "power-monitor.sh" | head -1 || echo "0"
}

# 检查caffeinate进程
check_caffeinate_pid() {
    pgrep -f "caffeinate" | head -1 || echo "0"
}

# 测试GitHub连接
check_github_status() {
    if curl -s --connect-timeout 5 -o /dev/null -w "%{http_code}" https://github.com | grep -q "200"; then
        echo "1"
    else
        echo "0"
    fi
}

# 测试网络延迟
get_network_latency() {
    ping -c 1 github.com 2>/dev/null | grep "time=" | awk -F'time=' '{print $2}' | awk '{print $1}' | tr -d 'ms' || echo "9999"
}

# 主监控逻辑
log "============================================"
log "📊 系统健康监控启动"
log "============================================"

log "配置:"
log "  间隔: 5分钟"
log "  日志: $LOG_FILE"
log "  数据: $DATA_FILE"
log "============================================"

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

    # 采集数据
    UPTIME=$(get_uptime_minutes)
    LOAD_AVG=$(get_load_avg)
    CPU_PERCENT=$(get_cpu_percent)
    MEMORY_PERCENT=$(get_memory_percent)
    DISK_PERCENT=$(get_disk_percent)
    OPENCLAW_PID=$(check_openclaw_pid)
    MONITOR_PID=$(check_monitor_pid)
    CAFFEINATE_PID=$(check_caffeinate_pid)
    GITHUB_STATUS=$(check_github_status)
    NETWORK_LATENCY=$(get_network_latency)

    # 写入CSV
    echo "$TIMESTAMP,$UPTIME,$LOAD_AVG,$CPU_PERCENT,$MEMORY_PERCENT,$DISK_PERCENT,$OPENCLAW_PID,$MONITOR_PID,$CAFFEINATE_PID,$GITHUB_STATUS,$NETWORK_LATENCY" >> "$DATA_FILE"

    # 每小时记录日志
    CURRENT_MINUTE=$(date +%M)
    if [ "$CURRENT_MINUTE" = "00" ]; then
        log "✅ 运行正常 | 负载: $LOAD_AVG | CPU: ${CPU_PERCENT}% | 内存: ${MEMORY_PERCENT}% | 磁盘: ${DISK_PERCENT}%"
    fi

    # 异常检测
    if [ "$OPENCLAW_PID" = "0" ]; then
        log "⚠️ OpenClaw Gateway未运行"
    fi

    if [ "$GITHUB_STATUS" = "0" ]; then
        log "⚠️ 网络异常: 无法连接到GitHub"
    fi

    if (( $(echo "$LOAD_AVG > 3.0" | bc -l 2>/dev/null || echo "0") ); then
        log "⚠️ 系统负载过高: $LOAD_AVG"
    fi

    # 5分钟采集一次
    sleep 300
done
