# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/bin/bash
# =============================================================================
# 查漏补缺分析器 (Gap Analyzer) - 优化版
# =============================================================================
set -e
# 版本：v2.0
# 创建时间：2026-05-09
# 创建者：小米辣
# 用途：检查记忆、知识、Git、PR、财务等全方位遗漏
# 许可证：MIT License
# 版权：Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载配置
source "$SCRIPT_DIR/lib/config.sh"
_CURRENT_LOG_FILE="$CFG_LOGS_DIR/gap-analyzer.log"

# 主检查函数
analyze_all_gaps() {
    local date="$1"
    
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  查漏补缺分析器 v2.0 - 小米辣                            ║"
    log_info "╚════════════════════════════════════════════════════════╝"
    
    local total_gaps=0
    
    log_info ""
    log_info "🔍 开始全方位检查..."
    
    # 1. 记忆系统检查
    log_info ""
    log_info "📋 1. 记忆系统检查"
    check_memory_gaps "$date"
    local memory_gaps=$?
    total_gaps=$((total_gaps + memory_gaps))
    
    # 2. 知识库检查
    log_info ""
    log_info "📚 2. 知识库检查"
    check_knowledge_gaps "$date"
    local knowledge_gaps=$?
    total_gaps=$((total_gaps + knowledge_gaps))
    
    # 3. Git状态检查
    log_info ""
    log_info "💻 3. Git状态检查"
    check_git_gaps "$date"
    local git_gaps=$?
    total_gaps=$((total_gaps + git_gaps))
    
    # 4. PR状态检查
    log_info ""
    log_info "📊 4. PR状态检查"
    check_pr_gaps "$date"
    local pr_gaps=$?
    total_gaps=$((total_gaps + pr_gaps))
    
    # 5. 财务状态检查
    log_info ""
    log_info "💰 5. 财务状态检查"
    check_financial_gaps "$date"
    local financial_gaps=$?
    total_gaps=$((total_gaps + financial_gaps))
    
    # 6. 系统状态检查
    log_info ""
    log_info "🔧 6. 系统状态检查"
    check_system_gaps "$date"
    local system_gaps=$?
    total_gaps=$((total_gaps + system_gaps))
    
    # 7. 学习进度检查
    log_info ""
    log_info "🎓 7. 学习进度检查"
    check_learning_gaps "$date"
    local learning_gaps=$?
    total_gaps=$((total_gaps + learning_gaps))
    
    # 生成综合报告
    log_info ""
    generate_comprehensive_report "$date" "$memory_gaps" "$knowledge_gaps" "$git_gaps" "$pr_gaps" "$financial_gaps" "$system_gaps" "$learning_gaps" "$total_gaps"
    
    return $total_gaps
}

