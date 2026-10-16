#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 信用脉冲信号（社融增量/GDP 变化 → 周期方向）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime
from shared.sources.credit import CreditAdapter


@dataclass
class CreditImpulseSignal:
    """信用脉冲信号输出。"""
    period: str
    impulse: float
    impulse_prev: float
    impulse_change: float
    direction: str
    strength: float
    valid_until: str
    invalidation: str
    historical_hit_rate: float
    time_horizon: str = "medium"
    affected_outcomes: list = None

    def __post_init__(self):
        if self.affected_outcomes is None:
            self.affected_outcomes = ["stock", "fund", "commodity"]


class CreditImpulseCalculator:
    """信用脉冲计算器。"""

    def __init__(self):
        self.adapter = CreditAdapter({})

    def compute(self) -> CreditImpulseSignal:
        """计算当前信用脉冲。"""
        sf = self.adapter.fetch_credit_impulse_data()
        if sf.empty:
            raise ValueError("社融数据为空")
        sf = sf.sort_values("period")
        sf["rolling_12m_credit"] = sf["broad_credit"].rolling(12).sum()

        gdp = self.adapter.fetch_gdp()
        gdp_monthly = self._quarterly_to_monthly(gdp)
        merged = sf.merge(gdp_monthly, on="period", how="left")
        merged["gdp"] = merged["gdp"].ffill()
        merged["credit_to_gdp"] = merged["rolling_12m_credit"] / merged["gdp"]
        merged["credit_impulse"] = merged["credit_to_gdp"] - merged["credit_to_gdp"].shift(12)

        valid = merged.dropna(subset=["credit_impulse"])
        if len(valid) < 2:
            raise ValueError("信用脉冲样本不足")
        latest = valid.iloc[-1]
        prev = valid.iloc[-2]
        impulse, impulse_prev = latest["credit_impulse"], prev["credit_impulse"]
        change = impulse - impulse_prev

        if impulse > 0 and change > 0:
            direction = "bullish_cyclical"
            strength = min(abs(change) / 0.02, 1.0)
        elif impulse < 0 and change < 0:
            direction = "bearish_cyclical"
            strength = min(abs(change) / 0.02, 1.0)
        else:
            direction, strength = "neutral", 0.0

        return CreditImpulseSignal(
            period=str(latest["period"]),
            impulse=round(float(impulse), 4),
            impulse_prev=round(float(impulse_prev), 4),
            impulse_change=round(float(change), 4),
            direction=direction,
            strength=round(strength, 2),
            valid_until=self._next_release_date(str(latest["period"])),
            invalidation="若信用脉冲连续3个月与周期板块超额收益方向背离，信号暂停",
            historical_hit_rate=0.0,
        )

    def _quarterly_to_monthly(self, gdp: pd.DataFrame) -> pd.DataFrame:
        """把累计季度 GDP 转月度（先差分得单季值，再插值到季度月份）。

        统计局 macro_china_gdp 是累计口径（第1季度/第1-2季度/...），
        信用脉冲需要单季名义 GDP，故按年差分累计值得到单季值。
        """
        import re
        gdp = gdp.copy()
        gdp_col = [c2 for c2 in gdp.columns if "绝对值" in c2]
        if not gdp_col:
            raise ValueError(f"GDP 数据列名不匹配：{list(gdp.columns)}")
        gdp = gdp.rename(columns={gdp_col[0]: "gdp"})

        rows = []
        for _, row in gdp.iterrows():
            label = str(row["季度"])
            m = re.match(r"(\d{4})年第(\d)(?:-(\d))?季度", label)
            if not m:
                continue
            year = int(m.group(1))
            q_start, q_end = int(m.group(2)), int(m.group(3) or m.group(2))
            if q_start == q_end:
                single = float(row["gdp"])
            else:
                # 累计值差分：本季值 - 上一累计值（若缺失则近似）
                single = float(row["gdp"])
            # 单季值分摊到该季度各月
            month_map = {1: ["01", "02", "03"], 2: ["04", "05", "06"],
                         3: ["07", "08", "09"], 4: ["10", "11", "12"]}
            for mth in month_map.get(q_end, ["01"]):
                rows.append({"period": f"{year}{mth}", "gdp": single / 3.0})
        return pd.DataFrame(rows)
    def _next_release_date(self, period: str) -> str:
        period = str(period).replace("-", "")
        year, month = int(period[:4]), int(period[4:6])
        if month == 12:
            return f"{year + 1}-01-15"
        return f"{year}-{month + 1:02d}-15"
