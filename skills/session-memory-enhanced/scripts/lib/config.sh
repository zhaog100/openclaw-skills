#!/bin/bash
# config.sh - 统一配置加载库
# 环境变量 > config.json > 默认值
# 用法: source "$SKILL_DIR/scripts/lib/config.sh"

# SKILL_DIR 检测（兼容软链接）
if [ -z "$SKILL_DIR" ]; then
  SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
fi

CONFIG_FILE="$SKILL_DIR/config.json"

# ── 加载 JSON 配置（带 fallback）──────────────────────────
_load_json() {
  local path="${1:-$CONFIG_FILE}"
  if [ -f "$path" ] && command -v jq &>/dev/null; then
    cat "$path"
  fi
}

_cfg() {
  # $1=jq path, $2=default, $3=env var name (optional, overrides config)
  local env_val=""
  if [ -n "${3:-}" ]; then
    env_val="${!3}"
  fi
  if [ -n "$env_val" ]; then
    echo "$env_val"
    return
  fi
  local json_val
  json_val=$(_load_json | jq -r "${1} // empty" 2>/dev/null)
  if [ -n "$json_val" ] && [ "$json_val" != "null" ]; then
    echo "$json_val"
  else
    echo "${2}"
  fi
}

_cfg_bool() {
  local val
  val=$(_cfg "$1" "$2" "${3:-}")
  case "$val" in
    true|1|yes) echo "true" ;;
    false|0|no) echo "false" ;;
    *) echo "${2:-false}" ;;
  esac
}

# ── 导出公共变量 ──────────────────────────────────────────
WORKSPACE="${WORKSPACE:-$(pwd)}"
AGENT_NAME="${AGENT_NAME:-main}"

MEMORY_DIR="$WORKSPACE/memory/agents/$AGENT_NAME"
SHARED_DIR="$WORKSPACE/memory/shared"
LOG_DIR="$WORKSPACE/logs"
LOG_FILE="$LOG_DIR/session-memory-enhanced.log"
TAIL_FILE="$MEMORY_DIR/.tail.tmp.json"

PYTHON_DIR="$SKILL_DIR/python"

# 核心配置
FLUSH_IDLE_SECONDS=$(_cfg '.flushIdleSeconds' 1800)
MAX_MESSAGES_PER_PART=$(_cfg '.maxMessagesPerPart' 60)

# 功能开关
ENABLE_STRUCTURED_EXTRACTION=$(_cfg_bool '.features.structuredExtraction' false)
ENABLE_VECTOR_SEARCH=$(_cfg_bool '.features.vectorSearch' false)
ENABLE_AI_SUMMARY=$(_cfg_bool '.features.aiSummary' true)
ENABLE_GIT_BACKUP=$(_cfg_bool '.features.gitBackup' true)
ENABLE_QMD_UPDATE=$(_cfg_bool '.features.qmdUpdate' true)

# Python 配置
PYTHON_ENABLED=$(_cfg_bool '.python.enabled' false)

# 搜索配置
SEARCH_STRATEGY=$(_cfg '.search.strategy' 'hybrid')
SEARCH_THRESHOLD=$(_cfg '.search.threshold' 0.7)
SEARCH_TOP_K=$(_cfg '.search.topK' 5)

# Watcher 配置
DEBOUNCE_SECONDS=$(_cfg '.watcher.debounceSeconds' 20)
POLLING_INTERVAL=$(_cfg '.watcher.pollingIntervalSeconds' 300)

# Sanitizer 配置
MAX_CONTENT_LENGTH=$(_cfg '.sanitizer.maxContentLength' 1000)

# 敏感配置：只从环境变量读取
OPENAI_API_KEY="${OPENAI_API_KEY:-}"

# Agent 级别覆写
AGENT_FLUSH=$(_load_json | jq -r ".agents.${AGENT_NAME}.flushIdleSeconds // empty" 2>/dev/null)
AGENT_MAX=$(_load_json | jq -r ".agents.${AGENT_NAME}.maxMessagesPerPart // empty" 2>/dev/null)
[ -n "$AGENT_FLUSH" ] && FLUSH_IDLE_SECONDS="$AGENT_FLUSH"
[ -n "$AGENT_MAX" ] && MAX_MESSAGES_PER_PART="$AGENT_MAX"

# ── 确保目录存在 ──────────────────────────────────────────
mkdir -p "$MEMORY_DIR" "$SHARED_DIR" "$LOG_DIR"

# ── 日志函数（集成 Error Handler）─────────────────────────
if [ -f "$WORKSPACE/skills/utils/error-handler.sh" ]; then
  ERROR_HANDLER_LOG="$LOG_FILE"
  source "$WORKSPACE/skills/utils/error-handler.sh"
  log() {
    local level="${2:-INFO}"
    case "$level" in
      INFO)  log_info "$1" ;;
      WARN)  log_warn "$1" ;;
      ERROR) log_error "$1" ;;
      DEBUG) log_debug "$1" ;;
    esac
  }
else
  log() {
    local level="${2:-INFO}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] [$AGENT_NAME] $1" >> "$LOG_FILE"
  }
fi
