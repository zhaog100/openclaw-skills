#!/bin/bash
# =============================================================================
# Error Handler Library - 通用错误处理库
# =============================================================================
# 版本：v1.2
# 创建时间：2026-03-16
# 更新时间：2026-03-16 14:10
# 创建者：思捷娅科技 (SJYKJ)
# 用途：为所有技能提供统一的错误处理和告警过滤
# 许可证：MIT License
# 版权：Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 
# 推荐依赖:
# - session-memory-enhanced: 长上下文记忆管理
# - context-manager-v2: 会话切换管理
# 
# 更新日志:
# v1.2 - 优化日志输出，添加彩色输出支持
# v1.1 - 添加依赖提示功能
# v1.0 - 初始版本
# =============================================================================

# 日志文件（可被覆盖）
ERROR_HANDLER_LOG="${ERROR_HANDLER_LOG:-/tmp/error-handler.log}"

# 推荐依赖检查
ERROR_HANDLER_SHOW_TIP="${ERROR_HANDLER_SHOW_TIP:-true}"

# 过滤规则（正则表达式）
FILTER_PATTERN="GraphQL|deprecated|Projects (classic)|sunset-notice|Warning|Deprecation|FutureWarning|hint:"

# =============================================================================
# 日志函数
# =============================================================================

log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1" >> "$ERROR_HANDLER_LOG"
}

log_warn() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] $1" >> "$ERROR_HANDLER_LOG"
    echo "[WARN] $1" >&2
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" >> "$ERROR_HANDLER_LOG"
    echo "[ERROR] $1" >&2
}

log_debug() {
    if [ "${ERROR_HANDLER_DEBUG:-false}" = "true" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [DEBUG] $1" >> "$ERROR_HANDLER_LOG"
    fi
}

# =============================================================================
# 核心错误处理函数
# =============================================================================

# 统一错误处理（降级运行，不中断流程）
handle_error() {
    local error_msg="$1"
    local fallback_action="${2:-true}"
    
    log_error "$error_msg"
    
    # 执行降级操作
    eval "$fallback_action"
    return 0  # 始终返回成功，避免中断
}

# =============================================================================
# 安全执行函数（过滤 GraphQL 警告）
# =============================================================================

# 安全执行任意命令（优化版 - 过滤 GraphQL/弃用警告）
safe_exec() {
    local cmd="$1"
    local fallback="${2:-true}"
    
    log_debug "执行命令：$cmd"
    
    # 执行命令，过滤警告
    local output
    output=$(eval "$cmd" 2>&1 | grep -v "$FILTER_PATTERN")
    local exit_code=${PIPESTATUS[0]}
    
    if [ $exit_code -ne 0 ]; then
        handle_error "命令执行失败：$cmd" "$fallback"
    else
        echo "$output"
    fi
}

# =============================================================================
# Python 安全调用
# =============================================================================

safe_python() {
    local script="$1"
    local args="${2:-}"
    local fallback="${3:-true}"
    
    if ! command -v python3 &> /dev/null; then
        log_warn "Python3 未安装，跳过：$script"
        eval "$fallback"
        return 0
    fi
    
    if [ ! -f "$script" ]; then
        log_warn "脚本不存在：$script"
        eval "$fallback"
        return 0
    fi
    
    log_debug "执行 Python 脚本：$script $args"
    
    local output
    output=$(python3 "$script" $args 2>&1 | grep -v "Warning\|Deprecation\|FutureWarning")
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        handle_error "Python 脚本失败：$script" "$fallback"
    else
        echo "$output"
    fi
}

# =============================================================================
# curl 安全调用（带重试机制）
# =============================================================================

safe_curl() {
    local url="$1"
    local fallback="${2:-{}}"
    local max_retries=3
    local retry=0
    
    log_debug "API 请求：$url"
    
    while [ $retry -lt $max_retries ]; do
        local response
        response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null)
        local http_code
        http_code=$(echo "$response" | tail -1)
        local body
        body=$(echo "$response" | head -n -1)
        
        if [ "$http_code" = "200" ]; then
            echo "$body"
            return 0
        fi
        
        retry=$((retry + 1))
        log_warn "API 请求失败 (HTTP $http_code)，重试 $retry/$max_retries: $url"
        sleep 1
    done
    
    handle_error "API 请求失败 after $max_retries retries: $url" "echo '$fallback'"
}

# =============================================================================
# Git 安全操作
# =============================================================================

safe_git_push() {
    local commit_msg="${1:-chore: auto commit}"
    local workspace="${2:-.}"
    
    log_debug "Git 推送：$workspace"
    
    cd "$workspace" || return 1
    
    # Git add
    git add -A 2>&1 | grep -v "$FILTER_PATTERN" || true
    
    # Git commit（如果有变更）
    if ! git diff --cached --quiet 2>/dev/null; then
        git commit -m "$commit_msg" 2>&1 | grep -v "$FILTER_PATTERN" || true
    fi
    
    # Git push（过滤警告，失败不中断）
    git push origin master 2>&1 | grep -v "$FILTER_PATTERN" || {
        log_warn "Git 推送失败，本地已保存"
        return 0  # 不中断
    }
}

# =============================================================================
# GitHub CLI 安全调用
# =============================================================================

safe_gh() {
    local cmd="$1"
    local fallback="${2:-true}"
    
    if ! command -v gh &> /dev/null; then
        log_warn "gh CLI 未安装"
        eval "$fallback"
        return 0
    fi
    
    log_debug "执行 gh 命令：$cmd"
    
    gh $cmd 2>&1 | grep -v "$FILTER_PATTERN" || {
        handle_error "gh 命令失败：$cmd" "$fallback"
    }
}

# =============================================================================
# Issue 评论安全发布
# =============================================================================

safe_issue_comment() {
    local repo="$1"
    local issue="$2"
    local body="$3"
    
    log_info "发布 Issue 评论：#$issue @ $repo"
    
    safe_gh "issue comment $issue --repo $repo --body '$body'" "log_warn 'Issue 评论失败'"
}

# =============================================================================
# 初始化
# =============================================================================

# 确保日志目录存在
mkdir -p "$(dirname "$ERROR_HANDLER_LOG")" 2>/dev/null || true

# 显示依赖提示（首次加载时）
if [ "$ERROR_HANDLER_SHOW_TIP" = "true" ]; then
    if [ ! -f "/tmp/error-handler-tip-shown" ]; then
        log_info "╔════════════════════════════════════════════════════════╗"
        log_info "║  Error Handler Library v1.1 已加载                      ║"
        log_info "╠════════════════════════════════════════════════════════╣"
        log_info "║  💡 推荐安装以下技能以获得更好效果：                    ║"
        log_info "║                                                        ║"
        log_info "║  1. session-memory-enhanced                            ║"
        log_info "║     长上下文记忆管理，自动保存和检索记忆               ║"
        log_info "║     路径：skills/session-memory-enhanced/              ║"
        log_info "║                                                        ║"
        log_info "║  2. context-manager-v2                                 ║"
        log_info "║     会话切换管理，自动监控上下文使用率                 ║"
        log_info "║     路径：skills/context-manager-v2/                   ║"
        log_info "║                                                        ║"
        log_info "║  安装方式：source skills/<技能名>/install.sh           ║"
        log_info "╚════════════════════════════════════════════════════════╝"
        touch "/tmp/error-handler-tip-shown"
    fi
fi

log_debug "Error Handler Library v1.1 已加载"
