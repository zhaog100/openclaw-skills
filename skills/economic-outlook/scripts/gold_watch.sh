#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 黄金区间盯价：触发（跌支撑/破止损/到阻力）才推 QQ，否则静默。去重防刷屏。
set -u
WS="$HOME/.openclaw/workspace"
EO="$WS/skills/economic-outlook"
STATE="$EO/data/gold_watch_state.json"
export PYTHONPATH="$HOME/.local/lib/python3.12/site-packages"
cd "$EO"
python3 - <<'PY' 1>"$STATE" 2>&1
import sys, os, json, re, importlib.util, datetime
sys.path.insert(0, os.getcwd()); sys.path.insert(0, 'shared')
import logging; logging.basicConfig(level=logging.INFO)
log = logging.getLogger("gold_watch")

# 区间配置（可改这里；支撑893/止损870/阻力975 来自今早报告）
WATCH = {"support": 893, "stop_loss": 870, "resistance": 975}

spec = importlib.util.spec_from_file_location("og", "skills/oil_gold/skill.py")
og = importlib.util.module_from_spec(spec); spec.loader.exec_module(og)
out = {"report_text_path": os.path.join(os.getcwd(), "..", "oil-gold-correlation", "reports", "report_text_latest.txt")}

# 读上次的去重 key
last_key = ""
state_f = os.path.join(os.getcwd(), "data", "gold_watch_state.json")
if os.path.exists(state_f):
    try:
        last_key = json.load(open(state_f)).get("last_alert_key", "")
    except Exception:
        last_key = ""

alert = og._gold_price_alert({**WATCH, "last_alert_key": last_key}, out)
price = alert.get("price")
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

if alert.get("triggered"):
    # 触发才推
    target = os.environ.get("QQ_TARGET_USER_ID", "")
    log.info("🔔 触发: %s | %s", now, alert.get("msg"))
    if target:
        import subprocess
        msg = alert.get("msg", "") + f"\n（{now} 沪金 {price:.0f}）"
        env = dict(os.environ); env["QQ_TARGET_USER_ID"] = target
        subprocess.run(["python3", "scripts/gold_watch_send.py", msg], env=env, timeout=120, capture_output=True)
        # 记 key 去重
        os.makedirs("data", exist_ok=True)
        json.dump({"last_alert_key": alert.get("alert_key",""), "at": now}, open(state_f,"w"))
        print("TRIGGERED")
    else:
        print("TRIGGERED_NO_TARGET")
else:
    log.info("未触发（%s），沪金 %s", alert.get("reason","?"), price if price else "?")
    print("OK")
PY
