#!/usr/bin/env python3
"""
Oil-Gold Correlation 配置文件
定义缓存目录、报告路径和目录创建函数

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
"""

import os
from pathlib import Path

# 缓存目录
CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# 报告输出目录
REPORT_TEXT = Path(__file__).parent / "reports"
REPORT_TEXT.mkdir(exist_ok=True)

# 媒体输出目录
MEDIA_DIR = Path(__file__).parent.parent / "media" / "oil-gold"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

def ensure_dirs():
    """确保所有必要目录存在"""
    CACHE_DIR.mkdir(exist_ok=True)
    REPORT_TEXT.mkdir(exist_ok=True)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    return True

def get_cache_path(key: str) -> Path:
    """获取缓存文件路径"""
    return CACHE_DIR / f"{key}.json"

def get_report_path(name: str) -> Path:
    """获取报告文件路径"""
    return REPORT_TEXT / f"{name}.txt"

def get_media_path(name: str) -> Path:
    """获取媒体文件路径"""
    return MEDIA_DIR / name