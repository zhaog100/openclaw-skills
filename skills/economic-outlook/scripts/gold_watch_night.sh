#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 黄金/白银夜盘盯价(21点起): 走新 signal+outcome 链路(东财AUM+AGM), 破档才推QQ, 否则静默
set -u
WS="$HOME/.openclaw/workspace"
EO="$WS/skills/economic-outlook"
STATE="$EO/data/gold_watch_state.json"
export PYTHONPATH="$HOME/.local/lib/python3.12/site-packages"
cd "$EO"
python3 - <<'PY'
import sys, os, json, datetime, tempfile, subprocess
sys.path.insert(0, os.getcwd()); sys.path.insert(0, 'shared')
from skills.gold_watch_signal.skill import GoldWatchSignalSkill
from skills.gold_watch_outcome.skill import GoldWatchOutcomeSkill

r = GoldWatchSignalSkill().execute({}).data
o = GoldWatchOutcomeSkill().execute({"gold_watch_signal": r}).data

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
price = r.get("sh_equiv", 0)
agm = r.get("agm_realtime", "")
src = r.get("au0_realtime_src", "")
state_f = os.path.join(os.getcwd(), "data", "gold_watch_state.json")
last_key = ""
if os.path.exists(state_f):
    try: last_key = json.load(open(state_f)).get("last_alert_key", "")
    except: pass

if o.get("triggered"):
    alerts = o.get("alerts") or [o.get("reason")]
    msg = "🔔 黄金盯价提醒\n" + "\n".join(alerts) + f"\n（{now} 沪金 {price} / 沪银 {agm} 元/千克, 源:{src}）"
    target = os.environ.get("QQ_TARGET_USER_ID", "")
    print("🔔 触发:", now, o.get("reason"))
    if target:
        gw_env = os.environ.get("OIL_GOLD_SKILL_DIR", "")
        gw = os.path.join(gw_env, "scripts", "send_qq_gw.py") if gw_env else ""
        if not gw or not os.path.exists(gw):
            _base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            gw = os.path.join(os.path.dirname(_base), "oil-gold-correlation", "scripts", "send_qq_gw.py")
        tmp = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
        tmp.write(msg + "\n\n⚠️ 区间参考，不构成投资建议"); tmp.close()
        env = dict(os.environ); env["QQ_TARGET_USER_ID"] = target
        rp = subprocess.run(["python3", gw, tmp.name], env=env, timeout=120, capture_output=True)
        os.unlink(tmp.name)
        if rp.returncode != 0:
            print("门面推送失败:", rp.stderr[:80] if rp.stderr else "?")
    key = f"trig_{o.get('trigger_type','')}_{price}_{agm}"
    os.makedirs("data", exist_ok=True)
    json.dump({"last_alert_key": key, "at": now}, open(state_f, "w"))
    print("TRIGGERED")
else:
    # 静默: 真静默(官家10-26'不破档别推') → 不输出文案, 只记状态, cron 不推
    key = f"silent_{price}_{agm}"
    os.makedirs("data", exist_ok=True)
    json.dump({"last_alert_key": key, "at": now, "reason": o.get("reason")}, open(state_f, "w"))
    # 故意不打 stdout(避免 cron 把静默行当文案推给官家); 状态已写 state 文件可查
    sys.exit(0)
PY
