#!/usr/bin/env python3
"""
历史走势分析报告 — 收集黄金石油近期走势数据，发现报告优化点
"""
# 版本: v3.3 | 石油黄金白银相关性分析
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from advisor import _fetch_akshare_single

def analyze():
    results = {}
    for key, name in [('gold', '黄金'), ('silver', '白银'), ('wti', '原油')]:
        df = _fetch_akshare_single(key, '90d')
        if df is None or len(df) < 20:
            print(f"=== {name}: 数据不足 ===")
            continue
        
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        
        print(f'=== {name} ({len(close)}个交易日) ===')
        print(f'最新收盘: {close.iloc[-1]:.2f}')
        
        # 均线
        ma5 = close.rolling(5).mean().iloc[-1]
        ma10 = close.rolling(10).mean().iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        ma60 = close.rolling(60).mean().iloc[-1] if len(close) >= 60 else None
        print(f'MA5={ma5:.1f} MA10={ma10:.1f} MA20={ma20:.1f}' + (f' MA60={ma60:.1f}' if ma60 else ''))
        
        # 趋势判断
        if ma5 > ma10 > ma20:
            trend = '多头排列 📈'
        elif ma5 < ma10 < ma20:
            trend = '空头排列 📉'
        else:
            trend = '交叉/震荡 ➡️'
        print(f'均线趋势: {trend}')
        
        # 价格相对位置
        if ma60:
            pos_vs_ma60 = '上方' if close.iloc[-1] > ma60 else '下方'
            print(f'价格 vs MA60: {pos_vs_ma60}')
        
        # 波动率
        returns = close.pct_change().dropna()
        vol_30 = returns.tail(20).std() * np.sqrt(252) * 100 if len(returns) >= 20 else 0
        vol_90 = returns.std() * np.sqrt(252) * 100
        print(f'近30日年化波动率: {vol_30:.1f}% | 近90日: {vol_90:.1f}%')
        
        # 最大回撤
        peak = close.expanding().max()
        drawdown = (close - peak) / peak
        max_dd = drawdown.min() * 100
        print(f'近90日最大回撤: {max_dd:.1f}%')
        
        # 近5日/10日/30日涨跌
        chg_5 = (close.iloc[-1] / close.iloc[-6] - 1) * 100 if len(close) >= 6 else 0
        chg_10 = (close.iloc[-1] / close.iloc[-11] - 1) * 100 if len(close) >= 11 else 0
        chg_30 = (close.iloc[-1] / close.iloc[-31] - 1) * 100 if len(close) >= 31 else 0
        print(f'近5日: {chg_5:+.1f}% | 近10日: {chg_10:+.1f}% | 近30日: {chg_30:+.1f}%')
        
        # 成交量趋势
        vol_5 = volume.rolling(5).mean().iloc[-1]
        vol_20 = volume.rolling(20).mean().iloc[-1]
        vol_ratio = vol_5 / vol_20 if vol_20 > 0 else 1
        print(f'量比(5日/20日): {vol_ratio:.2f}' + (' 放量' if vol_ratio > 1.3 else ' 缩量' if vol_ratio < 0.7 else ' 正常'))
        
        # 关键价位
        support_30 = low.tail(30).min()
        resist_30 = high.tail(30).max()
        print(f'30日最低(支撑): {support_30:.1f} | 30日最高(阻力): {resist_30:.1f}')
        
        results[key] = {
            'name': name,
            'latest': close.iloc[-1],
            'ma5': ma5, 'ma10': ma10, 'ma20': ma20,
            'trend': trend,
            'vol_30': vol_30,
            'max_dd': max_dd,
            'chg_5': chg_5, 'chg_10': chg_10, 'chg_30': chg_30,
            'support': support_30,
            'resist': resist_30,
        }
        print()
    
    # 联动性分析
    print('=== 联动性分析 ===')
    gold_df = _fetch_akshare_single('gold', '90d')
    silver_df = _fetch_akshare_single('silver', '90d')
    oil_df = _fetch_akshare_single('wti', '90d')
    
    if gold_df is not None and oil_df is not None:
        g_ret = gold_df['Close'].pct_change().dropna()
        o_ret = oil_df['Close'].pct_change().dropna()
        min_len = min(len(g_ret), len(o_ret))
        if min_len > 10:
            corr = g_ret.iloc[-min_len:].corr(o_ret.iloc[-min_len:])
            print(f'黄金-原油 90日收益率相关系数: {corr:.3f}')
            if corr < -0.5:
                print('→ 强负相关：避险主导，黄金涨原油跌')
            elif corr > 0.5:
                print('→ 强正相关：风险情绪主导，同涨同跌')
            else:
                print('→ 弱相关：走势相对独立')
    
    if gold_df is not None and silver_df is not None:
        g_price = gold_df['Close'].iloc[-1]
        s_price = silver_df['Close'].iloc[-1]
        if g_price > 0 and s_price > 0:
            # 统一为克价
            s_per_gram = s_price / 1000
            ratio = g_price / s_per_gram
            print(f'金银比(克价): {ratio:.1f}')
            if ratio < 50:
                print('→ 金银比偏低，白银相对更贵')
            elif ratio > 80:
                print('→ 金银比偏高，黄金相对更贵')
            else:
                print('→ 金银比处于正常区间')
    
    # 跨品种趋势对比
    print()
    print('=== 跨品种趋势对比 ===')
    for key in ['gold', 'silver', 'wti']:
        if key in results:
            r = results[key]
            print(f"{r['name']}: {r['trend']} | 5日{r['chg_5']:+.1f}% | 30日{r['chg_30']:+.1f}% | 波动率{r['vol_30']:.0f}%")

if __name__ == '__main__':
    analyze()
# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
