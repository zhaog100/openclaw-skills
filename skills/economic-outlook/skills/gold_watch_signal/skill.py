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

def _fetch_au0_realtime() -> dict:
    """沪金主连实时价降级链(官家 10-26: 东财AUM主 + 金投网实时备 + 七河PW渲染 + au0日线兜底, 贴 UI 实盘 862)。
    盘中分钟级在跳; 周末=周五收盘。返回 {price, ts, src} 或空 dict。"""
    # ① 主源: 东财 113.AUM(沪金2710, 官家10-27拍板锚主力, 贴中行卖出价862.62/曲合网沪金主力863.64口径)
    try:
        url = ("https://push2.eastmoney.com/api/qt/stock/get"
               "?secid=113.AUM&fields=f43,f57,f58,f86")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=6).read().decode("utf-8", "ignore"))
        data = d.get("data") or {}
        f43 = data.get("f43")
        if f43:
            price = f43 / 100.0 if f43 > 10000 else f43
            return {"price": round(price, 2), "ts": data.get("f86", ""), "src": "eastmoney_au2710"}
    except Exception:
        pass
    # ② 备源: 金投网 jijinhao 实时 code(官家 m.cngold.org/quote/gjs/ 页, JO_283972=858.77 实时在跳, 贴现货口径)
    r = _fetch_au0_jijinhao()
    if r:
        return r
    # ③ 备源: 七河期货 shfe-aum(PW 渲染, 官家 m.quheqihuo.com 页, 东财挂时用)
    r = _fetch_au0_quhe()
    if r:
        return r
    # ④ 兜底: au0 akshare 日线(全挂时用, 周末=周五收盘)
    au0 = _fetch_au0(2)
    if au0:
        return {"price": round(au0[0][-1], 2), "ts": "", "src": "au0_daily"}
    return {}


def _fetch_au0_jijinhao() -> dict:
    """金投网 jijinhao 沪金/上海金实时 code(官家 10-26 给的 m.cngold.org/quote/gjs/ 页)。
    从页面 JS 里扒真实 code: JO_283972(858.77 实时在跳) → 现货口径, JO_9753(863.38 贴UI) 备。
    返回 {price, ts, src} 或 {}。"""
    try:
        import urllib.request as _ur, re as _re
        # 先抓页面里的 code(认真分析, 不猜): 列表页 quote/gjs/ 的 JO_ code
        base = "https://m.cngold.org/quote/gjs/"
        req = _ur.Request(base, headers={"User-Agent": "Mozilla/5.0"})
        page = _ur.urlopen(req, timeout=6).read().decode("utf-8", "ignore")
        codes = sorted(set(_re.findall(r'JO_\d{4,6}', page)))
        if not codes:
            return {}
        # 批量拉价格
        url = "https://api.jijinhao.com/quoteCenter/realTime.htm?codes=" + ",".join(codes)
        req = _ur.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://m.cngold.org/"})
        raw = _ur.urlopen(req, timeout=6).read().decode("utf-8", "ignore")
        # 取 8xx 元/克(沪金/上海金口径)的 code, 优先实时(时间戳最近的)
        best = None
        for m in _re.finditer(r'"(JO_\d{4,6})"\s*:\s*\{(.{0,400})', raw):
            code, seg = m.group(1), m.group(2)
            q2 = _re.search(r'"q2"\s*:\s*([\d.]+)', seg)
            tm = _re.search(r'"time"\s*:\s*(\d+)', seg)
            if q2:
                val = float(q2.group(1))
                if 800 < val < 950:  # 沪金/上海金 口径区间
                    ts_int = int(tm.group(1)) if tm else 0
                    cand = {"price": round(val, 2), "ts": ts_int, "src": "jijinhao", "code": code}
                    if best is None or ts_int > best["ts"]:
                        best = cand
        if best:
            return best
    except Exception:
        pass
    return {}




