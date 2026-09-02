# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/bin/bash
# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 错误重试与 Fallback 机制
# 版本：v2.0.0
# 创建时间：2026-04-14
# 功能：捕获模型 API 错误，自动按 fallback chain 重试下一个模型

source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

FALLBACK_STATE="$DATA_DIR/fallback-state.json"
FALLBACK_LOG="$LOG_DIR/fallback.log"

# 日志
log_fallback() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$FALLBACK_LOG"
}

# 初始化状态文件
init_fallback_state() {
    if [ ! -f "$FALLBACK_STATE" ]; then
        cat > "$FALLBACK_STATE" << 'STATEEOF'
{
  "current_model": null,
  "fallback_active": false,
  "original_model": null,
  "error_count": 0,
  "last_error": null,
  "last_fallback": null,
  "error_history": [],
  "model_errors": {}
}
STATEEOF
        log_fallback "初始化 fallback 状态文件"
    fi
}

# 检查错误模式匹配
is_known_error() {
    local error_text="$1"
    local patterns
    patterns=$(jq -r '.fallback.error_patterns[]' "$CONFIG_FILE" 2>/dev/null)
    
    if [ -z "$patterns" ]; then
        # 默认错误模式
        patterns="Something went wrong
timeout
rate_limit
overloaded
500
502
503
429"
    fi
    
    while IFS= read -r pattern; do
        if echo "$error_text" | grep -qi "$pattern"; then
            return 0
        fi
    done <<< "$patterns"
    
    return 1
}

# 获取 fallback chain
get_fallback_chain() {
    local current_model="$1"
    local chain
    chain=$(jq -r --arg model "$current_model" '.fallback.chains[$model] // [] | .[]' "$CONFIG_FILE" 2>/dev/null)
    
    if [ -n "$chain" ]; then
        echo "$chain"
        return 0
    fi

    # 默认 fallback: agnes-2.0-flash
    if [ "$current_model" = "agnes/agnes-2.0-flash" ]; then
        printf 'agnes/agnes-2.0-flash\nagnes/agnes-2.0-flash\nagnes-2.0-flash\n'
    elif [ "$current_model" = "agnes/agnes-2.0-flash" ]; then
        printf 'agnes/agnes-2.0-flash\nagnes-2.0-flash\nagnes/agnes-2.0-flash\n'
    elif [ "$current_model" = "agnes/agnes-2.0-flash" ]; then
        printf 'agnes-2.0-flash\nagnes/agnes-2.0-flash\nagnes/agnes-2.0-flash\n'
    else
        printf 'agnes/agnes-2.0-flash\nagnes/agnes-2.0-flash\nagnes-2.0-flash\n'
    fi
}

# 检查模型是否在冷却期（错误太多）
is_model_cooled_down() {
    local model="$1"
    local last_error
    last_error=$(jq -r --arg m "$model" '.model_errors[$m].last_error // empty' "$FALLBACK_STATE" 2>/dev/null)
    
    if [ -z "$last_error" ]; then
        return 0  # 没有错误记录，可用
    fi
    
    local cooldown_seconds
    cooldown_seconds=$(jq -r '.fallback.cooldown.model_cooldown_seconds // 600' "$CONFIG_FILE" 2>/dev/null)
    
    local now=$(date +%s)
    local error_ts=$(date -d "$last_error" +%s 2>/dev/null || echo 0)
    local elapsed=$((now - error_ts))
    
    if [ "$elapsed" -lt "$cooldown_seconds" ]; then
        log_fallback "⏸️ 模型 $model 在冷却期（${elapsed}s < ${cooldown_seconds}s）"
        return 1
    fi
    
    return 0
}

# 记录模型错误
record_model_error() {
    local model="$1"
    local error_msg="$2"
    
    local temp=$(mktemp)
    jq --arg model "$model" \
       --arg error "$error_msg" \
       --arg now "$(date -Iseconds)" \
       '(.model_errors[$model].count //= 0) |
        (.model_errors[$model].count += 1) |
        (.model_errors[$model].last_error = $now) |
        (.model_errors[$model].last_error_msg = $error) |
        (.error_count += 1) |
        (.last_error = $now) |
        (.error_history += [{"model": $model, "error": $error, "time": $now}]) |
        (.error_history |= .[-20:])' \
       "$FALLBACK_STATE" > "$temp"
    mv "$temp" "$FALLBACK_STATE"
    
    log_fallback "❌ 模型 $model 错误: $error_msg"
}