# 检查记忆遗漏
check_memory_gaps() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "  📝 检查记忆系统完整性..."
    
    local gaps=0
    
    # 检查今日日志
    if [ ! -f "$daily_log" ]; then
        log_warn "  ⚠️ 今日日志不存在：$daily_log"
        gaps=$((gaps + 1))
    else
        log_info "  ✅ 今日日志：已创建"
        
        # 检查日志结构完整性
        local structure_gaps=0
        grep -q "## 今日完成" "$daily_log" || structure_gaps=$((structure_gaps + 1))
        grep -q "## 📊 今日统计" "$daily_log" || structure_gaps=$((structure_gaps + 1))
        grep -q "## 📝 学习笔记" "$daily_log" || structure_gaps=$((structure_gaps + 1))
        grep -q "## 💡 经验教训" "$daily_log" || structure_gaps=$((structure_gaps + 1))
        grep -q "## 🎯 明日计划" "$daily_log" || structure_gaps=$((structure_gaps + 1))
        
        if [ $structure_gaps -gt 0 ]; then
            log_warn "  ⚠️ 日志结构不完整：缺少 $structure_gaps 个章节"
            gaps=$((gaps + structure_gaps))
        else
            log_info "  ✅ 日志结构：完整"
        fi
        
        # 检查内容填充情况
        local content_score=$(check_daily_log_content "$daily_log")
        if [ $content_score -lt 3 ]; then
            log_warn "  ⚠️ 日志内容不够充实：评分 $content_score/10"
            gaps=$((gaps + 1))
        else
            log_info "  ✅ 日志内容：充实（评分 $content_score/10）"
        fi
    fi
    
    # 检查MEMORY.md
    if [ -f "$CFG_MEMORY_FILE" ]; then
        local last_modified=$(stat -c %Y "$CFG_MEMORY_FILE" 2>/dev/null || echo "0")
        local now=$(date +%s)
        local hours_ago=$(( (now - last_modified) / 3600 ))
        
        if [ $hours_ago -gt "$CFG_THRESHOLD_MEMORY_STALE" ]; then
            log_warn "  ⚠️ MEMORY.md 超过 ${CFG_THRESHOLD_MEMORY_STALE} 小时未更新（${hours_ago}小时前）"
            gaps=$((gaps + 1))
        else
            log_info "  ✅ MEMORY.md：已更新（${hours_ago}小时前）"
        fi
        
        # 检查MEMORY.md内容质量
        local memory_quality=$(check_memory_quality "$CFG_MEMORY_FILE")
        if [ $memory_quality -lt 5 ]; then
            log_warn "  ⚠️ MEMORY.md 内容质量较低"
            gaps=$((gaps + 1))
        fi
    else
        log_warn "  ⚠️ MEMORY.md 不存在"
        gaps=$((gaps + 1))
    fi
    
    # 检查HEARTBEAT.md
    if [ -f "$CFG_HEARTBEAT_FILE" ]; then
        local last_modified=$(stat -c %Y "$CFG_HEARTBEAT_FILE" 2>/dev/null || echo "0")
        local now=$(date +%s)
        local hours_ago=$(( (now - last_modified) / 3600 ))
        
        if [ $hours_ago -gt "$CFG_THRESHOLD_HEARTBEAT_STALE" ]; then
            log_warn "  ⚠️ HEARTBEAT.md 超过 ${CFG_THRESHOLD_HEARTBEAT_STALE} 小时未更新（${hours_ago}小时前）"
            gaps=$((gaps + 1))
        else
            log_info "  ✅ HEARTBEAT.md：已更新（${hours_ago}小时前）"
        fi
    fi
    
    log_info "  📊 记忆系统检查：发现 $gaps 个问题"
    return $gaps
}

# 检查知识库遗漏
check_knowledge_gaps() {
    local date="$1"
    
    log_info "  📚 检查知识库完整性..."
    
    local gaps=0
    
    # 检查知识库目录
    if [ -d "$CFG_KNOWLEDGE_DIR" ]; then
        local today_files=$(find "$CFG_KNOWLEDGE_DIR" -name "*.md" -mtime -1 2>/dev/null | wc -l)
        
        if [ $today_files -eq 0 ]; then
            log_warn "  ⚠️ 今日无新知识文档"
            gaps=$((gaps + 1))
        else
            log_info "  ✅ 今日知识文档：$today_files 个"
        fi
        
        # 检查知识库结构
        local index_files=$(find "$CFG_KNOWLEDGE_DIR" -name "INDEX.md" -o -name "README.md" 2>/dev/null | wc -l)
        if [ $index_files -eq 0 ]; then
            log_warn "  ⚠️ 知识库缺少索引文件"
            gaps=$((gaps + 1))
        fi
        
        # 检查知识库更新频率
        local recent_files=$(find "$CFG_KNOWLEDGE_DIR" -name "*.md" -mtime -7 2>/dev/null | wc -l)
        if [ $recent_files -lt 3 ]; then
            log_warn "  ⚠️ 知识库更新频率较低（7天内仅 $recent_files 个文件）"
            gaps=$((gaps + 1))
        fi
    else
        log_warn "  ⚠️ 知识库目录不存在：$CFG_KNOWLEDGE_DIR"
        gaps=$((gaps + 1))
    fi
    
    # 检查知识库索引
    if [ -f "$CFG_KNOWLEDGE_INDEX" ]; then
        log_info "  ✅ 知识索引：已创建"
        
        # 检查索引完整性
        local index_content=$(wc -l < "$CFG_KNOWLEDGE_INDEX")
        if [ $index_content -lt 10 ]; then
            log_warn "  ⚠️ 知识索引内容较少（仅 $index_content 行）"
            gaps=$((gaps + 1))
        fi
    else
        log_warn "  ⚠️ 知识索引不存在"
        gaps=$((gaps + 1))
    fi
    
    log_info "  📊 知识库检查：发现 $gaps 个问题"
    return $gaps
}

