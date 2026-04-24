#!/bin/bash
# =============================================================================
# 小米椒 🌶️‍🔥 运营定时任务统一入口 v2.0
# =============================================================================
# 用法: xiaomila-cron.sh <command>
# 命令:
#   hotspot-collect - 采集百度热搜并更新热点选题（09:00）
#   qmd-update     - 更新 QMD 知识库索引
#   morning-review - 午间回顾（12:00）：记忆+知识库+Git+QMD+索引
#   daily-review   - 每日回顾（23:50）：记忆+知识库+Git+QMD+索引+查漏补缺
#   weekly-report  - 每周运营总结（周五 18:10）
#   error-stats    - 错误统计（每小时:10）
#   cleanup        - 日志清理（02:10）
# 版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================

set -euo pipefail

# Bun/QMD PATH
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
INTEL_DIR="$WORKSPACE/intel"
LOG_DIR="$WORKSPACE/logs"
DOCS_DIR="$WORKSPACE/docs"
TODAY=$(date +%Y-%m-%d)
NOW=$(date '+%H:%M')
COMMAND="${1:-help}"

# PATH 确保能找到 qmd
export PATH="/home/zhaog/.local/bin:/home/zhaog/.npm-global/bin:$PATH"
export QMD_FORCE_CPU=1

mkdir -p "$LOG_DIR" "$MEMORY_DIR" "$INTEL_DIR" "$DOCS_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$COMMAND] $1" | tee -a "$LOG_DIR/xiaomijiao-cron.log"
}

# ============ 公共：QMD 更新 ============
do_qmd_update() {
    log "🔄 更新 QMD 向量索引..."
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
    git add -A >> "$LOG_DIR/git.log" 2>&1 || true

    if git diff --cached --quiet 2>/dev/null; then
        log "ℹ️ 无新变更需提交"
    else
        git commit -m "$MSG" >> "$LOG_DIR/git.log" 2>&1
        log "✅ Git 已提交"
    fi

    # 推送到 xiaomijiao remote（main 分支）
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
    if GIT_LFS_SKIP_PUSH=1 git -c http.version=HTTP/1.1 push xiaomijiao "$CURRENT_BRANCH" >> "$LOG_DIR/git.log" 2>&1; then
        log "✅ 已推送到 xiaomijiao remote main"
    else
        log "⚠️ 推送失败（网络？），下次重试"
    fi
}

# ============ 公共：统计待办进度 ============
do_check_todo() {
    if [ -f "$INTEL_DIR/运营待办.md" ]; then
        DONE=$(grep -c "\[x\]" "$INTEL_DIR/运营待办.md" 2>/dev/null || echo 0)
        TODO=$(grep -c "\[ \]" "$INTEL_DIR/运营待办.md" 2>/dev/null || echo 0)
        log "📋 待办进度: ✅${DONE} 完成 / ⏳${TODO} 待做"
    else
        log "⚠️ 运营待办.md 不存在"
    fi
}

# ============ 公共：统计文件变更 ============
do_check_changes() {
    cd "$WORKSPACE"
    INTEL_CHANGES=$(git diff --name-only HEAD -- intel/ 2>/dev/null | wc -l)
    MEMORY_CHANGES=$(git diff --name-only HEAD -- memory/ 2>/dev/null | wc -l)
    CONFIG_CHANGES=$(git diff --name-only HEAD -- "*.md" "*.json" 2>/dev/null | wc -l)
    log "📊 变更统计: intel/${INTEL_CHANGES} memory/${MEMORY_CHANGES} config/${CONFIG_CHANGES}"
    
    # 列出具体变更文件
    git diff --name-only HEAD 2>/dev/null | while read f; do
        log "  📄 $f"
    done
}

# ============ 公共：确保记忆文件存在 ============
do_ensure_memory() {
    MEMORY_FILE="$MEMORY_DIR/$TODAY.md"
    if [ -f "$MEMORY_FILE" ]; then
        LINES=$(wc -l < "$MEMORY_FILE")
        log "📅 今日记忆文件: ${LINES}行"
    else
        log "📝 创建今日记忆文件模板..."
        cat > "$MEMORY_FILE" << EOF
# 📅 $TODAY 运营日志

**日期**: $TODAY（$(date -d "$TODAY" +%A 2>/dev/null || echo "未知")）
**维护**: 小米椒 🌶️‍🔥

---

## 🎯 今日重点任务

### 商贸执行
- [ ] 待办事项

### 内容创作
- [ ] 待办事项

---

## 📝 工作记录

### 完成事项
_待记录_

### 学到经验
_待记录_

### 待处理
_待记录_

---

## 📊 数据摘要

| 项目 | 数据 |
|------|------|
| **微信公众号** | 待更新 |
| **闲鱼** | 待更新 |
| **小红书** | 待更新 |

---

_2026-04-24 | 小米椒 🌶️‍🔥 维护_

**版权**：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
EOF
        log "✅ 记忆模板已创建"
    fi
}

