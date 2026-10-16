#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — 多信息源并行采集器（避免单一源滞后/视角偏差）

设计原则（官家要求）：
- 采集尽可能多的信息源，单源会导致信息单一 + 滞后
- 多源并行：单个源挂了/滞后不影响其他
- 去重交叉验证：多源都报道的事件置信度高，单源标注"待确认"
- 失败隔离：每个源独立 try/except，失败记入 gaps 不崩

源分三类：
- 实时快讯: 财联社 / 东方财富 / 新浪 / 新华财经（抓当天政策/事件）
- 官方定向: 央行 / 发改委 / 国务院（官方政策原文）
- 大宗价格: 上海有色（金属，补东财被挡的缺口）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, re, time, logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import requests
except ImportError:
    requests = None

BASE_HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0"}

# ============ 信息源清单（可扩展，加源只改这里）============
SOURCES = {
    # === 财经快讯网站 ===
    "新华通讯社": {"url": "https://www.news.cn/", "type": "news", "desc": "新华社权威快讯"},
    "金十数据": {"url": "https://www.jin10.com/", "type": "news", "desc": "经济金融快讯"},
    "华尔街见闻": {"url": "https://wallstreetcn.com/live", "type": "news", "desc": "实时快讯"},
    "新浪财经": {"url": "https://finance.sina.com.cn/", "type": "news", "desc": "财经快讯"},
    # === 微信公众号（mp.weixin 直采正文，实测可通）===
    "公众号_财联社PSL": {"url": "https://mp.weixin.qq.com/s/0B572tdHZtZwUngmQCGLUQ", "type": "weixin", "desc": "央行PSL降息"},
    "公众号_人民网房贷": {"url": "https://mp.weixin.qq.com/s/XaWwCGAZ-skQ1sCEMBpsFw", "type": "weixin", "desc": "10月房贷贴息"},
    # === 官方政策/数据源（直采，不靠快讯转述）===
    "央行官网": {"url": "https://www.pbc.gov.cn/", "type": "policy", "desc": "PSL/降准/货币政策"},
    "发改委": {"url": "https://www.ndrc.gov.cn/", "type": "policy", "desc": "十五五/产业政策"},
    "国务院": {"url": "https://www.gov.cn/zhengce/zuixin.htm", "type": "policy", "desc": "国务院政策"},
    # === 官方数据源（补降级洞的免费替代）===
    "统计局": {"url": "https://www.stats.gov.cn/", "type": "data", "desc": "社零/失业率→补招聘指数"},
    "上交所": {"url": "https://www.sse.com.cn/", "type": "data", "desc": "股票/ETF资金流→补东财被挡"},
    "外汇局": {"url": "https://www.safe.gov.cn/", "type": "data", "desc": "汇率/外储→补人民币维度"},
    "金融监管总局": {"url": "https://www.nfra.gov.cn/", "type": "data", "desc": "贷款/信用（门户占位）"},
    # === 大宗数据 ===
    "上海有色": {"url": "https://www.shmet.com/", "type": "commodity", "desc": "金属大宗价格"},
    # === 海外央行/数据（交叉验证美联储/外需）===
    "美联储官网": {"url": "https://www.federalreserve.gov/", "type": "policy", "desc": "美联储利率/外需"},
    "IMF": {"url": "https://www.imf.org/", "type": "data", "desc": "全球经济数据"},
    "世界银行": {"url": "https://www.worldbank.org/", "type": "data", "desc": "发展/经济数据"},
    # === 财经媒体补充（多源交叉，更多视角）===
    "第一财经": {"url": "https://www.yicai.com/", "type": "news", "desc": "财经要闻"},
    "经济日报": {"url": "http://www.ce.cn/", "type": "news", "desc": "官方财经"},
    "澎湃财经": {"url": "https://www.thepaper.cn/channel_26934.htm", "type": "news", "desc": "财经时政"},
    "界面新闻": {"url": "https://www.jiemian.com/", "type": "news", "desc": "财经"},
    "中国基金报": {"url": "https://www.chnfund.com/", "type": "news", "desc": "基金/资管"},
    "证券时报": {"url": "https://www.stcn.com/", "type": "news", "desc": "证券"},
    # === 研报（占位，能采多少采多少，不通降级）===
    "东方财富研报": {"url": "https://data.eastmoney.com/report/", "type": "research", "desc": "研报（占位）"},
}

# 政策/经济关键词（用于从快讯里筛出与经济决策相关的条目）
POLICY_KEYWORDS = [
    "央行", "降准", "降息", "PSL", "抵押补充贷款", "国债", "专项债", "LPR", "MLF",
    "财政", "发改委", "国务院", "十五五", "新质生产力", "集成电路", "新能源",
    "房地产", "房贷", "保交楼", "棚改", "促消费", "社零", "出口", "关税",
    "中美", "美联储", "降息", "通胀", "CPI", "PPI", "GDP", "就业", "失业",
    "贴息", "补贴", "关税", "外资", "一带一路", "东盟", "人民币",
]


