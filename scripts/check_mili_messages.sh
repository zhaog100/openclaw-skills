#!/bin/bash
# 自动检查米粒儿新消息脚本
# 用法：bash scripts/check_mili_messages.sh
# 作者：小米粒
# 版本：v1.0.0

set -e

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="/tmp/mili_message_check.log"
LAST_CHECK_FILE="/tmp/mili_last_check_time.txt"

# 获取上次检查时间
if [ -f "$LAST_CHECK_FILE" ]; then
    LAST_CHECK=$(cat "$LAST_CHECK_FILE")
else
    LAST_CHECK="2026-03-12T00:00:00Z"
fi

# 记录本次检查时间
CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "$CURRENT_TIME" > "$LAST_CHECK_FILE"

echo "========================================" | tee -a "$LOG_FILE"
echo "检查时间：$(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

cd "$WORKSPACE"

# 1. Git拉取最新代码
echo "" | tee -a "$LOG_FILE"
echo "[1/3] 检查Git更新..." | tee -a "$LOG_FILE"
GIT_RESULT=$(git pull origin master 2>&1)
if echo "$GIT_RESULT" | grep -q "Already up to date"; then
    echo "✅ Git仓库：无新提交" | tee -a "$LOG_FILE"
    GIT_NEW="no"
else
    echo "✅ Git仓库：有新提交" | tee -a "$LOG_FILE"
    echo "$GIT_RESULT" | tee -a "$LOG_FILE"
    GIT_NEW="yes"
fi

# 2. 检查GitHub Issues新评论
echo "" | tee -a "$LOG_FILE"
echo "[2/3] 检查GitHub Issues..." | tee -a "$LOG_FILE"

ISSUES=$(gh issue list --state open --json number,title,updatedAt --jq '.[] | "\(.number)|\(.title)|\(.updatedAt)"' 2>/dev/null)

NEW_COMMENTS=""

while IFS='|' read -r ISSUE_NUM ISSUE_TITLE ISSUE_UPDATED; do
    # 检查是否有更新
    if [[ "$ISSUE_UPDATED" > "$LAST_CHECK" ]]; then
        echo "✅ Issue #$ISSUE_NUM 有更新：$ISSUE_TITLE" | tee -a "$LOG_FILE"

        # 获取最新评论
        LATEST_COMMENT=$(gh api "repos/zhaog100/openclaw-skills/issues/$ISSUE_NUM/comments" \
            --jq ".[-1] | {user: .user.login, created: .created_at, body: .body[0:200]}" 2>/dev/null)

        if [ -n "$LATEST_COMMENT" ] && [ "$LATEST_COMMENT" != "null" ]; then
            COMMENT_USER=$(echo "$LATEST_COMMENT" | jq -r '.user' 2>/dev/null)
            COMMENT_TIME=$(echo "$LATEST_COMMENT" | jq -r '.created' 2>/dev/null)

            # 检查评论内容（通过签名区分米粒儿和小米粒）
            COMMENT_BODY=$(echo "$LATEST_COMMENT" | jq -r '.body' 2>/dev/null)

            # 米粒儿的评论包含 "*米粒儿 -" 但不包含 "*小米粒 -"
            if echo "$COMMENT_BODY" | grep -q "\*米粒儿" && ! echo "$COMMENT_BODY" | grep -q "\*小米粒"; then
                if [[ "$COMMENT_TIME" > "$LAST_CHECK" ]]; then
                    echo "   📬 米粒儿新评论（$COMMENT_TIME）" | tee -a "$LOG_FILE"
                    NEW_COMMENTS="$NEW_COMMENTS\nIssue #$ISSUE_NUM: $ISSUE_TITLE\n   时间：$COMMENT_TIME\n   来源：米粒儿"
                fi
            fi
        fi
    fi
done <<< "$ISSUES"

if [ -z "$NEW_COMMENTS" ]; then
    echo "✅ GitHub Issues：无新评论" | tee -a "$LOG_FILE"
fi

# 3. 检查通知文件
echo "" | tee -a "$LOG_FILE"
echo "[3/3] 检查通知文件..." | tee -a "$LOG_FILE"

NOTIFY_FILES=(
    "/tmp/notify_mili.txt"
    "/tmp/review_approved.txt"
    "/tmp/review_rejected.txt"
    "/tmp/release_approved.txt"
)

FOUND_NOTIFY=""

for file in "${NOTIFY_FILES[@]}"; do
    if [ -f "$file" ]; then
        FILE_TIME=$(stat -c %Y "$file" 2>/dev/null || echo "0")
        LAST_CHECK_TIMESTAMP=$(date -d "$LAST_CHECK" +%s 2>/dev/null || echo "0")

        if [ "$FILE_TIME" -gt "$LAST_CHECK_TIMESTAMP" ]; then
            echo "✅ 发现通知文件：$file" | tee -a "$LOG_FILE"
            echo "   内容：$(head -1 "$file")" | tee -a "$LOG_FILE"
            FOUND_NOTIFY="$FOUND_NOTIFY\n$file"
        fi
    fi
done

if [ -z "$FOUND_NOTIFY" ]; then
    echo "✅ 通知文件：无新通知" | tee -a "$LOG_FILE"
fi

# 总结
echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "检查结果总结：" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

if [ "$GIT_NEW" = "yes" ] || [ -n "$NEW_COMMENTS" ] || [ -n "$FOUND_NOTIFY" ]; then
    echo "🎉 发现新消息！" | tee -a "$LOG_FILE"

    if [ "$GIT_NEW" = "yes" ]; then
        echo "  - Git有新提交" | tee -a "$LOG_FILE"
    fi

    if [ -n "$NEW_COMMENTS" ]; then
        echo "  - GitHub Issues有新评论" | tee -a "$LOG_FILE"
        echo -e "$NEW_COMMENTS" | tee -a "$LOG_FILE"
    fi

    if [ -n "$FOUND_NOTIFY" ]; then
        echo "  - 发现通知文件" | tee -a "$LOG_FILE"
        echo -e "$FOUND_NOTIFY" | tee -a "$LOG_FILE"
    fi

    # 返回特殊标记（用于调用者检测）
    echo "NEW_MESSAGE_FOUND"
else
    echo "✅ 暂无新消息" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "下次检查时间：$(date -d '+5 minutes' '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
