# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

"""LogProbAnalyzer — 对数概率熵分析与确定性评分"""

import math
from typing import List, Dict, Optional


def entropy_from_logprobs(logprobs: List[float]) -> float:
    """计算 Shannon 熵 H = -Σ p(x) * log2(p(x))

    Args:
        logprobs: 概率分布列表（非对数，直接是概率值）
    Returns:
        Shannon 熵（bits）
    """
    if not logprobs:
        return 0.0
    total = sum(logprobs)
    if total <= 0:
        return 0.0
    probs = [p / total for p in logprobs if p > 0]
    if not probs:
        return 0.0
    return -sum(p * math.log2(p) for p in probs)


def certainty_score(probabilities: List[float]) -> float:
    """确定性评分：0（完全随机）~ 100（完全确定）

    基于 Shannon 熵的归一化评分。
    熵越小 → 确定性越高 → 评分越高。
    """
    if not probabilities or sum(probabilities) <= 0:
        return 0.0
    entropy = entropy_from_logprobs(probabilities)
    n = len([p for p in probabilities if p > 0])
    if n <= 1:
        return 100.0
    max_entropy = math.log2(n)  # 均匀分布的熵
    if max_entropy <= 0:
        return 100.0
    score = (1.0 - entropy / max_entropy) * 100.0
    return round(max(0.0, min(100.0, score)), 1)


def analyze_trend(history: List[float], window: int = 5) -> Dict:
    """分析确定性趋势（最近N次调用的熵变化）

    Returns:
        dict: {direction, slope, avg, latest, min, max}
    """
    if not history:
        return {"direction": "unknown", "slope": 0, "avg": 0, "latest": 0, "min": 0, "max": 0}

    recent = history[-window:]
    n = len(recent)

    if n < 2:
        return {"direction": "stable", "slope": 0, "avg": recent[0], "latest": recent[0],
                "min": recent[0], "max": recent[0]}

    # 线性回归斜率
    x_mean = (n - 1) / 2.0
    y_mean = sum(recent) / n
    numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(recent))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    slope = numerator / denominator if denominator != 0 else 0

    direction = "stable"
    if slope < -0.05:
        direction = "falling"  # 熵下降 = 确定性提高（好事）
    elif slope > 0.05:
        direction = "rising"   # 熵上升 = 确定性下降（坏事）

    return {
        "direction": direction,
        "slope": round(slope, 4),
        "avg": round(y_mean, 4),
        "latest": recent[-1],
        "min": min(recent),
        "max": max(recent),
    }


def detect_anomaly(current_value: float, history: List[float], threshold: float = 2.0) -> Dict:
    """Z-score 异常检测

    Args:
        current_value: 当前熵值
        history: 历史熵值
        threshold: Z-score 阈值（默认2.0σ）
    """
    if len(history) < 2:
        return {"is_anomaly": False, "z_score": 0, "reason": "insufficient_data"}

    mean = sum(history) / len(history)
    variance = sum((h - mean) ** 2 for h in history) / len(history)
    std = math.sqrt(variance) if variance > 0 else 0

    if std == 0:
        is_anomaly = abs(current_value - mean) > 0.1
        return {"is_anomaly": is_anomaly, "z_score": float('inf') if is_anomaly else 0,
                "mean": mean, "std": 0}

    z_score = abs(current_value - mean) / std
    is_anomaly = z_score > threshold

    return {
        "is_anomaly": is_anomaly,
        "z_score": round(z_score, 2),
        "mean": round(mean, 4),
        "std": round(std, 4),
        "threshold": threshold,
    }
