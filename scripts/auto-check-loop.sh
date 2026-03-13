#!/bin/bash
# 自动检查循环脚本 - 每 1 分钟检查所有 Git 内容
# 确保正确接收小米粒提供的信息

WORKSPACE="/home/zhaog/.openclaw/workspace"
INBOX="$WORKSPACE/.mili_comm/inbox"
OUTBOX="$WORKSPACE/.mili_comm/outbox"
LOG_FILE="/tmp/auto-check.log"
REPO="zhaog100/openclaw-skills"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查 GitHub Issues 新评论
check_github_issues() {
    log "🔍 检查 GitHub Issues..."
    
    # 获取所有 Open Issues
    local issues=$(gh issue list --repo $REPO --state open --limit 30 2>/dev/null)
    
    if [ -n "$issues" ]; then
        # 检查每个 Issue 的最新评论
        echo "$issues" | while read -r line; do
            local issue_num=$(echo "$line" | awk '{print $1}')
            local issue_title=$(echo "$line" | cut -f2-)
            
            # 获取 Issue 评论（最近 5 条）
            local comments=$(gh issue view $REPO#$issue_num --comments --limit 5 2>/dev/null)
            
            # 检查是否有小米粒的评论（包含"小米粒"签名）
            if echo "$comments" | grep -q "小米粒"; then
                log "📬 Issue #$issue_num: 发现小米粒的新评论！"
                echo "📬 Issue #$issue_num: 小米粒回复了！" > /tmp/notify_mili.txt
                echo "$comments" > /tmp/mili_comment_$issue_num.txt
            fi
        done
    fi
}

# 检查 Git 提交记录
check_git_commits() {
    log "🔍 检查 Git 提交记录..."
    
    cd "$WORKSPACE"
    
    # 获取最近 5 个提交
    local commits=$(git log --oneline -5 2>/dev/null)
    
    # 检查是否有新提交（包含"小米粒"或特定标记）
    if echo "$commits" | grep -q "小米粒\|xiaomili"; then
        log "📝 发现小米粒的新 Git 提交！"
        echo "📝 小米粒提交了新代码！" > /tmp/notify_mili.txt
    fi
    
    # 检查是否有未推送的提交
    local unpushed=$(git log origin/master..master --oneline 2>/dev/null | wc -l)
    if [ "$unpushed" -gt 0 ]; then
        log "⚠️ 有 $unpushed 个未推送的提交"
    fi
}

# 检查 inbox 新文件
check_inbox() {
    log "🔍 检查 inbox 新文件..."
    
    local new_inbox=$(find "$INBOX" -name "*.md" -mmin -2 2>/dev/null | wc -l)
    if [ "$new_inbox" -gt 0 ]; then
        log "⚠️ 发现 $new_inbox 个新 inbox 文件！"
        echo "📬 小米粒回复了！inbox 有新文件！" > /tmp/notify_mili.txt
        
        # 显示新文件内容
        find "$INBOX" -name "*.md" -mmin -2 -exec cat {} \; 2>/dev/null
    fi
}

# 检查 outbox 确认发送
check_outbox() {
    log "🔍 检查 outbox 文件..."
    
    local new_outbox=$(find "$OUTBOX" -name "*.md" -mmin -2 2>/dev/null | wc -l)
    if [ "$new_outbox" -gt 0 ]; then
        log "📤 发现 $new_outbox 个新 outbox 文件"
    fi
}

# 检查 pending-skills-list.md 更新
check_pending_skills() {
    log "🔍 检查待开发技能清单..."
    
    cd "$WORKSPACE"
    
    # 检查文件是否有未提交的更改
    local changes=$(git status docs/pending-skills-list.md --porcelain 2>/dev/null)
    if [ -n "$changes" ]; then
        log "📋 pending-skills-list.md 有未提交的更改"
    fi
}

# 主循环
log "🔄 自动检查循环启动（每 1 分钟检查所有 Git 内容）"
log "📋 检查项：GitHub Issues + Git 提交 + inbox/outbox + pending-skills-list"

while true; do
    check_github_issues
    check_git_commits
    check_inbox
    check_outbox
    check_pending_skills
    log "✅ 检查完成，等待下一轮（60 秒）..."
    sleep 60
done
