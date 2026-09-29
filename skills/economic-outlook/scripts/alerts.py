#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""告警引擎（FR-08，PRD §9）：P0 指标阈值突破检测，阈值从 config/thresholds.json 读取（迁移只改配置）
版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)"""
import os, json, logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, 'config', 'thresholds.json')

DEFAULT_THRESHOLDS = {
    'cpi_yoy': {'min': -1.0, 'max': 3.0, 'desc': 'CPI 同比（温和区间）'},
    'ppi_yoy': {'min': -5.0, 'max': 5.0, 'desc': 'PPI 同比'},
    'unemployment': {'min': None, 'max': 7.0, 'desc': '城镇调查失业率'},
    'retail_yoy': {'min': -5.0, 'max': None, 'desc': '社零累计同比'},
    'exports_yoy': {'min': -10.0, 'max': None, 'desc': '出口同比'},
    'pmi': {'min': 45.0, 'max': None, 'desc': '制造业 PMI'},
    'gdp_yoy': {'min': 3.0, 'max': None, 'desc': 'GDP 同比'},
    'm2_yoy': {'min': 5.0, 'max': 12.0, 'desc': 'M2 同比'},
}


def load_thresholds():
    import json as _json
    merged = {k: dict(v) for k, v in DEFAULT_THRESHOLDS.items()}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, encoding='utf-8') as f:
                cfg = _json.load(f)
            th = cfg.get('thresholds', cfg)
            for k, v in th.items():
                if isinstance(v, dict):
                    merged.setdefault(k, {}).update(v)
        except Exception:
            pass
    return merged


def check_alerts(metrics, thresholds=None):
    th = thresholds or load_thresholds()
    alerts = []
    for key, rule in th.items():
        val = metrics.get(key)
        if val is None:
            continue
        try:
            val = float(val)
        except Exception:
            continue
        if rule.get('max') is not None and val > rule['max']:
            alerts.append({'metric': key, 'value': val, 'threshold': rule['max'], 'type': '高于上限', 'desc': rule.get('desc', key)})
        if rule.get('min') is not None and val < rule['min']:
            alerts.append({'metric': key, 'value': val, 'threshold': rule['min'], 'type': '低于下限', 'desc': rule.get('desc', key)})
    return alerts


def format_alerts(alerts):
    if not alerts:
        return "🟢 无告警：所有 P0 指标均在正常区间"
    lines = [f"🚨 触发 {len(alerts)} 项告警："]
    for a in alerts:
        lines.append(f"  ⚠️ {a['desc']}：当前 {a['value']}，{a['type']} {a['threshold']}")
    return "\n".join(lines)


def metrics_from_data(data):
    import pandas as pd
    m = {}
    cpi = data.get('cpi')
    if cpi is not None and len(cpi) and '全国-同比增长' in cpi.columns:
        v = cpi.iloc[0]['全国-同比增长']
        m['cpi_yoy'] = float(v) if pd.notna(v) else None
    ppi = data.get('ppi')
    if ppi is not None and len(ppi) and '当月同比增长' in ppi.columns:
        v = ppi.iloc[0]['当月同比增长']
        m['ppi_yoy'] = float(v) if pd.notna(v) else None
    un = data.get('unemployment')
    if un is not None and len(un):
        try:
            m['unemployment'] = float(un[un['value'].notna()].iloc[-1]['value'])
        except Exception:
            pass
    ret = data.get('retail')
    if ret is not None and len(ret) and '累计-同比增长' in ret.columns:
        v = ret.iloc[0]['累计-同比增长']
        m['retail_yoy'] = float(v) if pd.notna(v) else None
    exp = data.get('exports')
    if exp is not None and len(exp):
        v = exp['今值'].dropna()
        m['exports_yoy'] = float(v.iloc[-1]) if len(v) else None
    pmi = data.get('pmi')
    if pmi is not None and len(pmi):
        try:
            m['pmi'] = float(pmi.iloc[-1].iloc[1])
        except Exception:
            pass
    gdp = data.get('gdp')
    if gdp is not None and len(gdp) and '国内生产总值-同比增长' in gdp.columns:
        v = gdp.iloc[0]['国内生产总值-同比增长']
        m['gdp_yoy'] = float(v) if pd.notna(v) else None
    m2 = data.get('m2')
    if m2 is not None and len(m2) and '货币和准货币(M2)-同比增长' in m2.columns:
        v = m2.iloc[0]['货币和准货币(M2)-同比增长']
        m['m2_yoy'] = float(v) if pd.notna(v) else None
    return m


if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import fetch_macro
    data = fetch_macro.fetch_all(timeout=180)
    m = metrics_from_data(data)
    print("=== 指标 ===")
    for k, v in m.items():
        print(f"  {k}: {v}")
    print("\n=== 告警 ===")
    print(format_alerts(check_alerts(m)))
