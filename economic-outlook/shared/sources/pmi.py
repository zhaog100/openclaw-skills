#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — PMI 数据适配器（新订单/从业人员/新出口订单分项）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from .base import BaseAdapter, DataPoint
import akshare as ak
import pandas as pd
from datetime import datetime


class PMIAdapter(BaseAdapter):
    """PMI 数据适配器，基于 akshare macro_china_pmi。"""

    name = "pmi"

    def fetch(self, indicator: str = "pmi_new_order", **kwargs) -> list:
        """获取 PMI 数据历史。macro_china_pmi 仅总值，new_order 缺失时退回制造业总值代理。"""
        df = ak.macro_china_pmi()
        col_map = {
            "月份": "period", "制造业PMI": "pmi", "制造业-指数": "pmi",
            "非制造业-指数": "non_pmi",
            "新订单": "new_order", "新订单指数": "new_order",
            "生产指数": "production", "新出口订单": "new_export_order",
            "新出口订单指数": "new_export_order", "从业人员": "employment",
            "从业人员指数": "employment",
        }
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
        target = "new_order" if indicator == "pmi_new_order" else indicator
        # 分项缺失时退回制造业 PMI 总值（标注代理）
        if target not in df.columns and target in ("new_order", "production"):
            target = "pmi"
        if target not in df.columns:
            raise ValueError(f"PMI 列名不含 {target}，实际列：{list(df.columns)}")
        points = []
        for _, row in df.iterrows():
            try:
                v = float(row[target])
            except (ValueError, TypeError):
                continue
            points.append(DataPoint(indicator=indicator, period=str(row["period"]),
                                    value=v, unit="", source="国家统计局/akshare",
                                    updated_at=datetime.now().isoformat()))
        points.sort(key=lambda p: p.period)
        return points

    def fetch_with_production(self) -> pd.DataFrame:
        """同时获取新订单和生产分项。"""
        df = ak.macro_china_pmi()
        col_map = {"月份": "period", "新订单": "new_order", "新订单指数": "new_order", "生产指数": "production"}
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
        cols = [c for c in ["period", "new_order", "production"] if c in df.columns]
        return df[cols].dropna()

    def fetch_pmi_employment(self) -> pd.DataFrame:
        """获取 PMI 从业人员指数。"""
        df = ak.macro_china_pmi()
        col_map = {"月份": "period", "从业人员": "employment", "从业人员指数": "employment"}
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
        if "employment" not in df.columns:
            return pd.DataFrame(columns=["period", "employment"])
        return df[["period", "employment"]].dropna()

    def fetch_china_export_order(self) -> pd.DataFrame:
        """获取中国 PMI 新出口订单。"""
        df = ak.macro_china_pmi()
        col_map = {"月份": "period", "新出口订单": "new_export_order", "新出口订单指数": "new_export_order"}
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
        if "new_export_order" not in df.columns:
            return pd.DataFrame(columns=["period", "new_export_order"])
        return df[["period", "new_export_order"]].dropna()


def fetch_pmi() -> pd.DataFrame:
    """简单导出：PMI 原始 DataFrame。"""
    return ak.macro_china_pmi()


def fetch_pmi_items() -> pd.DataFrame:
    """PMI 分项 DataFrame。"""
    return PMIAdapter({}).fetch_with_production()
