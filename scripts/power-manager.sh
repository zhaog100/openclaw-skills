#!/bin/bash
# 智能电源管理
# 自动检测电源状态并调整策略

CONFIG_FILE="/tmp/power-manager-config.json"
LOG_FILE="/tmp/power-manager.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 配置参数
cat > "$CONFIG_FILE" << EOF
{
  "adapter": {
    "caffeinate": "-d -i -s",
    "check_interval": 300,
    "description": "电源适配器：完整保护"
  },
  "battery": {
    "caffeinate": "-i -u -t 60",
    "check_interval": 600,
    "wake_cycle": {
      "wake": 60,
      "sleep": 540
    },
    "description": "电池：周期唤醒"
  }
}
EOF

# 主监控循环
monitor_power() {
    local last_source=""

    while true; do
        # 检测电源状态
        if pmset -g ps | grep -q "AC Power"; then
            source="adapter"
        else
            source="battery"
        fi

        # 如果电源状态改变，重新配置
        if [ "$source" != "$last_source" ]; then
            log "电源切换: $last_source → $source"
            adjust_power_mode "$source"
            last_source="$source"
        fi

        sleep 60
    done
}

adjust_power_mode() {
    local mode=$1

    # 停止当前保护
    pkill -f caffeinate 2>/dev/null

    if [ "$mode" = "adapter" ]; then
        log "🔌 电源模式：完整保护"
        caffeinate -d -i -s > /dev/null 2>&1 &
    else
        log "🔋 电池模式：周期唤醒"
        # 每10分钟唤醒1分钟
        (
            while true; do
                caffeinate -i -u -t 60 > /dev/null 2>&1
                sleep 540
            done
        ) &
    fi

    echo $! > /tmp/caffeinate.pid
}

# 启动监控
log "============================================"
log "🤖 智能电源管理启动"
log "============================================"

# 初始化
if pmset -g ps | grep -q "AC Power"; then
    adjust_power_mode "adapter"
else
    adjust_power_mode "battery"
fi

# 启动监控（后台）
monitor_power &
MONITOR_PID=$!
echo $MONITOR_PID > /tmp/power-manager.pid

log "监控PID: $MONITOR_PID"
log "============================================"

cat << EOF

✅ 智能电源管理已启动

功能:
  🔄 自动检测电源状态
  🔌 电源适配器：完整保护
  🔋 电池模式：周期唤醒
  📊 动态调整功耗

查看日志:
  tail -f /tmp/power-manager.log

停止:
  bash scripts/stop-sleep.sh

EOF
