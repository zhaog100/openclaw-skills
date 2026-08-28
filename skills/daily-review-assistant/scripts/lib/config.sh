# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/bin/bash
# =============================================================================
# 配置文件 (Config)
# =============================================================================
# 版本：v2.0
# 创建时间：2026-05-09
# 用途：加载和提供配置信息
# 许可证：MIT License
# 版权：Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_DIR="$SKILL_DIR/config"
LOGS_DIR="$SKILL_DIR/logs"

# 配置文件路径
CONFIG_FILE="$CONFIG_DIR/config.json"

# 默认配置值
DEFAULT_WORKSPACE="${OPENCLAW_WORKSPACE:-${HOME}/.openclaw/workspace}"
DEFAULT_MEMORY_DIR="$DEFAULT_WORKSPACE/memory"
DEFAULT_KNOWLEDGE_DIR="$DEFAULT_WORKSPACE/knowledge"

# 加载配置
load_config() {
    # 首先检查配置文件是否存在
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "⚠️ 警告：配置文件不存在，使用默认配置"
        use_default_config
        return 0
    fi
    
    # 使用 jq 解析 JSON 配置
    if command -v jq &> /dev/null; then
        CFG_VERSION=$(jq -r '.version' "$CONFIG_FILE" 2>/dev/null || echo "2.0")
        CFG_SKILL_NAME=$(jq -r '.skill_name' "$CONFIG_FILE" 2>/dev/null || echo "daily-review-assistant")
        CFG_WORKSPACE=$(jq -r '.workspace' "$CONFIG_FILE" 2>/dev/null || echo "$DEFAULT_WORKSPACE")
        CFG_MEMORY_DIR=$(jq -r '.memory_dir' "$CONFIG_FILE" 2>/dev/null || echo "$DEFAULT_MEMORY_DIR")
        CFG_KNOWLEDGE_DIR=$(jq -r '.knowledge_dir' "$CONFIG_FILE" 2>/dev/null || echo "$DEFAULT_KNOWLEDGE_DIR")
        CFG_MEMORY_FILE=$(jq -r '.files.memory' "$CONFIG_FILE" 2>/dev/null || echo "$DEFAULT_WORKSPACE/MEMORY.md")
        CFG_HEARTBEAT_FILE=$(jq -r '.files.heartbeat' "$CONFIG_FILE" 2>/dev/null || echo "$DEFAULT_WORKSPACE/HEARTBEAT.md")
        CFG_KNOWLEDGE_INDEX=$(jq -r '.files.knowledge_index' "$CONFIG_FILE" 2>/dev/null || echo "$DEFAULT_KNOWLEDGE_DIR/INDEX.md")
        CFG_GIT_BRANCH=$(jq -r '.git.branch' "$CONFIG_FILE" 2>/dev/null || echo "master")
        CFG_GIT_REMOTE=$(jq -r '.git.remote' "$CONFIG_FILE" 2>/dev/null || echo "origin")
        CFG_THRESHOLD_MEMORY_STALE=$(jq -r '.thresholds.memory_stale_hours' "$CONFIG_FILE" 2>/dev/null || echo "24")
        CFG_THRESHOLD_HEARTBEAT_STALE=$(jq -r '.thresholds.heartbeat_stale_hours' "$CONFIG_FILE" 2>/dev/null || echo "12")
        CFG_THRESHOLD_PR_STALE=$(jq -r '.thresholds.pr_stale_days' "$CONFIG_FILE" 2>/dev/null || echo "7")
        CFG_FEATURE_TASK_REVIEW=$(jq -r '.features.task_review' "$CONFIG_FILE" 2>/dev/null || echo "true")
        CFG_FEATURE_GIT_REVIEW=$(jq -r '.features.git_review' "$CONFIG_FILE" 2>/dev/null || echo "true")
        CFG_FEATURE_ISSUE_REVIEW=$(jq -r '.features.issue_review' "$CONFIG_FILE" 2>/dev/null || echo "true")
        CFG_FEATURE_LEARNING_REVIEW=$(jq -r '.features.learning_review' "$CONFIG_FILE" 2>/dev/null || echo "true")
        CFG_FEATURE_PR_MONITORING=$(jq -r '.features.pr_monitoring' "$CONFIG_FILE" 2>/dev/null || echo "true")
        CFG_FEATURE_FINANCIAL_TRACKING=$(jq -r '.features.financial_tracking' "$CONFIG_FILE" 2>/dev/null || echo "true")
        CFG_NOTIFY_QQBOT=$(jq -r '.notifications.qqbot_enabled' "$CONFIG_FILE" 2>/dev/null || echo "true")
        CFG_QQBOT_ID=$(jq -r '.notifications.qqbot_id' "$CONFIG_FILE" 2>/dev/null || echo "YOUR_QQBOT_CHANNEL_ID")
        CFG_CRON_MORNING=$(jq -r '.cron.morning' "$CONFIG_FILE" 2>/dev/null || echo "0 12 * * *")
        CFG_CRON_FULL=$(jq -r '.cron.evening' "$CONFIG_FILE" 2>/dev/null || echo "50 23 * * *")
        CFG_LOGS_DIR=$(jq -r '.logs.dir' "$CONFIG_FILE" 2>/dev/null || echo "$LOGS_DIR")
        CFG_LOG_LEVEL=$(jq -r '.logs.level' "$CONFIG_FILE" 2>/dev/null || echo "info")
    else
        echo "⚠️ 警告：未找到 jq 命令，使用默认配置"
        use_default_config
    fi
}

