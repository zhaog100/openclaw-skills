#!/bin/bash
# =============================================================================
# 配置加载器 (Config Loader)
# =============================================================================
# 从 config/config.json 加载配置，环境变量优先
# 所有脚本 source 此文件获取配置
# =============================================================================

# 确定 SKILL_DIR（skill.sh 所在目录）
if [ -n "$SKILL_DIR" ]; then
    _SKILL_DIR="$SKILL_DIR"
elif [ -n "$SCRIPT_DIR" ]; then
    # 从 scripts/ 子目录推断
    _SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
else
    _SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

# 配置文件路径
CONFIG_FILE="${CONFIG_FILE:-$_SKILL_DIR/config/config.json}"

# 如果配置文件不存在，从 example 复制
if [ ! -f "$CONFIG_FILE" ]; then
    local_example="$_SKILL_DIR/config/config.example.json"
    if [ -f "$local_example" ]; then
        cp "$local_example" "$CONFIG_FILE"
    fi
fi

# JSON 解析辅助函数（兼容无 jq 环境）
_json_get() {
    local key="$1"
    local default="${2:-}"
    local file="$CONFIG_FILE"
    
    if [ ! -f "$file" ]; then
        echo "$default"
        return
    fi
    
    if command -v jq &>/dev/null; then
        local val
        val=$(jq -r ".$key // empty" "$file" 2>/dev/null)
        echo "${val:-$default}"
    else
        # 简单 grep 解析
        local val
        val=$(grep -o "\"$key\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" "$file" 2>/dev/null | sed 's/.*:.*"\([^"]*\)".*/\1/' | head -1)
        echo "${val:-$default}"
    fi
}

_json_get_bool() {
    local key="$1"
    local default="${2:-true}"
    local val
    val=$(_json_get "$key" "")
    case "$val" in
        false|0|no) echo "false" ;;
        true|1|yes|"") echo "$default" ;;
        *) echo "$default" ;;
    esac
}

_json_get_number() {
    local key="$1"
    local default="${2:-0}"
    local val
    val=$(_json_get "$key" "")
    echo "${val:-$default}"
}

# =============================================================================
# 加载配置（环境变量优先）
# =============================================================================

# Workspace
CFG_WORKSPACE="${WORKSPACE:-$(_json_get "workspace" "")}"
if [ "$CFG_WORKSPACE" = "auto" ] || [ -z "$CFG_WORKSPACE" ]; then
    CFG_WORKSPACE="$(cd "$_SKILL_DIR/../../.." && pwd)"
fi

# 路径
CFG_MEMORY_DIR="${MEMORY_DIR:-$(_json_get "paths.memoryDir" "memory")}"
CFG_KNOWLEDGE_DIR="${KNOWLEDGE_DIR:-$(_json_get "paths.knowledgeDir" "knowledge")}"
CFG_LOGS_DIR="${LOGS_DIR:-$(_json_get "paths.logsDir" "logs")}"
CFG_MEMORY_FILE="${MEMORY_FILE:-$(_json_get "paths.memoryFile" "MEMORY.md")}"
CFG_HEARTBEAT_FILE="${HEARTBEAT_FILE:-$(_json_get "paths.heartbeatFile" "HEARTBEAT.md")}"
CFG_KNOWLEDGE_INDEX="${KNOWLEDGE_INDEX:-$(_json_get "paths.knowledgeIndex" "KNOWLEDGE-INDEX.md")}"

# 解析为绝对路径
CFG_MEMORY_DIR="$CFG_WORKSPACE/$CFG_MEMORY_DIR"
CFG_KNOWLEDGE_DIR="$CFG_WORKSPACE/$CFG_KNOWLEDGE_DIR"
CFG_LOGS_DIR="$_SKILL_DIR/$CFG_LOGS_DIR"
CFG_MEMORY_FILE="$CFG_WORKSPACE/$CFG_MEMORY_FILE"
CFG_HEARTBEAT_FILE="$CFG_WORKSPACE/$CFG_HEARTBEAT_FILE"
CFG_KNOWLEDGE_INDEX="$CFG_KNOWLEDGE_DIR/$CFG_KNOWLEDGE_INDEX"

# 定时任务
CFG_CRON_MORNING="${CRON_MORNING:-$(_json_get "reviewTimes.morning" "0 12 * * *")}"
CFG_CRON_FULL="${CRON_FULL:-$(_json_get "reviewTimes.full" "50 23 * * *")}"

# Git 配置
CFG_GIT_BRANCH="${GIT_BRANCH:-$(_json_get "git.remoteBranch" "master")}"
CFG_GIT_AUTOCOMMIT="${GIT_AUTOCOMMIT:-$(_json_get_bool "git.autoCommit" "true")}"
CFG_GIT_AUTOPUSH="${GIT_AUTOPUSH:-$(_json_get_bool "git.autoPush" "true")}"
CFG_GIT_COMMIT_PREFIX="${GIT_COMMIT_PREFIX:-$(_json_get "git.commitMessagePrefix" "chore(daily)")}"

# 功能开关
CFG_FEATURE_TASK_REVIEW="${FEATURE_TASK_REVIEW:-$(_json_get_bool "features.taskReview" "true")}"
CFG_FEATURE_GIT_REVIEW="${FEATURE_GIT_REVIEW:-$(_json_get_bool "features.gitReview" "true")}"
CFG_FEATURE_ISSUE_REVIEW="${FEATURE_ISSUE_REVIEW:-$(_json_get_bool "features.issueReview" "true")}"
CFG_FEATURE_LEARNING_REVIEW="${FEATURE_LEARNING_REVIEW:-$(_json_get_bool "features.learningReview" "true")}"
CFG_FEATURE_GAP_ANALYSIS="${FEATURE_GAP_ANALYSIS:-$(_json_get_bool "features.gapAnalysis" "true")}"
CFG_FEATURE_MEMORY_UPDATE="${FEATURE_MEMORY_UPDATE:-$(_json_get_bool "features.memoryUpdate" "true")}"
CFG_FEATURE_KNOWLEDGE_UPDATE="${FEATURE_KNOWLEDGE_UPDATE:-$(_json_get_bool "features.knowledgeUpdate" "true")}"

# 阈值
CFG_THRESHOLD_MEMORY_STALE="${THRESHOLD_MEMORY_STALE:-$(_json_get_number "thresholds.memoryStaleHours" "24")}"
CFG_THRESHOLD_HEARTBEAT_STALE="${THRESHOLD_HEARTBEAT_STALE:-$(_json_get_number "thresholds.heartbeatStaleHours" "12")}"

# 日志函数（统一）
_COLOR_RED='\033[0;31m'
_COLOR_GREEN='\033[0;32m'
_COLOR_YELLOW='\033[1;33m'
_COLOR_BLUE='\033[0;34m'
_COLOR_NC='\033[0m'

log_info() {
    echo -e "${_COLOR_GREEN}[INFO]${_COLOR_NC} $1" | tee -a "${_CURRENT_LOG_FILE:-/dev/null}"
}

log_warn() {
    echo -e "${_COLOR_YELLOW}[WARN]${_COLOR_NC} $1" | tee -a "${_CURRENT_LOG_FILE:-/dev/null}" >&2
}

log_error() {
    echo -e "${_COLOR_RED}[ERROR]${_COLOR_NC} $1" | tee -a "${_CURRENT_LOG_FILE:-/dev/null}" >&2
}

# 确保目录存在
mkdir -p "$CFG_LOGS_DIR"
mkdir -p "$CFG_MEMORY_DIR"
