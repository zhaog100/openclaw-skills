#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P6 银行黄金成本项感知 — 三条腿并行(官家 10-24 拍板, 不要等他喂, 提前知道银行新信息)

腿1 工行官方公告页(Playwright, 已验证可通): 费率条款级
腿2 新浪7x24快讯 + 金投网(纯 requests, 已验证可通): 多行联动事件快讯
腿3 官家喂的银行App/公众号链接(10秒进四行条款对照表): 补银行私有渠道

触发: 命中 KEYWORDS → 打印影响判断; 未命中 → QUIET(静默不打扰)
降级链: 主力源挂 → 新浪7x24兜底

用法: python3 bank_gold_watch.py [all|icbc|feed]
输出: 命中条款/快讯清单 + 影响判断; 未命中 QUIET

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import sys, re, time, json, os, urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
KEYWORDS = ["积存金", "黄金", "贵金属", "手续费", "费率", "定投", "每克", "央行", "中行", "工行", "中信", "南京银行"]

# 官方源(Playwright 从首页/栏目真实入口进, 不猜URL — R-严谨): 工行/中行/中信 已验证可通
# 链接来源: 从各家首页导航扒出的真实公告/黄金栏目页(10-24 实测)
SOURCES = {
    "icbc": {"name": "中国工商银行", "url": "https://www.icbc.com.cn/column/1438058327061184562.html", "note": "更多公告页, 已通"},
    "boc": {"name": "中国银行", "url": "https://www.boc.cn/pbservice/bi2/", "note": "个人服务公告页(收费调整公告在此), 已通; 另: 金市观察 https://www.boc.cn/fimarkets/fm7/"},
    "citic": {"name": "中信银行", "url": "https://www.citicbank.com/personal/investment/reserve/", "note": "积存金产品页, 已通; 另: 服务公告 https://www.citicbank.com/common/servicenotice/"},
    "njbank": {"name": "南京银行", "url": None, "note": "本机DNS解析失败(域名未定), 待官家喂或确认官方域名"},
}

# 快讯源: 新浪7x24(开放JSON, 已验证) + 金投网(门户, 已验证)
FEED_SOURCES = {
    "sina7x24": "https://zhibo.sina.com.cn/api/zhibo/feed?cp=0&page=1&zhibo_id=152&tag_id=0&page_size=50",
    "cngold": "https://www.cngold.org/",
}


def _get(url, referer=None):
    h = {"User-Agent": UA}
    if referer:
        h["Referer"] = referer
    req = urllib.request.Request(url, headers=h)
    return urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")


def scan_banks_official() -> dict:
    """腿1: Playwright 扫工行/中行/中信 官方公告页(真实入口), 合并命中。
    R-严谨: 链接是从各家首页导航扒的真实入口, 不是猜的URL。"""
    out = {"bank": "official", "hits": [], "per_bank": {}}
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent=UA, locale="zh-CN", viewport={"width": 1366, "height": 900})
        ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined}); window.chrome={runtime:{}};")
        for key, src in SOURCES.items():
            if not src.get("url"):
                out["per_bank"][key] = {"note": src["note"]}
                continue
            page = ctx.new_page()
            bank_hits = []
            try:
                page.goto(src["url"], wait_until="domcontentloaded", timeout=30000)
                time.sleep(3)
                body = page.locator("body").inner_text()
                # 同时扫链接文本 + 正文里的关键词命中
                links = page.eval_on_selector_all("a", "els => els.map(a=>({t:a.textContent.trim(),h:a.href})).filter(x=>x.t)")
                for l in links:
                    if any(k in l["t"] for k in KEYWORDS):
                        bank_hits.append({"title": l["t"][:50], "url": l["h"][:80], "src": "link"})
                # 正文里直接含关键词的条目(公告标题常在正文里)
                for line in body.split("\n"):
                    line = line.strip()
                    if 6 < len(line) < 90 and any(k in line for k in KEYWORDS):
                        bank_hits.append({"title": line[:80], "src": "body"})
                # 去重
                seen = set(); dedup = []
                for h in bank_hits:
                    key2 = h["title"]
                    if key2 not in seen:
                        seen.add(key2); dedup.append(h)
                out["per_bank"][key] = {"name": src["name"], "hits": dedup[:15]}
                out["hits"].extend([{**h, "bank": src["name"]} for h in dedup])
            except Exception as e:
                out["per_bank"][key] = {"name": src["name"], "error": str(e)[:60]}
            page.close()
    return out


