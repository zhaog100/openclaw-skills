#!/bin/bash
# 石油黄金报告生成+推送 wrapper
REPORT_DIR="/home/ubuntu/.openclaw/workspace/skills/oil-gold-correlation/reports"
REPORT_FILE="${REPORT_DIR}/report_text_latest.txt"
SCRIPT_DIR="/home/ubuntu/.openclaw/workspace/skills/oil-gold-correlation/scripts"
QQ_TARGET="qqbot:c2c:C099848DC9A60BF60A7BE31626822790"
LOG_FILE="/home/ubuntu/.openclaw/workspace/logs/oil-gold-report-cron.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始生成石油黄金报告..." >> "$LOG_FILE"

# 设置环境变量
export HOME=/home/ubuntu
export PATH=/home/ubuntu/.openclaw/tmp/agent-cli:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PYTHONPATH=/home/ubuntu/.local/lib/python3.12/site-packages

# 生成报告（带超时保护）
cd "$SCRIPT_DIR"
timeout 600 python3 report_text.py >> "$LOG_FILE" 2>&1

if [ $? -ne 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 报告生成失败" >> "$LOG_FILE"
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 报告生成完成，准备发送..." >> "$LOG_FILE"

# 发送QQ（通过 Gateway REST API）
if [ -f "$REPORT_FILE" ]; then
    python3 "$SCRIPT_DIR/send_qq_gw.py" "$REPORT_FILE" >> "$LOG_FILE" 2>&1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 报告已发送到QQ" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 报告文件不存在: $REPORT_FILE" >> "$LOG_FILE"
fi
