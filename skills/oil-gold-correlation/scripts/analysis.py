#!/usr/bin/env python3
"""
石油黄金相关性分析引擎
支持：Pearson, Spearman, Kendall, Rolling, Granger, Cointegration, DCC-GARCH

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) - AI Agent
"""

import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings('ignore', category=FutureWarning)

# 可选依赖
try:
    from statsmodels.tsa.stattools import grangercausalitytests, adfuller, coint
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False


def load_data(period: str = "1y") -> pd.DataFrame:
    """从缓存加载数据为 DataFrame"""
    sys.path.insert(0, str(Path(__file__).parent))
    from fetch_data import fetch_data

    raw = fetch_data(period=period)
    if "gold" not in raw or "wti" not in raw:
        print("❌ 缺少黄金或原油数据")
        return pd.DataFrame()

    df = pd.DataFrame({
        "gold": raw["gold"]["close"],
        "wti": raw["wti"]["close"],
    }, index=pd.to_datetime(raw["gold"]["dates"]))

    # 添加收益率
    df["gold_ret"] = df["gold"].pct_change()
    df["wti_ret"] = df["wti"].pct_change()

    return df.dropna()


def _ensure_returns(df: pd.DataFrame) -> pd.DataFrame:
    """确保 DataFrame 含收益率列"""
    if "gold_ret" not in df.columns:
        df = df.copy()
        df["gold_ret"] = df["gold"].pct_change()
        df["wti_ret"] = df["wti"].pct_change()
        df = df.dropna()
    return df


def pearson_corr(df: pd.DataFrame) -> dict:
    """Pearson 线性相关系数"""
    df = _ensure_returns(df)
    r, p = stats.pearsonr(df["gold_ret"], df["wti_ret"])
    return {"pearson_r": round(r, 4), "p_value": round(p, 6), "significant": p < 0.05}


def spearman_corr(df: pd.DataFrame) -> dict:
    """Spearman 秩相关"""
    df = _ensure_returns(df)
    r, p = stats.spearmanr(df["gold_ret"], df["wti_ret"])
    return {"spearman_r": round(r, 4), "p_value": round(p, 6), "significant": p < 0.05}


def kendall_corr(df: pd.DataFrame) -> dict:
    """Kendall 秩相关"""
    df = _ensure_returns(df)
    r, p = stats.kendalltau(df["gold_ret"], df["wti_ret"])
    return {"kendall_tau": round(r, 4), "p_value": round(p, 6), "significant": p < 0.05}


def rolling_corr(df: pd.DataFrame, window: int = 30) -> pd.Series:
    """滚动窗口相关系数"""
    return df["gold_ret"].rolling(window).corr(df["wti_ret"])


def granger_test(df: pd.DataFrame, maxlag: int = 5) -> dict:
    """Granger 因果检验"""
    if not HAS_STATSMODELS:
        return {"error": "需要 statsmodels: pip install statsmodels"}

    results = {}
    # oil → gold
    try:
        test_og = grangercausalitytests(df[["gold_ret", "wti_ret"]], maxlag=maxlag, verbose=False)
        pvals_og = [test_og[lag][0]["ssr_ftest"][1] for lag in range(1, maxlag + 1)]
        results["oil_causes_gold"] = {
            "min_pvalue": round(min(pvals_og), 6),
            "best_lag": pvals_og.index(min(pvals_og)) + 1,
            "significant": min(pvals_og) < 0.05,
        }
    except Exception as e:
        results["oil_causes_gold"] = {"error": str(e)}

    # gold → oil
    try:
        test_go = grangercausalitytests(df[["wti_ret", "gold_ret"]], maxlag=maxlag, verbose=False)
        pvals_go = [test_go[lag][0]["ssr_ftest"][1] for lag in range(1, maxlag + 1)]
        results["gold_causes_oil"] = {
            "min_pvalue": round(min(pvals_go), 6),
            "best_lag": pvals_go.index(min(pvals_go)) + 1,
            "significant": min(pvals_go) < 0.05,
        }
    except Exception as e:
        results["gold_causes_oil"] = {"error": str(e)}

    return results


def cointegration_test(df: pd.DataFrame) -> dict:
    """协整检验（长期均衡关系）"""
    if not HAS_STATSMODELS:
        return {"error": "需要 statsmodels"}

    # Engle-Granger 协整检验
    score, pvalue, _ = coint(df["gold"], df["wti"])
    return {
        "coint_stat": round(score, 4),
        "p_value": round(pvalue, 6),
        "cointegrated": pvalue < 0.05,
        "interpretation": "存在长期均衡关系" if pvalue < 0.05 else "不存在长期均衡关系",
    }


