#!/bin/bash
# 系统健康检查 - 合并脚本
# 功能：上下文监控 + 模型检查 + 内存同步检查
# 频率: */15 分钟（替代原来的 */5 + */5 + */10）

export PATH="/home/zhaog/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export HOME="/home/zhaog"

LOG_DIR="$HOME/.openclaw/workspace/logs"
LOG_FILE="$LOG_DIR/system-health-check.log"
mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "═══ 系统健康检查开始 ═══"

# ── 1. 上下文监控 ────────────────────────────────────
log "1. 上下文监控"

THRESHOLD=85
sessions_json=$(openclaw sessions --active 120 --json 2>&1)

if [ $? -eq 0 ] && [ -n "$sessions_json" ]; then
    session_info=$(echo "$sessions_json" | jq -r '.sessions[] | select(.key | contains("qqbot")) | @base64' | head -1)
    if [ -n "$session_info" ]; then
        session_data=$(echo "$session_info" | base64 -d)
        usage=$(echo "$session_data" | jq -r '.usage // 0')
        log "   上下文使用率: ${usage}%"
        if [ "$usage" -ge "$THRESHOLD" ] 2>/dev/null; then
            log "   ⚠️ 超过阈值 (${THRESHOLD}%)，需要切换会话"
        else
            log "   ✅ 正常"
        fi
    else
        log "   ⚠️ 未找到 QQ 会话"
    fi
else
    log "   ⚠️ 获取会话信息失败"
fi

# ── 2. 模型检查 ──────────────────────────────────────
log "2. 模型检查"
current_model=$(openclaw status --json 2>&1 | jq -r '.model // "unknown"' 2>/dev/null)
log "   当前模型: $current_model"

# ── 3. 内存同步检查（轻量版） ─────────────────────────
log "3. 内存同步检查"
MEMORY_FILE="$HOME/.openclaw/workspace/MEMORY.md"
if [ -f "$MEMORY_FILE" ]; then
    lines=$(wc -l < "$MEMORY_FILE")
    log "   MEMORY.md: $lines 行"
    if [ "$lines" -gt 500 ]; then
        log "   ⚠️ 文件过大，建议精简"
    else
        log "   ✅ 正常"
    fi
fi

# ── 4. 系统资源检查 ──────────────────────────────────
log "4. 系统资源"
mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2*100}')
log "   内存: ${mem_usage}%"

load=$(cat /proc/loadavg | awk '{print $1}')
log "   负载: $load"

if [ "$mem_usage" -gt 80 ] 2>/dev/null; then
    log "   ⚠️ 内存使用过高"
fi

log "═══ 检查完成 ═══"
echo ""
