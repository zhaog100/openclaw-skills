#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — 周报固定格式（3.5）

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


def generate_weekly_report() -> str:
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

    # 状态向量（文档 D.2：GDP/CPI 双年对比 + 8Q 情景）
    state_vec = ""
    try:
        from core.state_vector import build_state_vector
        sv = build_state_vector()
        gdp = sv.get("gdp", sv.get("dimensions", {}).get("gdp", {}))
        state_vec = f"综合评分 {sv.get('total_score', 'N/A')}/100 | 8季度预测 Q1-Q8 | horizon 8Q"
    except Exception:
        state_vec = f"CPI {profile.get('_cpi', 'N/A')}% | PMI {profile.get('_pmi', 'N/A')} | 出口 {profile.get('_export_yoy', 'N/A')}% | 利差 {profile.get('_spread_10y', 'N/A')}% | 信用脉冲 {profile.get('_credit_impulse', 'N/A')}"

    # 信号层（8 个方向 + 强度）
    sig_lines = []
    for k, v in signals.items():
        sig_lines.append(f"  {v['name']}: {v['summary']}")
    sig_block = "\n".join(sig_lines)

    # 历史类比（新引擎：A-E 锚点 + 余弦相似度 + 后续资产）
    raw = analogy.get("raw", {})
    bm = raw.get("best_match", analogy["best_match"])
    sm = (raw.get("all_matches", [])[1]) if len(raw.get("all_matches", [])) > 1 else None
    ret = bm.get("subsequent_returns", {})
    analogy_line = f"当前最像 锚点{bm.get('code', bm.get('anchor', '?'))}（相似度 {bm.get('similarity', bm.get('match_rate', 0)):.0%}，历史区间 {bm.get('historical_period', '?')}）"
    analogy_line += f"\n  后续参考: 周期{ret.get('stock_cyclical', 0):+.1%} 防御{ret.get('stock_defensive', 0):+.1%} 债券{ret.get('bond', 0):+.1%} 大宗{ret.get('commodity', 0):+.1%} 人民币{ret.get('rmb', 0):+.1%}"
    if sm:
        analogy_line += f"\n  次相似: 锚点{sm.get('code', '?')}（{sm.get('similarity', 0):.0%}）"

    # 触发器（4 场景，仓位量化）
    trig_lines = []
    for k in ["加仓", "减仓", "切换", "观望"]:
        a = actions.get(k, {})
        trig_lines.append(f"  {a.get('status', '?')} {k}: {a.get('condition', '')} → {a.get('action', '')}（仓位 {a.get('position_change', 0):+d}% → {a.get('target_position', 60):.0f}%）")
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

    # 今日重大政策事件（多源实时采集）
    policy_block = ""
    try:
        import policy_updater
        rt = policy_updater.collect_realtime_policy()
        evs = rt.get("events", [])
        if evs:
            top = [e for e in evs if e.get("confidence") == "high"] or evs
            lines = []
            for e in top[:8]:
                conf = "多源✓" if e.get("confidence") == "high" else "单源"
                lines.append(f"  · {e.get('title','')[:40]}（{e.get('source','?')}，{conf}）")
            policy_block = ("\n├── 今日重大政策事件（多源实时）:\n" + "\n".join(lines)
                           + f"\n  覆盖 {rt.get('coverage','?')}")
    except Exception:
        policy_block = "\n├── 今日重大政策事件: 多源采集不可用（跳过）"

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
{policy_block}

⚠️ 宏观信号参考，不构成投资建议/商业决策。
"""
    return text


def main():
    print(generate_weekly_report())


if __name__ == "__main__":
    main()