# ============ 新增：知识库结构化整理 ============
do_knowledge_base_organize() {
    log "📚 开始知识库结构化整理..."
    
    # 检查 intel/ 目录文件
    INTEL_COUNT=$(find "$INTEL_DIR" -name "*.md" 2>/dev/null | wc -l)
    log "📊 intel/ 目录文件数: $INTEL_COUNT"
    
    # 检查是否有超过 7 天未更新的文件
    OLD_FILES=$(find "$INTEL_DIR" -name "*.md" -mtime +7 2>/dev/null | wc -l)
    if [ "$OLD_FILES" -gt 0 ]; then
        log "⚠️ 发现 $OLD_FILES 个超过 7 天未更新的文件"
        find "$INTEL_DIR" -name "*.md" -mtime +7 2>/dev/null | while read f; do
            log "  📄 $(basename $f) (超过 7 天)"
        done
    else
        log "✅ 所有文件更新正常"
    fi
    
    # 检查是否有重复文件
    DUPLICATE_FILES=$(find "$INTEL_DIR" -name "*.md" -exec basename {} \; 2>/dev/null | sort | uniq -d | wc -l)
    if [ "$DUPLICATE_FILES" -gt 0 ]; then
        log "⚠️ 发现 $DUPLICATE_FILES 个重复文件名"
    else
        log "✅ 无重复文件"
    fi
    
    log "✅ 知识库结构化整理完成"
}

# ============ 新增：索引同步更新 ============
do_index_sync() {
    log "📋 开始索引同步更新..."
    
    INDEX_FILE="$DOCS_DIR/完整索引清单.md"
    
    # 统计文件数
    INTEL_COUNT=$(find "$INTEL_DIR" -name "*.md" 2>/dev/null | wc -l)
    MEMORY_COUNT=$(find "$MEMORY_DIR" -name "*.md" 2>/dev/null | wc -l)
    LOG_COUNT=$(find "$LOG_DIR" -name "*.md" -o -name "*.log" 2>/dev/null | wc -l)
    TOTAL_COUNT=$((INTEL_COUNT + MEMORY_COUNT + LOG_COUNT))
    
    log "📊 文件统计: intel/${INTEL_COUNT} memory/${MEMORY_COUNT} logs/${LOG_COUNT} total/${TOTAL_COUNT}"
    
    # 更新索引文件（如果存在）
    if [ -f "$INDEX_FILE" ]; then
        # 更新文件统计数字
        sed -i "s/当前文件数：[0-9]* 个/当前文件数：${TOTAL_COUNT} 个/g" "$INDEX_FILE" 2>/dev/null || true
        log "✅ 索引文件已更新"
    else
        log "⚠️ 索引文件不存在，跳过更新"
    fi
    
    log "✅ 索引同步更新完成"
}

# ============ 新增：记忆同步更新 ============
do_memory_sync() {
    log "🧠 开始记忆同步更新..."
    
    MEMORY_FILE="$MEMORY_DIR/$TODAY.md"
    MEMORY_MD="$WORKSPACE/MEMORY.md"
    
    # 检查今日记忆文件
    if [ -f "$MEMORY_FILE" ]; then
        LINES=$(wc -l < "$MEMORY_FILE")
        log "📅 今日记忆: ${LINES}行"
    else
        log "⚠️ 今日记忆文件不存在"
    fi
    
    # 检查 MEMORY.md 最后更新时间
    if [ -f "$MEMORY_MD" ]; then
        LAST_UPDATE=$(stat -c %Y "$MEMORY_MD" 2>/dev/null || echo 0)
        TODAY_START=$(date -d "today 00:00" +%s 2>/dev/null || echo 0)
        if [ "$LAST_UPDATE" -lt "$TODAY_START" ]; then
            log "⚠️ MEMORY.md 今天未更新"
        else
            log "✅ MEMORY.md 今天已更新"
        fi
    else
        log "⚠️ MEMORY.md 不存在"
    fi
    
    log "✅ 记忆同步更新完成"
}