# 检查Git遗漏
check_git_gaps() {
    local date="$1"
    
    log_info "  💻 检查Git状态..."
    
    local gaps=0
    
    cd "$CFG_WORKSPACE" 2>/dev/null || return 1
    
    # 检查未提交文件
    local uncommitted=$(git status --porcelain 2>/dev/null | wc -l)
    
    if [ $uncommitted -gt 0 ]; then
        log_warn "  ⚠️ 有 $uncommitted 个未提交的文件"
        git status --porcelain 2>/dev/null | head -5 | while read status; do
            log_info "    - $status"
        done
        gaps=$((gaps + 1))
    else
        log_info "  ✅ Git 状态：干净"
    fi
    
    # 检查未推送提交
    local unpushed=$(git log "origin/$CFG_GIT_BRANCH..$CFG_GIT_BRANCH" --oneline 2>/dev/null | wc -l)
    
    if [ $unpushed -gt 0 ]; then
        log_warn "  ⚠️ 有 $unpushed 个未推送的提交"
        gaps=$((gaps + 1))
    else
        log_info "  ✅ Git 推送：已同步"
    fi
    
    # 检查今日提交
    local today_commits=$(git log --since="$date 00:00" --until="$date 23:59" --oneline 2>/dev/null | wc -l)
    log_info "  ✅ 今日提交：$today_commits 个"
    
    # 检查分支状态
    local branches=$(git branch --list 2>/dev/null | wc -l)
    local remote_branches=$(git branch -r 2>/dev/null | wc -l)
    
    if [ $branches -gt 10 ]; then
        log_warn "  ⚠️ 本地分支较多（$branches 个），建议清理"
        gaps=$((gaps + 1))
    fi
    
    # 检查大文件
    local large_files=$(git ls-files | xargs ls -lh 2>/dev/null | awk '{print $5}' | grep -E '^[0-9]+[M|G]' | wc -l)
    if [ $large_files -gt 0 ]; then
        log_warn "  ⚠️ 发现 $large_files 个大文件"
        gaps=$((gaps + 1))
    fi
    
    log_info "  📊 Git检查：发现 $gaps 个问题"
    return $gaps
}

# 检查PR遗漏
check_pr_gaps() {
    local date="$1"
    
    log_info "  📊 检查PR状态..."
    
    local gaps=0
    
    cd "$CFG_WORKSPACE" 2>/dev/null || return 1
    
    # 检查Open PRs
    local open_prs=$(gh pr list --author "$CFG_GITHUB_USERNAME" --state open 2>/dev/null | wc -l)
    
    if [ "$open_prs" != "0" ]; then
        log_info "  📋 Open PRs: $open_prs 个"
        
        # 检查是否有长时间未更新的PR
        local stale_prs
        stale_prs=$(gh pr list --author "$CFG_GITHUB_USERNAME" --state open --json updatedAt --jq ".[] | select(.updatedAt < \"$(date -d '180 days ago' +%Y-%m-%d)\")" 2>/dev/null | wc -l)
        stale_prs=${stale_prs:-0}
        if [ $stale_prs -gt 0 ]; then
            log_warn "  ⚠️ 有 $stale_prs 个PR长时间未更新"
            gaps=$((gaps + stale_prs))
        fi
        
        # 检查PR审核状态
        local review_required_prs
        review_required_prs=$(gh pr list --author "$CFG_GITHUB_USERNAME" --state open --json reviewDecision --jq '.[] | select(.reviewDecision == "REVIEW_REQUIRED")' 2>/dev/null | wc -l)
        review_required_prs=${review_required_prs:-0}
        if [ $review_required_prs -gt 0 ]; then
            log_warn "  ⚠️ 有 $review_required_prs 个PR需要审核"
            gaps=$((gaps + 1))
        fi
    fi
    
    # 检查已合并但未关闭的PR
    local merged_prs=$(gh pr list --author "$CFG_GITHUB_USERNAME" --state merged 2>/dev/null | wc -l)
    log_info "  ✅ Merged PRs: $merged_prs 个"
    
    # 检查是否有PR冲突
    local conflict_prs=$(gh pr list --author "$CFG_GITHUB_USERNAME" --state open --json mergeable --jq '.[] | select(.mergeable == "CONFLICTING")' 2>/dev/null | wc -l)
    if [ $conflict_prs -gt 0 ]; then
        log_warn "  ⚠️ 有 $conflict_prs 个PR存在冲突"
        gaps=$((gaps + conflict_prs))
    fi
    
    # 检查PR描述完整性
    local incomplete_prs=$(gh pr list --author "$CFG_GITHUB_USERNAME" --state open --json body --jq '.[] | select(.body | length < 50)' 2>/dev/null | wc -l)
    if [ $incomplete_prs -gt 0 ]; then
        log_warn "  ⚠️ 有 $incomplete_prs 个PR描述不够详细"
        gaps=$((gaps + 1))
    fi
    
    log_info "  📊 PR检查：发现 $gaps 个问题"
    return $gaps
}

