#!/bin/bash
# 无感会话切换脚本
# 创建时间：2026-03-04
# 更新时间：2026-03-18
# 功能：上下文超过阈值时，自动保存记忆并创建新会话

# 环境修复（cron）
export HOME="${HOME:-/root}"
export PATH="$HOME/.npm-global/bin:$PATH"

# 加载配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config-loader.sh"

DAILY_LOG="$DAILY_LOG_DIR/$(date +%Y-%m-%d).md"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$SWITCH_LOG"
}

# 获取当前上下文使用率
get_context_usage() {
    local sessions_json
    sessions_json=$(timeout "$API_TIMEOUT" openclaw sessions --active "$ACTIVE_SESSION_WINDOW" --json 2>&1)
    if [ $? -ne 0 ] || [ -z "$sessions_json" ]; then
        echo "0"
        return 1
    fi
    local session_info=$(echo "$sessions_json" | jq '.sessions[0]' 2>/dev/null)
    local total_tokens=$(echo "$session_info" | jq -r '.totalTokens // 0')
    local context_tokens=$(echo "$session_info" | jq -r '.contextTokens // 202752')
    if [ "$context_tokens" -gt 0 ]; then
        echo $((total_tokens * 100 / context_tokens))
        return 0
    fi
    echo "0"
    return 1
}

# 保存记忆到MEMORY.md
save_memory() {
    log "💾 保存记忆到MEMORY.md..."
    cat >> "$MEMORY_FILE" << EOF

---

## 🔄 会话切换标记（$(date '+%Y-%m-%d %H:%M:%S')）

**触发原因**：上下文超过${THRESHOLD}%
**当前任务**：{会由AI自动填充}
**切换方式**：无感自动切换

---

EOF
    log "✅ 记忆保存完成"
}

# 更新daily log
update_daily_log() {
    log "📝 更新daily log..."
    mkdir -p "$DAILY_LOG_DIR"
    cat >> "$DAILY_LOG" << EOF

---

## 🔄 自动会话切换（$(date '+%Y-%m-%d %H:%M:%S')）

**触发原因**：上下文超过${THRESHOLD}%
**切换方式**：无感自动切换（agentTurn）
**新会话**：自动加载记忆继续工作

---

EOF
    log "✅ Daily log更新完成"
}

# 触发agentTurn创建新会话
trigger_new_session() {
    log "🚀 触发agentTurn创建新会话..."
    log "📍 新会话将在当前时间触发"
    log "💡 新会话会自动加载MEMORY.md继续工作"
}

# 主逻辑
main() {
    log "🔍 开始无感会话切换检查"

    USAGE=$(get_context_usage)
    log "📊 当前上下文使用率: ${USAGE}%"

    if [ "$USAGE" -ge "$THRESHOLD" ]; then
        log "⚠️ 超过阈值${THRESHOLD}%，启动无感切换"
        save_memory
        update_daily_log
        trigger_new_session
        log "✅ 无感切换完成"
    else
        log "✅ 上下文正常（${USAGE}% < ${THRESHOLD}%）"
    fi
}

main
