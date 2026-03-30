#!/bin/bash
# =============================================================================
# 小米椒 🌶️‍🔥 运营定时任务统一入口
# =============================================================================
# 用法: xiaomila-cron.sh <command>
# 命令:
#   qmd-update     - 更新 QMD 知识库索引
#   morning-review - 午间回顾（12:10）：查漏补缺+更新记忆+Git+QMD
#   daily-review   - 每日回顾（23:30）：查漏补缺+更新记忆+Git+QMD
#   weekly-report  - 每周运营总结（周五 18:10）
#   error-stats    - 错误统计（每小时:10）
#   cleanup        - 日志清理（02:10）
# 版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================

set -euo pipefail

# Bun/QMD PATH
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

WORKSPACE="/home/zhaog/.openclaw/workspace"
MEDIA_DIR="$WORKSPACE/agents/xiaomijiao"
MEMORY_DIR="$MEDIA_DIR/memory"
INTEL_DIR="$MEDIA_DIR/intel"
LOG_DIR="$MEDIA_DIR/logs"
TODAY=$(date +%Y-%m-%d)
NOW=$(date '+%H:%M')
COMMAND="${1:-help}"
GITHUB_TOKEN="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"
REMOTE_URL="https://zhaog100:${GITHUB_TOKEN}@github.com/zhaog100/xiaomila-skills.git"

# PATH 确保能找到 qmd
export PATH="/home/zhaog/.local/bin:/home/zhaog/.npm-global/bin:$PATH"
export QMD_FORCE_CPU=1

mkdir -p "$LOG_DIR" "$MEMORY_DIR" "$INTEL_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$COMMAND] $1" | tee -a "$LOG_DIR/xiaomila-cron.log"
}

# ============ 公共：QMD 更新 ============
do_qmd_update() {
    log "更新 QMD 向量索引..."
    cd "$WORKSPACE"
    if command -v qmd &>/dev/null; then
        qmd update >> "$LOG_DIR/qmd-update.log" 2>&1 && log "✅ QMD 更新完成" || log "⚠️ QMD 更新失败"
    else
        log "⚠️ qmd 未找到，跳过"
    fi
}

# ============ 公共：Git 提交+推送 ============
do_git_push() {
    local MSG="$1"
    cd "$WORKSPACE"
    git add agents/xiaomijiao/ >> "$LOG_DIR/git.log" 2>&1 || true

    if git diff --cached --quiet -- agents/xiaomijiao/ 2>/dev/null; then
        log "ℹ️ 无新变更需提交"
    else
        git commit -m "$MSG" >> "$LOG_DIR/git.log" 2>&1
        log "✅ Git 已提交"
    fi

    # 推送到远程 main
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "bounty-1501")
    if GIT_LFS_SKIP_PUSH=1 git -c http.version=HTTP/1.1 push "$REMOTE_URL" "$CURRENT_BRANCH:main" >> "$LOG_DIR/git.log" 2>&1; then
        log "✅ 已推送到 xiaomila-skills.git main"
    else
        log "⚠️ 推送失败（网络？），下次重试"
    fi
}

# ============ 公共：统计待办进度 ============
do_check_todo() {
    if [ -f "$INTEL_DIR/运营待办.md" ]; then
        DONE=$(grep -c "\[x\]" "$INTEL_DIR/运营待办.md" 2>/dev/null || echo 0)
        TODO=$(grep -c "\[ \]" "$INTEL_DIR/运营待办.md" 2>/dev/null || echo 0)
        log "待办进度: ✅${DONE} 完成 / ⏳${TODO} 待做"
    fi
}