# 检查财务遗漏
check_financial_gaps() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "  💰 检查财务状态..."
    
    local gaps=0
    
    # 检查是否有财务记录
    if [ ! -f "$daily_log" ]; then
        log_warn "  ⚠️ 今日日志不存在，无法检查财务记录"
        gaps=$((gaps + 1))
        return $gaps
    fi
    
    # 检查财务章节
    if grep -q "## 💰 财务状态" "$daily_log"; then
        log_info "  ✅ 财务章节：已创建"
        
        # 检查是否有收益记录
        local bounty_info=$(grep -A 5 "## 💰 财务状态" "$daily_log" 2>/dev/null)
        if [ -z "$bounty_info" ] || echo "$bounty_info" | grep -q "Bounty PRs: 0"; then
            log_warn "  ⚠️ 今日无Bounty收益记录"
            gaps=$((gaps + 1))
        else
            log_info "  ✅ Bounty收益：已记录"
        fi
        
        # 检查待收款项目
        local pending_info=$(grep -A 5 "待收款" "$daily_log" 2>/dev/null)
        if [ -z "$pending_info" ]; then
            log_warn "  ⚠️ 待收款信息不完整"
            gaps=$((gaps + 1))
        fi
    else
        log_warn "  ⚠️ 缺少财务章节"
        gaps=$((gaps + 1))
    fi
    
    # 检查付款状态
    local payment_issues=$(grep -i "付款\|支付" "$daily_log" 2>/dev/null | wc -l)
    if [ $payment_issues -eq 0 ]; then
        log_warn "  ⚠️ 未检查付款状态"
        gaps=$((gaps + 1))
    fi
    
    log_info "  📊 财务检查：发现 $gaps 个问题"
    return $gaps
}

# 检查系统状态遗漏
check_system_gaps() {
    local date="$1"
    
    log_info "  🔧 检查系统状态..."
    
    local gaps=0
    
    # 检查磁盘空间
    local disk_usage=$(df -h "$CFG_WORKSPACE" 2>/dev/null | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $disk_usage -gt 80 ]; then
        log_warn "  ⚠️ 磁盘使用率较高：${disk_usage}%"
        gaps=$((gaps + 1))
    else
        log_info "  ✅ 磁盘空间：正常（${disk_usage}%）"
    fi
    
    # 检查内存使用
    local memory_usage=$(free 2>/dev/null | awk 'NR==2{printf "%.0f", $3*100/$2 }')
    if [ $memory_usage -gt 85 ]; then
        log_warn "  ⚠️ 内存使用率较高：${memory_usage}%"
        gaps=$((gaps + 1))
    else
        log_info "  ✅ 内存使用：正常（${memory_usage}%）"
    fi
    
    # 检查OpenClaw服务
    local openclaw_processes=$(pgrep -f "openclaw" 2>/dev/null | wc -l)
    if [ $openclaw_processes -eq 0 ]; then
        log_warn "  ⚠️ OpenClaw服务未运行"
        gaps=$((gaps + 1))
    else
        log_info "  ✅ OpenClaw服务：运行中（$openclaw_processes 个进程）"
    fi
    
    # 检查cron任务
    local cron_count=$(crontab -l 2>/dev/null | grep "daily-review" | wc -l)
    if [ $cron_count -eq 0 ]; then
        log_warn "  ⚠️ 定时任务未配置"
        gaps=$((gaps + 1))
    else
        log_info "  ✅ 定时任务：已配置（$cron_count 个）"
    fi
    
    log_info "  📊 系统检查：发现 $gaps 个问题"
    return $gaps
}