# 选择下一个可用模型
select_fallback_model() {
    local current_model="$1"
    local chain
    chain=$(get_fallback_chain "$current_model")
    
    while IFS= read -r candidate; do
        [ -z "$candidate" ] && continue
        if is_model_cooled_down "$candidate"; then
            echo "$candidate"
            return 0
        fi
    done <<< "$chain"
    
    # 所有 fallback 都不可用，尝试健康检查
    log_fallback "⚠️ 所有 fallback 模型都在冷却期，尝试负载均衡器"
    local best
    best=$("$SCRIPT_DIR/load-balancer.sh" get-best 2>/dev/null)
    if [ -n "$best" ] && [ "$best" != "main" ]; then
        echo "$best"
        return 0
    fi
    
    # 最终兜底
    echo "agnes/agnes-2.0-flash"
    return 0
}

# 执行 fallback 切换
do_fallback() {
    local failed_model="$1"
    local error_msg="$2"
    
    local enabled
    enabled=$(jq -r '.fallback.enabled // true' "$CONFIG_FILE" 2>/dev/null)
    if [ "$enabled" != "true" ]; then
        log_fallback "⏸️ Fallback 已禁用"
        return 1
    fi
    
    record_model_error "$failed_model" "$error_msg"
    
    local next_model
    next_model=$(select_fallback_model "$failed_model")
    
    log_fallback "🔄 Fallback: $failed_model → $next_model"
    
    # 更新状态
    local temp=$(mktemp)
    jq --arg original "$failed_model" \
       --arg current "$next_model" \
       --arg now "$(date -Iseconds)" \
       '(.original_model //= $original) |
        (.current_model = $current) |
        (.fallback_active = true) |
        (.last_fallback = $now)' \
       "$FALLBACK_STATE" > "$temp"
    mv "$temp" "$FALLBACK_STATE"
    
    # 执行模型切换
    "$SCRIPT_DIR/switch-model.sh" "$next_model" >> "$FALLBACK_LOG" 2>&1
    
    echo "$next_model"
    return 0
}

# 重置 fallback 状态（恢复正常后调用）
reset_fallback() {
    local temp=$(mktemp)
    jq '(.fallback_active = false) |
        (.current_model = null) |
        (.original_model = null)' \
       "$FALLBACK_STATE" > "$temp"
    mv "$temp" "$FALLBACK_STATE"
    log_fallback "✅ Fallback 状态已重置"
}

# 获取当前状态摘要
get_status() {
    local active
    active=$(jq -r '.fallback_active // false' "$FALLBACK_STATE" 2>/dev/null)
    local error_count
    error_count=$(jq -r '.error_count // 0' "$FALLBACK_STATE" 2>/dev/null)
    local current
    current=$(jq -r '.current_model // "none"' "$FALLBACK_STATE" 2>/dev/null)
    local original
    original=$(jq -r '.original_model // "none"' "$FALLBACK_STATE" 2>/dev/null)
    
    echo "╔════════════════════════════════════════╗"
    echo "║     Fallback 状态                      ║"
    echo "╠════════════════════════════════════════╣"
    echo "║ 激活: $active"
    echo "║ 原始模型: $original"
    echo "║ 当前模型: $current"
    echo "║ 累计错误: $error_count"
    echo "╚════════════════════════════════════════╝"
}

# CLI
case "${1:-}" in
    check)
        # 检查是否需要 fallback（传入错误信息和当前模型）
        init_fallback_state
        ERROR_MSG="${2:-}"
        CURRENT_MODEL="${3:-$(jq -r '.current_model // "agnes-2.0-flash"' "$FALLBACK_STATE" 2>/dev/null)}"
        
        if is_known_error "$ERROR_MSG"; then
            NEXT=$(do_fallback "$CURRENT_MODEL" "$ERROR_MSG")
            echo "🔄 已切换到: $NEXT"
        else
            echo "ℹ️ 非已知错误模式，跳过 fallback"
        fi
        ;;
    status)
        init_fallback_state
        get_status
        ;;
    reset)
        init_fallback_state
        reset_fallback
        echo "✅ Fallback 已重置"
        ;;
    chain)
        # 查看指定模型的 fallback chain
        MODEL="${2:-agnes-2.0-flash}"
        echo "📋 $MODEL 的 fallback chain:"
        get_fallback_chain "$MODEL" | while IFS= read -r m; do
            echo "  → $m"
        done
        ;;
    *)
        echo "用法: error-retry.sh <command> [args]"
        echo ""
        echo "命令:"
        echo "  check <error_msg> [current_model]  # 检查错误并触发 fallback"
        echo "  status                             # 查看 fallback 状态"
        echo "  reset                              # 重置 fallback 状态"
        echo "  chain [model]                      # 查看模型的 fallback chain"
        echo ""
        echo "AI 集成方式:"
        echo "  当检测到 'Something went wrong' 等错误时，AI 自动调用："
        echo "  scripts/error-retry.sh check \"\$ERROR_MSG\" \"\$CURRENT_MODEL\""
        ;;
esac
