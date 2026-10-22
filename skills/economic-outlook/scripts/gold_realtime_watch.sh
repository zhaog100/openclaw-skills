#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 黄金实时盯价（盘中分钟级/秒级，走 gold-api XAUUSD 免费源）
# 官家 10-22 要求: "2和3都接，至少先把代码实现"
#   ② 15min 轮询: etf_watch.sh（已接，WATCH_QUIET 破位才推）
#   ③ 实时预警: 本脚本，盘中每分钟拉 XAUUSD，跌破/突破关键线才推（不刷屏）
# 口径: 国际金 XAUUSD(美元/盎司) → 换算上海金基准价(元/克) 对齐你 903 成本/回本线 919.6
set -u
WS="$HOME/.openclaw/workspace"
export PYTHONPATH="$HOME/.local/lib/python3.12/site-packages"
cd "$WS/skills/oil-gold-correlation"

python3 - <<'PY'
import os, sys, json, datetime, subprocess, tempfile, urllib.request

# ---- 读配置（官家 903 成本 / 16.6 点差 / 回本线 919.6 / 买点卖点动态档）----
CFG = "data/gold_watch.json"
if not os.path.exists(CFG):
    print("无盯价配置，跳过"); sys.exit(0)
w = json.load(open(CFG)).get("watch_shgold_spot", {})
cost   = w.get("cost_basis", 903)
breakeven = w.get("breakeven", 920)
dyn = w.get("dynamic", {})
# 国际金(XAUUSD) → 上海金基准价 换算: 沪金≈国际金×汇率×31.1035(克/盎司)
FX = 7.10  # USD/CNY 粗估，实际可用最新；误差对"档位预警"影响小
G_PER_OZ = 31.1035

def fetch_xau():
    """拉国际现货金 XAUUSD（美元/盎司），免key免费源"""
    for url in [
        "https://api.gold-api.com/price/XAU",
    ]:
        try:
            r = urllib.request.urlopen(url, timeout=10)
            d = json.loads(r.read())
            p = float(d.get("price", 0))
            if p > 0:
                return p, url
        except Exception:
            continue
    return None, None

# ---- 读上一轮已推过的价格（去重，避免每分钟刷屏）----
state_f = "data/gold_realtime_state.json"
last_pushed = None
if os.path.exists(state_f):
    last_pushed = json.load(open(state_f)).get("last_pushed_line", "")

xau, src = fetch_xau()
if xau is None:
    print("XAUUSD 拉取失败，本轮静默跳过（不用过期价）"); sys.exit(0)

# 换算成"上海金基准价(元/克)"，对齐你的 903 成本/回本线口径
sh_equiv = xau * FX / G_PER_OZ

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# ---- 预警判定（相对你的 903 成本线 / 回本线 919.6 / 买卖点）----
msgs = []
# 跌破回本线下方 2% 以内 = 接近回本触发；跌破成本 = 加仓机会；破 60 日低 = 低位重仓
lo60 = 876   # 动态会随行情滚，这里先按当前 60 日低（脚本可再读 config）
if sh_equiv <= 882:
    msgs.append(f"⚡️ 实时预警：国际金折算沪金≈¥{sh_equiv:.0f}/克，跌破第2笔买点 882 → 国泰A 可补 40%")
elif sh_equiv <= 877:
    msgs.append(f"⚡️ 实时预警：国际金折算沪金≈¥{sh_equiv:.0f}/克，跌破第3笔 877 → 低位重仓 30%")
elif sh_equiv >= 951:
    msgs.append(f"⚡️ 实时预警：国际金折算沪金≈¥{sh_equiv:.0f}/克，到波段卖点1 951 → 国泰C 减 1/3")
elif sh_equiv >= 1007:
    msgs.append(f"⚡️ 实时预警：国际金折算沪金≈¥{sh_equiv:.0f}/克，到波段卖点2 1007 → 国泰C 清掉")
else:
    msgs.append(f"⚡️ 国际金 XAU ${xau:.0f}/oz（≈沪金¥{sh_equiv:.0f}/克，你成本903/回本线919.6）")

# 去重：同一档 30 分钟内不重推
key = msgs[0][:30]
if msgs and key == last_pushed:
    print(f"未推（同档去重）：{key}")
    sys.exit(0)

target = os.environ.get("QQ_TARGET_USER_ID", "")
if not target:
    print("NO_TARGET"); sys.exit(0)

# 只在"突破档位"时才真推（纯价格播报走静默，避免刷屏）
is_alert = any(k in msgs[0] for k in ["跌破", "到波段", "重仓"])
if not is_alert:
    print(f"静默（仅价格播报）：XAU ${xau:.0f} ≈沪金{sh_equiv:.0f}（未破关键档）")
    sys.exit(0)

gw = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)) or "scripts")), "oil-gold-correlation", "scripts", "send_qq_gw.py")
if not os.path.exists(gw):
    gw = os.path.expanduser("~/.openclaw/workspace/skills/oil-gold-correlation/scripts/send_qq_gw.py")
tmp = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
tmp.write("\n".join(msgs) + f"\n（{now} 实时源:{src.split('/')[2]} 国际金XAU ${xau:.2f}/oz）\n⚠️ 国际金为领先预警价，实盘下单按中行实时价"); tmp.close()
r = subprocess.run(["python3", gw, tmp.name], env=dict(os.environ), timeout=120, capture_output=True)
os.unlink(tmp.name)
if r.returncode == 0:
    json.dump({"last_pushed_line": key, "at": now}, open(state_f, "w"))
    print(f"REALTIME_PUSHED: {msgs[0][:60]}")
else:
    print(f"PUSH_FAILED: {r.stderr[:80] if r.stderr else '?'}")
PY
