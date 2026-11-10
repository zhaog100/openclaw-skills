#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 技能: economic-outlook/scripts/run_lottery_after_draw.sh
# 开奖日 21:20 自动重拉最新数据 + 出号(三式投注+历史号分析) + 推 QQ(走门面 send_qq_gw 双路)
# 用法: 由 OpenClaw cron 定时调用; 参数 kind=ssq|dlt
set -u
WS="$HOME/.openclaw/workspace"
EO="$WS/skills/economic-outlook"
CLOG="$WS/logs/lottery-after-draw-cron.log"
kind="${1:-ssq}"
export PYTHONPATH="$HOME/.local/lib/python3.12/site-packages"
cd "$EO"
echo "[$(date '+%F %T')] === 开奖后出号: $kind ===" >> "$CLOG"
# ① 强制重拉最新数据(不读旧缓存)
python3 skills/lottery_analysis/lottery_stats.py "$kind" > /dev/null 2>&1
# ② 出号+历史分析 → 报告文本
python3 skills/lottery_analysis/combined_ticket.py "$kind" > /tmp/lottery_report_$kind.txt 2>&1
rc=$?
echo "[$(date '+%F %T')] 出号 exit=$rc" >> "$CLOG"
# ③ 推 QQ(走门面 send_qq_gw 双路)
if [ $rc -eq 0 ]; then
  python3 skills/oil-gold-correlation/scripts/send_qq_gw.py /tmp/lottery_report_$kind.txt >> "$CLOG" 2>&1
  echo "[$(date '+%F %T')] 推送: $?" >> "$CLOG"
fi
