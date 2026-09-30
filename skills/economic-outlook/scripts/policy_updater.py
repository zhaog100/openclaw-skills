#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — 政策时间线更新器

每月从 国务院/发改委/央行官网 抓取新政，追加到 data/policy_timeline.json。
拉不到时如实标注"最后更新日期"和"覆盖范围"，不硬造。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys, json, logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

POLICY_FILE = os.path.join(BASE_DIR, "data", "policy_timeline.json")

# 政策源（官网 RSS/列表页，需合规抓取）
POLICY_SOURCES = [
    {"name": "国务院", "url": "https://www.gov.cn/zhengce/zuixin.htm", "type": "list"},
    {"name": "发改委", "url": "https://www.ndrc.gov.cn/xwdt/tzgg/", "type": "list"},
    {"name": "央行", "url": "https://www.pbc.gov.cn/goutongjiaoliu/113456/index.html", "type": "list"},
]

# 政策分类映射（关键词 → 影响方向）
POLICY_CATEGORIES = {
    "稳增长": ["降准", "降息", "专项债", "特别国债", "稳经济"],
    "产业": ["新质生产力", "集成电路", "新能源", "人工智能", "数字经济"],
    "地产": ["房地产", "棚改", "保交楼", "限购"],
    "消费": ["促消费", "家电", "汽车", "服务消费"],
}


def load_timeline():
    """加载现有政策时间线。"""
    if not os.path.exists(POLICY_FILE):
        return {"events": [], "last_updated": None, "coverage": []}
    with open(POLICY_FILE) as f:
        return json.load(f)


def ensure_meta():
    """确保时间线有 last_updated 和 coverage 元信息（3.3 要求）。"""
    data = load_timeline()
    if "last_updated" not in data:
        data["last_updated"] = None
    if "coverage" not in data:
        data["coverage"] = [s["name"] for s in POLICY_SOURCES]
    return data


def categorize(title: str) -> str:
    """按关键词给新政分类。"""
    for cat, kws in POLICY_CATEGORIES.items():
        if any(kw in title for kw in kws):
            return cat
    return "其他"


def fetch_new_policies() -> list:
    """
    抓取新政（合规，失败诚实降级）。

    返回: [{"title", "date", "category", "direction", "source"}, ...]
    """
    new_policies = []
    existing_titles = {e.get("title", "") for e in (load_timeline().get("events") or [])}
    for src in POLICY_SOURCES:
        try:
            import requests
            r = requests.get(src["url"], headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
            r.raise_for_status()
            # 简化：实际需解析 HTML 列表（bs4），此处标记需要人工接入解析
            logging.warning(f"[{src['name']}] 抓到 {len(r.text)} 字符，需人工接解析逻辑提取新政")
        except Exception as e:
            logging.warning(f"[{src['name']}] 抓取失败（官网可能反爬/需代理）: {str(e)[:40]}")
    return new_policies


def update_policy_timeline(force_note: str = None) -> dict:
    """更新政策时间线，写入 last_updated + coverage。"""
    data = ensure_meta()
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    new = fetch_new_policies()
    if new:
        for p in new:
            p["category"] = categorize(p.get("title", ""))
            p.setdefault("direction", "+")
            data["events"].append(p)
    if force_note:
        data["note"] = force_note
    with open(POLICY_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logging.info(f"政策时间线已更新: 共 {len(data.get('events', []))} 条 | 最后更新 {data['last_updated']}")
    return data


def show_meta():
    """显示政策时间线的最后更新日期 + 覆盖范围（3.3 至少要求）。"""
    data = ensure_meta()
    print(f"政策时间线: {len(data.get('events', []))} 条事件")
    print(f"  最后更新: {data.get('last_updated') or '未标注'}")
    print(f"  覆盖范围: {', '.join(data.get('coverage', []))}")
    return data


def collect_realtime_policy() -> dict:
    """多源并行采集当天政策/经济事件（新华社/金十/华尔街见闻/新浪/公众号/官方/大宗）。

    返回: {events: [{text, sources, confidence}], coverage, collected, failed}
    单个源失败不影响整体，去重交叉验证。
    """
    try:
        from shared.sources.news import collect_all, format_report
    except Exception as e:
        logging.warning(f"多源采集器不可用: {e}")
        return {"events": [], "coverage": "0", "error": str(e)}

    result = collect_all()
    events = []
    for ev in result.get("events", []):
        events.append({
            "title": ev.get("text", ""),
            "date": result.get("date", ""),
            "category": "实时政策",
            "direction": "+",
            "source": "/".join(ev.get("sources", [])[:3]),
            "confidence": ev.get("confidence", "single"),
            "keywords": ev.get("keywords", []),
        })
    return {
        "events": events,
        "coverage": result.get("coverage", "?"),
        "collected": result.get("collected", []),
        "failed": result.get("failed", {}),
        "cross_verified": result.get("stats", {}).get("cross_verified", 0),
    }


def append_realtime_events(max_events: int = 20) -> dict:
    """把多源采集的当天事件去重后追加进 policy_timeline.json（动态化）。"""
    data = ensure_meta()
    rt = collect_realtime_policy()
    if rt.get("error"):
        return {"skipped": True, "reason": rt["error"]}

    events = data.get("events", [])
    existing = {e.get("title", "") for e in events}
    added = 0
    for ev in rt.get("events", [])[:max_events]:
        if ev["title"] in existing:
            continue
        events.append(ev)
        existing.add(ev["title"])
        added += 1

    data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    data["realtime_sources"] = rt.get("collected", [])
    data["realtime_coverage"] = rt.get("coverage", "?")
    with open(POLICY_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return {"added": added, "total": len(events),
            "coverage": rt.get("coverage"), "cross_verified": rt.get("cross_verified", 0)}


if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "--fetch":
        update_policy_timeline(force_note="每月自动抓取（拉不到则保持原事件，仅刷新元信息）")
    else:
        show_meta()
