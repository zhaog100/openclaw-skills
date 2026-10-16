#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — 历史类比引擎（A: 5 锚点完整实现）

核心逻辑：
- 定义 5 个宏观锚点（信用/外需/内需/政策/冲击）
- 每个锚点对应一段历史区间 + 特征向量 + 后续资产表现
- 用当前状态向量与各锚点特征向量算余弦相似度
- 输出"当前最像哪段历史" + 后续资产参考

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys, json, logging
from dataclasses import dataclass, field
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'shared'))
sys.path.insert(0, os.path.join(BASE_DIR, 'signals'))
sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))

try:
    import numpy as np
except ImportError:
    np = None


@dataclass
class Anchor:
    """历史锚点定义。"""
    code: str
    name: str
    description: str
    historical_period: str
    feature_vector: dict
    subsequent_returns: dict
    key_signals: list = field(default_factory=list)


# ============ 5 个锚点定义（文档 A）============
ANCHORS = {
    "A": Anchor(
        code="A", name="信用扩张 + 外需改善",
        description="信用脉冲上行，全球PMI>50，出口改善，周期板块领涨",
        historical_period="2016Q1-2016Q4",
        feature_vector={"credit_impulse": +0.8, "global_pmi": +0.6, "pmi_new_order": +0.5,
                        "china_us_spread": +0.2, "domestic_retail": +0.3, "export_category": +0.7},
        subsequent_returns={"stock_cyclical": +0.25, "stock_defensive": +0.08,
                            "bond": -0.02, "commodity": +0.30, "rmb": +0.03},
        key_signals=["credit_impulse", "global_pmi", "pmi_orders"],
    ),
    "B": Anchor(
        code="B", name="信用收缩 + 外需走弱",
        description="信用脉冲下行，全球PMI<50，出口走弱，防御板块占优",
        historical_period="2018Q3-2019Q2",
        feature_vector={"credit_impulse": -0.7, "global_pmi": -0.6, "pmi_new_order": -0.5,
                        "china_us_spread": -0.3, "domestic_retail": -0.2, "export_category": -0.6},
        subsequent_returns={"stock_cyclical": -0.18, "stock_defensive": +0.10,
                            "bond": +0.06, "commodity": -0.15, "rmb": -0.04},
        key_signals=["credit_impulse", "global_pmi", "china_us_spread"],
    ),
    "C": Anchor(
        code="C", name="信用扩张 + 内需疲弱",
        description="信用脉冲上行，但社零低迷，结构性行情为主",
        historical_period="2019Q1-2019Q4",
        feature_vector={"credit_impulse": +0.7, "global_pmi": -0.1, "pmi_new_order": +0.2,
                        "china_us_spread": +0.1, "domestic_retail": -0.5, "export_category": +0.5},
        subsequent_returns={"stock_cyclical": +0.08, "stock_defensive": +0.12,
                            "bond": +0.03, "commodity": +0.05, "rmb": +0.01},
        key_signals=["credit_impulse", "domestic_category"],
    ),
    "D": Anchor(
        code="D", name="政策强刺激",
        description="专项债 + 特别国债超额落地，V型反转",
        historical_period="2020Q2-2020Q4",
        feature_vector={"credit_impulse": +0.9, "global_pmi": +0.2, "pmi_new_order": +0.6,
                        "china_us_spread": +0.3, "domestic_retail": +0.4, "export_category": +0.1},
        subsequent_returns={"stock_cyclical": +0.35, "stock_defensive": +0.15,
                            "bond": -0.05, "commodity": +0.40, "rmb": +0.05},
        key_signals=["credit_impulse", "policy_engine", "global_pmi"],
    ),
    "E": Anchor(
        code="E", name="外部冲击",
        description="VIX>30或中美利差极端，避险情绪主导，现金为王",
        historical_period="2022Q1-2022Q3",
        feature_vector={"credit_impulse": -0.3, "global_pmi": -0.7, "pmi_new_order": -0.4,
                        "china_us_spread": -0.8, "domestic_retail": -0.3, "export_category": -0.4},
        subsequent_returns={"stock_cyclical": -0.22, "stock_defensive": -0.05,
                            "bond": +0.04, "commodity": +0.15, "rmb": -0.08},
        key_signals=["china_us_spread", "global_pmi", "credit_impulse"],
    ),
}

