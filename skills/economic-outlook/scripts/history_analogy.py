#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.0 — 历史类比分析

当前经济画像 → 匹配历史上最相似的环境 → 历史上同状态后来怎么走 → 走向判断。
方法论：情景+信号的历史胜率交叉验证（不是精确预测，是"找相似情景的历史路径"）。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys, json, logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'shared'))
sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))

# ============================================================
# 一、历史锚点库（人工整理，每个锚点含特征画像 + 后续走向 + 结构启示）
# ============================================================
HISTORY_ANCHORS = [
    # ===== 3.1 五个锚点定义（信号组合 → 历史区间 → 走向）=====
    {
        "id": "A",
        "name": "信用扩张 + 外需改善",
        "label": "信用脉冲上行 + 全球PMI>50",
        "anchor_period": "2016Q1 / 2019Q1",
        "features": {
            "cpi_low": True, "credit_contraction": False, "spread_negative": False,
            "pmi_expanding": True, "export_weak": False, "policy_support": "moderate",
        },
        "outcome": "强复苏（信用+外需双驱动）",
        "path": "信用扩张叠加外需改善，总量+结构齐升，权益上行、周期盈利回暖",
        "structure": {
            "overweight": ["周期", "金融", "出口链", "高端制造"],
            "underweight": ["防御", "债券"],
        },
    },
    {
        "id": "B",
        "name": "信用收缩 + 外需走弱",
        "label": "信用脉冲下行 + 全球PMI<50",
        "anchor_period": "2018 / 2022",
        "features": {
            "cpi_low": True, "credit_contraction": True, "spread_negative": True,
            "pmi_expanding": False, "export_weak": True, "policy_support": "moderate",
        },
        "outcome": "弱复苏 + 结构分化",
        "path": "总量承压，科技/出海链扛旗，地产/传统消费偏弱，靠政策托底企稳",
        "structure": {
            "overweight": ["科技", "出海链", "半导体"],
            "underweight": ["地产链", "传统消费", "劳动密集出口"],
        },
    },
    {
        "id": "C",
        "name": "信用扩张 + 内需疲弱",
        "label": "信用脉冲上行 + 社零<均值",
        "anchor_period": "2014-2015",
        "features": {
            "cpi_low": True, "credit_contraction": False, "spread_negative": False,
            "pmi_expanding": True, "export_weak": False, "policy_support": "aggressive",
        },
        "outcome": "信用驱动强复苏（PPI 转正、盈利上行）",
        "path": "货币宽松+棚改货币化，社零虽弱但信用扩张带动工业利润、权益上行",
        "structure": {
            "overweight": ["周期", "金融", "基建", "地产链"],
            "underweight": ["防御", "债券"],
        },
    },
    {
        "id": "D",
        "name": "政策强刺激",
        "label": "专项债 + 特别国债超额落地",
        "anchor_period": "2020Q2 / 2023",
        "features": {
            "cpi_low": True, "credit_contraction": False, "spread_negative": False,
            "pmi_expanding": True, "export_weak": False, "policy_support": "aggressive",
        },
        "outcome": "政策托底强复苏（V 型反转）",
        "path": "财政+货币双发力，专项债/特别国债落地，经济急跌后 V 型反转",
        "structure": {
            "overweight": ["科技", "新能源", "基建链", "消费(服务)"],
            "underweight": ["传统制造", "地产链(后段)"],
        },
    },
    {
        "id": "E",
        "name": "外部冲击",
        "label": "VIX>30 或 中美利差极端倒挂",
        "anchor_period": "2020Q2(冲击) / 2025",
        "features": {
            "cpi_low": True, "credit_contraction": True, "spread_negative": True,
            "pmi_expanding": False, "export_weak": True, "policy_support": "aggressive",
        },
        "outcome": "冲击型急跌 + 强对冲（避险+科技双主线）",
        "path": "外部冲击 + 利差极端，短期急跌，避险(黄金)与科技出海双主线，后段强刺激托底",
        "structure": {
            "overweight": ["黄金", "科技", "出海链", "防御(黄金/短债)"],
            "underweight": ["传统周期", "地产链", "外需依赖"],
        },
    },
]


