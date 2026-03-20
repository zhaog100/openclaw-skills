#!/bin/bash
# =============================================================================
# 定时回顾更新助手 (daily-review-assistant)
# =============================================================================
# 版本：v1.1
# 创建时间：2026-03-16
# 创建者：思捷娅科技 (SJYKJ)
# 用途：定时回顾今日工作，查漏补缺，更新记忆和知识库
# 许可证：MIT License
# 版权：Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_SCRIPTS_DIR="$SKILL_DIR/scripts"

# 加载配置
source "$_SCRIPTS_DIR/lib/config.sh"

# 设置当前日志
_CURRENT_LOG_FILE="$CFG_LOGS_DIR/daily-review.log"
LOG_FILE="$_CURRENT_LOG_FILE"

# 显示帮助
show_help() {
    cat << EOF
╔════════════════════════════════════════════════════════╗
║     定时回顾更新助手 v1.1 - 思捷娅科技 (SJYKJ)          ║
╚════════════════════════════════════════════════════════╝

用法：$0 <命令> [选项]

命令:
  review                执行回顾（默认）
  status                查看状态
  cron-add [mode]       添加定时任务
  cron-remove           删除定时任务
  cron-status           查看定时任务状态
  help                  显示帮助

定时任务模式:
  morning               仅中午回顾上午
  full                  仅晚上回顾全天
  custom                自定义时间（交互式）
  default               默认（中午 + 晚上）

选项:
  --date      指定日期（YYYY-MM-DD，默认今天）
  --mode      模式（morning/full，默认 auto）

示例:
  $0 review                    # 回顾今天
  $0 review --date 2026-03-16  # 回顾指定日期
  $0 review --mode full        # 全天回顾
  $0 status                    # 查看状态
  $0 cron-add                  # 添加默认定时任务
  $0 cron-add morning          # 仅添加上午任务
  $0 cron-add custom           # 自定义定时任务
  $0 cron-status               # 查看定时任务状态
  $0 cron-remove               # 删除定时任务

版权：思捷娅科技 (SJYKJ)
EOF
}

# 回顾今日工作
do_review() {
    local date="$(date +%Y-%m-%d)"
    local mode="auto"
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --date) date="$2"; shift 2 ;;
            --mode) mode="$2"; shift 2 ;;
            *) shift ;;
        esac
    done
    
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  定时回顾更新助手 v1.1                                  ║"
    log_info "╠════════════════════════════════════════════════════════╣"
    log_info "║  日期：$date"
    log_info "║  模式：$mode"
    log_info "╚════════════════════════════════════════════════════════╝"
    
    local step=0
    local total=4

    if [ "$CFG_FEATURE_TASK_REVIEW" = "true" ]; then
        step=$((step + 1))
        log_info "📋 步骤 $step/$total: 回顾今日任务..."
        review_tasks "$date"
    fi

    if [ "$CFG_FEATURE_GIT_REVIEW" = "true" ]; then
        step=$((step + 1))
        log_info "💻 步骤 $step/$total: 回顾 Git 提交..."
        review_commits "$date"
    fi

    if [ "$CFG_FEATURE_ISSUE_REVIEW" = "true" ]; then
        step=$((step + 1))
        log_info "📝 步骤 $step/$total: 回顾 Issues..."
        review_issues "$date"
    fi

    if [ "$CFG_FEATURE_LEARNING_REVIEW" = "true" ]; then
        step=$((step + 1))
        log_info "📚 步骤 $step/$total: 回顾学习..."
        review_learning "$date"
    fi
    
    log_info "✅ 回顾完成！"
}

# 回顾任务
review_tasks() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    if [ -f "$daily_log" ]; then
        local tasks=$(grep -c "^\- \[x\]" "$daily_log" 2>/dev/null || echo "0")
        log_info "  ✅ 完成 $tasks 个任务"
    else
        log_warn "  ⚠️ 今日日志不存在：$daily_log"
    fi
}

# 回顾 Git 提交
review_commits() {
    local date="$1"
    local commits=$(git -C "$CFG_WORKSPACE" log --since="$date 00:00" --until="$date 23:59" --oneline 2>/dev/null | wc -l)
    log_info "  ✅ $commits 个 Git 提交"
}

