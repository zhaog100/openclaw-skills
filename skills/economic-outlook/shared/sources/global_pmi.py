#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 全球 PMI 数据采集（美国 ISM 替代全球 PMI）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from .base import BaseAdapter
import akshare as ak
import pandas as pd


class GlobalPMIAdapter(BaseAdapter):
    """全球 PMI 数据适配器（美国 ISM 制造业 PMI 作为外需代理）。"""

    name = "global_pmi"

    def fetch_global_pmi(self) -> pd.DataFrame:
        """获取全球/美国制造业 PMI。优先 global，退回美国 ISM。"""
        try:
            df = ak.macro_global_pmi()
            if not df.empty:
                df = df.rename(columns={"日期": "date", "全球制造业PMI": "global_pmi"})
                df["date"] = pd.to_datetime(df["date"])
                return df.sort_values("date")
        except Exception:
            pass
        try:
            df = ak.macro_usa_pmi()
            df = df.rename(columns={"商品": "item", "日期": "date", "今值": "global_pmi"})
            df["date"] = pd.to_datetime(df["date"])
            return df.sort_values("date")
        except Exception:
            return pd.DataFrame()

    def fetch_us_pmi(self) -> pd.DataFrame:
        """获取美国制造业 PMI。"""
        try:
            return ak.macro_usa_pmi()
        except Exception:
            return pd.DataFrame()


def fetch_global_pmi() -> pd.DataFrame:
    """简单导出：全球 PMI。"""
    return GlobalPMIAdapter({}).fetch_global_pmi()
