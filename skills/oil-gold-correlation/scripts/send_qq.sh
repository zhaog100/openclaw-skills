#!/bin/bash
# 发送QQ消息脚本 - 使用OpenClaw API
REPORT_FILE="${1:-/home/ubuntu/.openclaw/workspace/skills/oil-gold-correlation/reports/report_text_latest.txt}"
QQ_TARGET="qqbot:c2c:C099848DC9A60BF60A7BE31626822790"

if [ -f "$REPORT_FILE" ]; then
    MESSAGE=$(cat "$REPORT_FILE")
    openclaw message send --channel "QQ Bot default" --target "$QQ_TARGET" --message "$MESSAGE" 2>&1
else
    echo "报告文件不存在: $REPORT_FILE"
fi
