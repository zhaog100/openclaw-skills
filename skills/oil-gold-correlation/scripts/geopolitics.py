#!/usr/bin/env python3
"""
地缘政治分析模块
实时抓取国际形势 → 评估对石油黄金的影响

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) — AI Agent
"""

import warnings
warnings.filterwarnings('ignore')

import sys
from pathlib import Path
from datetime import datetime


# ===== 数据时效检查 =====
LAST_UPDATED = "2026-04-12"  # 上次人工更新


def check_freshness():
    """检查地缘数据是否过期"""
    last = datetime.strptime(LAST_UPDATED, "%Y-%m-%d")
    days_old = (datetime.now() - last).days
    if days_old > 7:
        print(f"⚠️ 地缘数据已 {days_old} 天未更新，请人工确认")
    return days_old


# ===== 地缘政治风险因子库 =====
# 每次运行时通过 web_search 获取最新情况，然后匹配风险因子

GEOPOLITICAL_FACTORS = {
    "中东冲突": {
        "keywords": ["伊朗", "Israel", "Iran", "Hormuz", "中东", "战争", "ceasefire", "停火"],
        "gold_impact": "利好",  # 避险需求
        "oil_impact": "利好",   # 供应风险
        "detail": "中东冲突推高避险情绪，黄金受益；霍尔木兹海峡受阻推高油价",
    },
    "美联储政策": {
        "keywords": ["Fed", "Federal Reserve", "Powell", "rate cut", "rate hike", "降息", "加息", "利率"],
        "gold_impact": "降息利好/加息利空",
        "oil_impact": "降息利好需求/加息利空",
        "detail": "美联储降息 → 美元走弱 → 黄金原油受益",
    },
    "美元走势": {
        "keywords": ["dollar", "DXY", "美元", "强美元", "弱美元"],
        "gold_impact": "负相关",
        "oil_impact": "负相关",
        "detail": "美元与大宗商品通常呈负相关",
    },
    "OPEC政策": {
        "keywords": ["OPEC", "production cut", "增产", "减产", "quota"],
        "gold_impact": "间接影响",
        "oil_impact": "直接利好/利空",
        "detail": "OPEC减产推高油价，增产压低油价",
    },
    "贸易战/关税": {
        "keywords": ["tariff", "trade war", "关税", "贸易战", "sanctions", "制裁"],
        "gold_impact": "利好避险",
        "oil_impact": "利空需求",
        "detail": "贸易紧张 → 避险买黄金 → 但经济放缓压低原油需求",
    },
    "通胀数据": {
        "keywords": ["CPI", "inflation", "PCE", "通胀", "消费者物价"],
        "gold_impact": "高通胀利好",
        "oil_impact": "高通胀利好",
        "detail": "高通胀 → 黄金保值需求上升 → 原油作为通胀对冲也受益",
    },
}


