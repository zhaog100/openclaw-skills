#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析平台 V3.1 — gold_watch_signal 微技能（单一职责）

官家 10-22 要求: 把黄金盯价三层(①秒级tick/②15min轮询/③分钟级)收敛进门面统一架构,
   按门面现有"信号+出口"粒度拆(跟 china_us_spread 等 18 个微技能同构):
     gold_watch_signal  : 纯计算——拉金价、算沪金口径价、动态买卖点、回本线、点差 (不推送)
     gold_watch_outcome : 出口——读 signal 结果判到价, 生成"申购/赎回国泰 A/C 哪只"文本, 走 send_qq_gw 门面推送
   频率不进技能, 进 scheduler (schedules.yaml 的 cron 参数): 1min/15min/每日摘要 都调同一个 workflow。

本技能 = 信号层: 拉国际金 XAUUSD(REST 兜底 + WS 接入点), 折算沪金基准价, 算动态买卖点/回本线。
   数据源优先级: XAU_WS_URL 配了就走 WebSocket 秒级 tick; 没配走免费 REST(gold-api)。
   官家实盘: 中行积存金 成本 903 / 点差 16.6 / 回本线 919.6 (config gold_watch.json)。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, json, urllib.request, statistics
from skills.base import BaseSkill

FX = 7.10            # USD/CNY 粗估(国际金→沪金口径换算)
G_PER_OZ = 31.1035   # 克/盎司
REST_XAU = "https://api.gold-api.com/price/XAU"   # 免费 REST 兜底源(国际金, 仅作参考)


def _fetch_au0(n_days=120):
    """拉国内沪金 AU0 主连日线(akshare, 各银行积存金的行情锚, 贴实盘)。
    返回 (close, high, low) 最近 n_days 日列表, 失败返回 None。"""
    try:
        import akshare as ak
        r = ak.futures_main_sina("AU0")
        r.columns = [c.lower() for c in r.columns]
        r = r.sort_values("日期").tail(n_days)
        return (r["收盘价"].tolist(), r["最高价"].tolist(), r["最低价"].tolist())
    except Exception:
        return None


