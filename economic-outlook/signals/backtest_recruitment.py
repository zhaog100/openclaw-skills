#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 招聘指数信号回测

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import pandas as pd
import numpy as np
from shared.sources.recruitment import RecruitmentAdapter


def backtest_recruitment_signal() -> dict:
    """回测 PMI 从业人员指数对失业率的预测力。"""
    adapter = RecruitmentAdapter({})
    pmi_emp = adapter.fetch_pmi_employment()
    if pmi_emp.empty:
        return {"error": "PMI从业人员数据为空"}

    try:
        import akshare as ak
        unemployment = ak.macro_china_urban_unemployment()
        unemployment = unemployment.rename(columns={"月份": "period", "失业率": "unemployment"})
    except Exception:
        return {"error": "失业率数据获取失败"}

    pmi_emp["period"] = pmi_emp["period"].astype(str).str.replace("-", "").str[:6]
    unemployment["period"] = unemployment["period"].astype(str).str.replace("-", "").str[:6]
    merged = pmi_emp.merge(unemployment, on="period", how="inner")
    if len(merged) < 12:
        return {"error": "对齐后数据不足12个月"}

    merged["emp_delta"] = merged["employment"].diff()
    merged["unemp_delta"] = merged["unemployment"].diff()
    valid = merged.dropna(subset=["emp_delta", "unemp_delta"])
    hit = (np.sign(valid["emp_delta"]) == -np.sign(valid["unemp_delta"])).mean()
    mae = abs(valid["emp_delta"] * 0.1 - valid["unemp_delta"]).mean()

    return {
        "sample_size": len(valid),
        "hit_rate": round(hit, 4),
        "mae": round(mae, 4),
        "note": "PMI从业人员上升对应失业率下降，方向一致率越高越好",
    }
