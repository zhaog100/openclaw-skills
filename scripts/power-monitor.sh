#!/bin/bash
# 功耗监控脚本 - 运行一周采集数据
# 每5分钟记录一次功耗数据

LOG_DIR="/Users/zhaog/.openclaw/workspace/data/power-logs"
LOG_FILE="$LOG_DIR/power-monitor.log"
DATA_FILE="$LOG_DIR/power-data.csv"

mkdir -p "$LOG_DIR"

# 初始化CSV
if [ ! -f "$DATA_FILE" ]; then
    echo "timestamp,power_source,cpu_percent,battery_percent,temperature,wifi_active,caffeinate_running" > "$DATA_FILE"
fi

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 获取电源状态
get_power_source() {
    if pmset -g ps | grep -q "AC Power"; then
        echo "adapter"
    else
        echo "battery"
    fi
}

# 获取电池百分比
get_battery_percent() {
    pmset -g batt | grep -oE '[0-9]+%' | head -1 | tr -d '%'
}

# 获取CPU占用
get_cpu_percent() {
    ps -A -o %cpu | awk '{s+=$1} END {printf "%.1f", s}'
}

# 获取温度（如果有）
get_temperature() {
    # macOS通常需要sudo或第三方工具
    # 这里用CPU占用率估算
    echo "N/A"
}

# 检查WiFi状态
check_wifi() {
    if networksetup -getairportpower en0 | grep -q "On"; then
        echo "1"
    else
        echo "0"
    fi
}

# 检查caffeinate运行状态
check_caffeinate() {
    if pgrep -f caffeinate > /dev/null; then
        echo "1"
    else
        echo "0"
    fi
}

# 主监控循环
log "============================================"
log "📊 功耗监控启动 - 计划运行一周"
log "============================================"
log "数据文件: $DATA_FILE"
log "日志文件: $LOG_FILE"
log "采样间隔: 5分钟"
log "运行周期: 7天"
log "============================================"

# 计算结束时间（7天后）
END_TIME=$(date -v +7d +%s)
START_TIME=$(date +%s)

echo ""
echo "📊 功耗监控已启动"
echo ""
echo "监控时长: 7天 (至 $(date -r $END_TIME '+%Y-%m-%d %H:%M'))"
echo "数据文件: $DATA_FILE"
echo "日志文件: $LOG_FILE"
echo ""
echo "查看实时数据:"
echo "  tail -f $DATA_FILE"
echo ""
echo "查看统计:"
echo "  bash scripts/power-stats.sh"
echo ""

ITERATION=0
while true; do
    ITERATION=$((ITERATION + 1))

    # 检查是否到期
    CURRENT_TIME=$(date +%s)
    if [ $CURRENT_TIME -ge $END_TIME ]; then
        log "✅ 一周监控完成"
        break
    fi

    # 采集数据
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    POWER_SOURCE=$(get_power_source)
    CPU_PERCENT=$(get_cpu_percent)
    BATTERY_PERCENT=$(get_battery_percent)
    TEMPERATURE=$(get_temperature)
    WIFI_ACTIVE=$(check_wifi)
    CAFFEINATE_RUNNING=$(check_caffeinate)

    # 写入CSV
    echo "$TIMESTAMP,$POWER_SOURCE,$CPU_PERCENT,$BATTERY_PERCENT,$TEMPERATURE,$WIFI_ACTIVE,$CAFFEINATE_RUNNING" >> "$DATA_FILE"

    # 每小时记录日志
    if [ $((ITERATION % 12)) -eq 0 ]; then
        log "已采集 $ITERATION 个样本，电池: ${BATTERY_PERCENT}%, CPU: ${CPU_PERCENT}%"
    fi

    # 每5分钟采集一次
    sleep 300
done

log "监控结束，共采集 $ITERATION 个样本"