# 检查学习进度遗漏
check_learning_gaps() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "  🎓 检查学习进度..."
    
    local gaps=0
    
    if [ ! -f "$daily_log" ]; then
        log_warn "  ⚠️ 今日日志不存在"
        gaps=$((gaps + 1))
        return $gaps
    fi
    
    # 检查学习笔记
    if grep -q "## 📝 学习笔记" "$daily_log"; then
        local learning_content=$(grep -A 10 "## 📝 学习笔记" "$daily_log" 2>/dev/null | grep -v "^#" | grep -v "^$" | wc -l)
        
        if [ $learning_content -eq 0 ]; then
            log_warn "  ⚠️ 学习笔记为空"
            gaps=$((gaps + 1))
        else
            log_info "  ✅ 学习笔记：已记录（$learning_content 条）"
        fi
        
        # 检查学习内容分类
        local has_new_knowledge=$(grep -q "### 今日学到的新知识" "$daily_log" && echo "true" || echo "false")
        local has_problems=$(grep -q "### 遇到的问题及解决方案" "$daily_log" && echo "true" || echo "false")
        local has_quality=$(grep -q "### 代码质量提升点" "$daily_log" && echo "true" || echo "false")
        
        if [ "$has_new_knowledge" = "false" ] || [ "$has_problems" = "false" ]; then
            log_warn "  ⚠️ 学习笔记分类不完整"
            gaps=$((gaps + 1))
        fi
    else
        log_warn "  ⚠️ 缺少学习笔记章节"
        gaps=$((gaps + 1))
    fi
    
    # 检查经验教训
    if grep -q "## 💡 经验教训" "$daily_log"; then
        local lessons_content=$(grep -A 10 "## 💡 经验教训" "$daily_log" 2>/dev/null | grep -v "^#" | grep -v "^$" | wc -l)
        
        if [ $lessons_content -eq 0 ]; then
            log_warn "  ⚠️ 经验教训为空"
            gaps=$((gaps + 1))
        else
            log_info "  ✅ 经验教训：已记录（$lessons_content 条）"
        fi
    else
        log_warn "  ⚠️ 缺少经验教训章节"
        gaps=$((gaps + 1))
    fi
    
    # 检查技能学习进度
    local skill_progress=$(find "$CFG_KNOWLEDGE_DIR" -name "*.md" -newer "$daily_log" 2>/dev/null | wc -l)
    if [ $skill_progress -eq 0 ]; then
        log_warn "  ⚠️ 今日无新技能学习记录"
        # 不增加gaps，因为不是每天都必须学习新技能
    else
        log_info "  ✅ 技能学习：$skill_progress 个新文档"
    fi
    
    log_info "  📊 学习检查：发现 $gaps 个问题"
    return $gaps
}

# 检查每日日志内容质量
check_daily_log_content() {
    local daily_log="$1"
    local score=0
    
    # 检查任务完成情况
    local tasks_completed
    tasks_completed=$(grep -c "^\\- \\[x\\]" "$daily_log" 2>/dev/null | tr -d '\n' || echo "0")
    tasks_completed=${tasks_completed:-0}
    if [ "$tasks_completed" -gt 0 ]; then
        score=$((score + 3))
    fi
    
    # 检查学习笔记
    local learning_content=$(grep -A 10 "## 📝 学习笔记" "$daily_log" 2>/dev/null | grep -v "^#" | grep -v "^$" | wc -l)
    if [ $learning_content -gt 0 ]; then
        score=$((score + 3))
    fi
    
    # 检查经验教训
    local lessons_content=$(grep -A 10 "## 💡 经验教训" "$daily_log" 2>/dev/null | grep -v "^#" | grep -v "^$" | wc -l)
    if [ $lessons_content -gt 0 ]; then
        score=$((score + 2))
    fi
    
    # 检查财务记录
    local financial_content=$(grep -A 5 "## 💰 财务状态" "$daily_log" 2>/dev/null | grep -v "^#" | grep -v "^$" | wc -l)
    if [ $financial_content -gt 0 ]; then
        score=$((score + 2))
    fi
    
    echo $score
}

