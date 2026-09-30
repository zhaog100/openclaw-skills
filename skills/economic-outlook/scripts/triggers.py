#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — 行动触发器（B: 4 场景动作，文档 _1 新版）

核心逻辑：
- 根据当前信号组合，判断触发哪个场景（加仓/减仓/切换/观望）
- 每个场景对应具体动作（仓位变化 %）+ 优先级 + 有效期
- cross_50 用"本周值与上周值跨 50"精确判定穿越
- 输出可执行的决策指令

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'shared'))
sys.path.insert(0, os.path.join(BASE_DIR, 'signals'))


@dataclass
class TriggerResult:
    """触发器结果。"""
    scenario: str            # add / reduce / switch / wait
    scenario_cn: str        # 加仓 / 减仓 / 切换 / 观望
    triggered: bool
    conditions: list        # [{signal, expected, actual, met}, ...]
    action: str
    position_change: float
    target_position: float
    priority: int
    valid_until: str
    notes: list = field(default_factory=list)


class TriggerEngine:
    """行动触发器引擎（文档 B _1 新版）。"""

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
        """检查单个信号条件是否满足（cross_50 用穿越判定）。"""
        sig = signals.get(sig_name)
        if not sig:
            return False
        if expected == "cross_50":
            # 全球PMI 穿越 50：本周值与上周值跨荣枯线
            detail = sig.detail or {}
            current = detail.get("global_pmi", 0)
            prev = detail.get("prev_global_pmi", current)
            return (current - 50) * (prev - 50) < 0
        if expected == "any":
            return self._detect_conflict(signals)
        return sig.direction == expected

    def _detect_conflict(self, signals: dict) -> bool:
        """检测信号冲突（有正有负）。"""
        from signals.aggregator import DIRECTION_SCORE
        directions = []
        for sig in signals.values():
            if sig is None:
                continue
            score = DIRECTION_SCORE.get(sig.direction, 0)
            if score != 0:
                directions.append(score)
        if len(directions) < 2:
            return False
        return any(d > 0 for d in directions) and any(d < 0 for d in directions)

    def _eval_scenario(self, key: str, signals: dict) -> TriggerResult:
        """评估单个场景，返回 TriggerResult。"""
        sc = self.SCENARIOS[key]
        logic = sc["logic"]
        conditions = []
        all_met = True
        any_met = False
        for sig_name, expected in sc["conditions"]:
            if sig_name == "conflict":
                met = self._detect_conflict(signals)
                actual = "有冲突" if met else "无冲突"
            else:
                sig = signals.get(sig_name)
                met = self._check_condition(sig_name, expected, signals)
                actual = sig.direction if sig else "N/A"
            conditions.append({"signal": sig_name, "expected": expected, "actual": actual, "met": met})
            if met:
                any_met = True
            if not met:
                all_met = False

        if logic in ("AND", "SINGLE"):
            triggered = all_met
        else:  # ANY
            triggered = any_met

        pos_change = sc["position_change"] if triggered else 0
        if triggered and key == "add":
            target = min(self.current_position + pos_change, 100)
        elif triggered and key == "reduce":
            target = max(self.current_position + pos_change, 0)
        else:
            target = self.current_position

        note = ""
        if triggered:
            note = {
                "add": "信用脉冲与PMI新订单双上行，确认周期启动",
                "reduce": "信用收缩 + 汇率承压，降低风险敞口",
                "switch": "全球PMI穿越荣枯线，风格切换",
                "wait": "信号方向冲突，等待确认",
            }.get(key, "")

        return TriggerResult(
            scenario=key, scenario_cn=sc["name"], triggered=triggered,
            conditions=conditions,
            action=sc["action"] if triggered else "不触发",
            position_change=pos_change,
            target_position=target,
            priority=sc["priority"],
            valid_until=self._next_week(),
            notes=[note] if note else [],
        )

    def evaluate(self, signals: dict = None) -> list:
        """评估所有场景，按优先级排序。"""
        if signals is None:
            from signals.aggregator import SignalAggregator
            signals = SignalAggregator().collect_all()

        results = [self._eval_scenario(k, signals) for k in self.SCENARIOS]
        results.sort(key=lambda x: (not x.triggered, x.priority))
        return results

    def _next_week(self) -> str:
        return (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    def print_triggers(self, results: list = None):
        if results is None:
            results = self.evaluate()
        print("=" * 60)
        print("行动触发器")
        print("=" * 60)
        for r in results:
            status = "✅ 触发" if r.triggered else "⭕ 未触发"
            print(f"\n[{r.priority}] {r.scenario_cn} {status}")
            print(f"    动作：{r.action}")
            if r.triggered:
                print(f"    仓位变化：{r.position_change:+d}% → 目标 {r.target_position:.0f}%")
            for c in r.conditions:
                mark = "✓" if c["met"] else "✗"
                print(f"    {mark} {c['signal']}: 期望 {c['expected']}，实际 {c['actual']}")
            for note in r.notes:
                print(f"    备注：{note}")
        print("=" * 60)


# ============ 兼容旧接口（check_anchor_triggers / build_action_checklist / format_triggers）============
ANCHOR_TRIGGERS = [
    {"name": "信用脉冲转正", "switch_to": "A", "hint": "切到信用扩张锚点"},
    {"name": "出口跌破 0", "switch_to": "E", "hint": "切到外部冲击锚点"},
    {"name": "CPI 破 2%", "switch_to": "A", "hint": "切到通胀回升锚点"},
    {"name": "政策托底转强", "switch_to": "D", "hint": "切到政策强刺激锚点"},
]


def check_anchor_triggers(profile: dict) -> list:
    return [{"name": t["name"], "triggered": False, "switch_to": t["switch_to"], "hint": t["hint"]}
            for t in ANCHOR_TRIGGERS]


def build_action_checklist(profile: dict, decisions: dict = None) -> dict:
    """兼容旧接口：返回 4 场景 dict（内部调新版 TriggerEngine）。"""
    eng = TriggerEngine()
    results = eng.evaluate()
    scene_key = {"加仓": "add", "减仓": "reduce", "切换": "switch", "观望": "wait"}
    out = {}
    for cn, key in scene_key.items():
        r = next(x for x in results if x.scenario == key)
        out[cn] = {
            "triggered": r.triggered,
            "status": ("✅ 已激活" if r.triggered else "⚪ 待触发"),
            "condition": " + ".join(f"{c['signal']}={c['expected']}" for c in r.conditions),
            "action": r.action,
            "position_change": r.position_change,
            "target_position": r.target_position,
        }
    return out


def format_triggers(profile: dict, decisions: dict = None) -> str:
    """兼容旧接口：格式化输出。"""
    eng = TriggerEngine()
    results = eng.evaluate()
    lines = ["", "=" * 48, "🎯 行动触发器（信号变化 → 该做什么）", "=" * 48,
             f"基础仓位: {eng.base_position:.0f}%"]
    for r in results:
        icon = "✅" if r.triggered else "⚪"
        lines.append(f"\n{icon} [{r.priority}] {r.scenario_cn}（优先级 {r.priority}）")
        lines.append(f"  动作: {r.action}")
        if r.triggered:
            lines.append(f"  仓位: {r.position_change:+d}% → 目标 {r.target_position:.0f}%")
        for c in r.conditions:
            mark = "✓" if c["met"] else "✗"
            lines.append(f"    {mark} {c['signal']}={c['expected']}（实际 {c['actual']}）")
    lines.append("\n⚠️ 以上为宏观信号参考，不构成投资建议/商业决策。")
    return "\n".join(lines)


def main():
    TriggerEngine().print_triggers()


if __name__ == "__main__":
    main()