# 方向 → 分值（与 aggregator 一致）
DIR_SCORE = {"bullish": +1, "bearish": -1, "neutral": 0,
             "bullish_cyclical": +1, "bearish_cyclical": -1,
             "expanding": +1, "contracting": -1, "high": +1, "low": -1}


class HistoryAnalogy:
    """历史类比引擎（文档 A）。"""

    def __init__(self):
        self.anchors = ANCHORS

    def _build_current_vector(self, signals: dict) -> dict:
        """从当前信号构建标准化特征向量（-1~+1）。"""
        vector = {}
        mapping = {
            "credit_impulse": "credit_impulse",
            "global_pmi": "global_pmi",
            "pmi_orders": "pmi_new_order",
            "china_us_spread": "china_us_spread",
            "domestic_category": "domestic_retail",
            "export_category": "export_category",
        }
        for sig_name, feat_key in mapping.items():
            sig = signals.get(sig_name)
            if sig:
                vector[feat_key] = DIR_SCORE.get(sig.direction, 0) * sig.strength
        return vector

    def _cosine_similarity(self, vec1: dict, vec2: dict) -> float:
        """两个特征向量的余弦相似度。"""
        keys = set(vec1) & set(vec2)
        if not keys:
            return 0.0
        if np is not None:
            a = np.array([vec1[k] for k in keys])
            b = np.array([vec2[k] for k in keys])
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            if na == 0 or nb == 0:
                return 0.0
            return float(np.dot(a, b) / (na * nb))
        # numpy 不可用时纯 Python 兜底
        import math
        dot = sum(vec1[k] * vec2[k] for k in keys)
        na = math.sqrt(sum(v * v for v in (vec1[k] for k in keys)))
        nb = math.sqrt(sum(v * v for v in (vec2[k] for k in keys)))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def match(self, signals: dict = None) -> dict:
        """匹配当前状态与历史锚点。"""
        if signals is None:
            from signals.aggregator import SignalAggregator
            signals = SignalAggregator().collect_all()

        current = self._build_current_vector(signals)
        matches = []
        for code, anchor in self.anchors.items():
            sim = self._cosine_similarity(current, anchor.feature_vector)
            matches.append({
                "code": code, "name": anchor.name,
                "similarity": round(sim, 3),
                "historical_period": anchor.historical_period,
                "subsequent_returns": anchor.subsequent_returns,
                "key_signals": anchor.key_signals,
            })
        matches.sort(key=lambda x: x["similarity"], reverse=True)
        best = matches[0]
        return {
            "best_match": best,
            "all_matches": matches,
            "current_vector": current,
            "recommendation": self._generate_recommendation(best),
            "updated_at": datetime.now().isoformat(),
        }

    def _generate_recommendation(self, best: dict) -> str:
        returns = best["subsequent_returns"]
        lines = [
            f"当前最像锚点 {best['code']}：{best['name']}（历史区间 {best['historical_period']}）",
            f"相似度：{best['similarity']:.1%}",
            "",
            "历史后续表现（参考）：",
            f"  周期板块：{returns.get('stock_cyclical', 0):+.1%}",
            f"  防御板块：{returns.get('stock_defensive', 0):+.1%}",
            f"  债券：{returns.get('bond', 0):+.1%}",
            f"  大宗：{returns.get('commodity', 0):+.1%}",
            f"  人民币：{returns.get('rmb', 0):+.1%}",
            "",
            f"关键信号：{'、'.join(best['key_signals'])}",
            "⚠️ 历史类比是找相似情景的历史路径，非精确预测；信号一旦变化锚点应切换。",
        ]
        return "\n".join(lines)

    def print_analogy(self, result: dict = None):
        if result is None:
            result = self.match()
        print("=" * 60)
        print("历史类比分析")
        print("=" * 60)
        print(result["recommendation"])
        print("\n所有锚点相似度：")
        for m in result["all_matches"]:
            print(f"  [{m['code']}] {m['name']}: {m['similarity']:.1%}")


