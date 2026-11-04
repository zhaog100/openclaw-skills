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
    unavailable_reason: str = ""


class ETFFlowCalculator:
    """ETF 资金流计算器。"""

    def __init__(self, lookback_weeks: int = 52):
        self.adapter = ETFFlowAdapter({})
        self.lookback_weeks = lookback_weeks

    def compute(self) -> ETFFlowSignal:
        """计算当前 ETF 资金流信号。"""
        flows = self.adapter.fetch_all_sector_flows(freq="W")
        if flows.empty:
            # 官家11-04 P1: 拉空不再 raise, 返回降级 signal(unavailable_reason 非空), skill 层显式标注
            import pandas as _pd
            today = _pd.Timestamp.now().strftime("%Y-%m-%d")
            return ETFFlowSignal(
                period=today, direction="unknown", strength=0.0,
                top_sectors=[], bottom_sectors=[],
                valid_until=today,
                invalidation="数据不可用",
                historical_hit_rate=0.0,
                unavailable_reason="东财 push2 限流/akshare ETF 份额数据拉空 (5min 后可重试)",
            )

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
