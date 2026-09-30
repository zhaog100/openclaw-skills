#!/bin/bash
# 发送QQ消息脚本 - 使用OpenClaw message工具
# 报告路径: /home/ubuntu/.openclaw/workspace/skills/oil-gold-correlation/reports/report_text_latest.txt

REPORT_FILE="${1:-/home/ubuntu/.openclaw/workspace/skills/oil-gold-correlation/reports/report_text_latest.txt}"
QQ_TARGET="${QQ_TARGET_USER_ID:-C099848DC9A60BF60A7BE31626822790}"

if [ -f "$REPORT_FILE" ]; then
    MESSAGE=$(cat "$REPORT_FILE")
    
    # 使用 OpenClaw message 工具发送
    openclaw message send \
        --channel qqbot \
        --target "$QQ_TARGET" \
        --message "$MESSAGE" 2>&1
else
    echo "[ERROR] 报告文件不存在: $REPORT_FILE" >&2
    exit 1
fi
