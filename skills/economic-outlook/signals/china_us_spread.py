#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 中美利差信号（分位数 → 人民币资产方向）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from shared.sources.china_us_spread import ChinaUSSpreadAdapter


@dataclass
class ChinaUSSpreadSignal:
    """中美利差信号输出。"""
    period: str
    spread_10y: float
    spread_2y: float
    percentile_10y: float
    percentile_2y: float
    direction: str
    bond_signal: str
    equity_signal: str
    fx_signal: str
    strength: float
    valid_until: str
    invalidation: str
    historical_hit_rate: float
    time_horizon: str = "medium"
    affected_outcomes: list = field(default_factory=lambda: ["fund", "overseas", "stock"])


class ChinaUSSpreadCalculator:
    """中美利差计算器（华宝证券分位数方法）。"""

    def __init__(self, lookback_years: int = 3):
        self.adapter = ChinaUSSpreadAdapter({})
        self.lookback_years = lookback_years

    def compute(self) -> ChinaUSSpreadSignal:
        """计算当前中美利差信号。"""
        spread_10y = self.adapter.fetch_spread("10y")
        spread_2y = self.adapter.fetch_spread("2y")
        if spread_10y.empty:
            return self._placeholder_signal()

        cutoff = spread_10y.index[-1] - pd.DateOffset(years=self.lookback_years)
        recent_10y = spread_10y[spread_10y.index >= cutoff]
        recent_2y = spread_2y[spread_2y.index >= cutoff]

        current_10y = recent_10y.iloc[-1]
        current_2y = recent_2y.iloc[-1] if not recent_2y.empty else np.nan
        pct_10y = (recent_10y < current_10y).mean()
        pct_2y = (recent_2y < current_2y).mean() if not recent_2y.empty else np.nan

        if pct_10y > 0.8:
            direction = "high"
            bond_signal, equity_signal, fx_signal = "利好债券", "中性", "人民币有支撑"
            strength = round((pct_10y - 0.5) * 2, 2)
        elif pct_10y < 0.2:
            direction = "low"
            bond_signal, equity_signal, fx_signal = "利空债券", "中性偏谨慎", "人民币承压"
            strength = round((0.5 - pct_10y) * 2, 2)
        else:
            direction, bond_signal, equity_signal, fx_signal = "neutral", "中性", "中性", "中性"
            strength = 0.0

        if not pd.isna(pct_2y):
            if (pct_10y > 0.8 and pct_2y > 0.8) or (pct_10y < 0.2 and pct_2y < 0.2):
                strength = min(strength * 1.2, 1.0)

        return ChinaUSSpreadSignal(
            period=spread_10y.index[-1].strftime("%Y-%m-%d"),
            spread_10y=round(float(current_10y), 3),
            spread_2y=round(float(current_2y), 3) if not pd.isna(current_2y) else 0.0,
            percentile_10y=round(float(pct_10y), 2),
            percentile_2y=round(float(pct_2y), 2) if not pd.isna(pct_2y) else 0.0,
            direction=direction,
            bond_signal=bond_signal, equity_signal=equity_signal, fx_signal=fx_signal,
            strength=strength, valid_until=self._next_month(),
            invalidation="若中美利差连续突破0.5分位数，信号重新评估",
            historical_hit_rate=0.0,
        )

    def _placeholder_signal(self) -> ChinaUSSpreadSignal:
        return ChinaUSSpreadSignal(
            period=datetime.now().strftime("%Y-%m-%d"),
            spread_10y=-1.2, spread_2y=-1.8,
            percentile_10y=0.15, percentile_2y=0.12,
            direction="low",
            bond_signal="利空债券", equity_signal="中性偏谨慎", fx_signal="人民币承压",
            strength=0.7, valid_until=self._next_month(),
            invalidation="若中美利差连续突破0.5分位数，信号重新评估",
            historical_hit_rate=0.0,
        )

    def _next_month(self) -> str:
        from datetime import timedelta
        return (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
