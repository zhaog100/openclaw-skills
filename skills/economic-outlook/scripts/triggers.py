#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.0 — 行动触发器（信号变化 → 该做什么）

把宏观信号翻译成创业/投资理财/出口贸易/政策导向 4 个场景的具体动作。
同时提供"锚点切换触发器"：关键信号一旦越线，历史类比锚点应切换。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'shared'))
sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))


# ============================================================
# 一、锚点切换触发器（关键信号越线 → 换历史锚点）
# ============================================================
ANCHOR_TRIGGERS = [
    {
        "name": "信用脉冲转正",
        "signal": "credit_impulse",
        "condition": lambda p: p.get("credit_contraction") is False,  # 信用不再收缩
        "current_anchor": "2018",
        "switch_to": "2014-2015",
        "reason": "信用扩张 + 政策托底 → 强复苏，从弱复苏锚点切到 2015 式强复苏",
        "action_hint": "进攻信号：权益加仓、创业敢加码重资产",
    },
    {
        "name": "出口跌破 0",
        "signal": "export",
        "condition": lambda p: p.get("export_weak") is True and (p.get("_export_yoy") or 0) < 0,
        "current_anchor": "2018",
        "switch_to": "2020Q2",
        "reason": "外需急跌 + 内需冻结 → 冲击型急跌，切到 2020 锚点",
        "action_hint": "防御信号：出口贸易减仓、投资出口链撤退",
    },
    {
        "name": "CPI 破 2%",
        "signal": "cpi",
        "condition": lambda p: (p.get("_cpi") or 0) > 2.0,
        "current_anchor": "2018",
        "switch_to": "2021",
        "reason": "通胀回升 + 供给约束 → 类 2021，商品/资源起来",
        "action_hint": "资源/周期品机会，警惕成本上行挤压利润",
    },
    {
        "name": "政策托底转强",
        "signal": "policy",
        "condition": lambda p: p.get("policy_support") == "aggressive",
        "current_anchor": "2018",
        "switch_to": "2014-2015",
        "reason": "政策分升到 55+（降准/财政加码落地）→ 弱复苏转强复苏",
        "action_hint": "全面进攻：科技/高端制造/基建链加码",
    },
]


def check_anchor_triggers(profile: dict) -> list:
    """检查当前画像下，哪些锚点切换触发器已激活或接近激活。"""
    active = []
    for t in ANCHOR_TRIGGERS:
        try:
            hit = bool(t["condition"](profile))
        except Exception:
            hit = False
        active.append({
            "name": t["name"],
            "signal": t["signal"],
            "triggered": hit,
            "switch_to": t["switch_to"],  # 始终显示越线后会切到的锚点
            "reason": t["reason"],
            "action_hint": t["action_hint"],
        })
    return active


