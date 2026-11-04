#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# P6 银行黄金成本项感知 cron 入口: 扫官方+快讯腿, 命中才推, 未命中静默
set -u
WS="$HOME/.openclaw/workspace"
export PYTHONPATH="$HOME/.local/lib/python3.12/site-packages"
export QQ_TARGET_USER_ID="C099848DC9A60BF60A7BE31626822790"
cd "$WS/skills/economic-outlook"
OUT=$(python3 scripts/bank_gold_watch.py all 2>&1)
if echo "$OUT" | grep -q "QUIET" && ! echo "$OUT" | grep -qE "命中 [1-9]"; then
  # 全静默: 无新命中, 不推
  exit 0
fi
# 有命中 → 推 QQ(走门面 send_qq_gw)
python3 - "$OUT" <<'PY'
import sys, os, subprocess
out = sys.argv[1] if len(sys.argv) > 1 else ""
# 只推真正命中的部分(去掉 QUIET 行和腿3提示行)
lines = [l for l in out.splitlines() if not l.strip().startswith("QUIET") and "官家喂】" not in l]
body = "\n".join(lines)
if not body.strip():
    sys.exit(0)
msg = "🏦 银行黄金成本项感知(每日9:00)\n" + body[:1500]
env = dict(os.environ)
r = subprocess.run(
    [sys.executable, os.path.join(os.environ["HOME"], ".openclaw/workspace/skills/oil-gold-correlation/scripts/send_qq_gw.py"),
     msg],
    capture_output=True, text=True, timeout=60, env=env,
)
print("推送:", "OK" if r.returncode == 0 else f"FAIL {r.stderr[:100]}")
PY
