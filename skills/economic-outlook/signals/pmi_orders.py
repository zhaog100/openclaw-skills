#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — PMI 新订单信号（月度变化 → 周期板块方向）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime
from shared.sources.pmi import PMIAdapter


@dataclass
class PMISignal:
    """PMI 新订单信号输出。"""
    period: str
    new_order: float
    delta: float
    ma3_delta: float
    direction: str
    strength: float
    valid_until: str
    invalidation: str
    historical_hit_rate: float
    time_horizon: str = "short"
    affected_outcomes: list = None

    def __post_init__(self):
        if self.affected_outcomes is None:
            self.affected_outcomes = ["stock", "fund", "commodity"]


class PMIOrdersSignal:
    """PMI 新订单 → 周期板块方向信号。"""

    def __init__(self):
        self.adapter = PMIAdapter({})

    def compute(self, lookback_months: int = 60) -> PMISignal:
        """计算当前 PMI 新订单信号。"""
        points = self.adapter.fetch()
        if len(points) < 4:
            raise ValueError("PMI 数据不足")
        df = pd.DataFrame([{"period": p.period, "value": p.value} for p in points])
        df["delta"] = df["value"].diff()
        df["ma3_delta"] = df["delta"].rolling(3).mean()
        latest = df.iloc[-1]
        delta, ma3 = latest["delta"], latest["ma3_delta"]

        if pd.isna(delta):
            direction, strength = "neutral", 0.0
        elif delta > 0 and (pd.isna(ma3) or ma3 > 0):
            direction = "bullish_cyclical"
            strength = min(abs(delta) / 2.0, 1.0)
        elif delta < 0 and (pd.isna(ma3) or ma3 < 0):
            direction = "bearish_cyclical"
            strength = min(abs(delta) / 2.0, 1.0)
        else:
            direction, strength = "neutral", 0.0

        return PMISignal(
            period=str(latest["period"]),
            new_order=float(latest["value"]),
            delta=float(delta) if not pd.isna(delta) else 0.0,
            ma3_delta=float(ma3) if not pd.isna(ma3) else 0.0,
            direction=direction,
            strength=round(strength, 2),
            valid_until=self._next_release_date(latest["period"]),
            invalidation="连续2个月方向背离则暂停信号",
            historical_hit_rate=0.0,
        )

    def _next_release_date(self, period: str) -> str:
        import calendar
        import re
        period = str(period)
        m = re.match(r"(\d{4})[年-]?(\d{1,2})", period)
        if not m:
            return (datetime.now().strftime("%Y-%m"))
        year, month = int(m.group(1)), int(m.group(2))
        ny, nm = (year + 1, 1) if month == 12 else (year, month + 1)
        last = calendar.monthrange(ny, nm)[1]
        return f"{ny}-{nm:02d}-{last:02d}"


# 兼容 aggregator 的字段名
def compute() -> PMISignal:
    return PMIOrdersSignal().compute()
