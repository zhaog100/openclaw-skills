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

def _em_parse(raw: bytes) -> dict:
    """东财 stock/get 响应解析: 兼容纯JSON / jQuery JSONP / utf-8-sig BOM。返 data dict 或 {}."""
    s = raw.decode("utf-8-sig", "ignore").lstrip()
    if s.startswith("jQuery") or s[0] == "(":
        i = s.index("("); j = s.rfind(")"); s = s[i+1:j if j > 0 else len(s)]
    if not s or s[0] != "{":
        return {}
    try:
        return (json.loads(s).get("data")) or {}
    except Exception:
        return {}


def _em_scale(v):
    """东财 118 市场字段: >10000 视为 ×100(2位小数), 否则原值。"""
    if v is None:
        return None
    return round(v / 100, 2) if v > 10000 else v


def _fetch_au0_realtime() -> dict:
    """沪金现货实时价降级链(官家11-01定稿, 按官方UI实盘口径):
    ① 主源: 东财 118.AU9999(上金所现货), 取 f43(最新价)。多节点并发+单节点2.5s超时。
       官家11-01实探: https 裸直连被防爬断连; http://push2 + push2delay 可通(833.0)。
    ② 降级: 东财全挂 → 金投网 jijinhao JO_71, 取 q5(最新价)。q2 是昨收, 勿混(854.76虚高~22元根子)。
    官家10-28锁死: 纸黄金/金条/国际金折算 一律不当现货基准; 两源都空才静默, 绝不冒值。"""
    import concurrent.futures as _cf
    UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
          "Referer": "https://quote.eastmoney.com/", "Accept": "*/*"}
    def _try_node(node):
        try:
            raw = urllib.request.urlopen(urllib.request.Request(node["url"], headers=UA), timeout=2.5).read()
            data = _em_parse(raw)
            f43 = data.get("f43")
            if f43 is None and data.get("f19") is not None:
                f43 = data.get("f19")   # f43/f19/f45 三者一致=最新价, 互为冗余验证
            if f43 is not None:
                price = _em_scale(f43)
                return (price, data.get("f86", ""), node["name"],
                        _em_scale(data.get("f19")), _em_scale(data.get("f45")))
        except Exception:
            pass
        return None
    F = "?invt=2&fltt=1&fields=f43,f57,f58,f44,f45,f46,f19,f60,f86&secid=118.AU9999&ut=fa5fd1943c7b386f172d6893dbfba10b"
    # 官家11-01: http push2 优先(实测最稳) + push2delay + 其余 https 节点兜底
    nodes = [
        {"name": "push2(http)", "url": "http://push2.eastmoney.com/api/qt/stock/get" + F},
        {"name": "push2delay(https)", "url": "https://push2delay.eastmoney.com/api/qt/stock/get" + F},
        {"name": "push2(https)", "url": "https://push2.eastmoney.com/api/qt/stock/get" + F},
        {"name": "2(https)", "url": "https://2.eastmoney.com/api/qt/stock/get" + F},
        {"name": "3(https)", "url": "https://3.eastmoney.com/api/qt/stock/get" + F},
        {"name": "4(https)", "url": "https://4.eastmoney.com/api/qt/stock/get" + F},
        {"name": "5(https)", "url": "https://5.eastmoney.com/api/qt/stock/get" + F},
        {"name": "11(https)", "url": "https://11.eastmoney.com/api/qt/stock/get" + F},
    ]
    with _cf.ThreadPoolExecutor(max_workers=8) as _ex:
        for _res in _ex.map(_try_node, nodes):
            if _res:
                p, ts, name, f19v, f45v = _res
                out = {"price": p, "ts": ts,
                       "src": "东财·上金所Au9999现货", "src_cn": "东财·上金所Au9999现货(" + name + ")",
                       "host": name}
                # 官家11-01: f43/f19/f45 交叉验证(官方UI实盘口径, 三者应一致=最新价)
                out["em_verify"] = {"f43": p, "f19": f19v, "f45": f45v,
                                     "consistent": all(x is not None and abs(x - p) < 0.5 for x in (f19v, f45v))}
                return out
    # ② 降级: 东财全挂 → 金投网 jijinhao JO_71, 取 q5(最新价), 绝不用 q2(昨收, 虚高~22元根子)
    jj = _fetch_au0_jijinhao()
    if jj.get("price"):
        jj["degraded"] = True   # 降级口径标记, outcome 层据此"只展示不自动触发"
        return dict(jj)
    # 官家11-01修正: Dailyhq 是日终快照/静态日行情(非实时), 不挂实时降级链, 只当 K线/档位基准
    # ③ 降级: 上金所官网实时挂牌 /graph/quotations (heyue=Au99.99 现货, 准实时快照)
    sd = _fetch_sge_direct()
    if sd.get("price"):
        sd["degraded"] = True   # 降级口径标记, outcome 层据此"只展示不自动触发"
        return dict(sd)
    return {}


