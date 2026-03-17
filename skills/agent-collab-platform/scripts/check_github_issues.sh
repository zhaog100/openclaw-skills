#!/bin/bash
# GitHub Issues 主动检查脚本
# 用于心跳系统调用，1 分钟自动轮询

cd $(pwd)/skills/agent-collab-platform

# 配置
REPO="zhaog100/openclaw-skills"
LAST_CHECK_FILE="logs/last_check_time"
CHECK_INTERVAL=120  # 秒（2 分钟轮询）

# 捕获中断信号
trap 'echo "🛑 停止检查"; exit 0' SIGINT SIGTERM

# 主循环：1 分钟轮询
echo "🚀 开始 GitHub Issues 轮询（每$CHECK_INTERVAL 秒）..."

while true; do

# 获取上次检查时间
if [ -f "$LAST_CHECK_FILE" ]; then
    LAST_CHECK=$(cat "$LAST_CHECK_FILE")
else
    LAST_CHECK="2026-01-01T00:00:00Z"
fi

# 获取当前时间（ISO 8601格式）
CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# 检查最近更新的Issues
echo "🔍 检查GitHub Issues（$LAST_CHECK 之后）..."

# 获取最近更新的Issues
RECENT_ISSUES=$(gh issue list --repo "$REPO" --state open --limit 10 --json number,title,updatedAt --jq ".[] | select(.updatedAt > \"$LAST_CHECK\") | .number")

if [ -z "$RECENT_ISSUES" ]; then
    echo "✅ 无新更新"
    echo "$CURRENT_TIME" > "$LAST_CHECK_FILE"
    exit 0
fi

# 检查每个Issue的最新评论
NEW_COMMENTS=0
for ISSUE_NUM in $RECENT_ISSUES; do
    echo "📋 检查 Issue #$ISSUE_NUM..."
    
    # 获取最新评论
    LATEST_COMMENT=$(gh issue view "$ISSUE_NUM" --repo "$REPO" --json comments --jq ".comments[-1] | {time: .createdAt, user: .author.login, body: .body[0:100]}")
    
    COMMENT_TIME=$(echo "$LATEST_COMMENT" | jq -r '.time')
    COMMENT_USER=$(echo "$LATEST_COMMENT" | jq -r '.user')
    
    # 检查是否是小米辣的评论
    if [ "$COMMENT_TIME" \> "$LAST_CHECK" ]; then
        echo "  🆕 新评论！用户: $COMMENT_USER, 时间: $COMMENT_TIME"
        NEW_COMMENTS=$((NEW_COMMENTS + 1))
        
        # 触发通知（写入通知文件）
        mkdir -p logs
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Issue #$ISSUE_NUM 有新评论（用户: $COMMENT_USER）" >> logs/new_comments.log
    fi
done

# 更新检查时间
echo "$CURRENT_TIME" > "$LAST_CHECK_FILE"

# 输出结果
if [ $NEW_COMMENTS -gt 0 ]; then
    echo "⚠️ 发现 $NEW_COMMENTS 个新评论！请查看 logs/new_comments.log"
else
    echo "✅ 检查完成，无新评论"
fi

# 等待下一轮检查
echo "⏰ 等待$CHECK_INTERVAL 秒（2 分钟）后下一轮检查..."
sleep $CHECK_INTERVAL
done
