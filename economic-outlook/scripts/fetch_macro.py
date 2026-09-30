#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济数据多源采集器（v3.1）
经济分析 Skill - 数据采集层

v3.1 新增（按 PRD P0）：
- 出口同比/进口同比（海关）
- 外汇储备
- 10年期国债收益率

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys, json, pickle, time, logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_TTL = 3600  # 1 小时缓存


def _cache_key(name):
    return os.path.join(CACHE_DIR, f'{name}.pkl')


def _load_cache(name, ttl=CACHE_TTL):
    p = _cache_key(name)
    if os.path.exists(p) and time.time() - os.path.getmtime(p) < ttl:
        with open(p, 'rb') as f:
            return pickle.load(f)
    return None


def _save_cache(name, data):
    with open(_cache_key(name), 'wb') as f:
        pickle.dump(data, f)


def fetch_cpi():
    c = _load_cache('cpi')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_china_cpi()
    _save_cache('cpi', df)
    return df


def fetch_ppi():
    c = _load_cache('ppi')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_china_ppi()
    _save_cache('ppi', df)
    return df


def fetch_pmi():
    c = _load_cache('pmi')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_china_pmi()
    _save_cache('pmi', df)
    return df


def fetch_m2():
    c = _load_cache('m2')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_china_money_supply()
    _save_cache('m2', df)
    return df


def fetch_gdp():
    c = _load_cache('gdp')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_china_gdp()
    _save_cache('gdp', df)
    return df


def fetch_shrzgm():
    c = _load_cache('shrzgm')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_china_shrzgm()
    _save_cache('shrzgm', df)
    return df


def fetch_shibor():
    c = _load_cache('shibor')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_china_shibor_all()
    _save_cache('shibor', df)
    return df


def fetch_lpr():
    c = _load_cache('lpr')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_china_lpr()
    _save_cache('lpr', df)
    return df


def fetch_real_estate():
    c = _load_cache('real_estate')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_china_real_estate()
    _save_cache('real_estate', df)
    return df


def fetch_gold():
    c = _load_cache('gold')
    if c is not None:
        return c
    import akshare as ak
    df = ak.futures_zh_daily_sina(symbol="AU0")
    _save_cache('gold', df)
    return df


def fetch_silver():
    c = _load_cache('silver')
    if c is not None:
        return c
    import akshare as ak
    df = ak.futures_zh_daily_sina(symbol="AG0")
    _save_cache('silver', df)
    return df


def fetch_unemployment():
    c = _load_cache('unemployment')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_china_urban_unemployment()
    _save_cache('unemployment', df)
    return df


def fetch_house_price():
    c = _load_cache('house_price')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_china_new_house_price()
    _save_cache('house_price', df)
    return df


def fetch_retail():
    c = _load_cache('retail')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_china_consumer_goods_retail()
    _save_cache('retail', df)
    return df


def fetch_insurance():
    c = _load_cache('insurance')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_china_insurance_income()
    _save_cache('insurance', df)
    return df


def fetch_exports():
    """出口同比（海关）"""
    c = _load_cache('exports')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_china_exports_yoy()
    _save_cache('exports', df)
    return df


def fetch_imports():
    """进口同比（海关）"""
    c = _load_cache('imports')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_china_imports_yoy()
    _save_cache('imports', df)
    return df


def fetch_fx_reserves():
    """外汇储备（月度）"""
    c = _load_cache('fx_reserves')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_china_fx_reserves_yearly()
    _save_cache('fx_reserves', df)
    return df


def fetch_bond_yield():
    """10年期国债收益率"""
    c = _load_cache('bond_yield')
    if c is not None:
        return c
    import akshare as ak
    df = ak.bond_china_yield()
    _save_cache('bond_yield', df)
    return df


def fetch_usa_pmi():
    """美国 ISM 制造业 PMI（外需领先指标）"""
    c = _load_cache('usa_pmi')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_usa_pmi()
    _save_cache('usa_pmi', df)
    return df


def fetch_usa_cpi():
    """美国 CPI 同比（外部金融条件）"""
    c = _load_cache('usa_cpi')
    if c is not None:
        return c
    import akshare as ak
    df = ak.macro_usa_cpi_yoy()
    _save_cache('usa_cpi', df)
    return df


def fetch_all(timeout=180):
    """拉取全部数据源（带超时保护），返回 dict"""
    import concurrent.futures
    t0 = time.time()
    fetchers = {
        'cpi': fetch_cpi, 'ppi': fetch_ppi, 'pmi': fetch_pmi,
        'm2': fetch_m2, 'gdp': fetch_gdp, 'shrzgm': fetch_shrzgm,
        'shibor': fetch_shibor, 'lpr': fetch_lpr,
        'real_estate': fetch_real_estate, 'gold': fetch_gold, 'silver': fetch_silver,
        'unemployment': fetch_unemployment, 'house_price': fetch_house_price,
        'retail': fetch_retail, 'insurance': fetch_insurance,
        'exports': fetch_exports, 'imports': fetch_imports,
        'fx_reserves': fetch_fx_reserves, 'bond_yield': fetch_bond_yield,
        'usa_pmi': fetch_usa_pmi, 'usa_cpi': fetch_usa_cpi,
    }
    result = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(fn): name for name, fn in fetchers.items()}
        for fut in concurrent.futures.as_completed(futs, timeout=timeout):
            name = futs[fut]
            try:
                result[name] = fut.result()
                logger.info(f"OK {name}: {len(result[name])} rows")
            except Exception as e:
                logger.warning(f"FAIL {name}: {str(e)[:60]}")
                result[name] = None
    ok = len([v for v in result.values() if v is not None])
    logger.info(f"采集完成 {ok}/{len(fetchers)}，耗时 {time.time()-t0:.1f}s")
    return result


if __name__ == '__main__':
    data = fetch_all()
    for k, v in data.items():
        print(f"{k}: {len(v)} 行" if v is not None else f"{k}: FAILED")
