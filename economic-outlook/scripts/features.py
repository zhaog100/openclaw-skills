#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指标计算引擎（FR-03，PRD §7）
经济分析 Skill - 特征层

功能：
- 同比/环比计算
- 扩散指数（多指标同向上行占比）
- 剪刀差（CPI-PPI、M2-社融、实际 vs 名义 GDP）
- 领先指标信号

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, logging, pickle
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, 'cache')


def _load(name):
    p = os.path.join(CACHE_DIR, f'{name}.pkl')
    if os.path.exists(p):
        with open(p, 'rb') as f:
            return pickle.load(f)
    return None


def yoy(series, periods=12):
    """同比（需要 12 期历史）"""
    if series is None or len(series) < periods + 1:
        return None
    cur, prev = series.iloc[-1], series.iloc[-(periods + 1)]
    if pd.isna(cur) or pd.isna(prev) or prev == 0:
        return None
    return (cur - prev) / abs(prev) * 100


def mom(series):
    """环比（上月）"""
    if series is None or len(series) < 2:
        return None
    cur, prev = series.iloc[-1], series.iloc[-2]
    if pd.isna(cur) or pd.isna(prev) or prev == 0:
        return None
    return (cur - prev) / abs(prev) * 100


def spread(cpi_df, ppi_df):
    """CPI-PPI 剪刀差（正=消费>工业，反映内需强于生产）"""
    cpi_yoy = ppi_yoy = None
    if cpi_df is not None and len(cpi_df) and '全国-同比增长' in cpi_df.columns:
        v = cpi_df.iloc[0]['全国-同比增长']
        cpi_yoy = float(v) if pd.notna(v) else None
    if ppi_df is not None and len(ppi_df) and '当月同比增长' in ppi_df.columns:
        v = ppi_df.iloc[0]['当月同比增长']
        ppi_yoy = float(v) if pd.notna(v) else None
    if cpi_yoy is None or ppi_yoy is None:
        return None
    return round(cpi_yoy - ppi_yoy, 2)


def diffusion_index(data):
    """
    扩散指数：统计多指标中"改善"的占比（0-100）
    改善判定：
      - PMI > 50
      - M2 同比上行
      - CPI 同比 > 前月
      - 社零累计同比 > 0
      - 出口同比 > 0
      - 失业率 < 前月
    """
    checks = []
    pmi = data.get('pmi')
    if pmi is not None and len(pmi):
        v = float(pmi.iloc[-1].iloc[1]) if len(pmi.iloc[-1]) > 1 else None
        if v is not None:
            checks.append(v > 50)
    m2 = data.get('m2')
    if m2 is not None and len(m2) > 2 and 'M2-同比' in m2.columns:
        cur, prev = m2.iloc[-1]['M2-同比'], m2.iloc[-2]['M2-同比']
        if pd.notna(cur) and pd.notna(prev):
            checks.append(float(cur) > float(prev))
    cpi = data.get('cpi')
    if cpi is not None and len(cpi) > 1 and '全国-同比增长' in cpi.columns:
        cur, prev = cpi.iloc[0]['全国-同比增长'], cpi.iloc[1]['全国-同比增长']
        if pd.notna(cur) and pd.notna(prev):
            checks.append(float(cur) > float(prev))
    retail = data.get('retail')
    if retail is not None and len(retail) and '累计-同比增长' in retail.columns:
        v = retail.iloc[0]['累计-同比增长']
        if pd.notna(v):
            checks.append(float(v) > 0)
    exports = data.get('exports')
    if exports is not None and len(exports):
        v = exports['今值'].dropna()
        if len(v):
            checks.append(float(v.iloc[-1]) > 0)
    un = data.get('unemployment')
    if un is not None and len(un) > 1:
        vals = un['value'].dropna() if 'value' in un.columns else None
        if vals is not None and len(vals) >= 2:
            checks.append(float(vals.iloc[-1]) < float(vals.iloc[-2]))

    if not checks:
        return None
    return round(sum(checks) / len(checks) * 100)


def compute_features(data):
    """输出完整特征字典"""
    cpi = data.get('cpi')
    ppi = data.get('ppi')
    m2 = data.get('m2')
    shrzgm = data.get('shrzgm')

    cpi_yoy = ppi_yoy = None
    if cpi is not None and len(cpi) and '全国-同比增长' in cpi.columns:
        v = cpi.iloc[0]['全国-同比增长']
        cpi_yoy = float(v) if pd.notna(v) else None
    if ppi is not None and len(ppi) and '当月同比增长' in ppi.columns:
        v = ppi.iloc[0]['当月同比增长']
        ppi_yoy = float(v) if pd.notna(v) else None

    m2_yoy = None
    if m2 is not None and len(m2) and '货币和准货币(M2)-同比增长' in m2.columns:
        v = m2.iloc[0]['货币和准货币(M2)-同比增长']
        m2_yoy = float(v) if pd.notna(v) else None

    # 社融为月度增量序列（亿元），取最新增量作参考（非同比）
    shrzgm_yoy = None
    shrzgm_latest = None
    if shrzgm is not None and len(shrzgm):
        v = shrzgm.iloc[0]['社会融资规模增量'] if '社会融资规模增量' in shrzgm.columns else None
        if pd.notna(v):
            shrzgm_latest = float(v)

    features = {
        'cpi_yoy': cpi_yoy,
        'ppi_yoy': ppi_yoy,
        'cpi_ppi_spread': spread(cpi, ppi),
        'm2_yoy': m2_yoy,
        'shrzgm_latest': shrzgm_latest,
        'm2_shrzgm_spread': None,  # 社融为增量序列，不直接做同比剪刀差
        'diffusion_index': diffusion_index(data),
    }
    return features


def interpret_features(features):
    """把特征转成人类可读的解读"""
    lines = []
    if features.get('cpi_ppi_spread') is not None:
        s = features['cpi_ppi_spread']
        if s > 1:
            lines.append(f"CPI-PPI 剪刀差 {s}pct（正）：消费价格强于工业，内需相对占优")
        elif s < -1:
            lines.append(f"CPI-PPI 剪刀差 {s}pct（负）：工业价格强于消费，生产端景气高于终端需求")
        else:
            lines.append(f"CPI-PPI 剪刀差 {s}pct：价格结构均衡")
    if features.get('m2_shrzgm_spread') is not None:
        s = features['m2_shrzgm_spread']
        if s > 1:
            lines.append(f"M2-社融剪刀差 {s}pct：货币供给快于信贷需求，资金未完全转化为实体投资")
        elif s < -1:
            lines.append(f"M2-社融剪刀差 {s}pct：信贷需求强于货币供给，实体融资偏紧")
        else:
            lines.append(f"M2-社融剪刀差 {s}pct：货币与信贷基本匹配")
    di = features.get('diffusion_index')
    if di is not None:
        if di >= 75:
            lines.append(f"扩散指数 {di}/100（强）：多数指标同向改善，经济动能向上")
        elif di >= 50:
            lines.append(f"扩散指数 {di}/100（中性）：改善与走弱指标并存，经济分化")
        else:
            lines.append(f"扩散指数 {di}/100（弱）：多数指标走弱，经济动能不足")
    return lines


if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import fetch_macro
    data = fetch_macro.fetch_all(timeout=180)
    f = compute_features(data)
    print("=== 特征 ===")
    for k, v in f.items():
        print(f"  {k}: {v}")
    print("\n=== 解读 ===")
    for line in interpret_features(f):
        print("  " + line)
