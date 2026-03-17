#!/bin/bash
# =============================================================================
# 定时回顾更新助手 (daily-review-helper)
# =============================================================================
# 版本：v1.0
# 创建时间：2026-03-16
# 创建者：思捷娅科技 (SJYKJ)
# 用途：定时回顾今日工作，查漏补缺，更新记忆和知识库
# 许可证：MIT License
# 版权：Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${WORKSPACE:-$(pwd)}"
LOG_FILE="$SCRIPT_DIR/logs/daily-review.log"

# 确保目录存在
mkdir -p "$SCRIPT_DIR/logs"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE" >&2
}

# 显示帮助
show_help() {
    cat << EOF
╔════════════════════════════════════════════════════════╗
║     定时回顾更新助手 v1.0 - 思捷娅科技 (SJYKJ)          ║
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
  morning               仅中午 12:00 回顾上午
  full                  仅晚上 23:50 回顾全天
  custom                自定义时间（交互式）
  default               默认（中午 12:00 + 晚上 23:50）

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
    local date="${1:-$(date +%Y-%m-%d)}"
    local mode="${2:-auto}"
    
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  定时回顾更新助手 v1.0                                  ║"
    log_info "╠════════════════════════════════════════════════════════╣"
    log_info "║  日期：$date"
    log_info "║  模式：$mode"
    log_info "╚════════════════════════════════════════════════════════╝"
    
    # 1. 回顾今日任务
    log_info "📋 步骤 1/4: 回顾今日任务..."
    review_tasks "$date"
    
    # 2. 回顾 Git 提交
    log_info "💻 步骤 2/4: 回顾 Git 提交..."
    review_commits "$date"
    
    # 3. 回顾 Issues
    log_info "📝 步骤 3/4: 回顾 Issues..."
    review_issues "$date"
    
    # 4. 回顾学习
    log_info "📚 步骤 4/4: 回顾学习..."
    review_learning "$date"
    
    log_info "✅ 回顾完成！"
}

# 回顾任务
review_tasks() {
    local date="$1"
    local daily_log="$WORKSPACE/memory/$date.md"
    
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
    local commits=$(git -C "$WORKSPACE" log --since="$date 00:00" --until="$date 23:59" --oneline 2>/dev/null | wc -l)
    log_info "  ✅ $commits 个 Git 提交"
}

# 回顾 Issues
review_issues() {
    local date="$1"
    log_info "  ⏳ Issues 回顾（待实现）"
}

# 回顾学习
review_learning() {
    local date="$1"
    local knowledge_files=$(find "$WORKSPACE/knowledge" -name "*.md" -mtime -1 2>/dev/null | wc -l)
    log_info "  ✅ $knowledge_files 个知识文档"
}

# 查看状态
show_status() {
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  定时回顾更新助手 - 状态                                ║"
    log_info "╚════════════════════════════════════════════════════════╝"
    
    # 检查配置
    if [ -f "$SCRIPT_DIR/config/config.json" ]; then
        log_info "✅ 配置文件：已创建"
    else
        log_warn "⚠️ 配置文件：未创建"
    fi
    
    # 检查日志
    if [ -f "$LOG_FILE" ]; then
        log_info "✅ 日志文件：已创建"
    else
        log_warn "⚠️ 日志文件：未创建"
    fi
    
    # 检查工作区
    if [ -d "$WORKSPACE" ]; then
        log_info "✅ 工作区：$WORKSPACE"
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
            # 仅上午
            local task="0 12 * * * $SCRIPT_DIR/skill.sh review --mode morning >> $LOG_FILE 2>&1"
            ;;
        full)
            # 仅全天
            local task="50 23 * * * $SCRIPT_DIR/skill.sh review --mode full >> $LOG_FILE 2>&1"
            ;;
        custom)
            # 自定义时间
            echo "请输入 Crontab 时间表达式（例如：0 12 * * *）："
            read -r cron_time
            echo "请输入要执行的命令参数（例如：review --mode morning）："
            read -r cmd_args
            local task="$cron_time $SCRIPT_DIR/skill.sh $cmd_args >> $LOG_FILE 2>&1"
            ;;
        default|*)
            # 默认：上午 + 全天
            local morning_task="0 12 * * * $SCRIPT_DIR/skill.sh review --mode morning >> $LOG_FILE 2>&1"
            local evening_task="50 23 * * * $SCRIPT_DIR/skill.sh review --mode full >> $LOG_FILE 2>&1"
            local task="$morning_task"$'\n'"$evening_task"
            ;;
    esac
    
    # 检查是否已存在
    if crontab -l 2>/dev/null | grep -q "daily-review-helper"; then
        log_warn "定时任务已存在"
        return 0
    fi
    
    # 添加定时任务
    (crontab -l 2>/dev/null | grep -v "daily-review-helper"; echo "$task") | crontab -
    log_info "✅ 定时任务已添加"
    
    case "$mode" in
        morning)
            log_info "   - 中午 12:00 回顾上午"
            ;;
        full)
            log_info "   - 晚上 23:50 回顾全天"
            ;;
        custom)
            log_info "   - 自定义任务：$task"
            ;;
        default|*)
            log_info "   - 中午 12:00 回顾上午"
            log_info "   - 晚上 23:50 回顾全天"
            ;;
    esac
}

# 删除定时任务
remove_cron() {
    log_info "删除定时任务..."
    
    # 删除定时任务
    crontab -l 2>/dev/null | grep -v "daily-review-helper" | crontab -
    log_info "✅ 定时任务已删除"
}

# 查看定时任务状态
show_cron_status() {
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  定时任务状态                                          ║"
    log_info "╚════════════════════════════════════════════════════════╝"
    
    local cron_tasks=$(crontab -l 2>/dev/null | grep "daily-review-helper" || true)
    
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
        review)
            shift
            do_review "$@"
            ;;
        status)
            show_status
            ;;
        cron-add)
            shift
            add_cron "$@"
            ;;
        cron-remove)
            remove_cron
            ;;
        cron-status)
            show_cron_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令：$command"
            show_help
            exit 1
            ;;
    esac
}

# 执行
main "$@"
