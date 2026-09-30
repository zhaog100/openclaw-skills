#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源统一封装（PRD V2.0 §15）
shared/sources.py

所有模块通过这里取数，不直接 import fetch_macro。
基于 config/sources.yaml（缺省用内置 akshare 源映射）。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys, logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))

# 指标名 → fetch_macro 里的数据 key 映射
INDICATOR_MAP = {
    'gdp': 'gdp', 'cpi': 'cpi', 'ppi': 'ppi', 'pmi': 'pmi',
    'm1': 'm2', 'm2': 'm2', '社融': 'shrzgm', 'shrzgm': 'shrzgm',
    '出口': 'exports', '进口': 'imports', 'exports': 'exports', 'imports': 'imports',
    '社零': 'retail', 'retail': 'retail', '固投': 'real_estate',
    '地产': 'real_estate', '商品房': 'real_estate', '房价': 'house_price',
    '失业率': 'unemployment', 'unemployment': 'unemployment',
    'lpr': 'lpr', 'shibor': 'shibor', '国债': 'bond_yield',
    '外汇储备': 'fx_reserves', 'gold': 'gold', 'silver': 'silver',
    '美国pmi': 'usa_pmi', '美国cpi': 'usa_cpi',
}


def get_source(name):
    """返回数据源适配器（按指标名）"""
    key = INDICATOR_MAP.get(name)
    if key is None:
        return None
    import fetch_macro
    return _Adapter(key, fetch_macro)


class _Adapter:
    """akshare 数据适配器（带缓存）"""
    def __init__(self, fetch_key, fetch_module):
        self.fetch_key = fetch_key
        self.fetch_module = fetch_module

    def fetch(self, name, freq='M'):
        """拉取单个指标（命中 1h 缓存）"""
        data = self.fetch_module.fetch_all(timeout=180)
        df = data.get(self.fetch_key)
        return df


def load_all():
    """一次拉取全部 21 个数据源"""
    import fetch_macro
    return fetch_macro.fetch_all(timeout=180)


if __name__ == '__main__':
    src = get_source('cpi')
    df = src.fetch('cpi') if src else None
    print(f"cpi: {len(df)} 行" if df is not None else "cpi: 无源")