# ============================================================
# 二、当前经济画像（从各信号/数据层自动提取，能拿真数据就真拿，拿不到用占位）
# ============================================================
def build_current_profile() -> dict:
    """构建当前经济画像（特征布尔值），数据源拉不到时如实标注。"""
    import akshare as ak
    from shared import cache

    profile = {
        "cpi_low": None,
        "credit_contraction": None,
        "spread_negative": None,
        "pmi_expanding": None,
        "export_weak": None,
        "policy_support": "unknown",
        "_data_gaps": [],
    }

    # CPI（macro_china_cpi 列：月份/本月值/同比/环比，索引列需取真实同比，排除“指数”值列）
    try:
        cpi = ak.macro_china_cpi()
        cpi_cols = list(cpi.columns)
        yoy_col = next((c for c in cpi_cols if "同比" in c and "指" not in c), None)
        if yoy_col is not None:
            latest_cpi = float(cpi.iloc[0][yoy_col])
        else:
            # 退而求其次：取第二列（通常是本月同比）
            latest_cpi = float(cpi.iloc[0].iloc[1])
        profile["cpi_low"] = latest_cpi < 1.5
        profile["_cpi"] = latest_cpi
    except Exception:
        profile["_data_gaps"].append("CPI")

    # 信用脉冲（收缩 = 真数据）
    try:
        from signals.credit_impulse import CreditImpulseCalculator
        sig = CreditImpulseCalculator().compute()
        profile["credit_contraction"] = sig.direction == "bearish_cyclical" or sig.impulse < 0
        profile["_credit_impulse"] = sig.impulse
    except Exception:
        profile["_data_gaps"].append("信用脉冲")

    # 中美利差（倒挂）
    try:
        from signals.china_us_spread import ChinaUSSpreadCalculator
        sig = ChinaUSSpreadCalculator().compute()
        profile["spread_negative"] = sig.spread_10y < 0
        profile["_spread_10y"] = sig.spread_10y
    except Exception:
        profile["_data_gaps"].append("中美利差")

    # PMI 扩张
    try:
        pmi_df = ak.macro_china_pmi()
        col = [c for c in pmi_df.columns if "制造业" in c and "指数" in c]
        if col:
            # macro_china_pmi 返回倒序（最新在前），取第一行最新
            latest_pmi = float(pmi_df.iloc[0][col[0]])
            profile["pmi_expanding"] = latest_pmi > 50
            profile["_pmi"] = latest_pmi
        else:
            profile["_data_gaps"].append("PMI")
    except Exception:
        profile["_data_gaps"].append("PMI")

    # 外需（出口同比）
    try:
        exp = ak.macro_china_exports_yoy()
        latest_exp = float(exp.iloc[0]["今值"]) if "今值" in exp.columns else None
        if latest_exp is not None:
            profile["export_weak"] = latest_exp < 3.0
            profile["_export_yoy"] = latest_exp
        else:
            profile["_data_gaps"].append("出口")
    except Exception:
        profile["_data_gaps"].append("出口")

    # 政策（本地静态，总能拿到）
    try:
        import policy_engine
        p = policy_engine.analyze_policy()
        # 政策分 > 50 视为积极托底
        profile["policy_support"] = "aggressive" if p["score"] >= 55 else ("moderate" if p["score"] >= 40 else "weak")
        profile["_policy_score"] = p["score"]
    except Exception:
        profile["_data_gaps"].append("政策")

    return profile


def _feat_match(a: bool, b: bool) -> int:
    """两个特征是否一致（None 视为中性不计分）"""
    if a is None or b is None:
        return 0
    return 1 if a == b else -1


