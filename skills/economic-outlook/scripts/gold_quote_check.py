#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""沪金现货行情独立验证脚本 (官家 11-01 定稿)
版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
Author: 小米粒 (Xiaomili) - AI Agent

拉两个源并逐项验证字段语义, 不需要 import 技能包:
  ① 东财 118.AU9999  → f43(最新价), f19/f45 冗余, f44高/f46开/f60昨收
  ② 金投网 JO_71     → q5(最新价, =q4=q63 同族), q2/q64=昨收(绝不用)

用法: python3 gold_quote_check.py
输出: 两源最新价 + 交叉验证(应一致=同秒现货), 不一致时标出口径漂移。
"""
import urllib.request, json, re, time, datetime

UA_WEB = ("Mozilla/5.0 (Windows NT 10.0; Win64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
UA_MOB = ("Mozilla/5.0 (Linux; Android 16; Pixel 10) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/156.0.0.0 Mobile Safari/537.36")
NOW_MS = lambda: str(time.time_ns() // 10**6)


def _get(url, referer, ua):
    h = {"User-Agent": ua, "Referer": referer, "Accept": "*/*"}
    return urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=10).read()


def em_scale(v):
    """东财 118 市场字段 >10000 视为 ×100(2位小数)。"""
    if v is None:
        return None
    return round(v / 100, 2) if v > 10000 else v


def fetch_eastmoney():
    """东财 118.AU9999 现货, 多节点并发取最新价 f43。返回 dict 或 None。"""
    import concurrent.futures as cf

    def parse(raw):
        s = raw.decode("utf-8-sig", "ignore").lstrip()
        if s.startswith("jQuery") or s[0] == "(":
            i = s.index("("); j = s.rfind(")"); s = s[i + 1:j if j > 0 else len(s)]
        return (json.loads(s).get("data")) or {}

    def try_node(url):
        try:
            d = parse(_get(url, "https://quote.eastmoney.com/", UA_WEB))
            if d.get("f43") is None and d.get("f19") is not None:
                d["f43"] = d["f19"]
            if d.get("f43") is None:
                return None
            return d
        except Exception:
            return None

    F = "?invt=2&fltt=1&fields=f43,f57,f58,f44,f45,f46,f19,f60,f86&secid=118.AU9999&ut=fa5fd1943c7b386f172d6893dbfba10b"
    nodes = [
        "http://push2.eastmoney.com/api/qt/stock/get" + F,
        "https://push2delay.eastmoney.com/api/qt/stock/get" + F,
        "https://push2.eastmoney.com/api/qt/stock/get" + F,
        "https://2.eastmoney.com/api/qt/stock/get" + F,
        "https://3.eastmoney.com/api/qt/stock/get" + F,
    ]
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        for d in ex.map(try_node, nodes):
            if d:
                ts = d.get("f86")
                return {
                    "price": em_scale(d.get("f43")),
                    "f19": em_scale(d.get("f19")), "f45": em_scale(d.get("f45")),
                    "high": em_scale(d.get("f44")), "open": em_scale(d.get("f46")),
                    "prev_close": em_scale(d.get("f60")),
                    "ts": datetime.datetime.fromtimestamp(ts).strftime("%m-%d %H:%M:%S") if ts else None,
                    "name": d.get("f58"),
                }
    return None


def fetch_jijinhao():
    """金投网 JO_71(黄金9999 现货), 取 q5 最新价。返回 dict 或 None。"""
    ALL = ("JO_9753,JO_92226,JO_9754,JO_71,JO_70,JO_73,JO_72,JO_75,JO_9751,JO_9752,"
           "JO_92224,JO_92225,JO_92276,JO_76,JO_74,JO_92277,JO_92278")
    url = "https://api.jijinhao.com/quoteCenter/realTime.htm?codes=" + ALL + "&_=" + NOW_MS()
    raw = _get(url, "https://m.cngold.org/", UA_MOB).decode("utf-8", "ignore")
    m = re.search(r'"JO_71"\s*:\s*\{(.{0,600})', raw)
    if not m:
        return None
    seg = m.group(1)

    def q(key):
        mm = re.search(r'"' + key + r'"\s*:\s*([\d.\-]+)', seg)
        return float(mm.group(1)) if mm else None

    ts = re.search(r'"time"\s*:\s*(\d+)', seg)
    q5, q4, q63, q2 = q("q5"), q("q4"), q("q63"), q("q2")
    if q5 is None or not (800 < q5 < 950):
        return None
    return {
        "price": q5, "q4": q4, "q63": q63, "prev_close(q2)": q2,
        "ts": datetime.datetime.fromtimestamp(int(ts.group(1)) / 1000).strftime("%m-%d %H:%M:%S") if ts else None,
    }


def main():
    em = fetch_eastmoney()
    jh = fetch_jijinhao()
    print("=== 东财 118.AU9999 (f43 最新价) ===")
    if em:
        print(f"  最新价 f43 = {em['price']} 元/克  | {em['name']}  | ts={em['ts']}")
        print(f"  冗余验证  f19={em['f19']}  f45={em['f45']}  (应与 f43 一致)")
        print(f"  参考      最高={em['high']}  今开={em['open']}  昨收={em['prev_close']}")
    else:
        print("  全节点失败(防爬/断连), 本轮降级用金投网")
    print("\n=== 金投网 JO_71 黄金9999 (q5 最新价) ===")
    if jh:
        print(f"  最新价 q5 = {jh['price']} 元/克  | ts={jh['ts']}")
        print(f"  冗余验证  q4={jh['q4']}  q63={jh['q63']}  (应与 q5 一致)")
        print(f"  昨收 q2 = {jh['prev_close(q2)']}  (绝不用, 虚高~22元的根子)")
    else:
        print("  拉取失败")
    if em and jh:
        diff = round(em["price"] - jh["price"], 2)
        same = abs(diff) < 1.0
        print(f"\n=== 交叉验证: 东财 {em['price']} vs 金投网 {jh['price']} → 差 {diff} 元 "
              f"{'✅ 一致(同秒现货)' if same else '⚠️ 口径/时点漂移, 以上金所 UI 为准'}")


if __name__ == "__main__":
    main()
