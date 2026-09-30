#!/usr/bin/env bash
# 经济分析一键入口
# 用法: ./run_report.sh [push]  (push 则输出推送用报告文本)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
CACHE="$SCRIPT_DIR/../cache"

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