# 使用默认配置
use_default_config() {
    CFG_VERSION="2.0"
    CFG_SKILL_NAME="daily-review-assistant"
    CFG_WORKSPACE="$DEFAULT_WORKSPACE"
    CFG_MEMORY_DIR="$DEFAULT_MEMORY_DIR"
    CFG_KNOWLEDGE_DIR="$DEFAULT_KNOWLEDGE_DIR"
    CFG_MEMORY_FILE="$DEFAULT_WORKSPACE/MEMORY.md"
    CFG_HEARTBEAT_FILE="$DEFAULT_WORKSPACE/HEARTBEAT.md"
    CFG_KNOWLEDGE_INDEX="$DEFAULT_KNOWLEDGE_DIR/INDEX.md"
    CFG_GIT_BRANCH="master"
    CFG_GIT_REMOTE="origin"
    CFG_THRESHOLD_MEMORY_STALE=24
    CFG_THRESHOLD_HEARTBEAT_STALE=12
    CFG_THRESHOLD_PR_STALE=7
    CFG_FEATURE_TASK_REVIEW="true"
    CFG_FEATURE_GIT_REVIEW="true"
    CFG_FEATURE_ISSUE_REVIEW="true"
    CFG_FEATURE_LEARNING_REVIEW="true"
    CFG_FEATURE_PR_MONITORING="true"
    CFG_FEATURE_FINANCIAL_TRACKING="true"
    CFG_NOTIFY_QQBOT="true"
    CFG_QQBOT_ID="YOUR_QQBOT_CHANNEL_ID"
    CFG_CRON_MORNING="0 12 * * *"
    CFG_CRON_FULL="50 23 * * *"
    CFG_LOGS_DIR="$LOGS_DIR"
    CFG_LOG_LEVEL="info"
}

# 日志函数
log_info() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [INFO] $message" | tee -a "$_CURRENT_LOG_FILE" 2>/dev/null || echo "[$timestamp] [INFO] $message"
}

log_warn() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [WARN] $message" | tee -a "$_CURRENT_LOG_FILE" 2>/dev/null || echo "[$timestamp] [WARN] $message"
}

log_error() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [ERROR] $message" | tee -a "$_CURRENT_LOG_FILE" 2>/dev/null || echo "[$timestamp] [ERROR] $message"
}

log_debug() {
    local message="$1"
    if [ "$CFG_LOG_LEVEL" = "debug" ]; then
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$timestamp] [DEBUG] $message" | tee -a "$_CURRENT_LOG_FILE" 2>/dev/null || echo "[$timestamp] [DEBUG] $message"
    fi
}

# 初始化日志目录
init_logs() {
    if [ ! -d "$CFG_LOGS_DIR" ]; then
        mkdir -p "$CFG_LOGS_DIR"
        log_info "创建日志目录：$CFG_LOGS_DIR"
    fi
}

# 清理旧日志
cleanup_logs() {
    local retention_days=${1:-30}
    if [ -d "$CFG_LOGS_DIR" ]; then
        find "$CFG_LOGS_DIR" -name "*.log" -mtime +$retention_days -delete 2>/dev/null || true
        log_info "清理 $retention_days 天前的日志文件"
    fi
}

# 检查依赖
check_dependencies() {
    local missing_deps=0
    
    # 检查 jq
    if ! command -v jq &> /dev/null; then
        log_warn "未找到 jq 命令，配置解析将受限"
    fi
    
    # 检查 gh (GitHub CLI)
    if ! command -v gh &> /dev/null; then
        log_warn "未找到 gh 命令，PR检查将受限"
    fi
    
    # 检查 git
    if ! command -v git &> /dev/null; then
        log_error "未找到 git 命令，Git检查将无法进行"
        missing_deps=$((missing_deps + 1))
    fi
    
    return $missing_deps
}

# 验证配置
validate_config() {
    local errors=0
    
    # 检查工作区
    if [ ! -d "$CFG_WORKSPACE" ]; then
        log_error "工作区不存在：$CFG_WORKSPACE"
        errors=$((errors + 1))
    fi
    
    # 检查记忆目录
    if [ ! -d "$CFG_MEMORY_DIR" ]; then
        mkdir -p "$CFG_MEMORY_DIR" 2>/dev/null || log_warn "无法创建记忆目录：$CFG_MEMORY_DIR"
    fi
    
    # 检查知识库目录
    if [ ! -d "$CFG_KNOWLEDGE_DIR" ]; then
        mkdir -p "$CFG_KNOWLEDGE_DIR" 2>/dev/null || log_warn "无法创建知识库目录：$CFG_KNOWLEDGE_DIR"
    fi
    
    return $errors
}

# 主初始化函数
init() {
    load_config
    init_logs
    cleanup_logs
    check_dependencies || true
    
    if validate_config; then
        log_info "配置验证通过"
    else
        log_error "配置验证失败"
        return 1
    fi
    
    return 0
}

# 执行初始化
init