#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 国内社零分项数据采集（总额 + 分项占位）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from .base import BaseAdapter
import akshare as ak
import pandas as pd


RETAIL_CATEGORIES = {
    "粮油食品": "粮油、食品类", "饮料": "饮料类", "烟酒": "烟酒类",
    "服装鞋帽": "服装鞋帽、针纺织品类", "化妆品": "化妆品类",
    "金银珠宝": "金银珠宝类", "日用品": "日用品类",
    "家电": "家用电器和音像器材类", "中西药品": "中西药品类",
    "文化办公": "文化办公用品类", "家具": "家具类", "通讯器材": "通讯器材类",
    "石油制品": "石油及制品类", "汽车": "汽车类", "建筑装潢": "建筑及装潢材料类",
}

CATEGORY_TO_SECTOR = {
    "汽车": ["汽车ETF", "新能源车ETF"], "家电": ["家电ETF"],
    "化妆品": ["消费ETF"], "金银珠宝": ["黄金ETF"],
    "食品饮料": ["食品饮料ETF", "白酒ETF"], "医药": ["医药ETF"],
}


class DomesticRetailAdapter(BaseAdapter):
    """国内社零分项数据适配器。"""

    name = "domestic_retail"


    def fetch(self, indicator: str = "", **kwargs):
        """抽象契约实现：返回空列表（本适配器走专用方法）。"""
        from .base import DataPoint
        return []

    def fetch_total(self) -> pd.DataFrame:
        """获取社零总额。"""
        try:
            df = ak.macro_china_consumer_goods_retail()
            df = df.rename(columns={"月份": "period", "当月": "total", "同比增长": "yoy"})
            return df
        except Exception:
            return pd.DataFrame()

    def fetch_all_categories(self) -> pd.DataFrame:
        """获取所有分品类（当前占位，需统计局/天软）。"""
        return pd.DataFrame()


def fetch_retail() -> pd.DataFrame:
    """简单导出：社零总额。"""
    return DomesticRetailAdapter({}).fetch_total()