def _fetch_agm_realtime() -> dict:
    """沪银主连实时价降级链(官家 10-26: 东财AGM主 + 金投网jijinhao备 + au1日线兜底, 类比黄金链)。
    单位: 元/千克(沪银口径)。盘中分钟级在跳; 周末=周五收盘。返回 {price, ts, src} 或空 dict。"""
    # ① 主源: 东财 113.ag2612(沪银2612, 官家10-27截图实盘合约, 130.23 元/克; 上期所12999元/千克=12.999元/克同口径)
    try:
        url = ("https://push2.eastmoney.com/api/qt/stock/get"
               "?secid=113.AGM&fields=f43,f57,f58,f86")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=6).read().decode("utf-8", "ignore"))
        data = d.get("data") or {}
        f43 = data.get("f43")
        if f43:
            price = f43 / 100.0 if f43 > 10000 else f43
            return {"price": round(price, 2), "ts": data.get("f86", ""), "src": "eastmoney_ag2612"}
    except Exception:
        pass
    # ② 备源: 金投网 jijinhao 沪银 code(JO_9754=13021 元/千克 一带, 从 quote/gjs/ 页扒)
    import urllib.request as _ur, re as _re
    try:
        req = _ur.Request("https://m.cngold.org/quote/gjs/", headers={"User-Agent": "Mozilla/5.0"})
        page = _ur.urlopen(req, timeout=6).read().decode("utf-8", "ignore")
        codes = sorted(set(_re.findall(r'JO_\d{4,6}', page)))
        url = "https://api.jijinhao.com/quoteCenter/realTime.htm?codes=" + ",".join(codes)
        req = _ur.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://m.cngold.org/"})
        raw = _ur.urlopen(req, timeout=6).read().decode("utf-8", "ignore")
        best = None
        for m in _re.finditer(r'"(JO_\d{4,6})"\s*:\s*\{(.{0,400})', raw):
            seg = m.group(2)
            q2 = _re.search(r'"q2"\s*:\s*([\d.]+)', seg)
            tm = _re.search(r'"time"\s*:\s*(\d+)', seg)
            if q2:
                val = float(q2.group(1))
                if 10000 < val < 15000:  # 沪银 元/千克 区间
                    ts_int = int(tm.group(1)) if tm else 0
                    cand = {"price": round(val, 2), "ts": ts_int, "src": "jijinhao_silver"}
                    if best is None or ts_int > best.get("ts", 0):
                        best = cand
        if best:
            return best
    except Exception:
        pass
    # ③ 兜底: au1 akshare 日线(全挂时, 周末=周五收盘)
    try:
        import akshare as ak
        r = ak.futures_main_sina("AG0")
        r.columns = [c.lower() for c in r.columns]
        r = r.sort_values("日期")
        return {"price": round(float(r.iloc[-1]["收盘价"]), 2), "ts": "", "src": "ag0_daily"}
    except Exception:
        pass
    return {}


