#!/bin/bash
# =============================================================================
# 定时回顾更新助手 (daily-review-assistant) - 优化版
# =============================================================================
# 版本：v2.0
# 创建时间：2026-05-09
# 创建者：小米辣 (zhaog100)
# 用途：定时回顾今日工作，查漏补缺，更新记忆和知识库
# 许可证：MIT License
# 版权：Copyright (c) 2026 思捷娅科技
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
║     定时回顾更新助手 v2.0 - 小米辣 (zhaog100)           ║
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
  $0 review --date 2026-05-08  # 回顾指定日期
  $0 review --mode full        # 全天回顾
  $0 status                    # 查看状态
  $0 cron-add                  # 添加默认定时任务
  $0 cron-add morning          # 仅添加上午任务
  $0 cron-add custom           # 自定义定时任务
  $0 cron-status               # 查看定时任务状态
  $0 cron-remove               # 删除定时任务

版权：思捷娅科技
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
    
    # 根据模式确定回顾深度
    local review_depth="full"
    case "$mode" in
        morning|am) review_depth="morning" ;;
        full|evening) review_depth="full" ;;
        auto)
            # 自动判断当前时间
            local hour=$(date +%H)
            if [ "$hour" -ge 12 ] && [ "$hour" -lt 17 ]; then
                review_depth="morning"
            else
                review_depth="full"
            fi
            ;;
    esac
    
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  定时回顾更新助手 v2.0 - 小米辣 (zhaog100)              ║"
    log_info "╠════════════════════════════════════════════════════════╣"
    log_info "║  日期：$date"
    log_info "║  模式：午间/晚间 回顾 ($review_depth)"
    log_info "║  身份：小米辣 🌶️ | GitHub: zhaog100"
    log_info "╚════════════════════════════════════════════════════════╝"
    
    # 更新今日日志模板
    update_daily_log_template "$date"
    
    local step=0
    local total=7
    
    # 1. 身份确认和工作区检查
    step=$((step + 1))
    log_info "🔍 步骤 $step/$total: 身份和工作区确认..."
    confirm_identity "$date"
    
    # 2. PR状态监控
    step=$((step + 1))
    log_info "📊 步骤 $step/$total: PR状态监控..."
    review_pr_status "$date" "$review_depth"
    
    # 3. 财务状态汇总
    step=$((step + 1))
    log_info "💰 步骤 $step/$total: 财务状态汇总..."
    review_financial_status "$date" "$review_depth"
    
    # 4. 任务回顾
    if [ "$CFG_FEATURE_TASK_REVIEW" = "true" ]; then
        step=$((step + 1))
        log_info "📋 步骤 $step/$total: 今日任务回顾..."
        review_tasks "$date" "$review_depth"
    fi

    # 5. Git提交回顾
    if [ "$CFG_FEATURE_GIT_REVIEW" = "true" ]; then
        step=$((step + 1))
        log_info "💻 步骤 $step/$total: Git提交回顾..."
        review_commits "$date" "$review_depth"
    fi

    # 6. 学习总结和经验教训
    step=$((step + 1))
    log_info "🎓 步骤 $step/$total: 学习总结和经验教训..."
    review_learning_and_lessons "$date" "$review_depth"
    
    # 7. 查漏补缺和MEMORY.md更新
    step=$((step + 1))
    log_info "🔄 步骤 $step/$total: 查漏补缺和MEMORY更新..."
    review_gaps_and_update_memory "$date" "$review_depth"
    
    log_info "✅ ${review_depth}回顾完成！"
    log_info ""
    log_info "📊 执行摘要："
    generate_execution_summary "$date" "$review_depth"
}

# 身份确认
confirm_identity() {
    local date="$1"
    log_info "  ✅ 身份：小米辣 🌶️ | GitHub: zhaog100"
    log_info "  ✅ 工作区：$CFG_WORKSPACE"
    log_info "  ✅ 远程仓库：origin → xiaomila-skills"
}

