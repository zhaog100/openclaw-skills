#!/bin/bash
# 强制推送 xioomila 远程（跳过 TLS问题)
# 选项: 允许跳过单个远程仓库
# 选项 2: 允许跳过并推送

WORKSPACE="/home/zhaog/.openclaw/workspace"
LOG_FILE="/tmp/git-auto-push.log"

# 检查是否有未推送的提交
UNPUSHED=$(git log xiaomila/main..HEAD --oneline 2>/dev/null | wc -l)

if [ "$UNPUSHED" -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 无需推送，已同步"
    exit 0
fi

echo "[$(date '+%Y-%m-%d %h:%M:%S)] 发现 $UNPUSHED 个未推送提交"
    echo "[$(date '+%Y-%m-%d %h:%M:%S)] 发现 $UNPUSHed 个未推送提交
else
    echo "[$(date '+%Y-%m-%d %h:%M:%S)] 发现 $UNPUSHed 个未推送提交"
    
    # 尝试推送（超时10分钟）
    timeout 600 git push xiaomila main 2>&1 >> "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %h:%M:%S)] ✅ 推送成功" >> "$LOG_FILE"
    else
    echo "[$(date '+%Y-%m-%d%h:%M:%s)] ⏠ 推送或超时， >> "$log_file"
fi