def _clean_text(html: str, source_type: str = "", limit: int = 20000) -> str:
    """去掉 HTML 标签，保留可读文本。微信公众号正文优先取 rich_media_content。"""
    if source_type == "weixin":
        m = re.search(r'<div[^>]*rich_media_content[^>]*>(.*?)</div>', html, re.S)
        if m:
            body = m.group(1)
        else:
            body = html
    else:
        body = html
    body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.S)
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.S)
    body = re.sub(r'<[^>]+>', ' ', body)
    body = re.sub(r'&nbsp;?', ' ', body)
    body = re.sub(r'&#39;', "'", body)
    body = re.sub(r'\u003e', '>', body)
    text = re.sub(r'\s+', ' ', body).strip()
    return text[:limit]





def _fetch_one(name: str, cfg: dict, timeout: int = 25) -> dict:
    """拉单个源（失败返回 error，不抛）。"""
    try:
        if requests is None:
            return {"source": name, "type": cfg["type"], "ok": False, "error": "requests 未安装"}
        r = requests.get(cfg["url"], headers=BASE_HEADERS, timeout=timeout)
        if r.status_code != 200:
            return {"source": name, "type": cfg["type"], "ok": False,
                    "error": f"HTTP {r.status_code}", "char_count": len(r.text or "")}
        if r.encoding in (None, "ISO-8859-1"):
            r.encoding = r.apparent_encoding
        text = _clean_text(r.text, cfg.get("type", ""))
        return {"source": name, "type": cfg["type"], "ok": True,
                "desc": cfg["desc"], "char_count": len(text),
                "raw": text[:8000],  # 截断存，避免太大
                "police_items": _extract_policy_items(text),
                "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    except Exception as e:
        return {"source": name, "type": cfg["type"], "ok": False, "error": str(e)[:60]}


def _extract_policy_items(text: str, max_items: int = 15) -> list:
    """从快讯文本里筛出经济政策相关条目。"""
    items = []
    # 按句切，命中关键词的留下
    for sent in re.split(r'[。！？.!?]', text):
        sent = sent.strip()
        if not (8 <= len(sent) <= 80):
            continue
        hit = [kw for kw in POLICY_KEYWORDS if kw in sent]
        if hit:
            items.append({"text": sent[:60], "keywords": hit})
        if len(items) >= max_items:
            break
    return items


def collect_all(sources: dict = None, max_workers: int = 8) -> dict:
    """多源并行采集，失败隔离。"""
    sources = sources or SOURCES
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(_fetch_one, n, c): n for n, c in sources.items()}
        for fut in as_completed(futures):
            name = futures[fut]
            results[name] = fut.result()

    ok = {k: v for k, v in results.items() if v.get("ok")}
    fail = {k: v for k, v in results.items() if not v.get("ok")}

    # 跨源交叉验证：汇总所有政策条目，多源都提到的置信度高
    all_items = []
    source_map = {}
    for name, r in ok.items():
        for item in r.get("police_items", []):
            key = item["text"][:20]
            source_map.setdefault(key, []).append(name)
            all_items.append({**item, "sources": [name]})

    # 去重：同一条多源合并，标注置信度
    merged = {}
    for key, srcs in source_map.items():
        # 取最长的完整文本
        full = next((i for i in all_items if i["text"][:20] == key), None)
        if full:
            confidence = "high" if len(srcs) >= 2 else "single"
            merged[key] = {"text": full["text"], "keywords": full["keywords"],
                          "sources": srcs, "confidence": confidence}

    events = sorted(merged.values(),
                    key=lambda x: (x["confidence"] != "high", -len(x["sources"])))

    return {
        "date": time.strftime("%Y-%m-%d"),
        "collected": list(ok.keys()),
        "failed": {k: v.get("error", "?") for k, v in fail.items()},
        "coverage": f"{len(ok)}/{len(results)} 源可达",
        "events": events[:30],
        "stats": {"ok_sources": len(ok), "fail_sources": len(fail),
                  "events_total": len(all_items), "cross_verified": sum(1 for e in merged.values() if e["confidence"] == "high")},
    }


def format_report(result: dict) -> str:
    """多源采集报告文本。"""
    lines = []
    lines.append(f"📡 多信息源并行采集（{result['date']}）— 避免单源滞后")
    lines.append(f"覆盖: {result['coverage']} | 跨源交叉验证事件 {result['stats']['cross_verified']} 条")
    lines.append("")
    lines.append("【可达源】" + "、".join(result["collected"]))
    if result["failed"]:
        lines.append("【失败源（不影响整体）】" + "；".join(f"{k}:{v[:20]}" for k, v in result["failed"].items()))
    lines.append("\n【今日重大政策/经济事件】（多源交叉，置信度 high=多源报道）")
    for e in result["events"][:15]:
        mark = "🔷" if e["confidence"] == "high" else "·"
        lines.append(f"  {mark} {e['text'][:50]}  （{'/'.join(e['sources'][:3])}）")
    lines.append("\n⚠️ 多源采集为信息参考，单源事件标注为待确认，重大决策请核实原始出处。")
    return "\n".join(lines)


def main():
    r = collect_all()
    print(format_report(r))


if __name__ == "__main__":
    main()