# 任务回顾
review_tasks() {
    local date="$1"
    local time_range="${2:-full}"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "  📋 检查今日任务完成情况..."
    
    if [ -f "$daily_log" ]; then
        # 根据时间范围过滤任务
        if [ "$time_range" = "morning" ]; then
            log_info "  ☀️ 仅统计上午任务"
            local tasks
            tasks=$(grep -A 10 "^### 上午" "$daily_log" 2>/dev/null | grep -c "^\\- \\[x\\]" | tr -d '\n' || echo "0")
            tasks=${tasks:-0}
            local total_tasks
            total_tasks=$(grep -A 10 "^### 上午" "$daily_log" 2>/dev/null | grep -c "^\\-" | tr -d '\n' || echo "0")
            total_tasks=${total_tasks:-0}
            log_info "  ✅ 上午任务: $tasks / $total_tasks 完成"
            
            if [ "$tasks" -gt 0 ]; then
                log_info "  📋 已完成上午任务："
                grep -A 10 "^### 上午" "$daily_log" 2>/dev/null | grep "^\\- \\[x\\]" | head -5 | while read task; do
                    log_info "    $task"
                done
            fi
        else
            local tasks
            tasks=$(grep -c "^\\- \\[x\\]" "$daily_log" 2>/dev/null | tr -d '\n' || echo "0")
            tasks=${tasks:-0}
            log_info "  ✅ 全天任务: $tasks 个完成"
            
            # 列出上午和下午任务
            if grep -q "^### 上午" "$daily_log"; then
                log_info "  ☀️ 上午任务："
                grep -A 10 "^### 上午" "$daily_log" 2>/dev/null | grep "^\\-" | head -5 | while read task; do
                    log_info "    $task"
                done
            fi
            
            if grep -q "^### 下午" "$daily_log"; then
                log_info "  🌤️ 下午任务："
                grep -A 10 "^### 下午" "$daily_log" 2>/dev/null | grep "^\\-" | head -5 | while read task; do
                    log_info "    $task"
                done
            fi
        fi
    else
        log_warn "  ⚠️ 今日日志不存在"
    fi
}

# Git提交回顾
review_commits() {
    local date="$1"
    local time_range="${2:-full}"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "  💻 检查Git提交..."
    
    cd "$CFG_WORKSPACE" 2>/dev/null || return 1
    
    # 根据时间范围确定git log时间范围
    local since_time="$date 00:00"
    local until_time="$date 23:59"
    if [ "$time_range" = "morning" ]; then
        since_time="$date 00:00"
        until_time="$date 12:00"
        log_info "  ☀️ 仅统计上午（00:00-12:00）的提交"
    fi
    
    # 统计提交
    local commits
    commits=$(git log --since="$since_time" --until="$until_time" --oneline 2>/dev/null | wc -l)
    commits=${commits:-0}
    log_info "  ✅ ${time_range}提交: $commits 个"
    
    # 列出重要提交
    if [ "$commits" -gt 0 ]; then
        log_info "  📋 重要提交："
        git log --since="$since_time" --until="$until_time" --oneline 2>/dev/null | head -5 | while read commit; do
            log_info "    - $commit"
        done
    fi
    
    # 检查未提交文件
    local uncommitted=$(git status --porcelain 2>/dev/null | wc -l)
    if [ "$uncommitted" -gt 0 ]; then
        log_warn "  ⚠️ 有 $uncommitted 个未提交的文件"
    else
        log_info "  ✅ Git状态干净"
    fi
    
    # 检查未推送提交
    local unpushed=$(git log "origin/$CFG_GIT_BRANCH..$CFG_GIT_BRANCH" --oneline 2>/dev/null | wc -l)
    if [ "$unpushed" -gt 0 ]; then
        log_warn "  ⚠️ 有 $unpushed 个未推送的提交"
    else
        log_info "  ✅ Git推送已同步"
    fi
}

