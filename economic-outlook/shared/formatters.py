#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 输出格式化（映射结果转纯文本）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
"""输出格式化（FR-07/FR-09）：把映射结果转纯文本"""


def stock_report(r):
    L = ["📈 股票/行业参考（合规：不推个股、不给买卖点）"]
    L.append(f"  周期位置: {r['cycle_position']}")
    L.append(f"  风格: {r['style']}")
    L.append("  景气行业:")
    L += [f"    · {s}" for s in r['hot_sectors']]
    L.append("  弱势板块:")
    L += [f"    · {s}" for s in r['cold_sectors']]
    L.append("  风险提示:")
    L += [f"    ⚠️ {x}" for x in r['risk']]
    L.append(f"  {r['disclaimer']}")
    return "\n".join(L)


def fund_report(r):
    L = ["💰 基金/资产配置参考（合规：不推具体基金）"]
    L.append(f"  股债: {r['equity_vs_bond']}")
    L.append(f"  风格: {r['style']}")
    L.append(f"  信用: {r['credit_spread']}")
    L.append(f"  {r['disclaimer']}")
    return "\n".join(L)


def startup_report(r):
    L = ["🚀 创业机会参考（合规：不承诺成功）"]
    L.append("  行业机会评分:")
    L += [f"    {i+1}. {name} {sc}" for i, (name, sc) in enumerate(r['industry_opportunity'])]
    L.append(f"  融资环境: {r['funding_env']}")
    L.append(f"  时机: {r['timing']}")
    L.append(f"  {r['disclaimer']}")
    return "\n".join(L)


def employment_report(r):
    L = ["👥 就业参考（合规：不承诺薪资/录用）"]
    L.append("  行业热度排名:")
    L += [f"    {i+1}. {name} {sc}" for i, (name, sc) in enumerate(r['industry_heat'])]
    L.append("  城市机会密度:")
    L += [f"    {n} {s}" for n, s in r['city_ranking']]
    L.append("  技能方向: " + " / ".join(r['skill_directions'][:5]))
    L.append(f"  {r['disclaimer']}")
    return "\n".join(L)


FORMATTERS = {'stock': stock_report, 'fund': fund_report,
              'startup': startup_report, 'employment': employment_report}
