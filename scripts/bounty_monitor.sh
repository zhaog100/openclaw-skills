#!/bin/bash
# Bounty 监控脚本（v2.0 - 质量过滤版）
# 每 30 分钟自动扫描新的 bounty 任务
# 只处理评分 ≥ 7 的高质量任务

WORKSPACE="/home/zhaog/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/bounty-monitor.log"
WATCHLIST="$WORKSPACE/data/bounty-watchlist.json"
KNOWN_ISSUES="$WORKSPACE/data/bounty-known-issues.txt"
LOW_QUALITY_LIST="$WORKSPACE/data/bounty-low-quality.txt"

# 设置 GitHub Token（从文件读取）
if [ -f "$WORKSPACE/.env" ]; then
    export GITHUB_TOKEN=$(grep GITHUB_TOKEN "$WORKSPACE/.env" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
fi

# 如果 .env 中没有，使用硬编码的 token
if [ -z "$GITHUB_TOKEN" ]; then
    export GITHUB_TOKEN="***REMOVED***"
fi

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$(dirname "$LOW_QUALITY_LIST")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 评估任务质量
evaluate_task() {
    local title="$1"
    local repo="$2"
    local labels="$3"
    local score=0
    
    # 1. 复杂度评估（越简单越好）
    if echo "$title" | grep -qiE "test|docs|fix|small|simple"; then
        score=$((score + 2))
    elif echo "$title" | grep -qiE "implement|feature|refactor"; then
        score=$((score + 1))
    elif echo "$title" | grep -qiE "redesign|rewrite|major"; then
        score=$((score + 0))
    fi
    
    # 2. 标签评估
    if echo "$labels" | grep -qi "good-first-issue"; then
        score=$((score + 2))
    fi
    if echo "$labels" | grep -qi "help-wanted"; then
        score=$((score + 1))
    fi
    
    # 3. 仓库活跃度（简化版）
    if echo "$repo" | grep -qiE "vllm|rustchain|algora"; then
        score=$((score + 2))
    fi
    
    # 4. 标题质量
    if [ ${#title} -lt 50 ]; then
        score=$((score + 1))
    fi
    
    echo $score
}

log "========== Bounty 监控启动（质量过滤版）=========="

# 检查 GitHub CLI 是否可用
if ! command -v gh &> /dev/null; then
    log "❌ 错误: GitHub CLI 未安装"
    exit 1
fi

# 检查是否已登录
if ! gh auth status &> /dev/null; then
    log "❌ 错误: GitHub CLI 未登录"
    exit 1
fi

# 创建已知 issues 文件（如果不存在）
touch "$KNOWN_ISSUES"
touch "$LOW_QUALITY_LIST"

# 扫描 bounty 任务
scan_bounty_issues() {
    log "🔍 扫描 GitHub bounty 任务（质量过滤：评分 ≥ 7）..."
    
    # 搜索最近的 bounty 任务
    ISSUES=$(gh search issues \
        --label bounty \
        --state open \
        --limit 20 \
        --json number,title,url,repository,createdAt,labels \
        --sort created \
        2>/dev/null)
    
    if [ $? -ne 0 ]; then
        log "⚠️ 搜索失败，可能是 API 限流"
        return 1
    fi
    
    # 解析 JSON 并检查新任务
    echo "$ISSUES" | jq -r '.[] | @base64' | while read -r issue_b64; do
        issue=$(echo "$issue_b64" | base64 -d)
        number=$(echo "$issue" | jq -r '.number')
        title=$(echo "$issue" | jq -r '.title')
        url=$(echo "$issue" | jq -r '.url')
        repo=$(echo "$issue" | jq -r '.repository.nameWithOwner')
        created=$(echo "$issue" | jq -r '.createdAt')
        labels=$(echo "$issue" | jq -r '.labels | .[].name' | tr '\n' ' ')
        
        # 检查是否已处理
        if grep -q "$url" "$KNOWN_ISSUES"; then
            continue
        fi
        
        # 检查是否在低质量列表
        if grep -q "$url" "$LOW_QUALITY_LIST"; then
            continue
        fi
        
        # 评估任务质量
        score=$(evaluate_task "$title" "$repo" "$labels")
        
        log "📊 任务 #$number 评分: $score/10"
        
        # 只处理高质量任务（评分 ≥ 7）
        if [ "$score" -lt 7 ]; then
            log "⚠️ 跳过低质量任务: $title（评分: $score）"
            echo "$url" >> "$LOW_QUALITY_LIST"
            continue
        fi
        
        # 记录高质量任务
        log "✨ 发现高质量 bounty 任务: #$number in $repo（评分: $score）"
        log "   标题: $title"
        log "   URL: $url"
        log "   创建时间: $created"
        log "   标签: $labels"
        
        # 添加到已知列表
        echo "$url" >> "$KNOWN_ISSUES"
        
        # 发送通知（可通过 QQ Bot）
        if command -v notify-send &> /dev/null; then
            notify-send "🌶️ 高质量 Bounty 任务（评分: $score）" "$title\n$repo"
        fi
    done
    
    log "✅ 扫描完成"
}

# 主流程
main() {
    scan_bounty_issues
    
    log "========== 监控完成 =========="
}

main
