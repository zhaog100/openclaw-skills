#!/usr/bin/env bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 技能: economic-outlook/scripts/run_report# 经济分析一键入口
# 用法: ./run_report.sh [push]  (push 则输出推送用报告文本)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
CACHE="$SCRIPT_DIR/../cache"

# ---- 防重复锁：手动跑时若 cron 刚推过且报告未过旧，跳过不刷屏 ----
REPORT="$CACHE/report_text.txt"
if [ "$1" != "--force" ] && [ -f "$REPORT" ]; then
  age=$(( $(date +%s) - $(stat -c %Y "$REPORT") ))
  max_age_hours=${ECONOMIC_REPORT_MAX_AGE_HOURS:-6}
  if [ "$age" -lt $(( max_age_hours * 3600 )) ]; then
    echo "=== 报告 ${age}s 前已生成（<$max_age_hoursh），跳过重新生成。强制用 --force ==="
    exit 0
  fi
fi

echo "=== 生成经济形势周报 ==="
python3 report_text.py > "$CACHE/report_text.txt" 2> "$CACHE/report_text.log"
echo "=== 报告已生成（$CACHE/report_text.txt），前 15 行：==="
head -15 "$CACHE/report_text.txt"
echo "..."

if [ "$1" = "push" ]; then
  echo "=== 推送文本（供 OpenClaw cron/QQ 通道读取）==="
  cat "$CACHE/report_text.txt"
fi
echo "=== 完成 ==="
