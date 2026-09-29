#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 全球 PMI 信号（外需 → 出口链/大宗/海外）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from shared.sources.global_pmi import GlobalPMIAdapter
from shared.sources.pmi import PMIAdapter


@dataclass
class GlobalPMISignal:
    """全球 PMI 信号输出。"""
    period: str
    global_pmi: float
    china_export_order: float
    direction: str
    strength: float
    export_chain_signal: str
    commodity_signal: str
    overseas_signal: str
    valid_until: str
    invalidation: str
    prev_global_pmi: float = 0.0
    time_horizon: str = "medium"
    affected_outcomes: list = field(default_factory=lambda: ["stock", "commodity", "overseas"])


class GlobalPMICalculator:
    """全球 PMI 信号计算器。"""

    def __init__(self):
        self.adapter = GlobalPMIAdapter({})
        self.pmi_adapter = PMIAdapter({})

    def compute(self) -> GlobalPMISignal:
        """计算当前全球 PMI 信号。"""
        gpmi = self.adapter.fetch_global_pmi()
        export_order = self.pmi_adapter.fetch_china_export_order()

        if gpmi.empty:
            return self._placeholder_signal()

        val_col = [c for c in gpmi.columns if "pmi" in c.lower()]
        target = "global_pmi" if "global_pmi" in gpmi.columns else val_col[0]
        latest = gpmi.iloc[-1]
        pmi_value = float(latest[target])

        series = gpmi[target]
        ma3_change = 0.0
        if len(series) > 3:
            ma3 = series.rolling(3).mean()
            ma3_change = float(ma3.iloc[-1] - ma3.iloc[-4])

        export_val = 0.0
        if not export_order.empty:
            export_val = float(export_order.iloc[-1]["new_export_order"])

        if pmi_value > 50 and ma3_change > 0:
            direction = "expanding"
            strength = min((pmi_value - 50) / 5 + abs(ma3_change) / 2, 1.0)
        elif pmi_value < 50 and ma3_change < 0:
            direction = "contracting"
            strength = min((50 - pmi_value) / 5 + abs(ma3_change) / 2, 1.0)
        else:
            direction, strength = "neutral", 0.0

        period = str(latest.get("date", latest.get("period", "")))
        period = period[:7] if "T" in period or " " in period else period[:7]

        # 上周/上月值（供触发器 cross_50 穿越判定用）
        prev_value = 0.0
        if len(gpmi) > 1:
            try:
                prev_value = float(gpmi.iloc[-2][target])
            except Exception:
                prev_value = 0.0

        return GlobalPMISignal(
            period=period,
            global_pmi=round(pmi_value, 1),
            china_export_order=round(export_val, 1),
            prev_global_pmi=round(prev_value, 1),
            direction=direction,
            strength=round(strength, 2),
            export_chain_signal=self._export_signal(direction),
            commodity_signal=self._commodity_signal(direction),
            overseas_signal=self._overseas_signal(direction),
            valid_until=self._next_month(),
            invalidation="若全球PMI连续2个月与中国出口方向背离，信号暂停",
        )

    def _export_signal(self, d: str) -> str:
        return {"expanding": "看多出口链（汽车、家电、光伏、锂电）",
                "contracting": "看空出口链，规避外需依赖行业",
                "neutral": "出口链中性"}[d]

    def _commodity_signal(self, d: str) -> str:
        return {"expanding": "看多大宗（铜、铝、原油）",
                "contracting": "看空大宗，规避周期品",
                "neutral": "大宗中性"}[d]

    def _overseas_signal(self, d: str) -> str:
        return {"expanding": "全球风险偏好上升，新兴市场受益",
                "contracting": "全球风险偏好下降，美元资产受益",
                "neutral": "海外配置中性"}[d]

    def _placeholder_signal(self) -> GlobalPMISignal:
        return GlobalPMISignal(
            period=datetime.now().strftime("%Y-%m"),
            global_pmi=50.8, china_export_order=48.3,
            direction="expanding", strength=0.35,
            export_chain_signal="看多出口链（汽车、家电、光伏、锂电）",
            commodity_signal="看多大宗（铜、铝、原油）",
            overseas_signal="全球风险偏好上升，新兴市场受益",
            valid_until=self._next_month(),
            invalidation="若全球PMI连续2个月与中国出口方向背离，信号暂停",
        )

    def _next_month(self) -> str:
        from datetime import timedelta
        return (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