JH_MOB_UA = ("Mozilla/5.0 (Linux; Android 16; Pixel 10) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/156.0.0.0 Mobile Safari/537.36")


def _fetch_sge_dailyhq() -> dict:
    """上金所官网官方日行情 /graph/Dailyhq (官家11-01给, 仅作 K线/档位基准, 不作实时下单锚).
    POST instid=Au99.99, 返回 time=[[date,open,high,low,close],...], 取末行 close=最新官方日价.
    **口径=日终快照/静态日行情, 非实时**(末行是最近交易日日收, 如 10-30 收 867, 比实时 833 偏高,
    若当实时锚会误判破档). 用作 20/60 日高低点/MA/档位计算的历史日线源; 非交易时段/休市返回上次行情."""
    try:
        import urllib.request as _ur, json as _js, urllib.parse as _up
        data = _up.urlencode({"instid": "Au99.99"}).encode()
        req = _ur.Request("https://www.sge.com.cn/graph/Dailyhq", data=data,
            headers={"User-Agent":"Mozilla/5.0","Referer":"https://www.sge.com.cn/",
                     "X-Requested-With":"XMLHttpRequest","Content-Type":"application/x-www-form-urlencoded"})
        d = _js.loads(_ur.urlopen(req, timeout=10).read().decode("utf-8","ignore"))
        rows = d.get("time")
        if rows:
            last = rows[-1]   # [date, open, high, low, close]
            close = float(last[4])
            if close:
                return {"price": close, "ts": last[0],
                        "src":"上金所官网官方日行情Au9999","src_cn":"上金所官网官方日行情Au9999","host":"sge.com.cn"}
    except Exception:
        pass
    return {}


def _fetch_sge_direct() -> dict:
    """上金所官网直连 sge.com.cn /graph/quotations (第3路降级, 国内直连, 官家11-01加).
    heyue 字段=当前标的(Au99.99 现货), data 末值=最新挂单价。
    **口径=官网准实时快照/第三方转源, 非 tick 级官方实时**(上金所无面向公众的官方实时API, tick 只走会员终端/Wind/Bloomberg)。
    东财/金投网全挂时顶上, 绝不用 au0期货日线。返回 {price, ts, src, src_cn, host} 或 {}."""
    try:
        import urllib.request as _ur, json as _js
        req = _ur.Request(
            "https://www.sge.com.cn/graph/quotations",
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.sge.com.cn/",
                     "X-Requested-With": "XMLHttpRequest"})
        d = _js.loads(_ur.urlopen(req, timeout=10).read().decode("utf-8", "ignore"))
        if d.get("heyue") == "Au99.99" and d.get("data"):
            last = float(str(d["data"][-1]).replace(",", "") or 0)
            if last:
                return {"price": last, "ts": d.get("delaystr", ""),
                        "src": "上金所官网直连Au9999现货", "src_cn": "上金所官网直连Au9999现货",
                        "host": "sge.com.cn"}
    except Exception:
        pass
    return {}