class GoldWatchSignalSkill(BaseSkill):
    name = "gold_watch_signal"
    description = "黄金实时盯价信号: 拉 XAUUSD/沪金价→折算沪金基准价+动态买卖点+回本线(纯计算不推送)"
    version = "1.0.0"
    depends_on: list = []

    def _cfg_path(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ws = os.path.dirname(base)   # economic-outlook -> workspace
        p = os.path.join(ws, "oil-gold-correlation", "data", "gold_watch.json")
        return p

    def _load_cfg(self):
        p = self._cfg_path()
        if not os.path.exists(p):
            return {}
        return json.load(open(p)).get("watch_shgold_spot", {})

    def _fetch_xau(self):
        """拉 XAUUSD(美元/盎司)。WS 源优先(XAU_WS_URL), 兜底 REST。"""
        ws_url = os.environ.get("XAU_WS_URL", "")
        if ws_url:
            # 接入点: 官家有 XAUUSD WebSocket tick 源时启用(websockets 连 ws_url、订阅、取最新价)
            # 骨架留口, 不硬造拉不通的 WS(当前无稳定免费 tick 源)
            pass
        try:
            r = urllib.request.urlopen(REST_XAU, timeout=10)
            return float(json.loads(r.read()).get("price", 0)), "rest"
        except Exception:
            return None, None

    def run(self, context: dict) -> dict:
        cfg = self._load_cfg()
        cost = cfg.get("cost_basis", 903)
        spread = cfg.get("spread", 16.6)
        breakeven = cfg.get("breakeven", round(cost + spread, 1))

        xau, xau_src = self._fetch_xau()
        au0 = _fetch_au0()
        dyn = cfg.get("dynamic", {})
        out = {"cost_basis": cost, "spread": spread, "breakeven": breakeven, "xauusd": xau}

        # 价格源优先级(官家 10-23 三连质疑后定): ① 国内沪金 AU0(自动、贴实盘、各行行情锚)
        #              ② 中行实盘价 boc_spot(校准锚, 官家截图喂) ③ 国际 XAUUSD 折算(仅兜底)
        off1 = dyn.get("band1_offset", 5)
        off2 = dyn.get("band2_offset", 5)
        lb1 = int(dyn.get("lookback_1", 20))
        lb2 = int(dyn.get("lookback_2", 60))
        use_au0 = bool(au0 and len(au0[0]) >= lb2)
        if use_au0:
            close, high, low = au0
            c_last = close[-1]
            hi1, lo1 = max(high[-lb1:]), min(low[-lb1:])
            hi2, lo2 = max(high[-lb2:]), min(low[-lb2:])
            mid1 = statistics.median(close[-lb1:])
            out.update({
                "success": True, "source": "au0", "price_basis": "国内沪金AU0(自动,各银行积存金行情锚)",
                "sh_equiv": round(c_last, 2), "au0_last": round(c_last, 2),
                "dyn_buy1": round(lo1 - off1, 2),   # 买点一档 = 近lb1日最低-偏移
                "dyn_buy2": round(lo2 - off2, 2),   # 买点二档 = 近lb2日最低-偏移
                "dyn_sell1": round(hi1, 2),         # 卖点一档 = 近lb1日最高
                "dyn_sell2": round(hi2, 2),         # 卖点二档 = 近lb2日最高
                "dyn_hi1": round(hi1, 2), "dyn_lo1": round(lo1, 2),
                "dyn_hi2": round(hi2, 2), "dyn_lo2": round(lo2, 2),
                "dyn_mid1": round(mid1, 2),
            })
            # 趋势过滤器(官家 10-24 要求: 均线要分析出"在跌", 不只给档位)
            # MA20 斜率(近段 vs 前段) + RSI14 + 现价 vs 20日低点 → 输出 trend_state
            ma20_now = statistics.mean(close[-lb1:]) if len(close) >= lb1 else None
            ma20_prev = statistics.mean(close[-2*lb1:-lb1]) if len(close) >= 2*lb1 else None
            slope = (ma20_now - ma20_prev) if (ma20_now is not None and ma20_prev is not None) else 0.0
            # RSI14
            n = 14
            if len(close) > n:
                gains = [max(close[i]-close[i-1], 0) for i in range(len(close)-n, len(close))]
                losses = [max(close[i-1]-close[i], 0) for i in range(len(close)-n, len(close))]
                _g, _l = statistics.mean(gains), statistics.mean(losses)
                rsi14 = 100.0 if _l == 0 else 100 - 100/(1 + _g/_l)
            else:
                rsi14 = None
            last_c = close[-1]
            dist_lo1 = round(last_c - lo1, 2)
            # 趋势判定: 跌势=MA20斜率<-2 且 RSI14<45; 涨势=斜率>+2; 否则横盘
            if slope < -2 and (rsi14 is None or rsi14 < 45):
                trend_state = "downtrend"
            elif slope > 2:
                trend_state = "uptrend"
            else:
                trend_state = "sideways"
            out.update({
                "trend_state": trend_state,
                "trend": {
                    "ma20_now": round(ma20_now, 2) if ma20_now is not None else None,
                    "ma20_prev": round(ma20_prev, 2) if ma20_prev is not None else None,
                    "ma20_slope": round(slope, 2),
                    "rsi14": round(rsi14, 1) if rsi14 is not None else None,
                    "dist_to_lo1": dist_lo1,
                    "note": "跌势=MA20斜率<-2且RSI<45; 买点触发在跌势中需官家确认防半山腰",
                },
            })
        else:
            # AU0 拉不到 → 退回实盘价/国际金折算, 动态均线退化为 config 固定档
            boc = cfg.get("boc_spot") or {}
            if boc.get("buy"):
                out.update({"success": True, "source": "boc_spot", "price_basis": "中行实盘客户买入价(AU0不可用)",
                            "sh_equiv": float(boc["buy"]), "boc_buy": boc["buy"], "boc_ts": boc.get("ts", "")})
            elif xau is not None:
                out.update({"success": True, "source": xau_src or "rest", "price_basis": "XAUUSD折算(AU0/实盘均不可用,近似)",
                            "sh_equiv": round(xau * FX / G_PER_OZ, 2)})
            else:
                out.update({"success": False, "source": "unavailable", "price_basis": "无可用源",
                            "error": "AU0/实盘价/国际金 均不可用, 本轮不用过期价"})
                return out
            # 退级: 动态档算不出, 用 config 里现有固定档(若没有则无动态档, 仅提示)
            out.setdefault("dyn_buy1", cfg.get("buy1"))
            out.setdefault("dyn_buy2", cfg.get("buy2"))
            out.setdefault("dyn_sell1", cfg.get("sell1"))
            out.setdefault("dyn_sell2", cfg.get("sell2"))

        out["targets"] = dyn.get("targets", ["hi20", "hi60"])
        out["min_target"] = cfg.get("breakeven", breakeven)  # 卖点须 ≥ 回本线
        out["bank_premium"] = cfg.get("bank_premium", 21)
        return out


if __name__ == "__main__":
    import sys
    skill = GoldWatchSignalSkill()
    r = skill.execute({})
    print(json.dumps(r.data if r.success else {"error": r.error}, ensure_ascii=False))
