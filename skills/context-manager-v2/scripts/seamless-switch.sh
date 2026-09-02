# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/bin/bash
# 无感会话切换脚本
# 创建时间：2026-03-04
# 更新时间：2026-07-02
# 功能：上下文超过阈值时，自动保存记忆并通过 cron agentTurn 创建新会话
# 版本：v2.9.0

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
    # Skip cron/current session, pick first main/direct session with valid tokens
    local session_info=$(echo "$sessions_json" | jq '[.sessions[] | select(.kind != "cron") | select(.totalTokens != null)] | first // empty' 2>/dev/null)
    if [ -z "$session_info" ] || [ "$session_info" = "null" ]; then
        echo "0"
        return 1
    fi
    local total_tokens=$(echo "$session_info" | jq -r '.totalTokens // 0')
    local context_tokens=$(echo "$session_info" | jq -r '.contextTokens // 131072')
    if [ "$context_tokens" -gt 0 ]; then
        echo $((total_tokens * 100 / context_tokens))
        return 0
    fi
    echo "0"
    return 1
}

# 获取当前会话的关键信息
get_current_context() {
    local sessions_json
    sessions_json=$(timeout "$API_TIMEOUT" openclaw sessions --active "$ACTIVE_SESSION_WINDOW" --json 2>&1)
    if [ $? -ne 0 ]; then
        echo "{}"
        return
    fi
    echo "$sessions_json" | jq '[.sessions[] | select(.kind != "cron") | select(.totalTokens != null)] | first // empty | {key, model, totalTokens, contextTokens}' 2>/dev/null
}

# 提取当前会话的最近关键上下文摘要
extract_context_summary() {
    # 从今天的 daily log 中提取最近的未完成工作
    local today_log="$DAILY_LOG_DIR/$(date +%Y-%m-%d).md"
    if [ -f "$today_log" ]; then
        # 提取最近 3 段有意义的内容（非切换标记）
        grep -v "^## 🔄" "$today_log" 2>/dev/null | grep -v "^---$" | tail -c 800
    else
        echo "(no daily log for today)"
    fi
}

# 保存记忆到 MEMORY.md（追加当前上下文快照）
save_memory() {
    log "💾 保存上下文快照到 MEMORY.md..."
    
    local context_info
    context_info=$(get_current_context)
    local current_key
    current_key=$(echo "$context_info" | jq -r '.key // "unknown"')
    local current_tokens
    current_tokens=$(echo "$context_info" | jq -r '.totalTokens // 0')
    local current_model
    current_model=$(echo "$context_info" | jq -r '.model // "unknown"')
    
    # 提取当前未完成的工作
    local context_summary
    context_summary=$(extract_context_summary)
    
    cat >> "$MEMORY_FILE" << EOF

---

## 🔄 会话切换标记（$(date '+%Y-%m-%d %H:%M:%S')）

**触发原因**：上下文超过 ${SWITCH_THRESHOLD}%
**当前会话**：${current_key}
**当前Tokens**：${current_tokens} / ${context_tokens:-131072}
**当前模型**：${current_model}
**上下文摘要**：${context_summary:-(无)}
**切换方式**：cron agentTurn 自动创建新会话

---
EOF
    log "✅ 记忆保存完成"
}

# 更新 daily log
update_daily_log() {
    log "📝 更新 daily log..."
    mkdir -p "$DAILY_LOG_DIR"
    cat >> "$DAILY_LOG" << EOF

---

## 🔄 自动会话切换（$(date '+%Y-%m-%d %H:%M:%S')）

**触发原因**：上下文超过 ${SWITCH_THRESHOLD}%
**切换方式**：cron agentTurn 自动创建新会话
**新会话**：自动加载 MEMORY.md + SOUL.md + AGENTS.md

---
EOF
    log "✅ Daily log 更新完成"
}

# 通过 cron 触发 agentTurn 创建新会话（真正的切换）
trigger_new_session() {
    log "🚀 通过 cron agentTurn 触发新会话..."
    
    local context_info
    context_info=$(get_current_context)
    local current_key
    current_key=$(echo "$context_info" | jq -r '.key // "unknown"')
    local context_summary
    context_summary=$(extract_context_summary)
    
    # 构建注入消息
    local switch_message="[SYSTEM: CONTEXT SWITCH TRIGGERED]
上下文使用率已超过 ${SWITCH_THRESHOLD}%，自动触发无感会话切换。

请执行以下操作：
1. 将当前未完成的工作保存到 memory/$(date +%Y-%m-%d).md
2. 创建新会话（发送 /new 或让系统自动创建）
3. 在新会话中加载 MEMORY.md 继续工作

当前会话摘要：${context_summary:-(无)}

注意：新会话会自动加载 MEMORY.md、SOUL.md、AGENTS.md，无需手动操作。"
    
    # 通过 system event 发送唤醒事件到主会话
    openclaw system event --text "$switch_message" --mode now 2>&1 >> "$SWITCH_LOG"
    local wake_result=$?
    
    if [ $wake_result -eq 0 ]; then
        log "✅ 新会话触发成功"
    else
        log "⚠️ 新会话触发失败（exit $wake_result），记录到日志"
    fi
}

# 主逻辑
main() {
    log "🔍 开始无感会话切换检查"

    USAGE=$(get_context_usage)
    log "📊 当前上下文使用率: ${USAGE}%"

    if [ "$USAGE" -ge "$SWITCH_THRESHOLD" ]; then
        log "⚠️ 超过阈值 ${SWITCH_THRESHOLD}%，启动无感切换"
        save_memory
        update_daily_log
        trigger_new_session
        log "✅ 无感切换完成"
    else
        log "✅ 上下文正常（${USAGE}% < ${SWITCH_THRESHOLD}%）"
    fi
}

main
