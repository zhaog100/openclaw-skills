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


    def fetch(self, indicator: str = "", **kwargs):
        """抽象契约实现：返回空列表（本适配器走专用方法）。"""
        from .base import DataPoint
        return []

    def fetch_global_pmi(self) -> pd.DataFrame:
        """获取全球/美国制造业 PMI。优先 global，退回美国 ISM（今值列）。"""
        for fn, val_col in [("macro_global_pmi", "全球制造业PMI"), ("macro_usa_pmi", "今值")]:
            try:
                df = getattr(ak, fn)()
                if df.empty:
                    continue
                if "日期" not in df.columns or val_col not in df.columns:
                    # 列名不匹配，跳过试下一个
                    continue
                df = df.rename(columns={"日期": "date", val_col: "global_pmi"})
                df = df.dropna(subset=["global_pmi"])
                df["date"] = pd.to_datetime(df["date"])
                return df.sort_values("date")
            except Exception:
                continue
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
