#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 信号组合器（8 信号加权 → 6 出口决策）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime


def _load_config():
    """从 config/signals.yaml 加载信号配置（缺失返回 None，用内置默认）。"""
    import os
    try:
        import yaml
        cfg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "signals.yaml")
        if os.path.exists(cfg_path):
            with open(cfg_path) as f:
                return yaml.safe_load(f) or {}
    except Exception:
        pass
    return {}


_SCFG = _load_config()

OUTCOMES = _SCFG.get("outcomes", ["stock", "fund", "startup", "employment", "commodity", "overseas"])

_DEFAULT_SIGNAL_WEIGHTS = {
    "pmi_orders": {"stock": 0.20, "fund": 0.15, "startup": 0.05, "employment": 0.10, "commodity": 0.20, "overseas": 0.05},
    "etf_flow": {"stock": 0.20, "fund": 0.20, "startup": 0.00, "employment": 0.00, "commodity": 0.00, "overseas": 0.00},
    "recruitment": {"stock": 0.05, "fund": 0.00, "startup": 0.20, "employment": 0.35, "commodity": 0.00, "overseas": 0.00},
    "credit_impulse": {"stock": 0.15, "fund": 0.20, "startup": 0.15, "employment": 0.05, "commodity": 0.20, "overseas": 0.10},
    "china_us_spread": {"stock": 0.10, "fund": 0.15, "startup": 0.05, "employment": 0.00, "commodity": 0.00, "overseas": 0.30},
    "global_pmi": {"stock": 0.10, "fund": 0.05, "startup": 0.05, "employment": 0.05, "commodity": 0.30, "overseas": 0.25},
    "export_category": {"stock": 0.10, "fund": 0.05, "startup": 0.25, "employment": 0.25, "commodity": 0.15, "overseas": 0.15},
    "domestic_category": {"stock": 0.10, "fund": 0.20, "startup": 0.25, "employment": 0.20, "commodity": 0.15, "overseas": 0.15},
}

SIGNAL_WEIGHTS = _SCFG.get("signal_weights", _DEFAULT_SIGNAL_WEIGHTS)
_DEFAULT_DIRECTIONS = {
    "bullish": 1, "bearish": -1, "neutral": 0,
    "bullish_cyclical": 1, "bearish_cyclical": -1,
    "expanding": 1, "contracting": -1,
    "high": 1, "low": -1,
}
DIRECTION_SCORE = _SCFG.get("direction_score", _DEFAULT_DIRECTIONS)


@dataclass
class SignalResult:
    """单个信号的标准化结果。"""
    name: str
    direction: str
    strength: float
    summary: str
    detail: dict


@dataclass
class OutcomeDecision:
    """单个出口的决策输出。"""
    outcome: str
    score: float
    direction: str
    confidence: float
    signals_used: list
    top_signals: list
    conflicts: list
    recommendation: str
    valid_until: str


