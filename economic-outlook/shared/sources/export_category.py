#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 出口品类数据采集（海关汇总 + 总额降级）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from .base import BaseAdapter
import akshare as ak
import pandas as pd
from datetime import datetime


CATEGORY_HS_MAP = {
    "服装": "61,62", "鞋帽": "64,65", "家具": "94", "家电": "84,85",
    "玩具": "95", "手机": "8517", "汽车": "87", "光伏": "8541",
    "锂电池": "8507", "集成电路": "8542", "船舶": "89", "工程机械": "8429",
}


class ExportCategoryAdapter(BaseAdapter):
    """出口品类数据适配器。"""

    name = "export_category"


    def fetch(self, indicator: str = "", **kwargs):
        """抽象契约实现：返回空列表（本适配器走专用方法）。"""
        from .base import DataPoint
        return []

    def fetch_summary(self) -> pd.DataFrame:
        """获取海关进出口汇总。"""
        try:
            return ak.macro_china_hgjck()
        except Exception:
            try:
                return ak.macro_china_exports_yoy()
            except Exception:
                return pd.DataFrame()

    def fetch_total_exports_yoy(self) -> pd.DataFrame:
        """获取出口总额同比（akshare 有）。"""
        try:
            return ak.macro_china_exports_yoy()
        except Exception:
            return pd.DataFrame()

    def fetch_category_volume_price(self, category: str) -> dict:
        """获取品类量价拆分（占位，需海关统计月报/CEIC）。"""
        return {"category": category, "period": datetime.now().strftime("%Y%m"),
                "yoy_value": None, "yoy_volume": None, "yoy_price": None}

    def fetch_all_categories(self) -> pd.DataFrame:
        """获取所有重点品类（当前占位）。"""
        rows = [self.fetch_category_volume_price(c) for c in CATEGORY_HS_MAP]
        return pd.DataFrame(rows)


def fetch_export_category() -> pd.DataFrame:
    """简单导出：出口品类。"""
    return ExportCategoryAdapter({}).fetch_all_categories()


def fetch_export_total() -> pd.DataFrame:
    """简单导出：出口总额同比。"""
    return ExportCategoryAdapter({}).fetch_total_exports_yoy()
