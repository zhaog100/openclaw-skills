#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.0 — 行动触发器（B: 4 场景动作完整实现）

核心逻辑：
- 根据当前信号组合，判断触发哪个场景（加仓/减仓/切换/观望）
- 每个场景对应具体动作（仓位变化 %）+ 优先级 + 有效期
- 输出可执行的决策指令

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'shared'))
sys.path.insert(0, os.path.join(BASE_DIR, 'signals'))


@dataclass
class TriggerResult:
    """触发器结果。"""
    scenario: str          # add / reduce / switch / wait
    scenario_cn: str      # 加仓 / 减仓 / 切换 / 观望
    triggered: bool
    conditions: list
    action: str
    position_change: float
    target_position: float
    priority: int
    valid_until: str
    notes: list = field(default_factory=list)


class TriggerEngine:
    """行动触发器引擎（文档 B）。"""

    SCENARIOS = {
        "add": {
            "name": "加仓",
            "conditions": [("credit_impulse", "bullish_cyclical"), ("pmi_orders", "bullish_cyclical")],
            "logic": "AND",
            "action": "股票仓位 +10%（顺周期/成长）",
            "position_change": +10,
            "priority": 1,
        },
        "reduce": {
            "name": "减仓",
            "conditions": [("credit_impulse", "bearish_cyclical"), ("china_us_spread", "low")],
            "logic": "AND",
            "action": "股票仓位 -10%（防御/现金）",
            "position_change": -10,
            "priority": 1,
        },
        "switch": {
            "name": "切换",
            "conditions": [("global_pmi", "cross_50")],
            "logic": "SINGLE",
            "action": "出口链 ↔ 防御板块切换",
            "position_change": 0,
            "priority": 2,
        },
        "wait": {
            "name": "观望",
            "conditions": [("conflict", "any")],
            "logic": "ANY",
            "action": "维持仓位，等待确认",
            "position_change": 0,
            "priority": 3,
        },
    }

    def __init__(self, base_position: float = 60.0):
        self.base_position = base_position
        self.current_position = base_position

    def _check_condition(self, sig_name: str, expected: str, signals: dict) -> bool:
        """检查单个信号条件是否满足。"""
        if expected == "any":
            # 冲突检测：是否存在方向不一致的信号对
            dirs = {}
            for k, s in signals.items():
                if s:
                    dirs[k] = s.direction
            from signals.aggregator import DIRECTION_SCORE
            vals = [DIRECTION_SCORE.get(d, 0) for d in dirs.values()]
            return any(v > 0 for v in vals) and any(v < 0 for v in vals)
        if sig_name == "global_pmi" and expected == "cross_50":
            s = signals.get("global_pmi")
            if s and "global_pmi" in s.detail:
                return s.detail["global_pmi"] != 50  # 穿越50（非中性区）
            return False
        s = signals.get(sig_name)
        return s is not None and s.direction == expected

    def evaluate(self, signals: dict = None) -> list:
        """评估所有场景，返回 TriggerResult 列表（按优先级排序）。"""
        if signals is None:
            from signals.aggregator import SignalAggregator
            signals = SignalAggregator().collect_all()

        results = []
        valid_until = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        for key, sc in self.SCENARIOS.items():
            cond_desc = []
            all_met = True
            for sig_name, expected in sc["conditions"]:
                met = self._check_condition(sig_name, expected, signals)
                cond_desc.append(f"{sig_name}={expected} → {'✓' if met else '✗'}")
                if not met:
                    all_met = False

            triggered = all_met if sc["logic"] in ("AND", "SINGLE") else any(
                self._check_condition(s, e, signals) for s, e in sc["conditions"])

            results.append(TriggerResult(
                scenario=key,
                scenario_cn=sc["name"],
                triggered=triggered,
                conditions=cond_desc,
                action=sc["action"],
                position_change=sc["position_change"],
                target_position=self.base_position + sc["position_change"] if triggered else self.base_position,
                priority=sc["priority"],
                valid_until=valid_until,
                notes=[sc["logic"]],
            ))

        results.sort(key=lambda r: r.priority)
        return results


# ============ 兼容旧接口（check_anchor_triggers / build_action_checklist / format_triggers）============
ANCHOR_TRIGGERS = [
    {"name": "信用脉冲转正", "switch_to": "A", "hint": "切到信用扩张锚点"},
    {"name": "出口跌破 0", "switch_to": "E", "hint": "切到外部冲击锚点"},
    {"name": "CPI 破 2%", "switch_to": "A", "hint": "切到通胀回升锚点"},
    {"name": "政策托底转强", "switch_to": "D", "hint": "切到政策强刺激锚点"},
]


def check_anchor_triggers(profile: dict) -> list:
    """检查锚点切换触发器（兼容旧接口）。"""
    out = []
    for t in ANCHOR_TRIGGERS:
        out.append({"name": t["name"], "triggered": False, "switch_to": t["switch_to"],
                    "hint": t["hint"]})
    return out


def build_action_checklist(profile: dict, decisions: dict = None) -> dict:
    """兼容旧接口：返回 4 场景 dict（内部调 TriggerEngine）。"""
    eng = TriggerEngine()
    from signals.aggregator import SignalAggregator
    signals = SignalAggregator().collect_all()
    results = eng.evaluate(signals)
    scene_key = {"加仓": "add", "减仓": "reduce", "切换": "switch", "观望": "wait"}
    out = {}
    for cn, key in scene_key.items():
        r = next(x for x in results if x.scenario == key)
        out[cn] = {
            "triggered": r.triggered,
            "status": ("✅ 已激活" if r.triggered else "⚪ 待触发"),
            "condition": " + ".join(c.split(" →")[0] for c in r.conditions),
            "action": r.action,
            "position_change": r.position_change,
            "target_position": r.target_position,
        }
    return out


def format_triggers(profile: dict, decisions: dict = None) -> str:
    """兼容旧接口：格式化输出。"""
    eng = TriggerEngine()
    results = eng.evaluate()
    lines = []
    lines.append("")
    lines.append("=" * 48)
    lines.append("🎯 行动触发器（信号变化 → 该做什么）")
    lines.append("=" * 48)
    lines.append(f"基础仓位: {eng.base_position:.0f}%")
    for r in results:
        icon = "✅" if r.triggered else "⚪"
        lines.append(f"\n{icon} [{r.priority}] {r.scenario_cn}（优先级 {r.priority}）")
        lines.append(f"  条件: {' + '.join(c.split(' →')[0] for c in r.conditions)}")
        for c in r.conditions:
            lines.append(f"    · {c}")
        lines.append(f"  动作: {r.action}")
        lines.append(f"  仓位变化: {r.position_change:+d}% → 目标 {r.target_position:.0f}%")
        lines.append(f"  有效期: {r.valid_until}")
    lines.append("\n⚠️ 以上为宏观信号参考，不构成投资建议/商业决策。重大决策请结合具体标的与自身风险承受力。")
    return "\n".join(lines)


def main():
    print(format_triggers({}))


if __name__ == "__main__":
    main()
