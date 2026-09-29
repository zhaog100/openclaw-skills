#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.0 — 周报固定格式（3.5）

按 官家 给定模板输出：
【宏观周报】YYYY-MM-DD
├── 状态向量: GDP/CPI/M1/...
├── 信号层: 8 信号方向+强度
├── 历史类比: 当前最像哪段（锚点 id + 特征）
├── 触发器: 加仓/减仓/切换/观望
├── 决策出口: 6 出口评分
└── 风险提示: 冲突信号

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "shared"))
sys.path.insert(0, os.path.join(BASE_DIR, "signals"))
sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))


def generate_weekly() -> str:
    """生成 3.5 固定格式周报。"""
    from signals.aggregator import SignalAggregator
    from signals.comprehensive_output import generate_comprehensive_report
    import history_analogy
    import triggers

    agg = SignalAggregator()
    rep = generate_comprehensive_report(agg)
    profile = history_analogy.build_current_profile()
    analogy = history_analogy.analyze(profile)
    actions = triggers.build_action_checklist(profile)
    signals = rep["signals"]
    outcomes = rep["outcomes"]

    # 状态向量（从画像取关键指标）
    cpi = profile.get("_cpi", "N/A")
    pmi = profile.get("_pmi", "N/A")
    credit = profile.get("_credit_impulse", "N/A")
    spread = profile.get("_spread_10y", "N/A")
    export = profile.get("_export_yoy", "N/A")
    policy = profile.get("_policy_score", "N/A")
    state_vec = f"GDP 4.6 | CPI {cpi}% | M1 4.0 | PMI {pmi} | 出口 {export}% | 利差 {spread}% | 信用脉冲 {credit}"

    # 信号层（8 个方向 + 强度）
    sig_lines = []
    for k, v in signals.items():
        sig_lines.append(f"  {v['name']}: {v['summary']}")
    sig_block = "\n".join(sig_lines)

    # 历史类比
    bm = analogy["best_match"]
    sm = analogy.get("second_match") or {}
    analogy_line = f"当前最像 [{bm['anchor']}]（{bm['match_rate']:.0%} 匹配）→ {bm['outcome']}"
    if sm.get("anchor"):
        analogy_line += f"\n  次相似: [{sm['anchor']}]（{sm['match_rate']:.0%}）"

    # 触发器（4 场景）
    trig_lines = []
    for k in ["加仓", "减仓", "切换", "观望"]:
        a = actions.get(k, {})
        trig_lines.append(f"  {a.get('status', '?')} {k}: {a.get('condition', '')} → {a.get('action', '')}")
    trig_block = "\n".join(trig_lines)

    # 决策出口（6 出口评分）
    out_lines = []
    for k in ["stock", "fund", "startup", "employment", "commodity", "overseas"]:
        o = outcomes.get(k, {})
        out_lines.append(f"  {k}: {o.get('score', 0):+.2f} ({o.get('direction', 'N/A')})")
    out_block = "\n".join(out_lines)

    # 风险提示（冲突信号）
    conflicts = []
    for k, o in outcomes.items():
        conflicts.extend(o.get("conflicts", []))
    risk_block = "\n".join(f"  ⚠️ {c}" for c in conflicts) if conflicts else "  无显著冲突"

    text = f"""【宏观周报】{datetime.now().strftime('%Y-%m-%d')}
├── 状态向量: {state_vec}
├── 信号层:
{sig_block}
├── 历史类比: {analogy_line}
├── 触发器:
{trig_block}
├── 决策出口:
{out_block}
└── 风险提示:
{risk_block}

⚠️ 宏观信号参考，不构成投资建议/商业决策。
"""
    return text


def main():
    print(generate_weekly())


if __name__ == "__main__":
    main()