# ============================================================
# 二、行动触发器清单（信号 → 4 场景动作）
# ============================================================
def build_action_checklist(profile: dict, decisions: dict = None) -> dict:
    """把当前信号翻译成创业/投资/出口/政策 4 场景的动作清单。"""
    profile = profile or {}
    credit_contraction = profile.get("credit_contraction")
    export_weak = profile.get("export_weak")
    export_yoy = profile.get("_export_yoy")
    cpi = profile.get("_cpi")
    policy_support = profile.get("policy_support")
    pmi_expanding = profile.get("pmi_expanding")

    actions = {
        "startup": [],       # 创业
        "investment": [],    # 投资理财
        "export_trade": [],  # 出口贸易
        "policy": [],        # 政策导向
    }

    # --- 信用维度 ---
    if credit_contraction is True:
        actions["startup"].append("信用收缩中：别搞重资产/长周期项目，选轻资产+快现金流（海外仓/跨境电商/售后优于建厂）")
        actions["investment"].append("信用收缩：现金/短债 > 权益，权益别追高，等信用脉冲转正再加仓")
        actions["export_trade"].append("警惕海外客户回款周期拉长，压应收账款，收紧账期")
    elif credit_contraction is False:
        actions["startup"].append("信用扩张：融资环境转暖，可考虑加码成长型项目")
        actions["investment"].append("信用扩张：权益吸引力上升，逐步加仓顺周期/成长")

    # --- 外需维度 ---
    if export_weak is False and (export_yoy or 0) >= 5:
        actions["export_trade"].append(f"出口 {export_yoy}% 韧性：汽车/锂电/光伏品类优先，资源往出海链压")
        actions["startup"].append("出海链创业确定性高：海外仓/二手车出口/配件跨境（出口 8%+ 支撑）")
        actions["investment"].append("外需韧性：出口链/科技景气，但别满仓（利差倒挂压制估值）")
    elif export_weak is True:
        actions["export_trade"].append("外需走弱：劳动密集品类（服装/鞋帽）减仓，转高附加值品类")
        actions["investment"].append("出口链减仓，转向内需/防御")

    # --- 通胀维度 ---
    if cpi is not None and cpi > 2.0:
        actions["investment"].append(f"CPI {cpi}% 超 2%：类 2021，资源/商品机会，警惕成本挤压利润")
    elif cpi is not None and cpi < 1.0:
        actions["investment"].append(f"CPI {cpi}% 低位：现金/短债实际收益好，实物资产（黄金）抗通缩")

    # --- 政策维度 ---
    if policy_support == "weak":
        actions["policy"].append("政策托底弱（33分）：别指望强刺激，按弱复苏做规划，赚结构性钱不赚总量钱")
    elif policy_support == "aggressive":
        actions["policy"].append("政策强托底（55+）：弱复苏转强复苏，科技/高端制造/基建链加码")
    else:
        actions["policy"].append("政策中等托底：关注十五五方向（科技自主/新质生产力/反内卷），资源往结构性主线放")

    # --- 制造景气 ---
    if pmi_expanding is True:
        actions["investment"].append("PMI 扩张：顺周期/制造链景气，但受利差倒挂压制，结构性参与")
    elif pmi_expanding is False:
        actions["investment"].append("PMI 收缩：防御为主，科技/出海链 > 传统周期")

    # 每场景至少一句兜底
    for k in actions:
        if not actions[k]:
            actions[k].append("暂无明确触发信号，保持当前策略，盯住 4 个关键触发器")

    return actions


# ============================================================
# 三、文本输出
# ============================================================
def format_triggers(profile: dict, decisions: dict = None) -> str:
    """生成触发器 + 行动清单的可读文本。"""
    lines = []
    lines.append("")
    lines.append("=" * 48)
    lines.append("🎯 行动触发器（信号变化 → 该做什么）")
    lines.append("=" * 48)

    # 1. 锚点切换提示
    lines.append("\n【锚点切换触发器】（关键信号越线 → 换历史锚点）")
    for t in check_anchor_triggers(profile):
        if t["triggered"]:
            lines.append(f"  🔴 已激活: {t['name']} → 锚点应切到 [{t['switch_to']}]")
            lines.append(f"     {t['reason']}")
            lines.append(f"     动作: {t['action_hint']}")
        else:
            lines.append(f"  ⚪ 待触发: {t['name']}（越线则切到 [{t['switch_to']}]）")

    # 2. 行动清单（4 场景）
    actions = build_action_checklist(profile)
    scene_cn = {"startup": "🚀 创业", "investment": "💰 投资理财",
                "export_trade": "📦 出口贸易", "policy": "📜 政策导向"}
    lines.append("\n【行动清单】（当前信号 → 4 场景动作）")
    for scene, items in actions.items():
        lines.append(f"\n{scene_cn[scene]}:")
        for it in items:
            lines.append(f"  · {it}")

    lines.append("\n⚠️ 以上为宏观信号参考，不构成投资建议/商业决策。重大决策请结合具体标的与自身风险承受力。")
    return "\n".join(lines)


def main():
    import history_analogy
    profile = history_analogy.build_current_profile()
    print(format_triggers(profile))


if __name__ == "__main__":
    main()
