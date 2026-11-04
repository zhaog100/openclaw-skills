#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 技能: oil-gold-correlation/scripts/run_report
# 石油黄金报告生成+推送 wrapper（路径相对定位，open_id 走环境变量）

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="${OIL_GOLD_SKILL_DIR:-$SCRIPT_DIR/../reports}"
REPORT_FILE="${REPORT_DIR}/report_text_latest.txt"
LOG_FILE="${OIL_GOLD_LOG:-$SCRIPT_DIR/../../..}/logs/oil-gold-report-cron.log"
LOG_FILE="${OIL_GOLD_LOG:-$(cd "$SCRIPT_DIR/../../.." && pwd)/logs/oil-gold-report-cron.log}"

if [ -z "$QQ_TARGET_USER_ID" ]; then
  echo "[ERROR] QQ_TARGET_USER_ID 未设置，拒绝推送（不硬编码 open_id）" >&2
  exit 1
fi
QQ_TARGET="$QQ_TARGET_USER_ID"

export HOME="${HOME:-$HOME}"
export PATH="$HOME/.openclaw/tmp/agent-cli:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export PYTHONPATH="${PYTHONPATH:-$HOME/.local/lib/python3.12/site-packages}"

TS_START="$(date '+%Y-%m-%d %H:%M:%S')"
echo "[$TS_START] 开始生成石油黄金报告..." >> "$LOG_FILE"

cd "$SCRIPT_DIR"
timeout 600 python3 report_text.py >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 报告生成失败" >> "$LOG_FILE"
    exit 1
fi

TS_OK="$(date '+%Y-%m-%d %H:%M:%S')"
echo "[$TS_OK] 报告生成完成，准备发送..." >> "$LOG_FILE"

if [ -f "$REPORT_FILE" ]; then
    python3 "$SCRIPT_DIR/send_qq_gw.py" "$REPORT_FILE" >> "$LOG_FILE" 2>&1
    TS_END="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "[$TS_END] 报告已发送到QQ" >> "$LOG_FILE"
else
    TS_END="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "[$TS_END] 报告文件不存在: $REPORT_FILE" >> "$LOG_FILE"
fi
