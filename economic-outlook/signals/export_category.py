#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 出口品类信号（量价拆分 → 行业/就业/创业/投资映射）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from shared.sources.export_category import ExportCategoryAdapter, CATEGORY_HS_MAP


@dataclass
class ExportCategorySignal:
    """出口品类信号输出。"""
    period: str
    categories: list
    top_categories: list
    bottom_categories: list
    employment_hint: list
    startup_hint: list
    investment_hint: list
    valid_until: str
    time_horizon: str = "medium"


class ExportCategoryCalculator:
    """出口品类计算器。"""

    def __init__(self):
        self.adapter = ExportCategoryAdapter({})

    def compute(self) -> ExportCategorySignal:
        """计算当前出口品类信号。"""
        df = self.adapter.fetch_all_categories()
        if df.empty or df["yoy_value"].isna().all():
            return self._placeholder_signal()

        results = []
        for _, row in df.iterrows():
            vol_yoy = row.get("yoy_volume") or 0
            price_yoy = row.get("yoy_price") or 0
            if vol_yoy > 0 and price_yoy > 0:
                status, score = "量价齐升", 85
            elif vol_yoy > 0 and price_yoy <= 0:
                status, score = "量增价跌", 60
            elif vol_yoy <= 0 and price_yoy > 0:
                status, score = "量减价升", 45
            else:
                status, score = "量价齐跌", 25
            results.append({"category": row["category"], "status": status, "score": score,
                            "yoy_volume": vol_yoy, "yoy_price": price_yoy})
        results.sort(key=lambda x: x["score"], reverse=True)

        return ExportCategorySignal(
            period=df["period"].iloc[0] if "period" in df.columns else "",
            categories=results,
            top_categories=[r["category"] for r in results[:5]],
            bottom_categories=[r["category"] for r in results[-3:]],
            employment_hint=self._map_employment(results[:5]),
            startup_hint=self._map_startup(results[:5]),
            investment_hint=self._map_investment(results[:5]),
            valid_until=self._next_month(),
        )

    def _map_employment(self, top_categories: list) -> list:
        mapping = {"汽车": ["装配工", "工程师", "外贸业务员"], "锂电池": ["工程师", "质检", "外贸"],
                   "光伏": ["工程师", "外贸", "安装运维"], "家电": ["装配工", "质检", "外贸"],
                   "集成电路": ["芯片设计", "封装测试", "设备工程师"], "船舶": ["焊工", "装配工", "工程师"],
                   "工程机械": ["装配工", "售后工程师", "外贸"]}
        return [{"category": c, "roles": mapping.get(c, [])} for c in top_categories if c in mapping]

    def _map_startup(self, top_categories: list) -> list:
        mapping = {"汽车": ["二手车出口", "海外售后", "汽车配件跨境"], "锂电池": ["海外仓", "售后", "回收"],
                   "光伏": ["海外安装", "运维", "分销"], "家电": ["品牌出海", "海外售后", "跨境电商"],
                   "集成电路": ["芯片设计", "测试服务", "设备代理"]}
        return [{"category": c, "directions": mapping.get(c, [])} for c in top_categories if c in mapping]

    def _map_investment(self, top_categories: list) -> list:
        return [f"{c}出口链" for c in top_categories]

    def _placeholder_signal(self) -> ExportCategorySignal:
        return ExportCategorySignal(
            period="", categories=[],
            top_categories=["汽车", "锂电池", "光伏", "集成电路", "船舶"],
            bottom_categories=["服装", "鞋帽", "家具"],
            employment_hint=[{"category": "汽车", "roles": ["装配工", "工程师", "外贸"]}],
            startup_hint=[{"category": "汽车", "directions": ["二手车出口", "海外售后"]}],
            investment_hint=["汽车出口链", "锂电出口链", "光伏出口链"],
            valid_until=self._next_month(),
        )

    def _next_month(self) -> str:
        from datetime import timedelta
        return (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