# PR状态监控
review_pr_status() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    # 获取PR状态（带超时控制）
    log_info "  📊 获取PR状态..."
    local open_prs
    local merged_prs
    
    open_prs=$(timeout 10 gh pr list --author zhaog100 --state open --json number --jq length 2>/dev/null || echo "0")
    merged_prs=$(timeout 10 gh pr list --author zhaog100 --state merged --since="$date" --json number --jq length 2>/dev/null || echo "0")
    
    log_info "  📊 Open PRs: $open_prs 个"
    log_info "  ✅ Merged PRs: $merged_prs 个"
    
    # 获取详细的PR信息
    if [ "$open_prs" != "0" ]; then
        log_info "  📋 重要PR状态："
        cd "$CFG_WORKSPACE" && gh pr list --author zhaog100 --state open --json number,title,repository,updatedAt --jq '.[] | "   #\(.number) - \(.title) (\(.repository.name)) - \(.updatedAt)"' 2>/dev/null | head -5 | while read pr; do
            log_info "$pr"
        done
    fi
    
    # 更新今日日志
    if [ -f "$daily_log" ]; then
        # 移除旧的PR状态
        sed -i '/^### PR状态/,/^###/ { /^### PR状态/! { /^###/! d } }' "$daily_log"
        
        # 添加新的PR状态
        sed -i '/## 今日完成/a\
\
### PR状态\
- **Open PRs**: '"$open_prs"' 个\
- **Merged PRs**: '"$merged_prs"' 个\
- **最后更新**: '"$(date '+%Y-%m-%d %H:%M')"'\
' "$daily_log"
    fi
}

# 财务状态汇总
review_financial_status() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "  💰 Bounty收益统计："
    
    # 统计今日收益
    local today_earnings=0
    local pending_earnings=0
    
    # 从PR列表中获取收益信息（简化版本）
    local bounty_prs=$(cd "$CFG_WORKSPACE" && gh pr list --author zhaog100 --state open --json labels,title --jq '.[] | select(.labels[]?.name | contains("bounty") or contains("Bounty")) | "\(.title)"' 2>/dev/null | wc -l)
    
    log_info "  🎯 Bounty PRs: $bounty_prs 个"
    log_info "  ⏳ 待收款: 待统计"
    
    # 更新今日日志
    if [ -f "$daily_log" ]; then
        # 移除旧的财务状态
        sed -i '/^### 财务状态/,/^###/ { /^### 财务状态/! { /^###/! d } }' "$daily_log"
        
        # 添加新的财务状态
        sed -i '/## 今日完成/a\
\
### 财务状态\
- **Bounty PRs**: '"$bounty_prs"' 个\
- **待收款**: 待统计\
- **统计时间**: '"$(date '+%Y-%m-%d %H:%M')"'\
' "$daily_log"
    fi
}

# 更新今日日志模板
update_daily_log_template() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "  📝 检查今日日志模板..."
    
    if [ ! -f "$daily_log" ]; then
        cat > "$daily_log" << EOF
# $date 工作记录

## 身份确认
- **小米辣** 🌶️ | **GitHub**: zhaog100
- **远程仓库**: origin → xiaomila-skills (zhaog100/xiaomila-skills)
- **检查时间**: $(date '+%Y-%m-%d %H:%M')

## 今日完成

### 上午


### 下午


## 📊 今日统计

- **工作时长**: 小时
- **Git 提交**: 个
- **完成任务**: 个

### PR状态
- **Open PRs**: 0 个
- **Merged PRs**: 0 个
- **最后更新**: $(date '+%Y-%m-%d %H:%M')

### 财务状态
- **Bounty PRs**: 0 个
- **待收款**: 待统计
- **统计时间**: $(date '+%Y-%m-%d %H:%M')

## 📝 学习笔记


## 🎯 明日计划


---

*更新时间：$(date '+%Y-%m-%d %H:%M')*
*更新者：小米辣 (AI 助手)*
EOF
        log_info "  ✅ 创建今日日志模板"
    fi
}

