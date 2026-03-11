#!/bin/bash
# Git 自动提交脚本（v1.0.0）
# 用于 auto-update-strategy 方案

set -e

WORKSPACE="/home/zhaog/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/git-auto-commit.log"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

cd "$WORKSPACE"

log "=== Git 自动提交开始 ==="

# 检查 Git 状态
if ! git status >/dev/null 2>&1; then
    log "❌ 错误：不在 Git 仓库中"
    exit 1
fi

# 添加所有变更
git add -A

# 检查是否有变更
if git diff-index --quiet HEAD --; then
    log "ℹ️  无变更需要提交"
else
    # 获取变更统计
    ADDED=$(git diff --cached --numstat | awk '{added+=$1} END {print added+0}')
    MODIFIED=$(git diff --cached --numstat | awk '{modified+=$2} END {print modified+0}')
    DELETED=$(git diff --cached --numstat | awk '{deleted+=$3} END {print deleted+0}')
    
    # 提交
    git commit -m "chore: auto-update (+$ADDED ~$MODIFIED -$DELETED)"
    
    log "✅ 提交成功：+$ADDED ~$MODIFIED -$DELETED"
    
    # 自动推送（如果配置了远程）
    if git remote | grep -q origin; then
        log "📤 推送到远程..."
        git push origin HEAD 2>&1 | tee -a "$LOG_FILE" || log "⚠️  推送失败（可能无网络）"
    fi
fi

log "=== Git 自动提交完成 ==="