def scan_sina7x24() -> dict:
    """腿2: 新浪7x24快讯, 抓黄金/银行相关条目。"""
    out = {"bank": "sina7x24", "hits": []}
    try:
        raw = _get(FEED_SOURCES["sina7x24"])
        # 新浪7x24返回多段JSON, 取第一段可解析的
        data = None
        for i in range(len(raw) - 1, 0, -1):
            try:
                data = json.loads(raw[:i])
                break
            except Exception:
                pass
        lst = (data or {}).get("result", {}).get("data", {}).get("feed", {}).get("list", [])
        for x in lst:
            text = x.get("rich_text", "") or x.get("title", "") or ""
            if any(k in text for k in KEYWORDS):
                out["hits"].append({"text": text[:80].replace("\n", " ")})
        out["total"] = len(lst)
    except Exception as e:
        out["error"] = f"新浪7x24抓取失败: {str(e)[:60]}"
    return out


def scan_cngold() -> dict:
    """腿2: 金投网(贵金属门户), 抓黄金相关消息。"""
    out = {"bank": "cngold", "hits": []}
    try:
        html = _get(FEED_SOURCES["cngold"])
        lines = [l.strip() for l in re.sub(r"<[^>]+>", "\n", html).split("\n")]
        seen = set()
        for l in lines:
            if 6 < len(l) < 90 and any(k in l for k in KEYWORDS) and l not in seen:
                seen.add(l)
                out["hits"].append({"text": l[:80]})
            if len(out["hits"]) >= 15:
                break
    except Exception as e:
        out["error"] = f"金投网抓取失败: {str(e)[:60]}"
    return out


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    all_hits = []

    if target in ("all", "icbc"):
        r = scan_banks_official()
        for key, pr in r.get("per_bank", {}).items():
            if "error" in pr:
                print(f"【{pr.get('name', key)}】⚠️ {pr['error']}")
            elif pr.get("note"):
                print(f"【{pr.get('name', key)}】{pr['note']}")
            elif pr.get("hits"):
                print(f"【{pr.get('name', key)}】官方页命中 {len(pr['hits'])} 条黄金相关条款:")
                for h in pr["hits"][:10]:
                    extra = f" → {h['url']}" if h.get("url") else ""
                    print(f"  - {h['title']}{extra}")
            else:
                print(f"【{pr.get('name', key)}】官方页无黄金相关新条款")
        all_hits += r.get("hits", [])

    if target in ("all", "feed"):
        r = scan_sina7x24()
        if r.get("error"):
            print(f"【新浪7x24】⚠️ {r['error']}")
        elif r.get("hits"):
            print(f"【新浪7x24快讯】黄金/银行相关 {len(r['hits'])} 条:")
            for h in r["hits"][:10]:
                print(f"  - {h['text']}")
            all_hits += r["hits"]

        r = scan_cngold()
        if r.get("error"):
            print(f"【金投网】⚠️ {r['error']}")
        elif r.get("hits"):
            print(f"【金投网】黄金相关 {len(r['hits'])} 条:")
            for h in r["hits"][:10]:
                print(f"  - {h['text']}")
            all_hits += r["hits"]

    # 腿3: 官家喂的银行私有渠道(中行/中信/南京), 公网拿不到, 等他丢链接我补进对照表
    print("\n【腿3·官家喂】南京银行(本机DNS未通)+各行App内公告(公网无自动源): 官家看到丢我链接, 我10秒进对照表")

    if all_hits:
        print(f"\n→ 影响判断: 共 {len(all_hits)} 条命中, 若涉及费率/手续费/大额门槛变动, 更新 gold_watch.json 或四行条款对照表")
    else:
        print("QUIET")


if __name__ == "__main__":
    sys.exit(main())
