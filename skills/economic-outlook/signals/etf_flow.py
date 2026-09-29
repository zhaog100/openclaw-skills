#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — ETF 资金流信号（份额变动率 → 行业 ETF 轮动，反转逻辑）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from shared.sources.etf_flow import ETFFlowAdapter


@dataclass
class ETFFlowSignal:
    """ETF 资金流信号输出。"""
    period: str
    direction: str
    strength: float
    top_sectors: list
    bottom_sectors: list
    valid_until: str
    invalidation: str
    historical_hit_rate: float
    time_horizon: str = "short"
    affected_outcomes: list = field(default_factory=lambda: ["stock", "fund"])


class ETFFlowCalculator:
    """ETF 资金流计算器。"""

    def __init__(self, lookback_weeks: int = 52):
        self.adapter = ETFFlowAdapter({})
        self.lookback_weeks = lookback_weeks

    def compute(self) -> ETFFlowSignal:
        """计算当前 ETF 资金流信号。"""
        flows = self.adapter.fetch_all_sector_flows(freq="W")
        if flows.empty:
            raise ValueError("ETF 资金流数据为空")

        flows = flows.tail(self.lookback_weeks)
        latest = flows.iloc[-1]
        percentile = latest.rank(pct=True)

        top = percentile.nsmallest(5)
        bottom = percentile.nlargest(5)
        top_sectors = [{"name": k, "percentile": round(v, 2), "signal": "看多"} for k, v in top.items()]
        bottom_sectors = [{"name": k, "percentile": round(v, 2), "signal": "看空"} for k, v in bottom.items()]

        avg_percentile = percentile.mean()
        if avg_percentile < 0.4:
            direction, strength = "bullish", round(1 - avg_percentile, 2)
        elif avg_percentile > 0.6:
            direction, strength = "bearish", round(avg_percentile, 2)
        else:
            direction, strength = "neutral", 0.0

        latest_date = flows.index[-1]
        valid_until = (latest_date + pd.Timedelta(days=7)).strftime("%Y-%m-%d")

        return ETFFlowSignal(
            period=latest_date.strftime("%Y-%m-%d"),
            direction=direction,
            strength=strength,
            top_sectors=top_sectors,
            bottom_sectors=bottom_sectors,
            valid_until=valid_until,
            invalidation="若资金流反转效应连续4周失效，信号暂停",
            historical_hit_rate=0.0,
        )
