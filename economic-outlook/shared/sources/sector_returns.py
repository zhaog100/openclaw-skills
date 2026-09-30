#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 周期板块收益数据采集（ETF 月度超额收益）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import akshare as ak
import pandas as pd
from datetime import datetime


def _to_monthly(df: pd.DataFrame, date_col: str, close_col: str) -> pd.Series:
    """日频收盘价转月度收益。"""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    df["year_month"] = df[date_col].dt.strftime("%Y%m")
    monthly = df.groupby("year_month")[close_col].last()
    return monthly.pct_change().dropna()


def fetch_etf_monthly(etf_code: str = "512400", start: str = "20170101", end: str = None) -> pd.Series:
    """获取 ETF 月度收益。"""
    if end is None:
        end = datetime.now().strftime("%Y%m%d")
    try:
        df = ak.fund_etf_hist_em(symbol=etf_code, period="daily", start_date=start, end_date=end, adjust="qfq")
        df = df.rename(columns={"日期": "date", "收盘": "close"})
        ret = _to_monthly(df, "date", "close")
        ret.name = f"etf_{etf_code}"
        return ret
    except Exception:
        return pd.Series(dtype=float)


def fetch_hs300_monthly(start: str = "20170101", end: str = None) -> pd.Series:
    """获取沪深 300 月度收益。"""
    if end is None:
        end = datetime.now().strftime("%Y%m%d")
    try:
        df = ak.stock_zh_index_daily(symbol="sh000300")
        df = df.rename(columns={"date": "date", "close": "close"})
        df["date"] = pd.to_datetime(df["date"])
        df = df[df["date"] >= pd.to_datetime(start)]
        ret = _to_monthly(df, "date", "close")
        ret.name = "hs300"
        return ret
    except Exception:
        return pd.Series(dtype=float)


def fetch_sector_returns(etf_code: str = "512400", start: str = "20170101", end: str = None) -> pd.DataFrame:
    """获取周期板块月度超额收益（ETF - 沪深300）。"""
    etf_ret = fetch_etf_monthly(etf_code, start, end)
    hs300_ret = fetch_hs300_monthly(start, end)
    df = pd.DataFrame({"etf_return": etf_ret, "hs300_return": hs300_ret}).dropna()
    df["excess_return"] = df["etf_return"] - df["hs300_return"]
    df["etf_code"] = etf_code
    return df


def fetch_sw_monthly(sw_code: str = "801050", start: str = "20100101", end: str = None) -> pd.Series:
    """获取申万行业指数月度收益（主源，绕开东财）。"""
    if end is None:
        end = datetime.now().strftime("%Y%m%d")
    try:
        df = ak.index_hist_sw(symbol=sw_code, period="month")
        df = df.rename(columns={"日期": "date", "收盘": "close"})
        df["date"] = pd.to_datetime(df["date"])
        df = df[(df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))]
        df["year_month"] = df["date"].dt.strftime("%Y%m")
        df = df.drop_duplicates(subset=["date"])
        returns = df.set_index("year_month")["close"].pct_change().dropna()
        returns.name = f"sw_{sw_code}"
        return returns
    except Exception:
        return pd.Series(dtype=float)


def fetch_sector_returns_sw(sw_code: str = "801050", start: str = "20100101", end: str = None) -> pd.DataFrame:
    """板块超额收益（申万行业指数 - 沪深300），东财挂了也能跑。"""
    if end is None:
        end = datetime.now().strftime("%Y%m%d")
    sw_ret = fetch_sw_monthly(sw_code, start, end)
    hs300_ret = fetch_hs300_monthly(start, end)
    if sw_ret.empty:
        return pd.DataFrame()
    hs300_aligned = hs300_ret.reindex(sw_ret.index)
    df = pd.DataFrame({"sw_return": sw_ret, "hs300_return": hs300_aligned}).dropna()
    df["excess_return"] = df["sw_return"] - df["hs300_return"]
    df["source"] = f"sw_{sw_code}"
    return df
