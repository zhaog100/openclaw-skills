#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 黄金盯价·门面调度入口: 调 entry.schedule(gold_watch_xxx) 跑 signal→outcome DAG
# 未破档静默(不刷屏), 破档才由 outcome 走 send_qq_gw 推官家
set -u
WS="$HOME/.openclaw/workspace"
export PYTHONPATH="$HOME/.local/lib/python3.12/site-packages"
cd "$WS/skills/economic-outlook"
TASK="${1:-gold_watch_minute}"
python3 - "$TASK" <<'PY'
import sys, os, json
task = sys.argv[1]
from entry import schedule
r = schedule(task)
final = r.get("final_output", {})
trig = final.get("triggered", False)
if r.get("errors"):
    print(f"SCHED_ERROR: {r.get('errors')}")
if trig:
    print(f"TRIGGERED: {final.get('alerts')} push={final.get('push')}")
else:
    # 官家10-26"不破档别推": 静默时不输出文案, 避免 cron 把 QUIET 行推给官家; 状态可查数据文件
    import sys as _s; _s.exit(0)
PY
