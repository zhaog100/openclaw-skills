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

# 区间配置（动态读今早报告里的最新支撑/阻力位，不写死；止损按现价动态算）
import re as _re
_rpt = os.path.join(os.getcwd(), "..", "oil-gold-correlation", "reports", "report_text_latest.txt")
WATCH = {"support": None, "stop_loss": None, "resistance": None}
if os.path.exists(_rpt):
    with open(_rpt, encoding="utf-8", errors="ignore") as _f:
        _txt = _f.read()
    # 取"黄金"那段的支撑/阻力（报告里第一个 支撑位/阻力位 是黄金）
    m_s = _re.search(r"支撑位:\s*¥?([0-9,.]+)", _txt)
    m_r = _re.search(r"阻力位:\s*¥?([0-9,.]+)", _txt)
    if m_s: WATCH["support"] = float(m_s.group(1).replace(",", ""))
    if m_r: WATCH["resistance"] = float(m_r.group(1).replace(",", ""))
    # 当前沪金价（取报告里 黄金 ¥XXX）
    m_p = _re.search(r"黄金 ¥([0-9,.]+)", _txt)
    if m_p: WATCH["_price"] = float(m_p.group(1).replace(",", ""))
# 止损：按支撑位下方 2.5% 动态算（支撑破了才算破位）；没读到则跳过止损
if WATCH.get("support"):
    WATCH["stop_loss"] = round(WATCH["support"] * 0.975, 2)
else:
    log.warning("报告未读到支撑/阻力位，本次盯价仅按能读到的项")

# 官家 10-26: 全部以新链路为准 → 东财 AUM/AGM + gold_watch_signal + gold_watch_outcome(含白银)
from skills.gold_watch_signal.skill import GoldWatchSignalSkill
from skills.gold_watch_outcome.skill import GoldWatchOutcomeSkill
sig = GoldWatchSignalSkill().execute({}).data
out = GoldWatchOutcomeSkill().execute({"gold_watch_signal": sig}).data
price = sig.get("sh_equiv") or out.get("sh_equiv")
agm = sig.get("agm_realtime", "")
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# 读上次的去重 key
last_key = ""
state_f = os.path.join(os.getcwd(), "data", "gold_watch_state.json")
if os.path.exists(state_f):
    try:
        last_key = json.load(open(state_f)).get("last_alert_key", "")
    except Exception:
        last_key = ""

if out.get("triggered"):
    # 触发才推
    alerts = out.get("alerts") or [out.get("reason", "")]
    target = os.environ.get("QQ_TARGET_USER_ID", "")
    log.info("🔔 触发: %s | %s", now, out.get("reason"))
    if target:
        import subprocess
        msg = "🔔 黄金盯价提醒\n" + "\n".join(alerts) + f"\n（{now} 沪金 {price} / 沪银 {agm} 元/千克, 源:{sig.get('au0_realtime_src','')}）"
        env = dict(os.environ); env["QQ_TARGET_USER_ID"] = target
        # 门面统一推送（方案A）：盯价消息写临时文件，复用门面 send_qq_gw.py（Gateway REST）
        # 路径走环境变量/相对定位，不硬编码绝对路径（合规关卡）
        import tempfile, os as _os
        gw_env = _os.environ.get("OIL_GOLD_SKILL_DIR", "")
        gw = _os.path.join(gw_env, "scripts", "send_qq_gw.py") if gw_env else ""
        if not gw or not _os.path.exists(gw):
            _base = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
            gw = _os.path.join(_os.path.dirname(_base), "oil-gold-correlation", "scripts", "send_qq_gw.py")
        _tmp = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
        _tmp.write(msg + "\n\n⚠️ 区间参考，不构成投资建议"); _tmp.close()
        r = subprocess.run(["python3", gw, _tmp.name], env=env, timeout=120, capture_output=True)
        _os.unlink(_tmp.name)
        if r.returncode != 0:
            log.warning("门面推送失败: %s", r.stderr[:80] if r.stderr else "?")
        key = f"trig_{out.get('trigger_type','')}_{price}_{agm}"
        os.makedirs("data", exist_ok=True)
        json.dump({"last_alert_key": key, "at": now}, open(state_f, "w"))
        print("TRIGGERED")
    else:
        print("TRIGGERED_NO_TARGET")
else:
    log.info("未触发（%s），沪金 %s", alert.get("reason","?"), price if price else "?")
    print("OK")
PY