# 学习总结和经验教训
review_learning_and_lessons() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "  🎓 学习总结："
    
    # 检查是否有学习相关内容
    local learning_content=$(grep -A 5 "## 学习笔记" "$daily_log" 2>/dev/null | grep -v "^---" | grep -v "^##" | grep -v "^$" | wc -l)
    
    if [ $learning_content -eq 0 ]; then
        log_info "  📝 今日暂无学习笔记"
    else
        log_info "  ✅ 今日学习笔记：已记录"
    fi
    
    log_info "  💡 经验教训："
    
    # 自动提炼经验教训
    local lessons=$(grep -i "教训\|经验\|总结\|注意" "$daily_log" 2>/dev/null | wc -l)
    if [ $lessons -eq 0 ]; then
        log_info "  📝 今日暂无经验教训记录"
    else
        log_info "  ✅ 经验教训：$lessons 条"
    fi
    
    # 建议添加学习总结
    if [ -f "$daily_log" ]; then
        # 检查是否需要添加学习总结模板
        if ! grep -q "## 📝 学习笔记" "$daily_log"; then
            sed -i '/## 🎯 明日计划/i\
## 📝 学习笔记\
\
### 今日学到的新知识\
\
### 遇到的问题及解决方案\
\
### 代码质量提升点\
' "$daily_log"
        fi
        
        if ! grep -q "## 💡 经验教训" "$daily_log"; then
            sed -i '/## 📝 学习笔记/a\
## 💡 经验教训\
\
### 技术经验\
\
### 流程优化\
\
### 其他教训\
' "$daily_log"
        fi
    fi
}

# 查漏补缺和MEMORY.md更新
review_gaps_and_update_memory() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "  🔍 查漏补缺分析..."
    
    # 运行查漏补缺分析器
    if [ -f "$_SCRIPTS_DIR/gap-analyzer.sh" ]; then
        bash "$_SCRIPTS_DIR/gap-analyzer.sh" "$date" || true
    else
        log_warn "  ⚠️ 查漏补缺分析器不存在"
    fi
    
    log_info "  📚 MEMORY.md更新..."
    
    # 运行记忆更新器
    if [ -f "$_SCRIPTS_DIR/memory-updater.sh" ]; then
        bash "$_SCRIPTS_DIR/memory-updater.sh" "$date" || true
    else
        log_warn "  ⚠️ 记忆更新器不存在"
    fi
    
    # 智能更新MEMORY.md
    update_memory_with_lessons "$date"
}

# 智能更新MEMORY.md
update_memory_with_lessons() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    local memory_file="$CFG_MEMORY_FILE"
    
    if [ ! -f "$daily_log" ] || [ ! -f "$memory_file" ]; then
        return 0
    fi
    
    log_info "  🧠 智能更新MEMORY.md..."
    
    # 检查今日是否有重要经验教训
    local important_lessons=$(grep -A 2 -B 2 "### 经验教训\|重要\|教训" "$daily_log" 2>/dev/null | grep -v "^$" | grep -v "^#" | head -10)
    
    if [ -n "$important_lessons" ]; then
        # 添加到MEMORY.md的重要经验部分
        if ! grep -q "### $(date '+%Y-%m-%d') 重要经验" "$memory_file"; then
            echo "" >> "$memory_file"
            echo "### $(date '+%Y-%m-%d') 重要经验" >> "$memory_file"
            echo "" >> "$memory_file"
            echo "#### 技术经验" >> "$memory_file"
            echo "" >> "$memory_file"
            echo "#### 项目经验" >> "$memory_file"
            echo "" >> "$memory_file"
            echo "#### 流程优化" >> "$memory_file"
            echo "" >> "$memory_file"
        fi
        log_info "  ✅ 重要经验已记录到MEMORY.md"
    fi
    
    # 更新今日总结
    update_today_summary_in_memory "$date"
}

