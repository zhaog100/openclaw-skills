#!/bin/bash

# 上下文监控与模型切换脚本
# 功能：监控上下文使用率，连续2次超过阈值时自动切换到长上下文模型

source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

STATE_FILE="$DATA_DIR/context-state.json"
LOG_FILE="$LOG_DIR/context-switch.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 初始化状态文件
init_state() {
    if [ ! -f "$STATE_FILE" ]; then
        cat > "$STATE_FILE" << EOF
{
  "consecutive_hits": 0,
  "last_check": null,
  "current_model": "zai/glm-5",
  "last_switch": null,
  "cooldown_until": null
}
EOF
        log "状态文件已初始化"
    fi
}

# 获取当前上下文使用率
get_context_usage() {
    local usage=$("$SCRIPT_DIR/get-context-usage.sh" 2>/dev/null)
    if [ -z "$usage" ] || ! [[ "$usage" =~ ^[0-9]+$ ]]; then
        usage=0
    fi
    echo "$usage"
}

# 检查是否在冷却期
is_in_cooldown() {
    local cooldown_until=$(jq -r '.cooldown_until // empty' "$STATE_FILE")
    if [ -z "$cooldown_until" ] || [ "$cooldown_until" = "null" ]; then
        return 1
    fi
    local now=$(date +%s)
    local cooldown_ts=$(date -d "$cooldown_until" +%s 2>/dev/null || echo 0)
    if [ $now -lt $cooldown_ts ]; then
        return 0
    else
        return 1
    fi
}

# 更新状态
update_state() {
    local hits=$1
    local model=$2
    local temp_file=$(mktemp)
    jq --arg hits "$hits" \
       --arg model "$model" \
       --arg now "$(date -Iseconds)" \
       '(.consecutive_hits = ($hits | tonumber)) |
        (.current_model = $model) |
        (.last_check = $now)' "$STATE_FILE" > "$temp_file"
    mv "$temp_file" "$STATE_FILE"
}

# 执行模型切换
switch_model() {
    local target_model=$1
    local current_model=$(jq -r '.current_model' "$STATE_FILE")
    log "切换模型：$current_model → $target_model"

    "$SCRIPT_DIR/switch-model.sh" "$target_model" >> "$LOG_FILE" 2>&1

    local cooldown_minutes=$(cfg '.context_switch_strategy.cooldown.duration_minutes' 10)
    local cooldown_until=$(date -d "+$cooldown_minutes minutes" -Iseconds)

    local temp_file=$(mktemp)
    jq --arg model "$target_model" \
       --arg switch_time "$(date -Iseconds)" \
       --arg cooldown "$cooldown_until" \
       '(.current_model = $model) |
        (.last_switch = $switch_time) |
        (.cooldown_until = $cooldown) |
        (.consecutive_hits = 0)' "$STATE_FILE" > "$temp_file"
    mv "$temp_file" "$STATE_FILE"
    log "模型切换完成，冷却期至 $cooldown_until"

    local notification_enabled=$(cfg '.context_switch_strategy.notification.enabled' false)
    if [ "$notification_enabled" = "true" ]; then
        local notification_msg=$(cfg '.context_switch_strategy.notification.message')
        echo "✅ $notification_msg"
    fi
}

# 主监控逻辑
main() {
    init_state

    if is_in_cooldown; then
        log "在冷却期内，跳过检查"
        exit 0
    fi

    local usage=$(get_context_usage)
    log "当前上下文使用率：${usage}%"

    local threshold=$(cfg '.context_switch_strategy.rules[0].threshold' 85)
    local consecutive_hits_required=$(cfg '.context_switch_strategy.rules[0].consecutive_hits' 2)
    local target_model_key=$(cfg '.context_switch_strategy.rules[0].target_model' 'long-context')
    local target_model=$(cfg ".models.\"$target_model_key\".id" "$target_model_key")

    local current_hits=$(jq -r '.consecutive_hits' "$STATE_FILE")

    if [ "$usage" -ge "$threshold" ]; then
        current_hits=$((current_hits + 1))
        log "超过阈值（$usage% >= $threshold%），连续命中次数：$current_hits"
        update_state "$current_hits" "$(jq -r '.current_model' "$STATE_FILE")"

        if [ "$current_hits" -ge "$consecutive_hits_required" ]; then
            log "达到连续${consecutive_hits_required}次阈值，触发模型切换"
            switch_model "$target_model"
        else
            log "未达到连续${consecutive_hits_required}次，继续监控"
        fi
    else
        if [ "$current_hits" -gt 0 ]; then
            log "未超过阈值，重置计数器"
            update_state "0" "$(jq -r '.current_model' "$STATE_FILE")"
        fi
    fi
}

main
