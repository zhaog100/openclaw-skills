"""
全局配置 — 集中管理路径和可配置参数
通过环境变量或默认值配置，避免硬编码路径
"""
# 版本: v3.3 | 石油黄金白银相关性分析
import os
from pathlib import Path

# ===== 基础路径 =====
# OPENCLAW_HOME: 默认 ~/.openclaw
OPENCLAW_HOME = Path(os.environ.get("OPENCLAW_HOME", Path.home() / ".openclaw"))

# ===== 输出目录 =====
# REPORT_DIR: 报告输出目录
REPORT_DIR = Path(os.environ.get(
    "OIL_GOLD_REPORT_DIR",
    OPENCLAW_HOME / "media" / "qqbot"
))

# ===== 缓存目录 =====
# CACHE_DIR: 数据缓存目录
CACHE_DIR = Path(os.environ.get(
    "OIL_GOLD_CACHE_DIR",
    Path("/tmp") / "oil-gold-cache"
))

# ===== 报告文件名 =====
REPORT_TEXT = REPORT_DIR / "oil-gold-report.txt"
REPORT_PNG = REPORT_DIR / "oil-gold-report.png"
REPORT_JPG = REPORT_DIR / "oil-gold-report.jpg"


def ensure_dirs():
    """确保所有输出目录存在"""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