# ============ 公共：统计文件变更 ============
do_check_changes() {
    cd "$WORKSPACE"
    INTEL_CHANGES=$(git diff --name-only HEAD -- agents/xiaomijiao/intel/ 2>/dev/null | wc -l)
    MEMORY_CHANGES=$(git diff --name-only HEAD -- agents/xiaomijiao/memory/ 2>/dev/null | wc -l)
    CONFIG_CHANGES=$(git diff --name-only HEAD -- agents/xiaomijiao/*.md 2>/dev/null | wc -l)
    log "变更统计: intel/${INTEL_CHANGES} memory/${MEMORY_CHANGES} config/${CONFIG_CHANGES}"
    
    # 列出具体变更文件
    git diff --name-only HEAD -- agents/xiaomijiao/ 2>/dev/null | while read f; do
        log "  📄 $f"
    done
}

# ============ 公共：确保记忆文件存在 ============
do_ensure_memory() {
    MEMORY_FILE="$MEMORY_DIR/$TODAY.md"
    if [ -f "$MEMORY_FILE" ]; then
        LINES=$(wc -l < "$MEMORY_FILE")
        log "今日记忆文件: ${LINES}行"
    else
        log "创建今日记忆文件模板..."
        cat > "$MEMORY_FILE" << EOF
# 📅 $TODAY 运营日志

## ✅ 完成事项
_待记录_

## 📚 今日学到
_待记录_

## 🔥 今日热点快照
_待记录_

## ⏳ 待处理
_待记录_

## 📊 数据复盘
_今日无已发布内容_

---
*小米椒 🌶️‍🔥*
EOF
        log "✅ 记忆模板已创建"
    fi
}

# ============ QMD 知识库更新（独立命令） ============
cmd_qmd_update() {
    do_qmd_update
}

# ============ 午间回顾（12:10）============
# 查漏补缺 + 更新记忆 + Git提交推送 + QMD更新
cmd_morning_review() {
    log "===== 午间运营回顾开始（$NOW）====="
    
    # 1. 确保记忆文件存在
    do_ensure_memory
    
    # 2. 统计上午工作变更
    do_check_changes
    
    # 3. 检查待办完成度
    do_check_todo
    
    # 4. Git 提交+推送
    do_git_push "docs(xiaomijiao): 午间回顾 - $TODAY"
    
    # 5. QMD 向量更新
    do_qmd_update
    
    log "===== 午间运营回顾完成 ====="
}

# ============ 每日回顾（23:30）============
# 查漏补缺 + 更新记忆 + Git提交推送 + QMD更新
cmd_daily_review() {
    log "===== 每日运营回顾开始（$NOW）====="
    
    # 1. 确保记忆文件存在
    do_ensure_memory
    
    # 2. 统计全天工作变更
    do_check_changes
    
    # 3. 检查待办完成度（全天总结）
    do_check_todo
    
    # 4. Git 提交+推送
    do_git_push "docs(xiaomijiao): 每日回顾 - $TODAY"
    
    # 5. QMD 向量更新
    do_qmd_update
    
    log "===== 每日运营回顾���成 ====="
}

# ============ 每周运营总结 ============
cmd_weekly_report() {
    log "===== 每周运营总结开始 ====="
    
    WEEK_END=$(date '+%Y-%m-%d')
    WEEK_START=$(date -d '7 days ago' '+%Y-%m-%d' 2>/dev/null || echo "$WEEK_END")
    REPORT_FILE="$MEMORY_DIR/weekly-${WEEK_END}.md"
    
    cd "$WORKSPACE"
    
    # 统计本周数据
    WEEK_COMMITS=$(git log --since="$WEEK_START" --oneline -- agents/xiaomijiao/ 2>/dev/null | wc -l)
    WEEK_FILES=$(find "$INTEL_DIR" -name "*.md" -newer "$MEMORY_DIR" -mtime -7 2>/dev/null | wc -l)
    WEEK_MEMORY=$(ls -1 "$MEMORY_DIR"/${WEEK_START}*.md "$MEMORY_DIR"/$(date -d '1 day ago' +%Y-%m-%d)*.md "$MEMORY_DIR"/$TODAY.md 2>/dev/null | sort -u | wc -l)
    
    cat > "$REPORT_FILE" << EOF
# 📈 小米椒周报: $WEEK_START ~ $WEEK_END

## 📊 本周数据
- Git 提交: ${WEEK_COMMITS} 次
- 文档更新: ${WEEK_FILES} 篇
- 运营日志: ${WEEK_MEMORY} 天

## 本周 Git 活动
\`\`\`
$(git log --since="$WEEK_START" --oneline -- agents/xiaomijiao/ 2>/dev/null | head -20)
\`\`\`

## 下周计划
_待填写_

---
*自动生成 by xiaomila-cron.sh | $WEEK_END*
EOF
    
    log "✅ 周报已生成: $REPORT_FILE"
    
    # 周报也走一遍 Git+QMD
    do_git_push "docs(xiaomijiao): 周报 - $WEEK_START ~ $WEEK_END"
    do_qmd_update
    
    log "===== 每周运营总结完成 ====="
}

# ============ 错误统计 ============
cmd_error_stats() {
    ERROR_LOG="$LOG_DIR/xiaomila-cron.log"
    [ ! -f "$ERROR_LOG" ] && return 0
    
    TODAY_ERRORS=$(grep "$TODAY" "$ERROR_LOG" 2>/dev/null | grep -c "⚠️\|❌\|ERROR\|失败" 2>/dev/null || echo "0")
    [ "$TODAY_ERRORS" -gt 0 ] && log "📊 今日错误: $TODAY_ERRORS"
}

# ============ 日志清理 ============
cmd_cleanup() {
    log "清理旧日志..."
    find "$LOG_DIR" -name "*.log" -mtime +7 -delete 2>/dev/null || true
    log "✅ 清理完成"
}

# ============ 帮助 ============
cmd_help() {
    cat << 'EOF'
小米椒 🌶️‍🔥 运营定时任务

用法: xiaomila-cron.sh <command>

命令:
  qmd-update      更新 QMD 知识库索引
  morning-review  午间回顾（查漏补缺+记忆+Git+QMD）
  daily-review    每日回顾（查漏补缺+记忆+Git+QMD）
  weekly-report   每周运营总结
  error-stats     错误统计
  cleanup         日志清理
  help            显示帮助
EOF
}

# ============ 路由 ============
case "$COMMAND" in
    qmd-update)      cmd_qmd_update ;;
    morning-review)  cmd_morning_review ;;
    daily-review)    cmd_daily_review ;;
    weekly-report)   cmd_weekly_report ;;
    error-stats)     cmd_error_stats ;;
    cleanup)         cmd_cleanup ;;
    help|*)          cmd_help ;;
esac
