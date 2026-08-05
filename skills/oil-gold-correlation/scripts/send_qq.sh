#!/bin/bash
# 发送QQ消息脚本
REPORT_FILE="${1:-/root/.openclaw/workspace/skills/oil-gold-correlation/reports/report_text_latest.txt}"

if [ -f "$REPORT_FILE" ]; then
    MESSAGE=$(cat "$REPORT_FILE")
    echo "$MESSAGE" | nc -w 5 api.openclaw.ai 8080 2>/dev/null || echo "发送失败"
else
    echo "报告文件不存在: $REPORT_FILE"
fi