# 检查MEMORY.md质量
check_memory_quality() {
    local memory_file="$1"
    local score=0
    
    # 检查文件长度
    local file_lines=$(wc -l < "$memory_file")
    if [ $file_lines -gt 50 ]; then
        score=$((score + 2))
    fi
    
    # 检查更新时间
    local last_update=$(grep -oP '最后更新：\K[0-9-]+' "$memory_file" 2>/dev/null || echo "2000-01-01")
    local update_date=$(date -d "$last_update" +%s 2>/dev/null || echo "0")
    local now=$(date +%s)
    local days_ago=$(( (now - update_date) / 86400 ))
    
    if [ $days_ago -lt 7 ]; then
        score=$((score + 3))
    elif [ $days_ago -lt 30 ]; then
        score=$((score + 2))
    fi
    
    # 检查内容分类
    local categories
    categories=$(grep -c "^## [A-Za-z]" "$memory_file" 2>/dev/null | tr -d '\n' || echo "0")
    categories=${categories:-0}
    if [ "$categories" -gt 5 ]; then
        score=$((score + 2))
    fi
    
    # 检查待办事项
    local todos=$(grep -c "^\- \[ \]" "$memory_file" 2>/dev/null || echo "0")
    if [ $todos -gt 0 ]; then
        score=$((score + 1))
    fi
    
    echo $score
}

# 生成综合报告
generate_comprehensive_report() {
    local date="$1"
    local memory_gaps="$2"
    local knowledge_gaps="$3"
    local git_gaps="$4"
    local pr_gaps="$5"
    local financial_gaps="$6"
    local system_gaps="$7"
    local learning_gaps="$8"
    local total_gaps="$9"
    
    log_info ""
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  综合查漏补缺报告                                        ║"
    log_info "╠════════════════════════════════════════════════════════╣"
    log_info "║  日期：$date"
    log_info "║  身份：小米辣 🌶️ | GitHub: $CFG_GITHUB_USERNAME"
    log_info "╠════════════════════════════════════════════════════════╣"
    
    # 按严重程度排序
    local critical_gaps=$((memory_gaps + system_gaps))
    local warning_gaps=$((knowledge_gaps + git_gaps + pr_gaps))
    local info_gaps=$((financial_gaps + learning_gaps))
    
    log_info "🔴 严重问题：$critical_gaps 个"
    log_info "🟡 警告问题：$warning_gaps 个"
    log_info "🔵 提醒事项：$info_gaps 个"
    log_info "════════════════════════════════════════════════════════"
    log_info "📊 总计：$total_gaps 个"
    
    if [ $critical_gaps -gt 0 ]; then
        log_info ""
        log_info "🔴 需要立即处理："
        [ $memory_gaps -gt 0 ] && log_info "  - 记忆系统问题：$memory_gaps 个"
        [ $system_gaps -gt 0 ] && log_info "  - 系统状态问题：$system_gaps 个"
    fi
    
    if [ $warning_gaps -gt 0 ]; then
        log_info ""
        log_info "🟡 建议尽快处理："
        [ $pr_gaps -gt 0 ] && log_info "  - PR状态问题：$pr_gaps 个"
        [ $git_gaps -gt 0 ] && log_info "  - Git状态问题：$git_gaps 个"
        [ $knowledge_gaps -gt 0 ] && log_info "  - 知识库问题：$knowledge_gaps 个"
    fi
    
    log_info ""
    log_info "╚════════════════════════════════════════════════════════╝"
    
    if [ $total_gaps -eq 0 ]; then
        log_info "🎉 完美！没有发现遗漏！"
        return 0
    elif [ $total_gaps -lt 5 ]; then
        log_info "👍 良好！发现的问题可以快速处理"
        return 1
    else
        log_info "⚠️ 需要重视！发现较多问题，建议逐一处理"
        return 2
    fi
}

# 主函数
main() {
    local date="${1:-$(date +%Y-%m-%d)}"
    
    analyze_all_gaps "$date"
}

main "$@"