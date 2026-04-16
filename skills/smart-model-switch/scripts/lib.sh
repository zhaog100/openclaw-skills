#!/bin/bash
# 共享配置加载器
# 所有脚本 source 此文件以获取统一配置
# 环境变量优先级高于 config.json

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="${SMART_MODEL_SWITCH_CONFIG:-$SKILL_DIR/config.json}"

# 从 config.json 读取值，支持环境变量覆盖
# 用法: cfg <jq_filter> [env_var_name]
# 如果 env_var_name 对应的环境变量存在则返回它，否则从 config.json 读取
cfg() {
    local filter="$1"
    local env_name="${2:-}"
    
    if [ -n "$env_name" ] && [ -n "${!env_name}" ]; then
        echo "${!env_name}"
        return
    fi
    
    jq -r "$filter" "$CONFIG_FILE" 2>/dev/null
}

# 路径解析：将 ~ 展开为 $HOME，支持相对路径（相对 SKILL_DIR）
resolve_path() {
    local p="$1"
    # 展开波浪号
    p="${p/#\~/$HOME}"
    # 如果是相对路径，基于 SKILL_DIR
    if [[ "$p" != /* ]]; then
        echo "$SKILL_DIR/$p"
    else
        echo "$p"
    fi
}

# 常用路径（带环境变量覆盖）
DATA_DIR="${SMART_MODEL_SWITCH_DATA_DIR:-$(resolve_path "$(cfg '.paths.data_dir' 'SMART_MODEL_SWITCH_DATA_DIR')")}"
LOG_DIR="${SMART_MODEL_SWITCH_LOG_DIR:-$(resolve_path "$(cfg '.paths.log_dir' 'SMART_MODEL_SWITCH_LOG_DIR')")}"
OPENCLAW_CONFIG_FILE="${OPENCLAW_CONFIG:-$(resolve_path "$(cfg '.paths.openclaw_config')")}"
OPENCLAW_STATUS_FILE="${OPENCLAW_STATUS:-$(resolve_path "$(cfg '.paths.openclaw_status')")}"
MODEL_SWITCH_REQ_DIR="${SMART_MODEL_SWITCH_REQ_DIR:-$(resolve_path "$(cfg '.paths.model_switch_requests')")}"

mkdir -p "$DATA_DIR" "$LOG_DIR" 2>/dev/null