# ============ 兼容旧接口（保留 build_current_profile / analyze / format_report）============
def build_current_profile() -> dict:
    """旧接口：构建当前画像（布尔特征），供 triggers 用。"""
    import akshare as ak
    profile = {"_data_gaps": []}
    try:
        cpi = ak.macro_china_cpi()
        yoy_col = next((c for c in cpi.columns if "同比" in c and "指" not in c), None)
        if yoy_col is not None:
            profile["_cpi"] = float(cpi.iloc[0][yoy_col])
            profile["cpi_low"] = profile["_cpi"] < 1.5
        else:
            profile["_data_gaps"].append("CPI")
    except Exception:
        profile["_data_gaps"].append("CPI")
    try:
        from signals.credit_impulse import CreditImpulseCalculator
        s = CreditImpulseCalculator().compute()
        profile["_credit_impulse"] = s.impulse
        profile["credit_contraction"] = s.direction == "bearish_cyclical" or s.impulse < 0
    except Exception:
        profile["_data_gaps"].append("信用脉冲")
    try:
        from signals.china_us_spread import ChinaUSSpreadCalculator
        s = ChinaUSSpreadCalculator().compute()
        profile["_spread_10y"] = s.spread_10y
        profile["spread_negative"] = s.spread_10y < 0
    except Exception:
        profile["_data_gaps"].append("中美利差")
    try:
        pmi_df = ak.macro_china_pmi()
        col = [c for c in pmi_df.columns if "制造业" in c and "指数" in c]
        if col:
            profile["_pmi"] = float(pmi_df.iloc[0][col[0]])
            profile["pmi_expanding"] = profile["_pmi"] > 50
        else:
            profile["_data_gaps"].append("PMI")
    except Exception:
        profile["_data_gaps"].append("PMI")
    try:
        exp = ak.macro_china_exports_yoy()
        if "今值" in exp.columns:
            profile["_export_yoy"] = float(exp.iloc[0]["今值"])
            profile["export_weak"] = profile["_export_yoy"] < 3.0
        else:
            profile["_data_gaps"].append("出口")
    except Exception:
        profile["_data_gaps"].append("出口")
    try:
        import policy_engine
        p = policy_engine.analyze_policy()
        profile["_policy_score"] = p["score"]
        profile["policy_support"] = "aggressive" if p["score"] >= 55 else ("moderate" if p["score"] >= 40 else "weak")
    except Exception:
        profile["_data_gaps"].append("政策")
    return profile


def analyze(profile: dict = None) -> dict:
    """旧接口：兼容返回结构（内部调新引擎）。"""
    res = HistoryAnalogy().match()
    return {
        "current_profile": profile or build_current_profile(),
        "best_match": {"anchor": res["best_match"]["code"] + " " + res["best_match"]["name"],
                        "match_rate": res["best_match"]["similarity"],
                        "outcome": res["best_match"]["name"],
                        "path": res["recommendation"],
                        "structure": {"overweight": [], "underweight": []}},
        "second_match": {"anchor": res["all_matches"][1]["code"], "match_rate": res["all_matches"][1]["similarity"]} if len(res["all_matches"]) > 1 else None,
        "data_gaps": (profile or {}).get("_data_gaps", []),
        "raw": res,
        "caveat": "历史类比是'找相似情景的历史路径'，不是精确预测。",
    }


def format_report(res: dict) -> str:
    """旧接口：格式化为文本。"""
    raw = res.get("raw", HistoryAnalogy().match())
    return HistoryAnalogy().print_analogy(raw)


def main():
    HistoryAnalogy().print_analogy()


if __name__ == "__main__":
    main()
