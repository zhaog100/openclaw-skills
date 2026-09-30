#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高频 Nowcasting（PRD V3.1 §10）
core/nowcast.py

用可用高频代理（社融 M1/PMI/出口动量）对当前季度 GDP 做 nowcast。
正式实现替换为动态因子模型 / MIDAS。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys, logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))


def nowcast_gdp(data=None) -> float:
    """
    基于领先指标动量的 GDP nowcast（占位实现）。
    用 PMI（经济景气）+ M2 + 社融 的近期走势外推当前季度 GDP 同比。
    """
    import pandas as pd
    if data is None:
        import fetch_macro
        data = fetch_macro.fetch_all(timeout=180)

    # 基准：最近一季度 GDP 同比
    base = 5.0
    gdp = data.get('gdp')
    if gdp is not None and len(gdp) and '国内生产总值-同比增长' in gdp.columns:
        v = gdp.iloc[0]['国内生产总值-同比增长']
        if pd.notna(v):
            base = float(v)

    # 动量修正：PMI 高于 50 且上行 → 加 0.1-0.2
    adj = 0.0
    pmi = data.get('pmi')
    if pmi is not None and len(pmi) >= 4:
        cur = float(pmi.iloc[-1].iloc[1]) if len(pmi.iloc[-1]) > 1 else 50
        prev = float(pmi.iloc[-4].iloc[1]) if len(pmi.iloc[-4]) > 1 else 50
        if cur > 50 and cur > prev:
            adj += 0.15
        elif cur < 50:
            adj -= 0.15

    return round(base + adj, 2)


if __name__ == '__main__':
    print(f"GDP nowcast: {nowcast_gdp()}%")
