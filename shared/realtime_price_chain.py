#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多源实时金价降级链(官家 10-24: 把这些行情源都接进去, 全挂才降级, 绝不拿旧数据冒充实时)

降级顺序(稳→松):
  ① PAXG Binance(免key, 黄金代币≈XAUUSD, 最稳)
  ② gold-api.com(免key, REST JSON)
  ③ 金投网 jijinhao(免key, 常返空)
  ④ Yahoo Finance(免key, XAUUSD=X, 本机常限流→拉不到自动跳)
  ⑤ TickDB(要key: 环境变量 TICKDB_KEY 设了才用, 没设自动跳过)
  ⑥ 探数(要key: TANCHU_KEY, 没设自动跳过)
  ⑦ QOS行情(本地部署: QOS_BASE 设了才用)
  全挂 → ok=False(调用方必须显式标"旧数据", 不静默回退)

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, json, urllib.request, re, time

FX = 7.10
G_PER_OZ = 31.1035
UA = {"User-Agent": "Mozilla/5.0"}


def _get(url, headers=None, timeout=8):
    h = dict(UA)
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def _fetch_paxg():
    try:
        d = json.loads(_get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT"))
        p = float(d.get("price", 0))
        if p:
            return {"usd": p, "src": "paxg_binance", "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
    except Exception:
        pass
    return None


def _fetch_goldapi():
    try:
        d = json.loads(_get("https://api.gold-api.com/price/XAU"))
        p = float(d.get("price", 0))
        if p:
            return {"usd": p, "src": "gold_api", "ts": d.get("updatedAt", "")}
    except Exception:
        pass
    return None


def _fetch_jijinhao():
    try:
        raw = _get("https://api.jijinhao.com/sQuoteCenter/realTime.htm?code=***",
                   headers={"Referer": "https://m.cngold.org/"})
        m = re.search(r'hq_str\s*=\s*"([^"]+)"', raw)
        if m:
            f = m.group(1).split(",")
            p = float(f[2]) if len(f) > 2 and f[2] else None
            if p:
                return {"usd": p, "src": "jijinhao", "ts": ""}
    except Exception:
        pass
    return None


def _fetch_yahoo():
    try:
        d = json.loads(_get("https://query1.finance.yahoo.com/v8/finance/chart/XAUUSD=X?range=1d&interval=1m"))
        meta = d["chart"]["result"][0]["meta"]
        p = float(meta.get("regularMarketPrice", 0))
        if p:
            return {"usd": p, "src": "yahoo", "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
    except Exception:
        pass
    return None


def _fetch_tickdb():
    """TickDB(要key): 环境变量 TICKDB_KEY 设了才用, 没设自动跳过(不报错)。"""
    key = os.environ.get("TICKDB_KEY", "")
    if not key:
        return None
    try:
        d = json.loads(_get("https://apiv1.tickdb.cn/real_time/xauusd", headers={"Authorization": f"Bearer {key}"}))
        p = float(d.get("price", d.get("data", {}).get("price", 0)) or 0)
        if p:
            return {"usd": p, "src": "tickdb", "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
    except Exception:
        pass
    return None


def _fetch_tanshu():
    """探数(要key): 环境变量 TANCHU_KEY 设了才用, 没设自动跳过。"""
    key = os.environ.get("TANCHU_KEY", "")
    if not key:
        return None
    try:
        d = json.loads(_get("https://api.tanshusoft.com/gold/price", headers={"X-Api-Key": key}))
        p = float(d.get("price", d.get("data", {}).get("price", 0)) or 0)
        if p:
            return {"usd": p, "src": "tanshu", "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
    except Exception:
        pass
    return None


def _fetch_qos():
    """QOS行情(本地部署): 环境变量 QOS_BASE 设了才用。"""
    base = os.environ.get("QOS_BASE", "")
    if not base:
        return None
    try:
        d = json.loads(_get(f"{base}/quote?symbol=XAUUSD"))
        p = float(d.get("price", d.get("data", {}).get("price", 0)) or 0)
        if p:
            return {"usd": p, "src": "qos", "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
    except Exception:
        pass
    return None


def get_realtime_gold() -> dict:
    """按降级链 PAXG→gold-api→jijinhao→yahoo→tickdb→tanshu→qos 取第一个拿到的实时价。
    全挂 → ok=False(调用方必须显式标"旧数据", 绝不静默回退)。"""
    for fn in (_fetch_paxg, _fetch_goldapi, _fetch_jijinhao, _fetch_yahoo,
               _fetch_tickdb, _fetch_tanshu, _fetch_qos):
        r = fn()
        if r:
            r["ok"] = True
            r["sh_conv"] = round(r["usd"] * FX / G_PER_OZ, 2)
            return r
    return {"ok": False, "usd": None, "src": "none", "ts": "",
            "note": "全部实时源不可用, 以下若用数据为旧缓存(非实时)"}


if __name__ == "__main__":
    print(json.dumps(get_realtime_gold(), ensure_ascii=False))
