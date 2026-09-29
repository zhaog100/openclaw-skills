#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 国内品类信号（社零分项 → 行业/就业/创业/投资映射）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from shared.sources.domestic_retail import DomesticRetailAdapter, RETAIL_CATEGORIES, CATEGORY_TO_SECTOR


@dataclass
class DomesticCategorySignal:
    """国内品类信号输出。"""
    period: str
    categories: list
    top_categories: list
    bottom_categories: list
    employment_hint: list
    startup_hint: list
    investment_hint: list
    valid_until: str
    time_horizon: str = "medium"


class DomesticCategoryCalculator:
    """国内品类计算器。"""

    def __init__(self):
        self.adapter = DomesticRetailAdapter({})

    def compute(self) -> DomesticCategorySignal:
        """计算当前国内品类信号。"""
        df = self.adapter.fetch_all_categories()
        if df.empty:
            return self._placeholder_signal()

        results = []
        for _, row in df.iterrows():
            cat = row["category"]
            yoy = row.get("yoy", 0)
            yoy_prev = row.get("yoy_prev", 0)
            marginal = (yoy - yoy_prev) if not pd.isna(yoy_prev) else 0
            score = 50 + yoy * 5 + marginal * 3
            score = max(0, min(100, score))
            results.append({"category": cat, "name": RETAIL_CATEGORIES.get(cat, cat),
                            "yoy": round(yoy, 1) if not pd.isna(yoy) else 0,
                            "marginal": round(marginal, 1), "score": round(score, 1)})
        results.sort(key=lambda x: x["score"], reverse=True)

        return DomesticCategorySignal(
            period=datetime.now().strftime("%Y-%m"),
            categories=results,
            top_categories=[r["category"] for r in results[:5]],
            bottom_categories=[r["category"] for r in results[-3:]],
            employment_hint=self._map_employment(results[:5]),
            startup_hint=self._map_startup(results[:5]),
            investment_hint=self._map_investment(results[:5]),
            valid_until=self._next_month(),
        )

    def _map_employment(self, top_categories: list) -> list:
        mapping = {"汽车": ["4S店销售", "维修技师", "汽车金融"], "家电": ["家电销售", "安装维修", "售后服务"],
                   "化妆品": ["美妆顾问", "电商运营", "品牌营销"], "金银珠宝": ["珠宝销售", "鉴定师", "设计师"],
                   "通讯器材": ["手机销售", "维修工程师", "渠道管理"], "食品饮料": ["食品加工", "渠道销售", "品控"]}
        return [{"category": c, "roles": mapping.get(c, [])} for c in top_categories if c in mapping]

    def _map_startup(self, top_categories: list) -> list:
        mapping = {"汽车": ["新能源汽车服务", "二手车交易", "充电桩运营"], "家电": ["智能家居服务", "家电清洗", "安装服务"],
                   "化妆品": ["国货美妆品牌", "美妆集合店", "直播电商"], "食品饮料": ["预制菜", "社区团购", "特色食品"]}
        return [{"category": c, "directions": mapping.get(c, [])} for c in top_categories if c in mapping]

    def _map_investment(self, top_categories: list) -> list:
        return [{"category": c, "sectors": CATEGORY_TO_SECTOR.get(c, [])} for c in top_categories if c in CATEGORY_TO_SECTOR]

    def _placeholder_signal(self) -> DomesticCategorySignal:
        return DomesticCategorySignal(
            period=datetime.now().strftime("%Y-%m"), categories=[],
            top_categories=["汽车", "家电", "化妆品", "通讯器材", "金银珠宝"],
            bottom_categories=["建筑装潢", "家具", "服装鞋帽"],
            employment_hint=[{"category": "汽车", "roles": ["4S店销售", "维修技师"]}],
            startup_hint=[{"category": "汽车", "directions": ["新能源汽车服务", "充电桩运营"]}],
            investment_hint=[{"category": "汽车", "sectors": ["汽车ETF", "新能源车ETF"]}],
            valid_until=self._next_month(),
        )

    def _next_month(self) -> str:
        from datetime import timedelta
        return (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