# ============ 新增：Git 库整理 ============
do_git_organize() {
    log "🔧 开始 Git 库整理..."
    
    cd "$WORKSPACE"
    
    # 检查未跟踪文件
    UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l)
    if [ "$UNTRACKED" -gt 0 ]; then
        log "⚠️ 发现 $UNTRACKED 个未跟踪文件"
        git ls-files --others --exclude-standard 2>/dev/null | while read f; do
            log "  📄 $f"
        done
    else
        log "✅ 无未跟踪文件"
    fi
    
    # 检查未暂存变更
    MODIFIED=$(git diff --name-only 2>/dev/null | wc -l)
    if [ "$MODIFIED" -gt 0 ]; then
        log "⚠️ 发现 $MODIFIED 个未暂存变更"
    else
        log "✅ 无未暂存变更"
    fi
    
    # 检查最近提交
    RECENT_COMMITS=$(git log --oneline -5 2>/dev/null | head -5)
    log "📊 最近 5 次提交:"
    echo "$RECENT_COMMITS" | while read commit; do
        log "  $commit"
    done
    
    log "✅ Git 库整理完成"
}

# ============ 新增：查漏补缺 ============
do_gap_check() {
    log "🔍 开始查漏补缺..."
    
    # 检查近期任务完成情况
    if [ -f "$INTEL_DIR/运营待办.md" ]; then
        PENDING=$(grep -c "\[ \]" "$INTEL_DIR/运营待办.md" 2>/dev/null || echo 0)
        log "📋 待办事项: $PENDING 项待处理"
        
        # 检查 P0 任务
        P0_COUNT=$(grep -A 10 "P0" "$INTEL_DIR/运营待办.md" 2>/dev/null | grep -c "\[ \]" || echo 0)
        if [ "$P0_COUNT" -gt 0 ]; then
            log "🔴 P0 任务: $P0_COUNT 项未完成"
        fi
    fi
    
    # 检查是否有 3 天以上未更新的记忆文件
    OLD_MEMORY=$(find "$MEMORY_DIR" -name "*.md" -mtime +3 2>/dev/null | wc -l)
    if [ "$OLD_MEMORY" -gt 0 ]; then
        log "⚠️ 发现 $OLD_MEMORY 个超过 3 天未更新的记忆文件"
    else
        log "✅ 记忆文件更新正常"
    fi
    
    # 检查是否有未发布的草稿
    # TODO: 添加微信公众号草稿检查
    
    log "✅ 查漏补缺完成"
}

# ============ QMD 知识库更新（独立命令） ============
cmd_qmd_update() {
    do_qmd_update
}

# ============ 午间回顾（12:00）============
# 记忆+知识库+Git+QMD+索引
cmd_morning_review() {
    log "===== 午间运营回顾开始（$NOW）====="
    
    # 1. 确保记忆文件存在
    do_ensure_memory
    
    # 2. 提取当日聊天记录
    do_extract_chats
    
    # 3. 统计上午工作变更
    do_check_changes
    
    # 4. 检查待办完成度
    do_check_todo
    
    # 5. 知识库结构化整理
    do_knowledge_base_organize
    
    # 6. 索引同步更新
    do_index_sync
    
    # 7. Git 提交+推送
    do_git_push "docs(xiaomijiao): 午间回顾 - $TODAY"
    
    # 8. QMD 向量更新
    do_qmd_update
    
    log "===== 午间运营回顾完成 ====="
}

# ============ 每日回顾（23:50）============
# 记忆+知识库+Git+QMD+索引+查漏补缺
cmd_daily_review() {
    log "===== 每日运营回顾开始（$NOW）====="
    
    # 1. 确保记忆文件存在
    do_ensure_memory
    
    # 2. 提取当日聊天记录
    do_extract_chats
    
    # 3. 统计全天工作变更
    do_check_changes
    
    # 4. 检查待办完成度（全天总结）
    do_check_todo
    
    # 5. 知识库结构化整理
    do_knowledge_base_organize
    
    # 6. 索引同步更新
    do_index_sync
    
    # 7. 记忆同步更新
    do_memory_sync
    
    # 8. Git 库整理
    do_git_organize
    
    # 9. 查漏补缺
    do_gap_check
    
    # 10. Git 提交+推送
    do_git_push "docs(xiaomijiao): 每日回顾 - $TODAY"
    
    # 11. QMD 向量更新
    do_qmd_update
    
    log "===== 每日运营回顾完成 ====="
}