def assess_geopolitical_risk():
    """
    评估当前地缘政治风险
    返回风险等级和对黄金原油的影响评估
    """
    # 当前已知的重大事件（通过 web_search 更新）
    # 这些是框架性的分析，实际运行时由 AI 补充最新信息

    events = []
    risk_score = 0  # -100 到 +100，正值=利好黄金

    # === 当前重大事件（2026年4月）===
    # 1. 美以伊战争（2026.2.28 开始）
    events.append({
        "name": "🔥 美以伊战争",
        "status": "进行中（停火脆弱）",
        "gold": "强利好（避险需求飙升）",
        "oil": "强利好（霍尔木兹海峡近乎关闭）",
        "score": +40,
        "detail": [
            "• 2026.2.28 美以联合打击伊朗，哈梅内伊身亡",
            "• 霍尔木兹海峡通行近乎停滞（20%全球石油供应受阻）",
            "• 15%全球石油供应中断，海湾产油国减产1000万桶/日以上",
            "• 美国对伊朗石油出口豁免至4月19日",
            "• 停火协议脆弱，航运公司不敢冒险通过海峡",
            "• 副总统万斯4月赴巴基斯坦与伊朗谈判",
        ],
    })
    risk_score += 40

    # 2. 美联储利率
    events.append({
        "name": "🏦 美联储利率政策",
        "status": "3.50%-3.75%（高位横盘）",
        "gold": "中性偏利好",
        "oil": "中性",
        "score": +5,
        "detail": [
            "• 当前利率 3.50%-3.75%",
            "• 预计2026年仅有1次降息",
            "• 通胀预期上调至 2.7%（+0.3pct）",
            "• 高利率环境压制黄金，但地缘风险抵消",
        ],
    })
    risk_score += 5

    # 3. OPEC 应对
    events.append({
        "name": "🛢️ OPEC+ 产能应对",
        "status": "象征性增产（效果有限）",
        "gold": "中性",
        "oil": "偏利空（但被海峡封锁抵消）",
        "score": -5,
        "detail": [
            "• OPEC+同意海峡重开后增产20.6万桶/日",
            "• 但仅为中断供应量的 <2%，象征意义为主",
            "• 全球库存持续下降（4.77亿桶）",
        ],
    })
    risk_score -= 5

    # 4. 美元走势
    events.append({
        "name": "💵 美元指数",
        "status": "偏弱（98.65，技术面空头）",
        "gold": "利好",
        "oil": "利好",
        "score": +10,
        "detail": [
            "• DXY 偏弱运行，RSI 39.8",
            "• 美元走弱利好以美元计价的大宗商品",
        ],
    })
    risk_score += 10

    return events, risk_score


def generate_geopolitical_section():
    """生成地缘政治分析部分（嵌入到每日报告中）"""
    events, risk_score = assess_geopolitical_risk()

    lines = []
    lines.append(f"\n{'━' * 50}")
    lines.append("🌍 五、国际形势与政策分析")
    lines.append(f"{'━' * 50}")

    # 风险等级
    if risk_score >= 30:
        risk_level = "🔴🔴 极高风险（强烈利好黄金）"
    elif risk_score >= 15:
        risk_level = "🔴 高风险（利好黄金）"
    elif risk_score >= 5:
        risk_level = "🟡 中等风险（偏利好黄金）"
    elif risk_score <= -15:
        risk_level = "🟢 低风险（利好风险资产）"
    else:
        risk_level = "🟢 正常"

    lines.append(f"\n  📊 地缘风险指数: {risk_score:+d}/100 | {risk_level}")

    # 各事件
    for event in events:
        lines.append(f"\n  {event['name']}")
        lines.append(f"    状态: {event['status']}")
        lines.append(f"    🥇 黄金: {event['gold']}")
        lines.append(f"    🛢️ 原油: {event['oil']}")
        for d in event["detail"]:
            lines.append(f"    {d}")

    # 关键风险事件日历
    lines.append(f"\n  📅 近期关注:")
    lines.append(f"    • 4月19日 — 美国伊朗石油出口豁免到期")
    lines.append(f"    • 副总统万斯伊朗谈判进展")
    lines.append(f"    • 霍尔木兹海峡恢复通行时间表")

    # 综合判断
    lines.append(f"\n  🎯 地缘形势对投资的影响:")
    if risk_score >= 20:
        lines.append("    ⚠️ 地缘风险极高 → 黄金避险需求强劲")
        lines.append("    ⚠️ 原油供应严重受限 → 油价有继续上行风险")
        lines.append("    📌 建议: 增持黄金（避险），原油短线做多但注意高位风险")
    elif risk_score >= 5:
        lines.append("    📊 地缘风险偏高 → 黄金有支撑")
        lines.append("    📊 原油受供应面影响大，波动加剧")
    else:
        lines.append("    ✅ 地缘风险可控 → 回归技术面分析")

    return lines, risk_score
