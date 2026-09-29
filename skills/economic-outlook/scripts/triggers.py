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
    """3.2 四场景动作：加仓 / 减仓 / 切换 / 观望（触发条件 + 动作量化）。"""
    p = profile or {}
    credit_up = p.get("credit_contraction") is False
    credit_down = p.get("credit_contraction") is True
    pmi_up = p.get("pmi_expanding") is True
    pmi_down = p.get("pmi_expanding") is False
    spread_low = p.get("spread_negative") is True
    global_up = p.get("_global_pmi") is not None and p["_global_pmi"] > 50
    global_down = p.get("_global_pmi") is not None and p["_global_pmi"] < 50
    # 信号冲突检测：看多与看空同时出现
    conflict = (credit_up and spread_low) or (credit_down and global_up)

    actions = {
        "加仓": {
            "triggered": False,
            "condition": "信用脉冲上行 + PMI 新订单上行",
            "action": "股票仓位 +10%（顺周期/成长）",
        },
        "减仓": {
            "triggered": False,
            "condition": "信用脉冲下行 + 中美利差低位",
            "action": "股票仓位 -10%（防御/现金）",
        },
        "切换": {
            "triggered": False,
            "condition": "全球 PMI 穿越 50",
            "action": "出口链 ↔ 防御 切换",
        },
        "观望": {
            "triggered": False,
            "condition": "信号冲突（多信号方向不一致）",
            "action": "维持仓位，等待确认",
        },
    }

    # 加仓
    if credit_up and pmi_up:
        actions["加仓"]["triggered"] = True
        actions["加仓"]["status"] = "✅ 已激活"
    else:
        actions["加仓"]["status"] = "⚪ 待触发"

    # 减仓
    if credit_down and spread_low:
        actions["减仓"]["triggered"] = True
        actions["减仓"]["status"] = "🔴 已激活"
    else:
        actions["减仓"]["status"] = "⚪ 待触发"

    # 切换
    if global_up or global_down:
        actions["切换"]["triggered"] = True
        actions["切换"]["status"] = "🔵 已激活"
        actions["切换"]["action"] = "全球PMI 上行 → 切换出口链；下行 → 切换防御" if global_up else "全球PMI 下行 → 切换防御"
    else:
        actions["切换"]["status"] = "⚪ 待触发"

    # 观望
    if conflict:
        actions["观望"]["triggered"] = True
        actions["观望"]["status"] = "⚠️ 已激活"
        actions["观望"]["detail"] = f"冲突信号: {'信用上行但利差低位' if credit_up and spread_low else '利差低位但全球PMI上行'}"
    else:
        actions["观望"]["status"] = "⚪ 未激活"

    return actions



