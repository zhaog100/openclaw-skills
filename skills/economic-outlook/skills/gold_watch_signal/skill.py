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
REST_XAU = "https://api.gold-api.com/price/XAU"   # 国际金实时源(gold-api, 稳定, 分钟级刷新)
# 口径铁律(官家10-24三连质疑后钉死): 国际金实时价只作"盘中分钟级趋势参考",
#   推给官家的买卖基准价 = au0 国内沪金(贴实盘864~880), 国际金折算沪金(~918)比实盘虚高~40元, 禁作基准
#   两者交叉验证: 实时折算价 vs au0日线 差>30元 → 报警(源异常或汇率漂移)


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

# 盘中实时源(官家 10-24 发的金投网 jijinhao 实时接口, 分钟级):
#   sQuoteCenter/realTime.htm?code=JO_92233 返回 var hq_str="现货黄金,最新价,昨收,高,低,..."
#   JO_92233 = 现货黄金(美元/盎司), 再按 FX/G_PER_OZ 折沪金口径。au0 日线只用于算 20/60 日均线档。
JH_REALTIME_URL = "https://api.jijinhao.com/sQuoteCenter/realTime.htm?code=JO_92233"


def _fetch_realtime_spot() -> dict:
    """拉国际现货金 XAUUSD 实时价(美元/盎司, 分钟级)。主 gold-api(REST JSON, 稳), 备 jijinhao。
    口径: 仅作盘中分钟级趋势参考, 非推给官家的买卖基准(基准=au0国内沪金)。"""
    import re
    # 主源: gold-api REST JSON(实测稳定, 有 updatedAt 时间戳)
    try:
        req = urllib.request.Request(REST_XAU, headers={"User-Agent": "Mozilla/5.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=10).read().decode("utf-8", "ignore"))
        spot = d.get("price")
        if spot:
            return {"spot_usd": float(spot), "ts": d.get("updatedAt", ""), "src": "gold-api"}
    except Exception:
        pass
    # 备源: 金投网 jijinhao hq_str(可能返空, 降级)
    try:
        req = urllib.request.Request(
            JH_REALTIME_URL,
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://m.cngold.org/"},
        )
        raw = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", "ignore")
        m = re.search(r'hq_str\s*=\s*"([^"]+)"', raw)
        if not m:
            return {}
        f = m.group(1).split(",")
        spot = float(f[2]) if len(f) > 2 else None
        if not spot:
            return {}
        return {"spot_usd": spot, "ts": "", "src": "jijinhao"}
    except Exception:
        return {}


def _fetch_realtime_multisource() -> dict:
    """多源降级链(官家10-24: 源要多, 全挂才降级): PAXG Binance(稳主) → gold-api → jijinhao。
    全挂返回 {}(调用方退 au0 日线 + 标'盘中滞后'), 绝不拿旧缓存冒充实时。
    复用 shared/realtime_price_chain 模块; 拿不到该模块则退回单源 _fetch_realtime_spot。"""
    try:
        import os, json as _json, sys
        _shared = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "shared")
        if _shared not in sys.path:
            sys.path.insert(0, _shared)
        from realtime_price_chain import get_realtime_gold
        r = get_realtime_gold()
        if r.get("ok") and r.get("usd"):
            return {"spot_usd": r["usd"], "ts": r.get("ts", ""), "src": r.get("src", "multisource")}
    except Exception:
        pass
    # 兜底单源
    return _fetch_realtime_spot()


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

        # 双源口径(官家 10-25 拍板 1+2, "实时+准确, 不截图"):
        #   ① 主基准 = 国际金实时(PAXG/gold-api, 7x24 在动) 折上海金口径
        #   ② au0 沪金日线 = 均线/动态档参考(算 20/60 日高低点用)
        #   推给官家的 sh_equiv = ①实时折算价(有①用①, ①挂退 au0 收盘②)
        rt = _fetch_realtime_multisource()
        sh_rt = round(rt["spot_usd"] * FX / G_PER_OZ, 2) if rt.get("spot_usd") else None

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
            # 口径铁律(官家10-24): 推给官家的买卖基准 = au0 国内沪金(贴实盘), 国际金实时价只作盘中参考
            # 均线档永远 au0 日线算; 实时国际金价 vs au0 折算交叉验证, 差>30元报警
            # 双源: sh_equiv = 国际金实时折算(①主), au0 收盘(②参考)
            base = sh_rt if sh_rt else round(c_last, 2)
            if rt.get("spot_usd"):
                out.update({
                    "success": True, "source": "国际金实时+沪金参考",
                    "price_basis": "基准=国际金实时折上海金(7x24), au0沪金日线作均线参考",
                    "sh_equiv": base,
                    "intl_realtime": {"usd": rt["spot_usd"], "sh_conv": sh_rt,
                                       "ts": rt.get("ts", ""), "src": rt.get("src")},
                    "au0_last": round(c_last, 2),
                    "au0_note": "au0为周五收盘(周末不更新), 均线档仍按au0日线算",
                })
                # 交叉验证: 国际金折算 vs au0 收盘, 差>30 提示口径/汇率漂移(仅提示不改基准)
                diff = abs(sh_rt - round(c_last, 2))
                if diff > 30:
                    out["cross_check"] = {"diff": round(diff, 1), "alert": True,
                                          "note": f"国际金折算{sh_rt} vs au0收盘{round(c_last,2)} 差{diff:.0f}元, 口径/汇率漂移提示"}
                else:
                    out["cross_check"] = {"diff": round(diff, 1), "alert": False}
            else:
                out.update({
                    "success": True, "source": "沪金日线",
                    "price_basis": "国际金实时源不可用, 退au0沪金日线(周末=周五收盘)",
                    "sh_equiv": round(c_last, 2), "au0_last": round(c_last, 2),
                    "warn": "国际金实时源不可用, 本轮为au0日线价",
                })
            # 均线档(永远 au0 日线算) + 原 update 里的档位字段保留
            # 1+2 双源: 档位也切国际金实时口径(和现价同一口, 消除 ~47 元基差)
            # 档位 = 国际金实时价 + (au0 高低点相对 au0 收盘的偏移), 结构仍用 au0 日线 20/60 日高低点
            base_rt = sh_rt if sh_rt else round(c_last, 2)
            au0_rel_lo1 = lo1 - c_last
            au0_rel_hi1 = hi1 - c_last
            au0_rel_lo2 = lo2 - c_last
            au0_rel_hi2 = hi2 - c_last
            out.update({
                "dyn_buy1": round(base_rt + au0_rel_lo1 - off1, 2),   # 买点一档 = 实时基准+近lb1日最低偏移-偏移量
                "dyn_buy2": round(base_rt + au0_rel_lo2 - off2, 2),   # 买点二档 = 实时基准+近lb2日最低偏移-偏移量
                "dyn_sell1": round(base_rt + au0_rel_hi1, 2),        # 卖点一档 = 实时基准+近lb1日最高偏移
                "dyn_sell2": round(base_rt + au0_rel_hi2, 2),        # 卖点二档 = 实时基准+近lb2日最高偏移
                "dyn_hi1": round(base_rt + au0_rel_hi1, 2), "dyn_lo1": round(base_rt + au0_rel_lo1, 2),
                "dyn_hi2": round(base_rt + au0_rel_hi2, 2), "dyn_lo2": round(base_rt + au0_rel_lo2, 2),
                "dyn_mid1": round(base_rt + (mid1 - c_last), 2),
                "dyn_note": "档位=国际金实时价+au0 20/60日高低偏移(与现价同口径, 消除基差)",
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
                trend_state = "跌势"
            elif slope > 2:
                trend_state = "涨势"
            else:
                trend_state = "横盘"
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