def interpret_correlation(r: float) -> str:
    """解读相关系数"""
    abs_r = abs(r)
    if abs_r > 0.7:
        strength = "强"
    elif abs_r > 0.4:
        strength = "中等"
    elif abs_r > 0.2:
        strength = "弱"
    else:
        strength = "极弱/无"

    direction = "正相关（同涨同跌）" if r > 0 else "负相关（反向变动）" if r < 0 else "无方向"
    return f"{strength}{direction}"


def run_all(df: pd.DataFrame, window: int = 30) -> dict:
    """运行全部分析"""
    print("=" * 50)
    print("📊 石油-黄金相关性分析报告")
    print("=" * 50)

    # 基础统计
    print(f"\n📅 数据范围: {df.index[0].date()} ~ {df.index[-1].date()}")
    print(f"📈 样本数: {len(df)} 个交易日")
    print(f"🥇 黄金: ${df['gold'].iloc[-1]:,.2f} | WTI: ${df['wti'].iloc[-1]:,.2f}")

    # 1. Pearson
    p = pearson_corr(df)
    print(f"\n--- Pearson 相关系数 ---")
    print(f"  r = {p['pearson_r']} (p={p['p_value']}) {'✅ 显著' if p['significant'] else '❌ 不显著'}")
    print(f"  解读: {interpret_correlation(p['pearson_r'])}")

    # 2. Spearman
    s = spearman_corr(df)
    print(f"\n--- Spearman 秩相关 ---")
    print(f"  ρ = {s['spearman_r']} (p={s['p_value']}) {'✅ 显著' if s['significant'] else '❌ 不显著'}")

    # 3. Kendall
    k = kendall_corr(df)
    print(f"\n--- Kendall 秩相关 ---")
    print(f"  τ = {k['kendall_tau']} (p={k['p_value']}) {'✅ 显著' if k['significant'] else '❌ 不显著'}")

    # 4. 滚动相关
    rc = rolling_corr(df, window)
    print(f"\n--- {window}日滚动相关系数 ---")
    print(f"  当前: {rc.iloc[-1]:.4f}")
    print(f"  区间: [{rc.min():.4f}, {rc.max():.4f}]")
    rc_clean = rc.dropna()
    if len(rc_clean) >= 2:
        trend_ref = float(rc_clean.iloc[0])
        trend = '上升↗' if rc.iloc[-1] > trend_ref else '下降↘' if rc.iloc[-1] < trend_ref else '持平→'
    else:
        trend = '数据不足'
    print(f"  趋势: {trend}")

    # 5. Granger
    print(f"\n--- Granger 因果检验 ---")
    g = granger_test(df)
    for direction, result in g.items():
        if "error" in result:
            print(f"  {direction}: ⚠️ {result['error']}")
        else:
            print(f"  {direction}: p={result['min_pvalue']} (lag={result['best_lag']}) {'✅' if result['significant'] else '❌'}")

    # 6. 协整
    print(f"\n--- 协整检验 ---")
    ci = cointegration_test(df)
    if "error" in ci:
        print(f"  ⚠️ {ci['error']}")
    else:
        print(f"  统计量: {ci['coint_stat']} | p={ci['p_value']}")
        print(f"  结论: {ci['interpretation']}")

    return {
        "pearson": p,
        "spearman": s,
        "kendall": k,
        "rolling_current": round(rc.iloc[-1], 4),
        "rolling_range": [round(rc.min(), 4), round(rc.max(), 4)],
        "granger": g,
        "cointegration": ci,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="石油黄金相关性分析")
    parser.add_argument("--period", default="1y")
    parser.add_argument("--method", default="all", choices=["all", "pearson", "spearman", "granger", "cointegration"])
    parser.add_argument("--window", type=int, default=30)
    args = parser.parse_args()

    df = load_data(args.period)
    if df.empty:
        sys.exit(1)

    if args.method == "all":
        result = run_all(df, args.window)
    else:
        func_map = {
            "pearson": pearson_corr,
            "spearman": spearman_corr,
            "granger": granger_test,
            "cointegration": cointegration_test,
        }
        result = func_map[args.method](df)
        print(json.dumps(result, indent=2, default=str))
