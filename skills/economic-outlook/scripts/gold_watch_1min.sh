#!/bin/bash
# 经济面门面: 黄金盯价 1min 轮询 (交易日盘中 9:30-14:45, 破档才推, 未破档静默)
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# Author: 小米粒 (Xiaomili) - AI Agent
E="$HOME/.openclaw/workspace/skills/economic-outlook"
LOG="$HOME/.openclaw/workspace/logs/gold_watch.log"
mkdir -p "$(dirname "$LOG")"
now=$(date +%s)
# 时间窗口: 交易日(周一~五) 9:30-14:45 (CST)
dow=$(date +%u); hm=$(date +%H%M)
if [ "$dow" -gt 5 ]; then exit 0; fi
if [ "$hm" -lt 0930 ] || [ "$hm" -gt 1445 ]; then exit 0; fi
echo "[$(date '+%F %T')] run outcome" >> "$LOG"
out=$(cd "$E" && PYTHONPATH="$E" python3 skills/gold_watch_outcome/skill.py 2>>"$LOG")
echo "[$(date '+%F %T')] $out" >> "$LOG"
