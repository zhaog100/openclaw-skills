#!/bin/bash
# 小米粒自动检查脚本 - 每1分钟执行

LOG_FILE="/tmp/xiaomili_auto_check.log"
REPO_DIR="/root/.openclaw/workspace"

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 检查开始 =====" >> "$LOG_FILE"

# 1. Git拉取最新代码
cd "$REPO_DIR"
git fetch --all >> "$LOG_FILE" 2>&1

# 2. 检查最新提交
LATEST_COMMIT=$(git log --oneline -1)
echo "最新提交: $LATEST_COMMIT" >> "$LOG_FILE"

# 3. 检查GitHub Issues评论
echo "检查Issue #7..." >> "$LOG_FILE"
gh issue view 7 --json comments --jq '.comments[-1] | "作者: \(.author.login), 时间: \(.createdAt)"' >> "$LOG_FILE" 2>&1

# 4. 检查.mili_comm/目录
echo "检查.mili_comm/目录..." >> "$LOG_FILE"
find "$REPO_DIR/.mili_comm" -type f -mmin -1 >> "$LOG_FILE" 2>&1

echo "===== 检查完成 =====" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