class SignalAggregator:
    """信号组合器。"""

    def __init__(self):
        self.signals = {}

    def collect_all(self) -> dict:
        """采集所有信号，返回标准化结果（失败降级 neutral）。"""
        results = {}

        # 1. PMI 新订单
        results["pmi_orders"] = self._safe(
            lambda: self._pmi(),
            "PMI新订单",
        )
        # 2. 信用脉冲
        results["credit_impulse"] = self._safe(
            lambda: self._credit(),
            "信用脉冲",
        )
        # 3. ETF 资金流
        results["etf_flow"] = self._safe(
            lambda: self._etf(),
            "ETF资金流",
        )
        # 4. 出口品类
        results["export_category"] = self._safe(
            lambda: self._export(),
            "出口品类",
        )
        # 5. 国内品类
        results["domestic_category"] = self._safe(
            lambda: self._domestic(),
            "国内品类",
        )
        # 6. 中美利差
        results["china_us_spread"] = self._safe(
            lambda: self._spread(),
            "中美利差",
        )
        # 7. 招聘指数
        results["recruitment"] = self._safe(
            lambda: self._recruit(),
            "招聘指数",
        )
        # 8. 全球 PMI
        results["global_pmi"] = self._safe(
            lambda: self._global(),
            "全球PMI",
        )

        self.signals = results
        return results

    def _pmi(self):
        from signals.pmi_orders import PMIOrdersSignal
        s = PMIOrdersSignal().compute()
        return SignalResult("PMI新订单", s.direction, s.strength,
                            f"新订单 {s.new_order}，月度变化 {s.delta:+.1f}",
                            {"new_order": s.new_order, "delta": s.delta})

    def _credit(self):
        from signals.credit_impulse import CreditImpulseCalculator
        s = CreditImpulseCalculator().compute()
        return SignalResult("信用脉冲", s.direction, s.strength,
                            f"信用脉冲 {s.impulse:+.4f}，月度变化 {s.impulse_change:+.4f}",
                            {"impulse": s.impulse, "change": s.impulse_change})

    def _etf(self):
        from signals.etf_flow import ETFFlowCalculator
        s = ETFFlowCalculator().compute()
        return SignalResult("ETF资金流", s.direction, s.strength,
                            f"整体 {s.direction}，看多 {[x['name'] for x in s.top_sectors[:3]]}",
                            {"top": s.top_sectors, "bottom": s.bottom_sectors})

    def _export(self):
        from signals.export_category import ExportCategoryCalculator
        s = ExportCategoryCalculator().compute()
        return SignalResult("出口品类",
                            "bullish" if s.top_categories else "neutral",
                            0.6,
                            f"上行 {s.top_categories[:3]}，下行 {s.bottom_categories[:2]}",
                            {"top": s.top_categories, "bottom": s.bottom_categories})

    def _domestic(self):
        from signals.domestic_category import DomesticCategoryCalculator
        s = DomesticCategoryCalculator().compute()
        return SignalResult("国内品类",
                            "bullish" if s.top_categories else "neutral",
                            0.6,
                            f"上行 {s.top_categories[:3]}，下行 {s.bottom_categories[:2]}",
                            {"top": s.top_categories, "bottom": s.bottom_categories})

    def _spread(self):
        from signals.china_us_spread import ChinaUSSpreadCalculator
        s = ChinaUSSpreadCalculator().compute()
        return SignalResult("中美利差", s.direction, s.strength,
                            f"10Y利差 {s.spread_10y}%，分位数 {s.percentile_10y:.0%}",
                            {"spread": s.spread_10y, "pct": s.percentile_10y})

    def _recruit(self):
        from signals.recruitment import RecruitmentCalculator
        s = RecruitmentCalculator().compute()
        return SignalResult("招聘指数", s.direction, s.strength,
                            f"PMI从业人员 {s.pmi_employment}，方向 {s.direction}",
                            {"pmi_employment": s.pmi_employment,
                             "industries": [x['name'] for x in s.hot_industries[:3]]})

    def _global(self):
        from signals.global_pmi import GlobalPMICalculator
        s = GlobalPMICalculator().compute()
        return SignalResult("全球PMI", s.direction, s.strength,
                            f"全球PMI {s.global_pmi}，方向 {s.direction}",
                            {"global_pmi": s.global_pmi, "export_order": s.china_export_order})

    def _safe(self, fn, name):
        try:
            return fn()
        except Exception as e:
            return SignalResult(name, "neutral", 0.0, f"采集失败: {str(e)[:40]}", {})

    def aggregate_for_outcome(self, outcome: str) -> OutcomeDecision:
        """为指定出口聚合信号。"""
        if not self.signals:
            self.collect_all()

        weights = {}
        for sig_name, w in SIGNAL_WEIGHTS.items():
            weights[sig_name] = w.get(outcome, 0)

        total_weight = sum(weights.values())
        if total_weight == 0:
            return OutcomeDecision(outcome, 0.0, "neutral", 0.0, [], [], [],
                                   "该出口暂无有效信号", self._next_month())

        weighted_score = 0.0
        contributions = []
        directions = []

        for sig_name, weight in weights.items():
            if weight == 0:
                continue
            sig = self.signals.get(sig_name)
            if not sig:
                continue
            dscore = DIRECTION_SCORE.get(sig.direction, 0)
            contribution = dscore * sig.strength * weight
            weighted_score += contribution
            contributions.append({"name": sig.name, "contribution": round(contribution, 4),
                                  "direction": sig.direction, "strength": sig.strength})
            directions.append(dscore)

        score = max(-1, min(1, weighted_score / total_weight))
        bull_th = _SCFG.get("decision", {}).get("bullish_threshold", 0.15)
        bear_th = _SCFG.get("decision", {}).get("bearish_threshold", -0.15)
        if score > bull_th:
            direction = "bullish"
        elif score < bear_th:
            direction = "bearish"
        else:
            direction = "neutral"

        consistency = abs(sum(directions)) / len(directions) if directions else 0
        confidence = min(consistency * total_weight / 2, 1.0)
        confidence = round(confidence, 2)

        contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
        top_signals = contributions[:3]

        conflicts = []
        pos = [c for c in contributions if c["contribution"] > 0.01]
        neg = [c for c in contributions if c["contribution"] < -0.01]
        if pos and neg:
            conflicts.append(f"{pos[0]['name']}（看多）与 {neg[0]['name']}（看空）方向冲突")

        recommendation = self._generate_recommendation(outcome, direction, score, top_signals, conflicts)

        return OutcomeDecision(outcome, round(score, 3), direction, confidence,
                               list(weights.keys()), top_signals, conflicts,
                               recommendation, self._next_month())

    def aggregate_all(self) -> dict:
        if not self.signals:
            self.collect_all()
        return {o: self.aggregate_for_outcome(o) for o in OUTCOMES}

    def _generate_recommendation(self, outcome, direction, score, top_signals, conflicts):
        dir_cn = {"bullish": "看多", "bearish": "看空", "neutral": "中性"}[direction]
        outcome_cn = {"stock": "股票", "fund": "基金", "startup": "创业",
                      "employment": "就业", "commodity": "大宗", "overseas": "海外配置"}[outcome]
        if abs(score) > 0.5:
            strength_cn = "强"
        elif abs(score) > 0.25:
            strength_cn = "中等"
        else:
            strength_cn = "弱"
        drivers = "、".join([s["name"] for s in top_signals[:2]]) if top_signals else "无"
        conflict_text = f"；注意：{conflicts[0]}" if conflicts else ""
        return f"{outcome_cn}：{dir_cn}（{strength_cn}，评分 {score:+.2f}）。主要驱动：{drivers}{conflict_text}。"

    def _next_month(self) -> str:
        from datetime import timedelta
        return (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