# ============ 每周运营总结 ============
cmd_weekly_report() {
    log "===== 每周运营总结开始 ====="
    
    WEEK_END=$(date '+%Y-%m-%d')
    WEEK_START=$(date -d '7 days ago' '+%Y-%m-%d' 2>/dev/null || echo "$WEEK_END")
    REPORT_FILE="$MEMORY_DIR/weekly-${WEEK_END}.md"
    
    cd "$WORKSPACE"
    
    # 统计本周数据
    WEEK_COMMITS=$(git log --since="$WEEK_START" --oneline 2>/dev/null | wc -l)
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
$(git log --since="$WEEK_START" --oneline 2>/dev/null | head -20)
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

# ============ 从所有会话提取当日聊天记录 ============
do_extract_chats() {
    local SKILL_SCRIPT="$WORKSPACE/skills/multi-channel-memory/scripts/extract-chats.sh"
    if [ -x "$SKILL_SCRIPT" ]; then
        log "提取多通道聊天记录（$TODAY）..."
        bash "$SKILL_SCRIPT" "$TODAY" 2>&1 | grep -E "SUCCESS|ERROR|消息数" | while read line; do
            log "$line"
        done
    else
        log "⚠️ multi-channel-memory 技能未安装，跳过聊天记录提取"
    fi
}

# ============ 错误统计 ============
cmd_error_stats() {
    ERROR_LOG="$LOG_DIR/xiaomijiao-cron.log"
    [ ! -f "$ERROR_LOG" ] && return 0
    
    TODAY_ERRORS=$(grep "$TODAY" "$ERROR_LOG" 2>/dev/null | grep -c "⚠️\|❌\|ERROR\|失败" || true)
    [ "${TODAY_ERRORS:-0}" -gt 0 ] && log "📊 今日错误: $TODAY_ERRORS"
}

# ============ 日志清理 ============
cmd_cleanup() {
    log "清理旧日志..."
    find "$LOG_DIR" -name "*.log" -mtime +7 -delete 2>/dev/null || true
    log "✅ 清理完成"
}

# ============ 热点采集 ============
cmd_hotspot_collect() {
    log "===== 开始采集百度热搜 ====="
    
    # 执行热点采集脚本
    if [ -x "$WORKSPACE/scripts/hotspot-collector.sh" ]; then
        "$WORKSPACE/scripts/hotspot-collector.sh" >> "$LOG_DIR/hotspot.log" 2>&1
        log "✅ 热点采集完成"
    else
        log "❌ 热点采集脚本不存在或无执行权限"
        return 1
    fi
}

# ============ 每晚学习总结（21:00）============
cmd_ai_summary() {
    log "===== 每晚AI学习总结开始（$NOW）====="
    
    SUMMARY_FILE="$MEMORY_DIR/ai学习-$TODAY.md"
    
    cat > "$SUMMARY_FILE" << EOF
# 🤖 AI每日学习总结
**日期**: $TODAY
**时间**: 21:00

## 📚 今日学到的新知识
_待填充_

## 🔧 今日技能/工具更新
_待填充_

## 💡 今日优化/改进
_待填充_

## 📝 明日待实践
_待填充_

---
*自动生成 by xiaomila-cron.sh*
EOF
    
    log "✅ 学习总结模板已创建: $SUMMARY_FILE"
    
    # Git提交
    cd "$WORKSPACE"
    git add "$SUMMARY_FILE" >> "$LOG_DIR/git.log" 2>&1 || true
    git commit -m "docs: AI学习总结 - $TODAY" >> "$LOG_DIR/git.log" 2>&1 || true
    log "✅ 学习总结已提交"
    
    log "===== 每晚AI学习总结完成 ====="
}

# ============ 帮助 ============
cmd_help() {
    cat << 'EOF'
小米椒 🌶️‍🔥 运营定时任务 v2.0

用法: xiaomila-cron.sh <command>

命令:
  hotspot-collect  采集百度热搜并更新热点选题
  ai-summary       每晚AI学习总结（21:00）
  qmd-update       更新 QMD 知识库索引
  morning-review   午间回顾（记忆+知识库+Git+QMD+索引）
  daily-review     每日回顾（记忆+知识库+Git+QMD+索引+查漏补缺）
  weekly-report    每周运营总结
  error-stats      错误统计
  cleanup          日志清理
  help             显示帮助
EOF
}

# ============ 路由 ============
case "$COMMAND" in
    hotspot-collect) cmd_hotspot_collect ;;
    ai-summary)      cmd_ai_summary ;;
    qmd-update)      cmd_qmd_update ;;
    morning-review)  cmd_morning_review ;;
    daily-review)    cmd_daily_review ;;
    weekly-report)   cmd_weekly_report ;;
    error-stats)     cmd_error_stats ;;
    cleanup)         cmd_cleanup ;;
    help|*)          cmd_help ;;
esac
