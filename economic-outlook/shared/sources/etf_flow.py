#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — ETF 资金流数据采集（行业 ETF 成交额代理）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from .base import BaseAdapter
import akshare as ak
import pandas as pd
from datetime import datetime


SECTOR_ETF_MAP = {
    "有色金属": ["512400", "159881"],
    "煤炭": ["515220"],
    "钢铁": ["515210"],
    "新能源": ["516160", "515030"],
    "半导体": ["512480", "159995"],
    "医药": ["512010", "159929"],
    "消费": ["159928", "512600"],
    "银行": ["512800"],
    "证券": ["512880"],
    "地产": ["512200"],
    "汽车": ["516110"],
}


class ETFFlowAdapter(BaseAdapter):
    """ETF 资金流数据适配器。"""

    name = "etf_flow"


    def fetch(self, indicator: str = "", **kwargs):
        """抽象契约实现：返回空列表（本适配器走专用方法）。"""
        from .base import DataPoint
        return []

    def fetch_etf_scale(self, etf_code: str, start: str = "20200101") -> pd.DataFrame:
        """获取单只 ETF 行情（用成交额近似资金流）。"""
        try:
            df = ak.fund_etf_hist_em(symbol=etf_code, period="daily", start_date=start,
                                     end_date=datetime.now().strftime("%Y%m%d"), adjust="")
            df = df.rename(columns={"日期": "date", "成交额": "amount", "换手率": "turnover", "收盘": "close"})
            df["date"] = pd.to_datetime(df["date"])
            return df.sort_values("date")
        except Exception:
            return pd.DataFrame()

    def fetch_sector_flow(self, sector: str, start: str = "20200101", freq: str = "W") -> pd.Series:
        """获取行业 ETF 资金流汇总。"""
        codes = SECTOR_ETF_MAP.get(sector, [])
        flows = []
        for code in codes:
            df = self.fetch_etf_scale(code, start)
            if df.empty:
                continue
            s = df.set_index("date")["amount"]
            flows.append(s)
        if not flows:
            return pd.Series(dtype=float)
        combined = pd.concat(flows, axis=1).sum(axis=1)
        combined.name = sector
        if freq == "W":
            combined = combined.resample("W").sum()
        elif freq == "M":
            combined = combined.resample("ME").sum()
        return combined

    def fetch_all_sector_flows(self, start: str = "20200101", freq: str = "W") -> pd.DataFrame:
        """获取所有行业 ETF 资金流。"""
        result = {}
        for sector in SECTOR_ETF_MAP:
            s = self.fetch_sector_flow(sector, start, freq)
            if not s.empty:
                result[sector] = s
        return pd.DataFrame(result)


def fetch_etf_flow() -> pd.DataFrame:
    """简单导出：行业 ETF 资金流。"""
    return ETFFlowAdapter({}).fetch_all_sector_flows()
