#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 决策出口统一报告（6 出口整合文本）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from datetime import datetime
from signals.aggregator import SignalAggregator
from outcomes.stock import map_stock
from outcomes.fund import map_fund
from outcomes.startup import map_startup
from outcomes.employment import map_employment
from outcomes.commodity import map_commodity
from outcomes.overseas import map_overseas


def generate_outcome_report(agg: SignalAggregator = None) -> dict:
    """生成 6 出口完整决策报告。"""
    if agg is None:
        agg = SignalAggregator()
    agg.collect_all()

    reports = {
        "stock": map_stock(agg),
        "fund": map_fund(agg),
        "startup": map_startup(agg),
        "employment": map_employment(agg),
        "commodity": map_commodity(agg),
        "overseas": map_overseas(agg),
    }

    # 整合文本
    text = f"📈 决策出口报告（{datetime.now().strftime('%Y-%m-%d')}）\n{'='*40}\n"
    for key, title in [
        ("stock", "股票/行业"), ("fund", "基金"), ("startup", "创业"),
        ("employment", "就业"), ("commodity", "大宗"), ("overseas", "海外配置"),
    ]:
        r = reports[key]
        text += f"\n【{title}】{r['recommendation']}\n"
        text += _detail_line(key, r)

    return {"date": datetime.now().strftime("%Y-%m-%d"), "outcomes": reports, "text": text}


def _detail_line(key: str, r: dict) -> str:
    """按出口类型输出细节行。"""
    lines = []
    if key == "stock":
        if r.get("overweight"):
            lines.append(f"  超配: {', '.join(r['overweight'])}")
        if r.get("underweight"):
            lines.append(f"  低配: {', '.join(r['underweight'])}")
        lines.append(f"  周期位置: {r['cycle_position']} / 风格: {r['style']}")
    elif key == "fund":
        lines.append(f"  权益倾向: {r['equity_bias']}")
        if r.get("etf_rotation"):
            lines.append(f"  ETF轮动参考: {', '.join(r['etf_rotation'])}")
    elif key == "startup":
        if r.get("hot_directions"):
            lines.append(f"  热点方向: {', '.join(r['hot_directions'])}")
    elif key == "employment":
        lines.append(f"  行业: {', '.join(r['hot_industries'])}")
        lines.append(f"  城市: {', '.join(r['hot_cities'])}")
        lines.append(f"  技能: {', '.join(r['hot_skills'])}")
    elif key == "commodity":
        lines.append(f"  需求方向: {r['demand']} / 品种: {', '.join(r['items'])}")
    elif key == "overseas":
        alloc = r.get("allocation", {})
        lines.append("  配置: " + " | ".join(f"{k}{v}" for k, v in alloc.items()))
    lines.append(f"  {r['disclaimer']}")
    return "\n".join(lines)
