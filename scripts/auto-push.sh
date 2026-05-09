#!/bin/bash
# 自动推送脚本 - 每小时推送一次

WORKSPACE="/home/zhaog/.openclaw/workspace"
LOG_FILE="/tmp/git-auto-push.log"

cd "$WORKSPACE" || exit 1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始推送..." >> "$LOG_FILE"

# 检查是否有未推送的提交
UNPUSHED=$(git log xiaomila/main..HEAD --oneline 2>/dev/null | wc -l)

if [ "$UNPUSHED" -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 无需推送，已同步" >> "$LOG_FILE"
    exit 0
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 发现 $UNPUSHED 个未推送提交" >> "$LOG_FILE"

# 尝试推送（超时10分钟）
timeout 600 git push xiaomila main 2>&1 >> "$LOG_FILE"

if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 推送成功" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ 推送失败或超时" >> "$LOG_FILE"
fi