def _fetch_intl_silver() -> dict:
    """国际银 XAGUSD 实时价(gold-api XAG, 盘中参考, 类比黄金 gold-api XAU)。
    返回 {usd, ts, src} 或 {}。"""
    try:
        req = urllib.request.Request("https://api.gold-api.com/price/XAG", headers={"User-Agent": "Mozilla/5.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=6).read().decode("utf-8", "ignore"))
        p = d.get("price")
        if p:
            return {"usd": float(p), "ts": d.get("updatedAt", ""), "src": "gold-api-XAG"}
    except Exception:
        pass
    return {}

def _fetch_au0_quhe() -> dict:
    """七河期货 shfe-aum(沪金主力)PW 渲染取价, 东财 AUM 的备源。返回 {price, ts, src} 或 {}。"""
    try:
        import asyncio, re as _re
        from playwright.async_api import async_playwright

        async def _run():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
                ctx = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36")
                page = await ctx.new_page()
                await page.goto("https://m.quheqihuo.com/quote/shfe-aum.html",
                                 wait_until="domcontentloaded", timeout=15000)
                await page.wait_for_timeout(3000)
                text = await page.inner_text("body")
                await browser.close()
                return text

        text = asyncio.run(_run())
        # 七河页面: "沪金最新价格" 段, 862.xx 一带数字; 取最接近 860 的数(沪金主连口径)
        nums = [float(x) for x in _re.findall(r'\b8[0-9]{2}\.[0-9]{2}\b', text)]
        if not nums:
            return {}
        # 沪金主连最新价常是"最新价"后的数, 取 850~880 区间里最大(最新)的
        cands = [x for x in nums if 840 <= x <= 900]
        if not cands:
            return {}
        return {"price": round(max(cands), 2), "ts": "", "src": "quheqihuo_shfe_aum"}
    except Exception:
        return {}

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
        d = json.loads(urllib.request.urlopen(req, timeout=6).read().decode("utf-8", "ignore"))
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
        raw = urllib.request.urlopen(req, timeout=6).read().decode("utf-8", "ignore")
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
            r = urllib.request.urlopen(REST_XAU, timeout=6)
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
        au0_rt = _fetch_au0_realtime()
        agm_rt = _fetch_agm_realtime()      # 官家 10-26: 白银也接进来(东财AGM主 + 金投网备 + au1日线兜底)
        intl_ag = _fetch_intl_silver()      # 国际银 XAG 盘中参考(类比黄金 gold-api XAU)
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
            # C 双轨: 基准 = au0 沪金(官家 UI 862 实盘口径)
            # 盘中优先东财 113.AUM 实时价(分钟级在跳), 全挂退 au0 日线(周五收盘)
            base = round(au0_rt["price"], 2) if au0_rt.get("price") else round(c_last, 2)
            if rt.get("spot_usd"):
                out.update({
                    "success": True, "source": "沪金基准+国际金盘中参考",
                    "price_basis": "基准=沪金(盘中=东财AUM实时862, 贴官家UI实盘; 周末=au0周五收盘), 国际金实时(7x24)仅作盘中参考",
                    "sh_equiv": base,
                    "au0_realtime": au0_rt.get("price"),
                    "au0_realtime_src": au0_rt.get("src", ""),
                    "agm_realtime": agm_rt.get("price"),
                    "agm_realtime_src": agm_rt.get("src", ""),
                    "intl_silver": intl_ag,
                    "au0_realtime_src": au0_rt.get("src", "au0_daily"),
                    "intl_realtime": {"usd": rt["spot_usd"], "sh_conv": sh_rt,
                                       "ts": rt.get("ts", ""), "src": rt.get("src")},
                    "au0_last": round(c_last, 2),
                    "au0_note": "盘中基准=东财113.AUM沪金主连实时(贴官家UI 862); 周末退au0日线周五收盘",
                })
                # 交叉验证: 国际金折算 vs 沪金实时, 差>30 提示口径/汇率漂移(仅提示不改基准)
                diff = abs(sh_rt - base)
                if diff > 30:
                    out["cross_check"] = {"diff": round(diff, 1), "alert": True,
                                          "note": f"国际金折算{sh_rt} vs 沪金实时{base} 差{diff:.0f}元, 口径/汇率漂移提示"}
                else:
                    out["cross_check"] = {"diff": round(diff, 1), "alert": False}
            else:
                out.update({
                    "success": True, "source": "沪金日线",
                    "price_basis": "国际金实时源不可用, 基准=沪金au0(盘中=东财AUM, 周末=au0周五收盘)",
                    "sh_equiv": base, "au0_last": round(c_last, 2),
                    "warn": "国际金实时源不可用, 国际金盘中参考缺失, 基准仍为沪金",
                })
            # C 双轨: 档位=au0 沪金日线算(和基准同口径, 贴官家 UI 862), 国际金实时只作盘中参考
            out.update({
                "dyn_buy1": round(lo1 - off1, 2),   # 买点一档 = au0近lb1日最低-偏移
                "dyn_buy2": round(lo2 - off2, 2),   # 买点二档 = au0近lb2日最低-偏移
                "dyn_sell1": round(hi1, 2),         # 卖点一档 = au0近lb1日最高
                "dyn_sell2": round(hi2, 2),         # 卖点二档 = au0近lb2日最高
                "dyn_hi1": round(hi1, 2), "dyn_lo1": round(lo1, 2),
                "dyn_hi2": round(hi2, 2), "dyn_lo2": round(lo2, 2),
                "dyn_mid1": round(mid1, 2),
                "dyn_note": "档位=au0沪金20/60日高低(贴官家UI实盘口径), 国际金实时作盘中参考",
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
