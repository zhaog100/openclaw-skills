#!/usr/bin/env python3
"""
全局配置常量 — 集中管理所有魔法字符串（URL、API端点、数据源等）

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) - AI Agent
版本: v1.0.0
"""

# ─── FRED API ───────────────────────────────────────────────
FRED_API_BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv"

# FRED 核心数据系列（多周期共振分析使用）
FRED_CORE_SERIES = {
    "UMCSENT": {"name": "密歇根消费者信心指数", "unit": "指数", "impact": "<70悲观/>90乐观"},
    "DFII10": {"name": "10年期TIPS实际利率", "unit": "%", "impact": "与黄金负相关"},
    "INDPRO": {"name": "工业生产指数", "unit": "指数", "impact": ">100扩张/<100收缩"},
}

# ─── 大宗商品 yfinance 代码 ─────────────────────────────────
COMMODITY_SYMBOLS = {
    "gold": "GC=F",       # 黄金期货
    "wti": "CL=F",        # WTI 原油期货
    "silver": "SI=F",     # 白银期货
    "palladium": "PA=F",  # 钯金期货
    "platinum": "PL=F",   # 铂金期货
}

# ─── 地缘政治 RSS 源 ────────────────────────────────────────
RSS_SOURCES = [
    ("https://search.cnbc.com/rs/search/combinedcms/view.xml?"
     "partnerId=wrss01&id=10001147", "CNBC Top"),
    ("https://search.cnbc.com/rs/search/combinedcms/view.xml?"
     "partnerId=wrss01&id=103700022", "CNBC Economy"),
    ("https://feeds.marketwatch.com/marketwatch/topstories/", "MarketWatch"),
    ("https://seekingalpha.com/market_currents.xml", "SeekingAlpha"),
    ("https://www3.nhk.or.jp/rss/news/cat0.xml", "NHK Japan"),
    ("https://www.koreaherald.com/common/rss.php", "Korea Herald"),
    ("https://www.eia.gov/rss/todayinenergy.xml", "EIA能源署"),
    ("https://www.ecb.europa.eu/rss/press.html", "ECB欧洲央行"),
    ("https://news.un.org/feed/subscribe/en/news/all/rss.xml", "UN News"),
    ("https://www.imf.org/en/News/rss", "IMF国际货币基金"),
    ("https://www.gold.org/rss.xml", "WGC世界黄金协会"),
    ("https://www.fxstreet.com/rss", "FXStreet"),
]

# ─── AKShare 数据源 ─────────────────────────────────────────
AKSHARE_SYMBOLS = {
    "gold_spot": "spot_gold_fx",
    "gold_future": "gold_usd",
    "silver_spot": "spot_silver_fx",
    "wti_crude": "crude_wti_fx",
    "brent_crude": "crude_brent_fx",
}

# ─── 多周期分析 ─────────────────────────────────────────────
MTA_TIMEFRAMES = {
    "short": {"days": 7, "label": "1周", "weight": 0.15},
    "medium": {"days": 30, "label": "1月", "weight": 0.25},
    "long": {"days": 180, "label": "半年", "weight": 0.30},
    "trend": {"days": 365, "label": "1年", "weight": 0.30},
}

MTA_COMMODITIES = {
    "gold": {"name": "黄金", "yf_symbol": "GC=F", "ak_key": "gold_spot"},
    "silver": {"name": "白银", "yf_symbol": "SI=F", "ak_key": "silver_spot"},
    "crude": {"name": "原油", "yf_symbol": "CL=F", "ak_key": "wti_crude"},
}

# ─── 数据缓存 ────────────────────────────────────────────────
from pathlib import Path

DATA_CACHE_DIR = "/tmp/oil_gold_cache"
CACHE_DIR = Path(DATA_CACHE_DIR)

# ─── 报告输出 ────────────────────────────────────────────────
REPORT_DIR = Path(__file__).parent.parent / "reports"
REPORT_TEXT = REPORT_DIR / "report_text_latest.txt"

def ensure_dirs():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