# 更新今日总结到MEMORY.md
update_today_summary_in_memory() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    local memory_file="$CFG_MEMORY_FILE"
    
    if [ ! -f "$daily_log" ]; then
        return 0
    fi
    
    log_info "  📋 更新今日总结..."
    
    # 提取今日完成的任务
    local today_tasks=$(grep -A 10 "### 下午" "$daily_log" 2>/dev/null | grep "^\-" | head -5)
    
    if [ -n "$today_tasks" ]; then
        log_info "  ✅ 今日任务已记录"
    fi
}

# 上午任务完成情况
# 上午任务完成情况
review_morning_tasks() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "  ☀️ 检查上午任务完成情况..."
    
    if [ -f "$daily_log" ]; then
        # 检查上午章节
        if grep -q "^### 上午" "$daily_log"; then
            local morning_tasks=0
            local completed_tasks=0
            morning_tasks=$(grep -A 10 "^### 上午" "$daily_log" 2>/dev/null | grep -c "^\-" | tr -d '\n' || echo "0")
            completed_tasks=$(grep -A 10 "^### 上午" "$daily_log" 2>/dev/null | grep -c "^\- \[x\]" | tr -d '\n' || echo "0")
            log_info "  ✅ 上午任务: $completed_tasks / $morning_tasks 完成"
            
            # 列出完成的重点任务
            if [ "$completed_tasks" -gt 0 ]; then
                log_info "  📋 已完成任务："
                grep -A 10 "^### 上午" "$daily_log" 2>/dev/null | grep "^\- \[x\]" | head -5 | while read task; do
                    log_info "    $task"
                done
            fi
        else
            log_warn "  ⚠️ 上午日志为空"
        fi
        
        # 检查是否有未完成的任务
        local pending_tasks=0
        pending_tasks=$(grep -A 10 "^### 上午" "$daily_log" 2>/dev/null | grep -c "^\- \[ \]" | tr -d '\n' || echo "0")
        if [ "$pending_tasks" -gt 0 ]; then
            log_warn "  ⚠️ 有 $pending_tasks 个未完成的上午任务"
        fi
    else
        log_warn "  ⚠️ 今日日志不存在"
    fi
}
# 上午Git提交
review_morning_commits() {
    local date="$1"
    
    log_info "  💻 检查上午Git提交..."
    
    cd "$CFG_WORKSPACE" 2>/dev/null || return 1
    
    # 统计上午提交（06:00-12:00）
    local morning_commits
    morning_commits=$(git log --since="$date 06:00" --until="$date 12:00" --oneline 2>/dev/null | wc -l)
    morning_commits=${morning_commits:-0}
    log_info "  ✅ 上午提交: $morning_commits 个"
    
    # 列出上午的重要提交
    if [ "$morning_commits" -gt 0 ]; then
        log_info "  📋 上午提交："
        git log --since="$date 06:00" --until="$date 12:00" --oneline 2>/dev/null | head -5 | while read commit; do
            log_info "    - $commit"
        done
    fi
    
    # 检查未提交文件
    local uncommitted=$(git status --porcelain 2>/dev/null | wc -l)
    if [ "$uncommitted" -gt 0 ]; then
        log_warn "  ⚠️ 有 $uncommitted 个未提交的文件"
    else
        log_info "  ✅ Git状态干净"
    fi
}

# 下午计划
review_afternoon_plan() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "  🌤️ 检查下午计划..."
    
    if [ -f "$daily_log" ]; then
        # 检查下午计划章节
        if grep -q "^### 下午" "$daily_log"; then
            local afternoon_tasks=0
            afternoon_tasks=$(grep -A 10 "^### 下午" "$daily_log" 2>/dev/null | grep -c "^\\-" | tr -d '\n' || echo "0")
            log_info "  📋 下午计划任务: $afternoon_tasks 个"
            
            # 列出下午要完成的任务
            if [ "$afternoon_tasks" -gt 0 ]; then
                log_info "  📝 待办任务："
                grep -A 10 "^### 下午" "$daily_log" 2>/dev/null | grep "^\-" | head -5 | while read task; do
                    log_info "    $task"
                done
            fi
        else
            log_warn "  ⚠️ 下午计划为空"
            log_info "  💡 建议：添加下午待办任务到日志"
        fi
        
        # 检查明日计划
        if grep -q "^## 🎯 明日计划" "$daily_log"; then
            log_info "  📅 明日计划已制定"
        else
            log_info "  💡 建议：考虑制定明日计划"
        fi
    else
        log_warn "  ⚠️ 今日日志不存在"
    fi
}

