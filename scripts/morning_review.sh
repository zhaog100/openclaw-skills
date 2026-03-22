#!/bin/bash
# 早间回顾脚本（每天12:00）
# 功能：快速回顾今日待办、检查系统状态、提醒重要事项
# 版权声明：MIT License | Copyright (c) 2026 思捷_GUIDEYA科技 (SJYKJ)

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="/tmp/morning_review.log"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') [morning-review] $1" >> "$LOG_FILE"; }

cd "$WORKSPACE" || exit 1

# 1. 系统健康检查
log "=== System Health ==="
echo "Disk:" $(df -h / | tail -1 | awk '{print $5}')
echo "Memory:" $(free -h | head -2 | tail -1 | awk '{print $3"/"$2}')
echo "Gateway:" $(openclaw gateway status 2>/dev/null | head -1 || echo "unknown")

# 2. PR状态快速检查
log "=== Open PRs ==="
for repo in "Comfy-Org/ComfyUI" "Scottcjn/rustchain-bounties"; do
  count=$(gh pr list --repo "$repo" --author zhaog100 --state open --json number --jq 'length' 2>/dev/null || echo "0")
  [ "$count" -gt 0 ] 2>/dev/null && echo "$repo: $count open PRs" >> "$LOG_FILE"
done

# 3. Git同步状态
log "=== Git Status ==="
git status --short | wc -l | xargs -I{} echo "{} uncommitted changes"

# 4. 今日重点（从MEMORY-LITE读取）
log "=== Today's Focus ==="
grep -A5 "紧急待办" MEMORY-LITE.md 2>/dev/null >> "$LOG_FILE"

log "Morning review completed"
