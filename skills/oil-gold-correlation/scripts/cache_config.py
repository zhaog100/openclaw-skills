#!/usr/bin/env python3
"""
统一缓存配置文件
规范缓存格式、TTL、路径等设置

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
"""

from pathlib import Path
from datetime import datetime, timedelta
import json
import pickle

# 缓存目录配置
CACHE_DIR = Path(__file__).parent.parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# 缓存TTL配置（秒）
CACHE_TTL = {
    "market_data": 300,      # 行情数据 5分钟
    "fred_data": 3600,       # FRED数据 1小时
    "analysis_results": 1800, # 分析结果 30分钟
    "news_data": 900,        # 新闻数据 15分钟
}

def get_cache_path(key: str, format_type: str = "json") -> Path:
    """获取缓存文件路径"""
    if format_type == "json":
        return CACHE_DIR / f"{key}.json"
    elif format_type == "pickle":
        return CACHE_DIR / f"{key}.pkl"
    else:
        return CACHE_DIR / f"{key}.cache"

def is_cache_valid(cache_file: Path, ttl_seconds: int) -> bool:
    """检查缓存是否有效"""
    if not cache_file.exists():
        return False
    
    mtime = cache_file.stat().st_mtime
    return (datetime.now().timestamp() - mtime) < ttl_seconds

def save_cache_json(key: str, data: dict, cache_type: str = "market_data"):
    """保存JSON格式缓存"""
    cache_file = get_cache_path(key, "json")
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_cache_json(key: str, cache_type: str = "market_data"):
    """加载JSON格式缓存"""
    cache_file = get_cache_path(key, "json")
    if is_cache_valid(cache_file, CACHE_TTL[cache_type]):
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_cache_pickle(key: str, data, cache_type: str = "market_data"):
    """保存pickle格式缓存"""
    cache_file = get_cache_path(key, "pickle")
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)

def load_cache_pickle(key: str, cache_type: str = "market_data"):
    """加载pickle格式缓存"""
    cache_file = get_cache_path(key, "pickle")
    if is_cache_valid(cache_file, CACHE_TTL[cache_type]):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    return None

def clear_expired_cache():
    """清理过期缓存"""
    for cache_file in CACHE_DIR.glob("*"):
        if cache_file.is_file():
            # 根据文件扩展名确定TTL
            ttl = CACHE_TTL["market_data"]  # 默认TTL
            if "fred" in cache_file.name:
                ttl = CACHE_TTL["fred_data"]
            elif "analysis" in cache_file.name:
                ttl = CACHE_TTL["analysis_results"]
            
            if not is_cache_valid(cache_file, ttl):
                cache_file.unlink(missing_ok=True)
                print(f"清理过期缓存: {cache_file.name}")