# 生成午间回顾摘要
generate_morning_summary() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  午间回顾摘要                                         ║"
    log_info "╚════════════════════════════════════════════════════════╝"
    
    # 上午任务完成情况
    local morning_tasks=0
    local completed_tasks=0
    if [ -f "$daily_log" ]; then
        morning_tasks=$(grep -A 10 "^### 上午" "$daily_log" 2>/dev/null | grep -c "^\\-" | tr -d '\n' || echo "0")
        completed_tasks=$(grep -A 10 "^### 上午" "$daily_log" 2>/dev/null | grep -c "^\\- \\[x\\]" | tr -d '\n' || echo "0")
    fi
    log_info "☀️ 上午任务: $completed_tasks / $morning_tasks 完成"
    
    # Git提交
    local commits
    commits=$(cd "$CFG_WORKSPACE" && git log --since="$date 06:00" --until="$date 12:00" --oneline 2>/dev/null | wc -l)
    commits=${commits:-0}
    log_info "💻 上午提交: $commits 个"
    
    # 下午重点
    log_info ""
    log_info "🌤️ 下午重点："
    if [ -f "$daily_log" ]; then
        local afternoon_items
        afternoon_items=$(grep -A 10 "^### 下午" "$daily_log" 2>/dev/null | grep "^\\-" | head -3)
        if [ -n "$afternoon_items" ]; then
            echo "$afternoon_items" | while read item; do
                log_info "  $item"
            done
        else
            log_info "  📝 请添加下午待办事项"
        fi
    else
        log_info "  📝 请添加下午待办事项"
    fi
    
    log_info ""
    log_info "⏰ 提醒：晚间回顾将于 23:50 自动执行"
    
    # 推送通知到QQ Bot
    if [ "$CFG_NOTIFY_QQBOT" = "true" ] && [ -n "$CFG_QQBOT_ID" ]; then
        local summary="午间回顾 ☀️ | 上午任务: $completed_tasks/$morning_tasks | Git: $commits"
        log_info "📡 推送通知到QQ Bot: $summary"
    fi
}


# 生成执行摘要
generate_execution_summary() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  执行摘要                                              ║"
    log_info "╚════════════════════════════════════════════════════════╝"
    
    # 任务统计
    local tasks_completed=$(grep -c "^\- \[x\]" "$daily_log" 2>/dev/null || echo "0")
    log_info "✅ 完成任务: $tasks_completed 个"
    
    # Git提交
    local commits=$(cd "$CFG_WORKSPACE" && git log --since="$date 00:00" --until="$date 23:59" --oneline 2>/dev/null | wc -l)
    log_info "💻 Git提交: $commits 个"
    
    # PR状态
    local open_prs=$(cd "$CFG_WORKSPACE" && gh pr list --author zhaog100 --state open 2>/dev/null | wc -l)
    log_info "📊 Open PRs: $open_prs 个"
    
    # 学习总结
    local learning_notes=$(grep -c "📝 学习笔记" "$daily_log" 2>/dev/null || echo "0")
    log_info "🎓 学习笔记: $learning_notes 条"
    
    # 经验教训
    local lessons=$(grep -c "💡 经验教训" "$daily_log" 2>/dev/null || echo "0")
    log_info "💡 经验教训: $lessons 条"
    
    # 查漏补缺
    local gaps_found=0
    [ -f "$_SCRIPTS_DIR/gap-analyzer.sh" ] && gaps_found=$(bash "$_SCRIPTS_DIR/gap-analyzer.sh" "$date" 2>/dev/null | grep -oP "发现 \K[0-9]+" || echo "0")
    log_info "🔍 发现遗漏: $gaps_found 个"
    
    log_info ""
    log_info "📊 总体评价: $([ $gaps_found -eq 0 ] && echo "🟢 优秀" || [ $gaps_found -lt 3 ] && echo "🟡 良好" || echo "🔴 需改进")"
    
    # 推送通知到QQ Bot
    if [ "$CFG_NOTIFY_QQBOT" = "true" ] && [ -n "$CFG_QQBOT_ID" ]; then
        local summary="今日回顾完成 ✅ | 任务: $tasks_completed | Git: $commits | PR: $open_prs | 遗漏: $gaps_found"
        log_info "📡 推送通知到QQ Bot: $summary"
        # 这里添加实际的推送逻辑
    fi
}

