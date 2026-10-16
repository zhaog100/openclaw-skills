#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 上海金现货盯价（动态算法，不写死价格）
# 官家在中行 App 买黄金ETF联接基金（国泰A/C），跟上海金/沪金走
# 买点/卖点每次按 20日/60日 高低动态算，offset 可调
set -u
WS="$HOME/.openclaw/workspace"
export PYTHONPATH="$HOME/.local/lib/python3.12/site-packages"
cd "$WS/skills/oil-gold-correlation"

python3 - <<'PY'
import os, sys, json, datetime, subprocess, tempfile

CFG = "data/gold_watch.json"
if not os.path.exists(CFG):
    CFG = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "economic-outlook", "data", "gold_watch.json")
if not os.path.exists(CFG):
    print("无上海金现货盯价配置，跳过")
    sys.exit(0)

w = json.load(open(CFG)).get("watch_shgold_spot", {})
dyn = w.get("dynamic")
if not dyn:
    print("无动态算法配置，跳过")
    sys.exit(0)

# 拉沪金期货(元/克) 最近 60 日
try:
    import akshare as ak
    end = datetime.datetime.now().strftime("%Y%m%d")
    df = ak.futures_main_sina(symbol="AU0", start_date="20260701", end_date=end)
    close = df['收盘价'].astype(float)
except Exception:
    print("沪金期货价不可用，本轮静默跳过（不推、不用过期价）")
    sys.exit(0)

cur = close.iloc[-1]
lb1 = dyn.get("lookback_1", 20)
lb2 = dyn.get("lookback_2", 60)
lo1, hi1 = close.tail(lb1).min(), close.tail(lb1).max()
lo2, hi2 = close.tail(lb2).min(), close.tail(lb2).max()
mid1 = (lo1 + hi1) / 2

# 动态买点/卖点
off1 = dyn.get("band1_offset", 5)
off2 = dyn.get("band2_offset", 5)
buy1 = lo1 - off1
buy2 = lo2 - off2
targets = dyn.get("targets", ["mid20", "hi20", "hi60"])
tmap = {"mid20": mid1, "hi20": hi1, "hi60": hi2}
sell_pts = [tmap[t] for t in targets if t in tmap]
no_chase = tmap.get(dyn.get("no_chase", "hi20"), hi1)

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# 判定（买卖双向，动态价）
msgs = []
sell_hit = [s for s in sell_pts if cur >= s]
if sell_hit:
    top = max(sell_hit)
    idx = sell_pts.index(top)
    verb = "清掉" if idx >= 2 else f"减 1/{len(sell_pts)-idx}"
    msgs.append(f"🎯 沪金现货 ¥{cur:.0f}/克，达目标{idx+1}(¥{top:.0f})，波段仓可{verb}")
if cur <= buy2:
    msgs.append(f"🟢 沪金现货 ¥{cur:.0f}/克，跌到补仓点(¥{buy2:.0f})，波段仓可补 / 实物仓低位重仓")
elif cur <= buy1:
    msgs.append(f"🟢 沪金现货 ¥{cur:.0f}/克，跌到第一买点(¥{buy1:.0f})，波段仓可进首笔 / 实物仓可加")
elif cur >= no_chase:
    msgs.append(f"⚠️ 沪金现货 ¥{cur:.0f}/克，到 20日高(¥{no_chase:.0f})，高位别追、别新建波段仓")

# ---- 每日必推盯价摘要（官家 2026-10-16 定：没触发也推当日摘要，触发则推操作指令）----
if not msgs:
    # 区间内未触发：推摘要（当前价 + 动态区间 + 离各档距离 + 今天该干啥）
    d_buy1 = cur - buy1
    d_sell1 = sell_pts[0] - cur
    summary = (
        f"📊 黄金盯价摘要（{now}）\n"
        f"沪金现货 ¥{cur:.0f}/克，区间内未触发\n"
        f"  离买点1(¥{buy1:.0f}) 还差 {d_buy1:.0f} 元\n"
        f"  离卖点1(¥{sell_pts[0]:.0f}) 还差 {d_sell1:.0f} 元\n"
        f"  今天: 区间内持有，到价才动"
    )
    print(f"未触发（{now}）沪金现货 ¥{cur:.0f}/克 | 买点 {buy1:.0f}/{buy2:.0f} 卖点 {sell_pts[0]:.0f}/{sell_pts[1]:.0f}/{sell_pts[2]:.0f} 别追 {no_chase:.0f}")
    target = os.environ.get("QQ_TARGET_USER_ID", "")
    if not target:
        print("SUMMARY_NO_TARGET")
        sys.exit(0)
    gw = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "oil-gold-correlation", "scripts", "send_qq_gw.py")
    if not os.path.exists(gw):
        gw = os.path.expanduser("~/.openclaw/workspace/skills/oil-gold-correlation/scripts/send_qq_gw.py")
    gw = os.path.abspath(gw)
    tmp = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
    tmp.write(summary + "\n\n⚠️ 仅供参考，不构成投资建议"); tmp.close()
    r = subprocess.run(["python3", gw, tmp.name], env=dict(os.environ), timeout=120, capture_output=True)
    os.unlink(tmp.name)
    if r.returncode == 0:
        print(f"SUMMARY_PUSHED: 区间内未触发，摘要已推")
    else:
        print(f"SUMMARY_PUSH_FAILED: {r.stderr[:80] if r.stderr else '?'}")
    sys.exit(0)

# 触发了 → 去重（同价不重复推操作指令）
state_f = "data/gold_watch_state.json"
last_key = ""
if os.path.exists(state_f):
    last_key = json.load(open(state_f)).get("last_alert_key", "")
key = f"{msgs[0][:20]}"
if key == last_key:
    print(f"未触发（与上次同价 {key}）")
    sys.exit(0)

target = os.environ.get("QQ_TARGET_USER_ID", "")
if not target:
    print("TRIGGERED_NO_TARGET")
    sys.exit(0)

msg = "\n".join(msgs) + f"\n（{now} 沪金现货 ¥{cur:.0f}/克，动态区间: 买 {buy1:.0f}/{buy2:.0f} 卖 {sell_pts[0]:.0f}/{sell_pts[1]:.0f}/{sell_pts[2]:.0f}）"
gw = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "oil-gold-correlation", "scripts", "send_qq_gw.py")
if not os.path.exists(gw):
    gw = os.path.expanduser("~/.openclaw/workspace/skills/oil-gold-correlation/scripts/send_qq_gw.py")
gw = os.path.abspath(gw)
tmp = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
tmp.write(msg + "\n\n⚠️ 仅供参考，不构成投资建议"); tmp.close()
r = subprocess.run(["python3", gw, tmp.name], env=dict(os.environ), timeout=120, capture_output=True)
os.unlink(tmp.name)
if r.returncode == 0:
    os.makedirs("data", exist_ok=True)
    json.dump({"last_alert_key": key, "at": now}, open(state_f, "w"))
    print(f"TRIGGERED: {msgs[0][:60]}")
else:
    print(f"PUSH_FAILED: {r.stderr[:80] if r.stderr else '?'}")
PY
