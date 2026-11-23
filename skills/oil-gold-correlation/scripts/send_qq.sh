#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)# 技能: oil-gold-correlation/scripts/send_qq# 发送QQ消息脚本 - 使用OpenClaw message工具
# 报告路径: 相对定位 reports/（不写死绝对路径）

REPORT_FILE="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/reports/report_text_latest.txt}"
# 加载技能 .env（cron 环境无交互 shell 时提供 QQ_TARGET_USER_ID）
_OL_ENV="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../.env"
if [ -f "$_OL_ENV" ]; then
  set -a
  . "$_OL_ENV"
  set +a
fi
if [ -z "$QQ_TARGET_USER_ID" ]; then
  echo "[ERROR] QQ_TARGET_USER_ID 未设置，拒绝推送（不硬编码 open_id）" >&2
  exit 1
fi
QQ_TARGET="$QQ_TARGET_USER_ID"

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
