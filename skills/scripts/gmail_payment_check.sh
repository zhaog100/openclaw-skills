#!/bin/bash
# Gmail付款监控定时任务脚本
LOG_FILE="$HOME/.openclaw/workspace/logs/gmail_payment_check.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始检查Gmail付款..." >> "$LOG_FILE"

# 运行检查脚本
bash "$HOME/.openclaw/workspace/scripts/check_gmail_payments.sh" 2>&1 | tee -a "$LOG_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检查完成" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
