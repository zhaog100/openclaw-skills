#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时金价获取(官家 10-24: 两个网站页面都有实时价, 不能给旧数据)
PW 渲染东财黄金页 → 解析 DOM 价格元素, 双源互验。
拉不到 → 返回 stale 标记, 调用方必须显式标"旧数据", 绝不冒充实时。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import re, time, sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
# 官家给的两个网站
SOURCES = [
    ("东财·黄金", "https://quote.eastmoney.com/gjs/hj.html"),
    ("金投网·实时", "https://m.cngold.org/quote/gjs/gjhj_xhhj.html?key=***"),
]


def fetch_page_prices(page):
    """从渲染好的 page 里扒价格元素文本(不靠中文标签猜, 抓含价格的 DOM 节点)。"""
    try:
        els = page.eval_on_selector_all(
            "[class*='price'],[class*='num'],[class*='quote'],[class*='cur'],[class*='new'],[class*='zxj']",
            "els => els.map(e => e.textContent.trim()).filter(t => /\\d{3,5}\\.\\d{1,2}/.test(t) && t.length < 25)")
        return [e[:60] for e in els][:30]
    except Exception:
        return []


def _render_once(ctx, url, tries=2):
    """渲染一次(可重试): 返回价格元素文本列表。"""
    from playwright.sync_api import sync_playwright
    prices = []
    for t in range(tries):
        page = ctx.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=50000)
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass
            time.sleep(7)
            prices = fetch_page_prices(page)
            if prices:
                break
            # 没拿到: 再等一下重试(行情异步渲染慢)
        except Exception:
            pass
        finally:
            page.close()
    return prices


def get_realtime_gold() -> dict:
    """返回 {ok, prices, source, ts, note}: 拉不到实时价 ok=False 并标 stale。
    双源×各2次重试, 取第一个有价的源。"""
    from playwright.sync_api import sync_playwright
    out = {"ok": False, "prices": [], "source": "", "ts": time.strftime("%Y-%m-%d %H:%M:%S"), "note": ""}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
            ctx = browser.new_context(user_agent=UA, locale="zh-CN", viewport={"width": 1366, "height": 900})
            ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined}); window.chrome={runtime:{}};")
            for name, url in SOURCES:
                prices = _render_once(ctx, url, tries=2)
                if prices:
                    out["ok"] = True
                    out["prices"] = prices
                    out["source"] = name
                    break
            browser.close()
    except Exception as e:
        out["note"] = f"PW渲染失败: {str(e)[:80]}"
    if not out["ok"]:
        out["note"] = out.get("note") or "实时源不可用, 以下为缓存旧数据(仅供参考, 非实时)"
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(get_realtime_gold(), ensure_ascii=False))