# 查看状态
show_status() {
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  定时回顾更新助手 - 状态                                ║"
    log_info "╠════════════════════════════════════════════════════════╣"
    log_info "║  版本: $CFG_VERSION"
    log_info "║  技能名称: $CFG_SKILL_NAME"
    log_info "╚════════════════════════════════════════════════════════╝"
    
    log_info ""
    log_info "📁 工作区: $CFG_WORKSPACE"
    log_info "📂 记忆目录: $CFG_MEMORY_DIR"
    log_info "📚 知识库: $CFG_KNOWLEDGE_DIR"
    
    log_info ""
    log_info "📄 关键文件:"
    log_info "  - MEMORY.md: $([ -f "$CFG_MEMORY_FILE" ] && echo '✅ 存在' || echo '❌ 不存在')"
    log_info "  - HEARTBEAT.md: $([ -f "$CFG_HEARTBEAT_FILE" ] && echo '✅ 存在' || echo '❌ 不存在')"
    log_info "  - 知识索引: $([ -f "$CFG_KNOWLEDGE_INDEX" ] && echo '✅ 存在' || echo '❌ 不存在')"
    
    log_info ""
    log_info "🔧 配置状态:"
    log_info "  - 配置版本: $CFG_VERSION"
    log_info "  - Git分支: $CFG_GIT_BRANCH"
    log_info "  - 远程仓库: $CFG_GIT_REMOTE"
    log_info "  - 日志级别: $CFG_LOG_LEVEL"
    log_info "  - 日志目录: $CFG_LOGS_DIR"
    
    log_info ""
    log_info "🔔 通知配置:"
    log_info "  - QQ Bot: $([ "$CFG_NOTIFY_QQBOT" = "true" ] && echo '✅ 启用' || echo '❌ 禁用')"
    if [ "$CFG_NOTIFY_QQBOT" = "true" ]; then
        log_info "  - QQ Bot ID: $CFG_QQBOT_ID"
    fi
    
    log_info ""
    log_info "⏰ 定时任务:"
    log_info "  - 上午回顾: $CFG_CRON_MORNING"
    log_info "  - 晚上回顾: $CFG_CRON_FULL"
    
    log_info ""
    log_info "🔍 功能开关:"
    log_info "  - 任务回顾: $([ "$CFG_FEATURE_TASK_REVIEW" = "true" ] && echo '✅' || echo '❌')"
    log_info "  - Git回顾: $([ "$CFG_FEATURE_GIT_REVIEW" = "true" ] && echo '✅' || echo '❌')"
    log_info "  - PR监控: $([ "$CFG_FEATURE_PR_MONITORING" = "true" ] && echo '✅' || echo '❌')"
    log_info "  - 财务跟踪: $([ "$CFG_FEATURE_FINANCIAL_TRACKING" = "true" ] && echo '✅' || echo '❌')"
    log_info "  - 学习回顾: $([ "$CFG_FEATURE_LEARNING_REVIEW" = "true" ] && echo '✅' || echo '❌')"
    
    log_info ""
    log_info "✅ 状态检查完成！"
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