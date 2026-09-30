#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指标计算（FR-03，PRD V3.1 §9）
core/indicators.py

同比/环比/剪刀差/扩散指数。复用 scripts/features.py 的真实计算。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys, logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))

import features as _feat


def yoy(series):
    """同比（百分比）"""
    import pandas as pd
    if series is None or len(series) < 13:
        return []
    s = pd.Series(series).astype(float)
    return [s.iloc[i] / s.iloc[i-12] - 1 for i in range(12, len(s))]


def mom(series):
    """环比（百分比）"""
    import pandas as pd
    if series is None or len(series) < 2:
        return []
    s = pd.Series(series).astype(float)
    return [s.iloc[i] / s.iloc[i-1] - 1 for i in range(1, len(s))]


def scissors(a, b):
    """剪刀差（两序列逐点相减）"""
    return [x - y for x, y in zip(a, b)]


def compute(data):
    """对 fetch_macro 的 data dict 计算完整特征（复用 features.py）"""
    return _feat.compute_features(data)


if __name__ == '__main__':
    import fetch_macro
    data = fetch_macro.fetch_all(timeout=180)
    f = compute(data)
    print("特征:", f)
