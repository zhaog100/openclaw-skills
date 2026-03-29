#!/bin/bash
# 智能节能防睡眠脚本
# 平衡：防睡眠 + 节能降耗

LOG_FILE="/tmp/smart-sleep.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检测电源状态
check_power() {
    if pmset -g ps | grep -q "AC Power"; then
        echo "adapter"
    else
        echo "battery"
    fi
}

# 节能模式配置
POWER_SOURCE=$(check_power)

log "============================================"
log "🛡️ 智能节能防睡眠启动"
log "============================================"
log "电源状态: $POWER_SOURCE"

# 停止之前的进程
pkill -f caffeinate 2>/dev/null

if [ "$POWER_SOURCE" = "adapter" ]; then
    # 使用电源适配器：完整保护
    log "🔌 电源模式：完整保护"
    caffeinate -d -i -s &
    log "  ✅ 防止显示器睡眠"
    log "  ✅ 防止系统空闲睡眠"

else
    # 使用电池：节能模式
    log "🔋 电池模式：节能保护"

    # 方案1：周期性唤醒（最节能）
    # 每5分钟唤醒一次，其他时间允许轻度睡眠
    while true; do
        # 唤醒30秒，保持网络连接
        caffeinate -i -u -t 30
        log "  ⚡ 唤醒30秒保持网络"

        # 休眠4.5分钟
        sleep 270
        log "  😴 节能休眠中..."
    done &
fi

CAFFEINATE_PID=$!
echo $CAFFEINATE_PID > /tmp/caffeinate.pid

log ""
log "✅ 保护已启动 (PID: $CAFFEINATE_PID)"
log ""
log "功能:"
log "  ✅ 保持网络连接"
log "  ✅ 智能节能调度"
log "  ✅ 自动适配电源/电池"
log ""
log "停止: bash scripts/stop-sleep.sh"
log "============================================"