# 回顾 Issues
review_issues() {
    log_info "  ⏳ Issues 回顾（待实现）"
}

# 回顾学习
review_learning() {
    local knowledge_files=$(find "$CFG_KNOWLEDGE_DIR" -name "*.md" -mtime -1 2>/dev/null | wc -l)
    log_info "  ✅ $knowledge_files 个知识文档"
}

# 查看状态
show_status() {
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  定时回顾更新助手 - 状态                                ║"
    log_info "╚════════════════════════════════════════════════════════╝"
    
    if [ -f "$CONFIG_FILE" ]; then
        log_info "✅ 配置文件：已创建"
    else
        log_warn "⚠️ 配置文件：未创建"
    fi
    
    if [ -f "$LOG_FILE" ]; then
        log_info "✅ 日志文件：已创建"
    else
        log_warn "⚠️ 日志文件：未创建"
    fi
    
    if [ -d "$CFG_WORKSPACE" ]; then
        log_info "✅ 工作区：$CFG_WORKSPACE"
    else
        log_error "❌ 工作区：不存在"
    fi
}

# 添加定时任务
add_cron() {
    local mode="${1:-default}"
    
    log_info "添加定时任务..."
    
    case "$mode" in
        morning)
            local task="$CFG_CRON_MORNING $SKILL_DIR/skill.sh review --mode morning >> $LOG_FILE 2>&1"
            ;;
        full)
            local task="$CFG_CRON_FULL $SKILL_DIR/skill.sh review --mode full >> $LOG_FILE 2>&1"
            ;;
        custom)
            echo "请输入 Crontab 时间表达式（例如：0 12 * * *）："
            read -r cron_time
            echo "请输入要执行的命令参数（例如：review --mode morning）："
            read -r cmd_args
            local task="$cron_time $SKILL_DIR/skill.sh $cmd_args >> $LOG_FILE 2>&1"
            ;;
        default|*)
            local morning_task="$CFG_CRON_MORNING $SKILL_DIR/skill.sh review --mode morning >> $LOG_FILE 2>&1"
            local evening_task="$CFG_CRON_FULL $SKILL_DIR/skill.sh review --mode full >> $LOG_FILE 2>&1"
            local task="$morning_task"$'\n'"$evening_task"
            ;;
    esac
    
    if crontab -l 2>/dev/null | grep -q "daily-review-assistant"; then
        log_warn "定时任务已存在"
        return 0
    fi
    
    (crontab -l 2>/dev/null | grep -v "daily-review-assistant"; echo "$task") | crontab -
    log_info "✅ 定时任务已添加"
    
    case "$mode" in
        morning) log_info "   - 上午回顾：$CFG_CRON_MORNING" ;;
        full) log_info "   - 全天回顾：$CFG_CRON_FULL" ;;
        custom) log_info "   - 自定义任务：$task" ;;
        default|*)
            log_info "   - 上午回顾：$CFG_CRON_MORNING"
            log_info "   - 全天回顾：$CFG_CRON_FULL"
            ;;
    esac
}

# 删除定时任务
remove_cron() {
    log_info "删除定时任务..."
    crontab -l 2>/dev/null | grep -v "daily-review-assistant" | crontab -
    log_info "✅ 定时任务已删除"
}

# 查看定时任务状态
show_cron_status() {
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  定时任务状态                                          ║"
    log_info "╚════════════════════════════════════════════════════════╝"
    
    local cron_tasks=$(crontab -l 2>/dev/null | grep "daily-review-assistant" || true)
    
    if [ -n "$cron_tasks" ]; then
        log_info "✅ 定时任务已启用"
        echo ""
        echo "$cron_tasks"
    else
        log_warn "⚠️ 定时任务未启用"
        echo ""
        echo "使用 ./skill.sh cron-add 添加定时任务"
    fi
}

# 主函数
main() {
    local command="${1:-review}"
    
    case "$command" in
        review) shift; do_review "$@" ;;
        status) show_status ;;
        cron-add) shift; add_cron "$@" ;;
        cron-remove) remove_cron ;;
        cron-status) show_cron_status ;;
        help|--help|-h) show_help ;;
        *) log_error "未知命令：$command"; show_help; exit 1 ;;
    esac
}

main "$@"
