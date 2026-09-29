#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 信用脉冲数据采集（社融增量 + 名义GDP）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from .base import BaseAdapter
import akshare as ak
import pandas as pd


class CreditAdapter(BaseAdapter):
    """信用脉冲数据适配器。"""

    name = "credit"


    def fetch(self, indicator: str = "", **kwargs):
        """抽象契约实现：返回空列表（本适配器走专用方法）。"""
        from .base import DataPoint
        return []

    def fetch_social_financing(self) -> pd.DataFrame:
        """社融增量月度数据。"""
        df = ak.macro_china_shrzgm()
        col_map = {"月份": "period", "社会融资规模增量": "total", "人民币贷款": "rmb_loan",
                   "企业债券": "corp_bond", "股票融资": "equity", "政府债券": "gov_bond"}
        return df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    def fetch_gdp(self) -> pd.DataFrame:
        """名义 GDP 季度数据。"""
        return ak.macro_china_gdp()

    def fetch_credit_impulse_data(self) -> pd.DataFrame:
        """信用脉冲计算所需原始数据（剔除股票融资的广义信贷）。"""
        sf = self.fetch_social_financing()
        keep = [c for c in ["period", "total", "equity"] if c in sf.columns]
        sf = sf[keep].dropna()
        sf["period"] = sf["period"].astype(str).str.replace("-", "").str[:6]
        sf["broad_credit"] = sf["total"] - sf.get("equity", 0)
        return sf


def fetch_credit_data() -> pd.DataFrame:
    """简单导出：信用脉冲原始数据。"""
    return CreditAdapter({}).fetch_credit_impulse_data()


def fetch_gdp() -> pd.DataFrame:
    """简单导出：名义 GDP。"""
    return CreditAdapter({}).fetch_gdp()
