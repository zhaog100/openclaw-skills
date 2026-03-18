#!/bin/bash
# =============================================================================
# 定时回顾更新助手 (daily-review-helper)
# =============================================================================
# 版本：v1.1
# 创建时间：2026-03-16
# 创建者：思捷娅科技 (SJYKJ)
# 用途：定时回顾今日工作，查漏补缺，更新记忆和知识库
# 许可证：MIT License
# 版权：Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================

set -e

# 加载配置
_SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$_SKILL_ROOT/scripts/lib/config.sh"

LOG_FILE="$LOG_DIR/daily-review.log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE" >&2; }

# 显示帮助
show_help() {
    cat << EOF
╔════════════════════════════════════════════════════════╗
║     定时回顾更新助手 v${CFG_VERSION} - 思捷娅科技 (SJYKJ)       ║
╚════════════════════════════════════════════════════════╝

用法：$0 <命令> [选项]

命令:
  review                执行回顾（默认）
  status                查看状态
  cron-add [mode]       添加定时任务
  cron-remove           删除定时任务
  cron-status           查看定时任务状态
  help                  显示帮助

选项:
  --date <YYYY-MM-DD>   指定日期（默认今天）
  --mode <morning|full> 回顾模式（默认 auto）

示例:
  $0 review
  $0 review --date 2026-03-16
  $0 status
  $0 cron-add
  $0 cron-remove
EOF
}

# 回顾今日工作
do_review() {
    local date="${1:-$(date +%Y-%m-%d)}"
    local mode="${2:-auto}"

    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  定时回顾更新助手 v${CFG_VERSION}                          ║"
    log_info "╠════════════════════════════════════════════════════════╣"
    log_info "║  日期：$date"
    log_info "║  模式：$mode"
    log_info "╚════════════════════════════════════════════════════════╝"

    local step=0
    local total=0

    [ "$CFG_F_TASK" = "true" ]    && total=$((total+1))
    [ "$CFG_F_GIT" = "true" ]     && total=$((total+1))
    [ "$CFG_F_ISSUE" = "true" ]   && total=$((total+1))
    [ "$CFG_F_LEARN" = "true" ]   && total=$((total+1))

    [ "$CFG_F_TASK" = "true" ]    && { step=$((step+1)); log_info "📋 步骤 $step/$total: 回顾今日任务...";  review_tasks "$date"; }
    [ "$CFG_F_GIT" = "true" ]     && { step=$((step+1)); log_info "💻 步骤 $step/$total: 回顾 Git 提交..."; review_commits "$date"; }
    [ "$CFG_F_ISSUE" = "true" ]   && { step=$((step+1)); log_info "📝 步骤 $step/$total: 回顾 Issues...";   review_issues "$date"; }
    [ "$CFG_F_LEARN" = "true" ]   && { step=$((step+1)); log_info "📚 步骤 $step/$total: 回顾学习...";     review_learning "$date"; }

    log_info "✅ 回顾完成！"
}

review_tasks() {
    local date="$1"
    local daily_log="$MEMORY_DIR/$date.md"
    if [ -f "$daily_log" ]; then
        local tasks=$(grep -c "^\- \[x\]" "$daily_log" 2>/dev/null || echo "0")
        log_info "  ✅ 完成 $tasks 个任务"
    else
        log_warn "  ⚠️ 今日日志不存在：$daily_log"
    fi
}

review_commits() {
    local date="$1"
    local commits=$(git -C "$CFG_WORKSPACE" log --since="$date 00:00" --until="$date 23:59" --oneline 2>/dev/null | wc -l)
    log_info "  ✅ $commits 个 Git 提交"
}

review_issues() {
    log_info "  ⏳ Issues 回顾（待实现）"
}

review_learning() {
    local knowledge_files=$(find "$KNOWLEDGE_DIR" -name "*.md" -mtime -1 2>/dev/null | wc -l)
    log_info "  ✅ $knowledge_files 个知识文档"
}

show_status() {
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  定时回顾更新助手 - 状态                                ║"
    log_info "╚════════════════════════════════════════════════════════╝"
    [ -f "$_SKILL_ROOT/config/config.json" ] && log_info "✅ 配置文件：已创建" || log_warn "⚠️ 配置文件：未创建"
    [ -f "$LOG_FILE" ] && log_info "✅ 日志文件：已创建" || log_warn "⚠️ 日志文件：未创建"
    log_info "✅ 工作区：$CFG_WORKSPACE"
}

add_cron() {
    local mode="${1:-default}"
    local hour_m=$(echo "$CFG_REVIEW_MORNING" | cut -d: -f1)
    local min_m=$(echo "$CFG_REVIEW_MORNING" | cut -d: -f2)
    local hour_e=$(echo "$CFG_REVIEW_EVENING" | cut -d: -f1)
    local min_e=$(echo "$CFG_REVIEW_EVENING" | cut -d: -f2)

    if crontab -l 2>/dev/null | grep -q "$CFG_CRON_ID"; then
        log_warn "定时任务已存在"; return 0
    fi

    local tasks=""
    case "$mode" in
        morning) tasks="$min_m $hour_m * * * $_SKILL_ROOT/skill.sh review --mode morning >> $LOG_FILE 2>&1" ;;
        full)    tasks="$min_e $hour_e * * * $_SKILL_ROOT/skill.sh review --mode full >> $LOG_FILE 2>&1" ;;
        default|*)
            tasks="$min_m $hour_m * * * $_SKILL_ROOT/skill.sh review --mode morning >> $LOG_FILE 2>&1
$min_e $hour_e * * * $_SKILL_ROOT/skill.sh review --mode full >> $LOG_FILE 2>&1"
            ;;
    esac

    (crontab -l 2>/dev/null | grep -v "$CFG_CRON_ID"; echo "$tasks") | crontab -
    log_info "✅ 定时任务已添加"
}

remove_cron() {
    crontab -l 2>/dev/null | grep -v "$CFG_CRON_ID" | crontab -
    log_info "✅ 定时任务已删除"
}

show_cron_status() {
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  定时任务状态                                          ║"
    log_info "╚════════════════════════════════════════════════════════╝"
    local cron_tasks=$(crontab -l 2>/dev/null | grep "$CFG_CRON_ID" || true)
    if [ -n "$cron_tasks" ]; then
        log_info "✅ 定时任务已启用"; echo ""; echo "$cron_tasks"
    else
        log_warn "⚠️ 定时任务未启用"
    fi
}

main() {
    local command="${1:-review}"
    case "$command" in
        review)     shift; do_review "$@" ;;
        status)     show_status ;;
        cron-add)   shift; add_cron "$@" ;;
        cron-remove) remove_cron ;;
        cron-status) show_cron_status ;;
        help|--help|-h) show_help ;;
        *)          log_error "未知命令：$command"; show_help; exit 1 ;;
    esac
}

main "$@"
