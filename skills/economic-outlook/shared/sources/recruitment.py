#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 招聘数据采集（PMI 从业人员 + 工资指数）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from .base import BaseAdapter
import akshare as ak
import pandas as pd


INDUSTRY_JOB_MAP = {
    "高端制造": ["机械设备", "电气设备", "化工"],
    "半导体": ["电子", "集成电路"],
    "新能源": ["电力设备", "汽车"],
    "医疗健康": ["医药生物", "医疗服务"],
    "养老": ["养老服务", "社会工作"],
    "互联网": ["计算机", "传媒"],
}


class RecruitmentAdapter(BaseAdapter):
    """招聘数据适配器。"""

    name = "recruitment"


    def fetch(self, indicator: str = "", **kwargs):
        """抽象契约实现：返回空列表（本适配器走专用方法）。"""
        from .base import DataPoint
        return []

    def fetch_salary_index(self) -> pd.DataFrame:
        """获取财新新经济行业入职平均工资水平。"""
        try:
            df = ak.index_neaw_cx()
            df = df.rename(columns={"日期": "date", "新经济行业入职平均工资水平": "salary_index"})
            df["date"] = pd.to_datetime(df["date"])
            return df
        except Exception:
            return pd.DataFrame()

    def fetch_pmi_employment(self) -> pd.DataFrame:
        """获取 PMI 从业人员指数。"""
        try:
            df = ak.macro_china_pmi()
            col_map = {"月份": "period", "从业人员": "employment", "从业人员指数": "employment"}
            df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
            if "employment" not in df.columns:
                return pd.DataFrame(columns=["period", "employment"])
            return df[["period", "employment"]].dropna()
        except Exception:
            return pd.DataFrame()


def fetch_recruitment() -> pd.DataFrame:
    """简单导出：PMI 从业人员。"""
    return RecruitmentAdapter({}).fetch_pmi_employment()
