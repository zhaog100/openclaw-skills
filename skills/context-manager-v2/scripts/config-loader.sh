#!/bin/bash
# config-loader.sh - 从 config.json 加载配置（环境变量优先）
# 用法: source "$SKILL_DIR/scripts/config-loader.sh"

CONFIG_LOADER_VERSION="1.0.0"

# 获取技能目录（相对于脚本位置）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_DIR="$(cd "$SKILL_DIR/../.." && pwd)"

# 配置文件路径
CONFIG_FILE="$SKILL_DIR/config.json"

# 读取 JSON 配置值（需要 jq）
config_get() {
    local key="$1"
    local default="${2:-}"
    jq -r ".$key // empty" "$CONFIG_FILE" 2>/dev/null || echo "$default"
}

# 获取配置值：环境变量 > config.json > 默认值
cfg() {
    local key="$1"
    local env_var="$2"
    local default="${3:-}"

    # 1. 环境变量优先
    if [ -n "${!env_var:-}" ]; then
        echo "${!env_var}"
        return
    fi

    # 2. config.json
    local value
    value=$(config_get "$key")
    if [ -n "$value" ]; then
        echo "$value"
        return
    fi

    # 3. 默认值
    echo "$default"
}

# ===== 加载所有配置 =====

# 阈值
THRESHOLD=$(cfg 'thresholds.dialog' CTX_THRESHOLD 60)
STARTUP_THRESHOLD=$(cfg 'thresholds.startup_warning' CTX_STARTUP_THRESHOLD 30)
ERROR_THRESHOLD=$(cfg 'thresholds.error_per_hour' CTX_ERROR_THRESHOLD 5)

# 监控
ACTIVE_SESSION_WINDOW=$(cfg 'monitor.active_session_window_minutes' CTX_ACTIVE_WINDOW 120)
MAX_RETRIES=$(cfg 'monitor.max_retries' CTX_MAX_RETRIES 3)
RETRY_DELAY=$(cfg 'monitor.retry_delay_seconds' CTX_RETRY_DELAY 5)
API_TIMEOUT=$(cfg 'monitor.api_timeout_seconds' CTX_API_TIMEOUT 30)

# 通知
NOTIFICATION_COOLDOWN=$(cfg 'notifications.cooldown_seconds' CTX_COOLDOWN 3600)
FEISHU_CHANNEL=$(cfg 'notifications.feishu_channel' CTX_FEISHU_CHANNEL "feishu")
FEISHU_ACCOUNT=$(cfg 'notifications.feishu_account' CTX_FEISHU_ACCOUNT "main")
FEISHU_TARGET=your_feishu_target
QQ_TARGET=your_qq_target

# 路径（相对于 workspace）
LOG_DIR="$WORKSPACE_DIR/$(cfg 'paths.log_dir' CTX_LOG_DIR 'logs')"
MONITOR_LOG="$WORKSPACE_DIR/$(cfg 'paths.monitor_log' CTX_MONITOR_LOG 'logs/context-monitor.log')"
ERROR_LOG="$WORKSPACE_DIR/$(cfg 'paths.error_log' CTX_ERROR_LOG 'logs/context-errors.log')"
SWITCH_LOG="$WORKSPACE_DIR/$(cfg 'paths.switch_log' CTX_SWITCH_LOG 'logs/seamless-switch.log')"
ERROR_STATS="$WORKSPACE_DIR/$(cfg 'paths.error_stats' CTX_ERROR_STATS 'logs/context-error-stats.txt')"
MEMORY_FILE="$WORKSPACE_DIR/$(cfg 'paths.memory_file' CTX_MEMORY_FILE 'MEMORY.md')"
DAILY_LOG_DIR="$WORKSPACE_DIR/$(cfg 'paths.daily_log_dir' CTX_DAILY_LOG_DIR 'memory')"

# 临时文件
COOLDOWN_FILE=$(cfg 'tmp.cooldown_file' CTX_COOLDOWN_FILE '/tmp/context-notification-cooldown')
ERROR_COUNT_PREFIX=$(cfg 'tmp.error_count_prefix' CTX_ERROR_COUNT_PREFIX '/tmp/context-error-count_')

# 工具脚本
ERROR_HANDLER="$SKILL_DIR/$(cfg 'paths.utils_error_handler' CTX_ERROR_HANDLER '../utils/error-handler.sh')"

# 确保日志目录存在
mkdir -p "$LOG_DIR"
