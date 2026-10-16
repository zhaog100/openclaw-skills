#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 中美利差数据采集（中美国债收益率）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from .base import BaseAdapter
import akshare as ak
import pandas as pd


class ChinaUSSpreadAdapter(BaseAdapter):
    """中美利差数据适配器。"""

    name = "china_us_spread"


    def fetch(self, indicator: str = "", **kwargs):
        """抽象契约实现：返回空列表（本适配器走专用方法）。"""
        from .base import DataPoint
        return []

    def fetch_yields(self, start_date: str = "20150101") -> pd.DataFrame:
        """获取中美国债收益率，计算各期限利差。"""
        try:
            df = ak.bond_zh_us_rate(start_date=start_date)
        except Exception:
            return pd.DataFrame()
        col_map = {
            "日期": "date",
            "中国国债收益率2年": "cn_2y", "中国国债收益率5年": "cn_5y",
            "中国国债收益率10年": "cn_10y", "中国国债收益率30年": "cn_30y",
            "美国国债收益率2年": "us_2y", "美国国债收益率5年": "us_5y",
            "美国国债收益率10年": "us_10y", "美国国债收益率30年": "us_30y",
        }
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
        if "date" not in df.columns:
            return pd.DataFrame()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        for tenor in ["2y", "5y", "10y", "30y"]:
            cn, us = f"cn_{tenor}", f"us_{tenor}"
            if cn in df.columns and us in df.columns:
                df[f"spread_{tenor}"] = df[cn] - df[us]
        return df

    def fetch_spread(self, tenor: str = "10y", start_date: str = "20150101") -> pd.Series:
        """获取指定期限的中美利差序列。"""
        df = self.fetch_yields(start_date)
        if df.empty:
            return pd.Series(dtype=float)
        col = f"spread_{tenor}"
        if col not in df.columns:
            return pd.Series(dtype=float)
        s = df.set_index("date")[col].dropna()
        s.name = col
        return s

    def fetch_rmb_fixing(self, start_date: str = "20150101") -> pd.Series:
        """获取美元兑人民币中间价。"""
        try:
            df = ak.currency_boc_safe()
            df = df.rename(columns={"日期": "date", "美元": "usd_cny"})
            df["date"] = pd.to_datetime(df["date"])
            df = df[df["date"] >= pd.to_datetime(start_date)]
            return df.set_index("date")["usd_cny"].dropna()
        except Exception:
            return pd.Series(dtype=float)


def fetch_spread() -> pd.Series:
    """简单导出：10Y 中美利差。"""
    return ChinaUSSpreadAdapter({}).fetch_spread("10y")
