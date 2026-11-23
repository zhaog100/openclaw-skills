# -*- coding: utf-8 -*-
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""akshare 接口兼容层 - 集中处理 1.20.42+ 的接口更名/移除。

背景: akshare 1.20.42~1.20.65 移除了若干 macro_* 接口、部分更名。
本模块提供:
  1. COMPAT_MAP: 旧接口名 → 新接口名（可直接调用的替代）
  2. DEGRADE: 已移除且无直接替代的接口 → 降级为空 DataFrame（不崩）
  3. call(fn, *args, **kw): 统一入口，自动走 兼容/原样/降级 三态

用法:
    from shared.ak_compat import call
    df = call('macro_china_shrzgm')      # 自动用新接口
    df = call('macro_usa_pmi')           # 自动降级空表
    df = call('macro_china_cpi')         # 原样调用
"""
import pandas as pd
import akshare as ak

# 旧名 → 新名（官方 1.20.42+ 更名映射，已验证可用）
COMPAT_MAP = {
    'macro_china_shrzgm': 'macro_china_social_financing',
    'macro_china_money_supply': 'macro_china_money_supply_em',
    'macro_china_shibor_all': 'interest_rate_shibor_js',
    'macro_china_lpr': 'interest_rate_lpr_em',
}

# 已移除且无直接替代 → 降级为空 DataFrame（带 reason 属性）
DEGRADE = {
    'macro_china_exports_yoy', 'macro_china_imports_yoy',
    'macro_china_fx_reserves_yearly', 'macro_usa_pmi',
    'macro_china_hgjck', 'bond_zh_us_rate',
    'currency_boc_safe', 'index_neaw_cx', 'stock_zh_index_daily',
}

# 新接口列名 → 下游期望的旧列名（归一化，兼容旧代码）
_COLUMN_RENAME = {
    'interest_rate_lpr_em': {'1年期LPR': 'LPR1Y', '5年期以上LPR': 'LPR5Y'},
}

_EMPTY = pd.DataFrame()


def call(old_name, *args, **kw):
    """统一调用入口: 兼容映射 / 原样 / 降级 三态。返回 DataFrame。"""
    if old_name in COMPAT_MAP:
        new_fn = getattr(ak, COMPAT_MAP[old_name], None)
        if new_fn:
            try:
                df = new_fn(*args, **kw)
                # 列名归一化（新接口列名 → 下游期望的旧列名）
                renames = _COLUMN_RENAME.get(COMPAT_MAP[old_name])
                if renames and isinstance(df, pd.DataFrame) and not df.empty:
                    df = df.rename(columns=renames)
                return df
            except Exception:
                pass
        # 新接口也不可用 → 降级
        return _EMPTY
    if old_name in DEGRADE:
        return _EMPTY
    # 原样调用
    fn = getattr(ak, old_name, None)
    if fn is None:
        return _EMPTY
    try:
        return fn(*args, **kw)
    except Exception:
        return _EMPTY


def available(name):
    """该接口当前是否可产出非空数据（用于上层决策）。"""
    return name not in DEGRADE