def _fetch_au0_jijinhao(code=None) -> dict:
    """金投网 jijinhao 实时(官家 10-26 给 m.cngold.org/quote/gjs/ 页; 官家 11-01 定稿)。
    接口 = quoteCenter/realTime.htm?codes=... (官家 11-01 指定, 多 code 一次拉全量行情)。
    只认 JO_71[黄金9999]=上金所 Au9999 现货主报价口; 纸黄金/金条/T+D 全弃。
    **取 q5(最新价)**, 绝不用 q2(昨收/前结算, 虚高~22元, 是 854.76 vs 833 偏高根子)。
    响应是 `var quote_json = {...}` 包装(官家 11-01 实测), 须剥壳再按 code 匹配。
    code=None 默认 JO_71。返回 {price, ts, src} 或 {}。"""
    try:
        import urllib.request as _ur, re as _re
        want = code or "JO_71"
        # 官家11-01指定: 多 code 全量行情口(官方页面一次拉 17 个 code), JO_71 在内
        ALL = ("JO_9753,JO_92226,JO_9754,JO_71,JO_70,JO_73,JO_72,JO_75,JO_9751,JO_9752,"
               "JO_92224,JO_92225,JO_92276,JO_76,JO_74,JO_92277,JO_92278")
        url = "https://api.jijinhao.com/quoteCenter/realTime.htm?codes=" + ALL + "&_=" + str(__import__("time").time_ns() // 10**6)
        req = _ur.Request(url, headers={"User-Agent": JH_MOB_UA, "Referer": "https://m.cngold.org/"})
        raw = _ur.urlopen(req, timeout=6).read().decode("utf-8", "ignore")
        # 直接对整段 raw 匹配: `var quote_json = {...}` 里的 "JO_71" 带引号在原文中完整存在,
        # 不必剥壳(贪婪 \{[\s\S]*\} 会把前引号吃掉导致带引号匹配失败)
        m = _re.search(r'"' + want + r'"\s*:\s*\{(.{0,600})', raw)
        if m:
            seg = m.group(1)
            # 官家11-01定稿: 最新价 = q5(=q4=q63=833 同族); q2/q64=昨收854.76 绝不用
            q5 = _re.search(r'"q5"\s*:\s*([\d.]+)', seg)
            q4 = _re.search(r'"q4"\s*:\s*([\d.]+)', seg)
            q63 = _re.search(r'"q63"\s*:\s*([\d.]+)', seg)
            tm = _re.search(r'"time"\s*:\s*(\d+)', seg)
            nm = _re.search(r'"showName"\s*:\s*"([^"]+)"', seg)
            if q5:
                val = float(q5.group(1))
                if 800 < val < 950:
                    src = "金投网·" + (nm.group(1) if nm else "黄金9999")
                    return {"price": round(val, 2), "ts": int(tm.group(1)) if tm else 0,
                            "src": src, "src_cn": src, "code": want, "q5": val,
                            # q5/q4/q63 交叉验证(官方UI口径, 三者应一致=最新价 833)
                            "jh_verify": {"q5": val, "q4": float(q4.group(1)) if q4 else None,
                                          "q63": float(q63.group(1)) if q63 else None}}
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
            return {"price": round(price, 2), "ts": data.get("f86", ""), "src": "东财·沪银主力", "src_cn": "东财·沪银主力"}
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
                    cand = {"price": round(val, 2), "ts": ts_int, "src": "金投网·沪银", "src_cn": "金投网·沪银"}
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



def _fetch_sge_dailyhq() -> dict:
    """上金所官网 Dailyhq(权威, 官家10-27给). 拉到才用, 本机网络常超时→自动跳过不阻塞.
    返回 {price, ts, src} 或 {}。"""
    try:
        import urllib.request as _ur, re as _re, time as _time
        req = _ur.Request("https://www.sge.com.cn/graph/Dailyhq",
                          headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.sge.com.cn/"})
        r = _ur.urlopen(req, timeout=6).read().decode("utf-8", "ignore")
        m = _re.findall(r'Au99\.99[^0-9]{0,40}?([0-9]{3}\.[0-9]{1,3})', r)
        if m:
            return {"price": round(float(m[0]), 2), "ts": "", "src": "上金所官网(日行情)", "src_cn": "上金所官网(日行情)"}
    except Exception:
        pass
    return {}


def _fetch_tencent_fx_est() -> dict:
    """腾讯 hf_GC 国际金 × 汇率估算上海金(官家10-27给, 末位备源). 拉到才用, 差基差→明标估算.
    返回 {price, ts, src, est} 或 {}。"""
    try:
        import urllib.request as _ur
        req = _ur.Request("https://qt.gtimg.cn/q=hf_GC", headers={"User-Agent": "Mozilla/5.0"})
        t = _ur.urlopen(req, timeout=6).read().decode("utf-8", "ignore")
        f = t.split("~")
        if len(f) > 3 and f[3]:
            usd = float(f[3])
            FX = 7.10; G = 31.1035
            sh = round(usd * FX / G, 2)
            return {"price": sh, "ts": f[6] if len(f) > 6 else "", "src": "腾讯国际金×汇率估算", "src_cn": "腾讯国际金×汇率估算", "est": True}
    except Exception:
        pass
    return {}


def _fetch_au9999_kline(n_days=130):
    """东财 118.AU9999(上金所现货) 日线K线(官家10-28给的 quote.eastmoney 118.AU9999 有K线, fqt=0)。
    返回 (close, high, low) 最近 n_days 日, 供算现货 20/60 日高低点档位; 失败 None。
    口径: 现货 Au9999(贴官家截图), 替代 au0 期货日线算档, 整套全锚现货。"""
    try:
        import urllib.request as _ur, json as _json
        url = ("https://92.push2his.eastmoney.com/api/qt/stock/kline/get?"
               "secid=118.AU9999&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58"
               "&klt=101&fqt=0&end=20500101&lmt=%d" % n_days)
        req = _ur.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"})
        d = _json.loads(_ur.urlopen(req, timeout=10).read().decode("utf-8", "ignore"))
        kl = ((d.get("data") or {}).get("klines")) or []
        if not kl:
            return None
        close, high, low = [], [], []
        for k in kl:
            f = k.split(",")
            close.append(float(f[2])); high.append(float(f[3])); low.append(float(f[4]))
        return (close, high, low)
    except Exception:
        return None
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
        return {"price": round(max(cands), 2), "ts": "", "src": "七河·沪金(PW渲染)", "src_cn": "七河·沪金(PW渲染)"}
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
        return {"spot_usd": spot, "ts": "", "src": "金投网·上金所现货", "src_cn": "金投网·上金所现货"}
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
        au9999_k = _fetch_au9999_kline()   # 官家10-28: 现货Au9999 K线(东财118.AU9999), 档位全锚现货
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
        # 官家10-28: 档位全锚现货Au9999 K线(东财118.AU9999), au0期货日线降为兜底
        # 官家10-28 861根子: 基准只认真实现货实时价(au0_rt=东财118.AU9999/金投网现货),
        # 现货K线拉空只影响档位、绝不退 au0期货日线(861) 或国际金折算(877) 当基准
        # 15:12实拉: au0_rt=866.69拉到但sh_equiv=None → else分支(503行)把拉到价丢了
        # 修死: K线拉空时基准仍用 au0_rt, 档位退 au0期货日线算; 两现货源全空才静默
        # 官家11-01降级: 东财AU9999全挂时, 第二现货源=金投网jijinhao realTime JO_71(黄金9999现货, 准实时)
        au0_rt_eff = au0_rt   # 兼容: 若 au0_rt 为空, _fetch_au0_realtime 已自动降级到 jijinhao, 这里 au0_rt_eff 即降级结果
        if not au0_rt_eff.get("price"):
            out["success"] = False
            out["price_basis"] = "现货实时价不可用(东财AU9999+金投网jijinhao全挂), 本轮静默(不触发申购, 不退期货au0/国际金折算)"
            out["intl_ref_only"] = {"usd": xau, "sh_conv": round(xau * FX / G_PER_OZ, 2) if xau else None,
                                      "note": "仅国际金参考, 绝不冒充现货/不触发申购"}
            return out
        base = round(au0_rt_eff["price"], 2)   # 基准=现货实时价(东财AU9999优先, 挂则金投网jijinhao JO_71降级), 永不退期货861/国际金877
        out["au0_realtime"] = base
        # 官家11-01: _fetch_au0_realtime 已在降级时(东财全挂→金投网)给 dict 打 degraded=True
        # 直接读那个标记; 不要再用 not price and price 反推(au0_rt_eff==au0_rt 时恒 False, 14:24 实测坑)
        _is_degraded = bool(au0_rt_eff.get("degraded"))
        out["au0_realtime_src"] = ((au0_rt_eff.get("src_cn") or au0_rt_eff.get("src", "")) + ("(降级)" if _is_degraded else ""))
        out["degraded_basis"] = _is_degraded
        use_au9999 = bool(au9999_k and len(au9999_k[0]) >= lb2)
        use_au0 = (not use_au9999) and bool(au0 and len(au0[0]) >= lb2)
        if use_au9999 or use_au0:   # K线或期货日线任一拉到, 档位就能算, 基准都用 base(现货价)
            if use_au9999:
                close, high, low = au9999_k
            else:
                close, high, low = au0
            c_last = close[-1]
            hi1, lo1 = max(high[-lb1:]), min(low[-lb1:])
            hi2, lo2 = max(high[-lb2:]), min(low[-lb2:])
            mid1 = statistics.median(close[-lb1:])
            # 基准=base(现货实时价), 档位=K线或期货日线 20/60日高低(K线拉空退期货日线, 基准不受影响)
            c_last_ref = c_last   # K线/期货收盘仅作参考展示, 不作基准
            if rt.get("spot_usd"):
                # 国际金只进 intl_realtime 当参考展示, 绝不赋 sh_equiv/不触发申购; sh_equiv=现货 base
                out.update({
                    "success": True, "source": "沪金基准+国际金盘中参考",
                    "price_basis": "基准=沪金(盘中=东财AUM实时862, 贴官家UI实盘; 周末=au0周五收盘), 国际金实时(7x24)仅作盘中参考",
                    "sh_equiv": base,
                    "au0_realtime": base,
                    "au0_realtime_src": out.get("au0_realtime_src", au0_rt_eff.get("src_cn") or au0_rt_eff.get("src", "")),
                    "agm_realtime": agm_rt.get("price"),
                    "agm_realtime_src": agm_rt.get("src", ""),
                    "intl_silver": intl_ag,
                    "intl_realtime": {"usd": rt["spot_usd"], "sh_conv": sh_rt,
                                       "ts": rt.get("ts", ""), "src": rt.get("src")},
                    "au0_last": round(c_last, 2),
                    "au0_note": "基准=东财118.AU9999现货(贴官家两网站869口径); 现货拉空时退K线收盘, 绝不回退国际金折算价",
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
            # K线档位源全挂但基准 base 已拉到(东财 或 降级金投网 jijinhao) → 退 config 固定档, 基准不丢, success=True
            # 绝不能静默: 基准价已拿到, 只用固定档, 照样能跑破档判定
            out.update({
                "success": True, "source": "沪金现货基准+固定档(K线挂, 动态档退config)",
                "price_basis": "基准=沪金现货(东财AU9999优先/挂则金投网jijinhao降级); K线档位挂退固定档, 国际金仅作盘中参考",
                "sh_equiv": base, "au0_realtime": base,
            })
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
