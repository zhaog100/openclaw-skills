#!/bin/bash
# =============================================================================
# 配置加载器 (Config Loader)
# =============================================================================
# 所有脚本共享的配置加载逻辑
# 优先级：环境变量 > config.json > 默认值
# =============================================================================

# 技能根目录（从调用者的 SCRIPT_DIR 上一级）
if [ -z "$_SKILL_ROOT" ]; then
  # 如果从 scripts/ 下调用，SCRIPT_DIR 指向 scripts/
  _SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[1]:-${BASH_SOURCE[0]}}")/.." && pwd)"
fi

# 定位 config.json（优先技能根目录下的 config/）
_CONFIG_FILE="${DAILY_REVIEW_CONFIG:-$_SKILL_ROOT/config/config.json}"
if [ ! -f "$_CONFIG_FILE" ]; then
  _CONFIG_FILE="$_SKILL_ROOT/config/config.example.json"
fi

# 加载配置（使用 jq，无 jq 则用 grep 简单解析）
_load_config() {
  if command -v jq &>/dev/null && [ -f "$_CONFIG_FILE" ]; then
    CFG_WORKSPACE="${WORKSPACE:-$(jq -r '.workspace // empty' "$_CONFIG_FILE" 2>/dev/null)}"
    CFG_VERSION="$(jq -r '.version // "1.0.0"' "$_CONFIG_FILE" 2>/dev/null)"
    CFG_CRON_ID="$(jq -r '.cronIdentifier // "daily-review-helper"' "$_CONFIG_FILE" 2>/dev/null)"
    CFG_REVIEW_MORNING="$(jq -r '.reviewTimes[0] // "12:00"' "$_CONFIG_FILE" 2>/dev/null)"
    CFG_REVIEW_EVENING="$(jq -r '.reviewTimes[1] // "23:50"' "$_CONFIG_FILE" 2>/dev/null)"
    # Features
    CFG_F_TASK="$(jq -r '.features.taskReview // true' "$_CONFIG_FILE" 2>/dev/null)"
    CFG_F_GIT="$(jq -r '.features.gitReview // true' "$_CONFIG_FILE" 2>/dev/null)"
    CFG_F_ISSUE="$(jq -r '.features.issueReview // true' "$_CONFIG_FILE" 2>/dev/null)"
    CFG_F_LEARN="$(jq -r '.features.learningReview // true' "$_CONFIG_FILE" 2>/dev/null)"
    CFG_F_GAP="$(jq -r '.features.gapAnalysis // true' "$_CONFIG_FILE" 2>/dev/null)"
    CFG_F_MEMORY="$(jq -r '.features.memoryUpdate // true' "$_CONFIG_FILE" 2>/dev/null)"
    CFG_F_KNOWLEDGE="$(jq -r '.features.knowledgeUpdate // true' "$_CONFIG_FILE" 2>/dev/null)"
    CFG_F_GITCOMMIT="$(jq -r '.features.gitAutoCommit // true' "$_CONFIG_FILE" 2>/dev/null)"
  else
    # Fallback defaults
    CFG_VERSION="${CFG_VERSION:-1.0.0}"
    CFG_CRON_ID="${CFG_CRON_ID:-daily-review-helper}"
    CFG_REVIEW_MORNING="${CFG_REVIEW_MORNING:-12:00}"
    CFG_REVIEW_EVENING="${CFG_REVIEW_EVENING:-23:50}"
    CFG_F_TASK="${CFG_F_TASK:-true}"
    CFG_F_GIT="${CFG_F_GIT:-true}"
    CFG_F_ISSUE="${CFG_F_ISSUE:-true}"
    CFG_F_LEARN="${CFG_F_LEARN:-true}"
    CFG_F_GAP="${CFG_F_GAP:-true}"
    CFG_F_MEMORY="${CFG_F_MEMORY:-true}"
    CFG_F_KNOWLEDGE="${CFG_F_KNOWLEDGE:-true}"
    CFG_F_GITCOMMIT="${CFG_F_GITCOMMIT:-true}"
  fi

  # WORKSPACE: 环境变量 > config.json > 自动检测
  if [ -z "$CFG_WORKSPACE" ]; then
    # 向上查找包含 MEMORY.md 的目录（OpenClaw workspace 特征）
    local _dir="$_SKILL_ROOT"
    while [ "$_dir" != "/" ]; do
      if [ -f "$_dir/MEMORY.md" ] || [ -f "$_dir/AGENTS.md" ]; then
        CFG_WORKSPACE="$_dir"
        break
      fi
      _dir="$(dirname "$_dir")"
    done
  fi
  if [ -z "$CFG_WORKSPACE" ]; then
    CFG_WORKSPACE="$(pwd)"
  fi
}

_load_config

# 导出常用路径
export _SKILL_ROOT
export CFG_WORKSPACE
export MEMORY_DIR="$CFG_WORKSPACE/memory"
export KNOWLEDGE_DIR="$CFG_WORKSPACE/knowledge"
export MEMORY_FILE="$CFG_WORKSPACE/MEMORY.md"
export LOG_DIR="$_SKILL_ROOT/logs"
export SCRIPTS_DIR="$_SKILL_ROOT/scripts"

# 确保目录存在
mkdir -p "$LOG_DIR" 2>/dev/null