# ============================================================
# 三、历史类比：匹配度打分 + 走向输出
# ============================================================
def analyze(profile: dict = None) -> dict:
    """当前画像 → 匹配历史锚点 → 输出走向判断。"""
    if profile is None:
        profile = build_current_profile()

    scored = []
    for anchor in HISTORY_ANCHORS:
        score = 0
        f = anchor["features"]
        # 6 个特征逐一比对
        score += _feat_match(profile.get("cpi_low"), f.get("cpi_low"))
        score += _feat_match(profile.get("credit_contraction"), f.get("credit_contraction"))
        score += _feat_match(profile.get("spread_negative"), f.get("spread_negative"))
        score += _feat_match(profile.get("pmi_expanding"), f.get("pmi_expanding"))
        score += _feat_match(profile.get("export_weak"), f.get("export_weak"))
        # 政策支持度（字符串三档）
        if profile.get("policy_support") == f.get("policy_support"):
            score += 1
        scored.append({"anchor": anchor, "score": score, "match_rate": round((score + 6) / 12, 2)})

    scored.sort(key=lambda x: x["match_rate"], reverse=True)
    top = scored[0]
    runner = scored[1] if len(scored) > 1 else None

    result = {
        "current_profile": profile,
        "best_match": {
            "anchor": top["anchor"]["name"],
            "match_rate": top["match_rate"],
            "outcome": top["anchor"]["outcome"],
            "path": top["anchor"]["path"],
            "structure": top["anchor"]["structure"],
        },
        "second_match": {
            "anchor": runner["anchor"]["name"] if runner else None,
            "match_rate": runner["match_rate"] if runner else None,
            "outcome": runner["anchor"]["outcome"] if runner else None,
        } if runner else None,
        "data_gaps": profile.get("_data_gaps", []),
        "caveat": "历史类比是'找相似情景的历史胜率'，不是精确预测；最大变量是政策力度与外需走向。",
    }
    return result


# ============================================================
# 四、文本输出
# ============================================================
def format_report(res: dict) -> str:
    """生成可读的历史类比报告。"""
    p = res["current_profile"]
    bm = res["best_match"]
    sm = res["second_match"]
    lines = []
    lines.append("=" * 48)
    lines.append("🕰️  历史类比分析（当前经济画像 → 历史上最像哪一年）")
    lines.append("=" * 48)

    lines.append("\n【当前画像】")
    lines.append(f"  CPI低位: {'是' if p.get('cpi_low') else '否' if p.get('cpi_low') is False else '未知'}"
                 + (f"（{p['_cpi']}%）" if p.get('_cpi') is not None else ""))
    lines.append(f"  信用收缩: {'是' if p.get('credit_contraction') else '否' if p.get('credit_contraction') is False else '未知'}"
                 + (f"（脉冲 {p['_credit_impulse']}）" if p.get('_credit_impulse') is not None else ""))
    lines.append(f"  利差倒挂: {'是' if p.get('spread_negative') else '否' if p.get('spread_negative') is False else '未知'}"
                 + (f"（10Y {p['_spread_10y']}%）" if p.get('_spread_10y') is not None else ""))
    lines.append(f"  制造扩张: {'是' if p.get('pmi_expanding') else '否' if p.get('pmi_expanding') is False else '未知'}"
                 + (f"（PMI {p['_pmi']}）" if p.get('_pmi') is not None else ""))
    lines.append(f"  外需偏弱: {'是' if p.get('export_weak') else '否' if p.get('export_weak') is False else '未知'}"
                 + (f"（出口 {p['_export_yoy']}%）" if p.get('_export_yoy') is not None else ""))
    lines.append(f"  政策托底: {p.get('policy_support', '未知')}"
                 + (f"（{p['_policy_score']}分）" if p.get('_policy_score') is not None else ""))

    lines.append("\n【最相似历史环境】")
    lines.append(f"  ★ {bm['anchor']}: 匹配度 {bm['match_rate']:.0%}")
    lines.append(f"  当时走向: {bm['outcome']}")
    lines.append(f"  历史路径: {bm['path']}")
    lines.append(f"  结构启示: 超配 {', '.join(bm['structure']['overweight'])} | 回避 {', '.join(bm['structure']['underweight'])}")

    if sm and sm.get("anchor"):
        lines.append(f"\n  次相似: {sm['anchor']}（{sm['match_rate']:.0%}）→ {sm.get('outcome', '')}")

    if res["data_gaps"]:
        lines.append(f"\n⚠️ 数据缺口（这些维度没拿到，匹配度打折）: {', '.join(res['data_gaps'])}")

    lines.append(f"\n{res['caveat']}")
    return "\n".join(lines)


def main():
    res = analyze()
    print(format_report(res))


if __name__ == "__main__":
    main()
