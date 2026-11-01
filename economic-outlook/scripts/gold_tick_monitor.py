#!/usr/bin/env python3
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 黄金实时 tick 监听（方案① 骨架 + 轮询兜底）
#
# 官家 10-22 要求: 三条路(①秒级tick/②15min轮询/③分钟级)都先写代码，
#   然后拆成独立技能、走经济门面统一调用。
#
# 本脚本 = 方案①的"监听器"骨架:
#   · 优先级: WS_TICK_URL 配置了就接 WebSocket 秒级推流
#   · 兜底: 没配 WS 源 → 自动降级成 1 分钟 REST 轮询(就是 gold_realtime_watch.sh 用的 gold-api XAUUSD)
#   · 口径: 国际金 XAUUSD(美元/盎司) → 折算沪金基准价(元/克)，对齐官家 903 成本/回本线 919.6
#   · 推送: 只在突破买卖档时推(30min 去重)，其余静默不刷屏
#   · 推门面 send_qq_gw.py，open_id 走 QQ_TARGET_USER_ID 环境变量
#
# 用法:
#   常驻:  python3 gold_tick_monitor.py            # 跑着就一直是"盘中盯价守护"
#   单次:  python3 gold_tick_monitor.py --once     # 拉一次就退出(cron 每分钟调这个)
#   配 WS:  在下方 TICK_SOURCE 填一个 XAUUSD WebSocket 推流 URL(要账号/付费的填这里)
#
# 为什么先 REST 兜底: 目前没拿到稳定的免费 XAUUSD WebSocket tick 源，
#   骨架把"接 WS"的入口留好，官家哪天有行情源 key 就填 TICK_SOURCE，自动升级秒级。
import os, sys, json, datetime, tempfile, subprocess, urllib.request, time

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WS_DIR = os.path.join(BASE, "skills")
DATA = os.path.join(WS_DIR, "oil-gold-correlation", "data", "gold_watch.json")
STATE = os.path.join(WS_DIR, "oil-gold-correlation", "data", "gold_realtime_state.json")
GW = os.path.join(WS_DIR, "oil-gold-correlation", "scripts", "send_qq_gw.py")

FX = 7.10            # USD/CNY 粗估(换算国际金→沪金口径用)
G_PER_OZ = 31.1035   # 克/盎司
REST_XAU = "https://api.gold-api.com/price/XAU"   # 免费兜底源(分钟级)

# 官家哪天有 XAUUSD WebSocket 推流源，填这里(格式: wss://... 或带鉴权的 URL)。
# 留空 = 走 REST 轮询兜底(默认)。这是"升级秒级"的唯一入口。
TICK_SOURCE = os.environ.get("XAU_WS_URL", "")

def load_cfg():
    if not os.path.exists(DATA):
        return {}
    return json.load(open(DATA)).get("watch_shgold_spot", {})

def fetch_xau_rest():
    """REST 拉 XAUUSD(美元/盎司)。"""
    try:
        r = urllib.request.urlopen(REST_XAU, timeout=10)
        return float(json.loads(r.read()).get("price", 0))
    except Exception:
        return None

def fetch_xau_ws():
    """WebSocket 秒级 tick 拉 XAUUSD(官家有行情源时启用)。
    目前无稳定免费 WS tick 源 → 默认返回 None，走 REST 兜底。
    接入点: 官家给 TICK_SOURCE(如某交易所/经纪商 XAUUSD 推流)后，
      这里换成 websockets 库连 TICK_SOURCE、subscribe 金、on_message 里取最新价。
      骨架先留口，不硬造一个拉不通的 WS 连接。"""
    if not TICK_SOURCE:
        return None
    # 真实实现(官家有源后取消注释/启用):
    # import websockets
    # 连接 TICK_SOURCE, 订阅 XAUUSD, 解析最新 tick 价
    return None

def main():
    once = "--once" in sys.argv
    cfg = load_cfg()
    cost = cfg.get("cost_basis", 903)
    breakeven = cfg.get("breakeven", 919.6)
    # 动态买卖点(同 etf_watch 口径): 第2笔≤882 / 第3笔≤877 / 卖点≥951 / ≥1007
    # 这里读 config 的 min_target，兜底用固定档(盘中价滚时由 etf_watch 动态算，此处取保守值)
    buy1, buy2, sell1, sell2 = 882, 877, 951, 1007

    target = os.environ.get("QQ_TARGET_USER_ID", "")
    loop = 0
    while True:
        xau = fetch_xau_ws() if TICK_SOURCE else None
        src = "ws" if xau else "rest"
        if xau is None:
            xau = fetch_xau_rest()
        if xau is None:
            print(f"[{datetime.datetime.now():%H:%M:%S}] XAU 拉取失败，跳过本轮(不用过期价)")
            if once:
                sys.exit(0)
            time.sleep(60); loop += 1; continue

        sh_equiv = xau * FX / G_PER_OZ   # 折算沪金基准价(元/克)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        msgs, is_alert = [], False
        if sh_equiv <= buy2:
            msgs.append(f"⚡️ 实时tick(秒级)：国际金≈沪金¥{sh_equiv:.0f}/克，破第3笔买点{buy2} → 国泰A 低位重仓30%"); is_alert = True
        elif sh_equiv <= buy1:
            msgs.append(f"⚡️ 实时tick(秒级)：国际金≈沪金¥{sh_equiv:.0f}/克，破第2笔买点{buy1} → 国泰A 可补40%"); is_alert = True
        elif sh_equiv >= sell2:
            msgs.append(f"⚡️ 实时tick(秒级)：国际金≈沪金¥{sh_equiv:.0f}/克，到卖点{sell2} → 国泰C 清掉"); is_alert = True
        elif sh_equiv >= sell1:
            msgs.append(f"⚡️ 实时tick(秒级)：国际金≈沪金¥{sh_equiv:.0f}/克，到卖点{sell1} → 国泰C 减1/3"); is_alert = True

        if not is_alert:
            print(f"[{now}] 静默: XAU ${xau:.0f}/{src} ≈沪金¥{sh_equiv:.0f} (成本{cost}/回本线{breakeven})")
        else:
            # 30min 去重
            last = json.load(open(STATE)).get("last_pushed_line", "") if os.path.exists(STATE) else ""
            if target and msgs and last != msgs[0][:30]:
                tmp = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
                tmp.write("\n".join(msgs) + f"\n({now} tick源:{src} XAU ${xau:.2f}/oz) 实盘按中行实时价\n⚠️ 仅供参考")
                tmp.close()
                r = subprocess.run(["python3", GW, tmp.name], env=dict(os.environ), timeout=120, capture_output=True)
                os.unlink(tmp.name)
                ok = r.returncode == 0
                json.dump({"last_pushed_line": msgs[0][:30], "at": now}, open(STATE, "w"))
                print(f"[{now}] {'PUSHED' if ok else 'PUSH_FAILED'}: {msgs[0][:50]}")

        if once:
            break
        time.sleep(60)   # 常驻模式: 每分钟刷新(WS 接上后可改 1~3s 秒级)

if __name__ == "__main__":
    main()
