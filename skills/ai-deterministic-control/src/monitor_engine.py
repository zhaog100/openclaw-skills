# Copyright (c) 2026 思捷娅科技 (SJYKJ)

"""
MonitorEngine — 随机性监控引擎（Z-score 异常检测）
"""

import json
import os
import statistics
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict

from consistency_checker import ConsistencyReport
from config_manager import DeterministicConfig


@dataclass
class TrendAnalysis:
    status: str
    mean_score: float = 0.0
    stdev: float = 0.0
    trend_direction: str = "stable"
    data_points: int = 0

    def to_dict(self):
        return asdict(self)


@dataclass
class Anomaly:
    index: int
    timestamp: str
    score: float
    z_score: float
    severity: str

    def to_dict(self):
        return asdict(self)


class MonitorEngine:
    HISTORY_FILE = "monitor_history.json"
    WINDOW_SIZE = 30
    ZSCORE_THRESHOLD = 2.0

    def __init__(self, data_dir=None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        self.history_path = os.path.join(self.data_dir, self.HISTORY_FILE)
        self.history = self._load_history()

    def record_check(self, report, config):
        """记录一次一致性检查结果"""
        entry = {
            "timestamp": self._now(),
            "temperature": config.temperature,
            "top_p": config.top_p,
            "seed": config.seed,
            "composite_score": round(report.composite_score, 4),
            "char_similarity": round(report.char_similarity, 4),
            "semantic_similarity": round(report.semantic_similarity, 4),
            "num_samples": len(report.samples),
            "alert_level": report.alert.level.value if report.alert else "ok",
        }
        self.history.append(entry)
        # Keep last 1000 entries
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        self._save_history()

    def analyze_trend(self, days=7):
        """分析趋势"""
        recent = self._filter_recent(days)
        scores = [e["composite_score"] for e in recent]
        if not scores:
            return TrendAnalysis(status="no_data")
        mean = statistics.mean(scores)
        stdev = statistics.stdev(scores) if len(scores) > 1 else 0.0
        direction = self._calc_direction(scores)
        status = "stable" if stdev < 0.1 else "volatile"
        return TrendAnalysis(status=status, mean_score=round(mean, 4),
                             stdev=round(stdev, 4), trend_direction=direction,
                             data_points=len(scores))

    def detect_anomalies(self):
        """Z-score 异常检测"""
        scores = [e["composite_score"] for e in self.history]
        if len(scores) < 3:
            return []
        mean = statistics.mean(scores)
        stdev = statistics.stdev(scores)
        if stdev == 0:
            return []
        anomalies = []
        for i, entry in enumerate(self.history):
            z = abs((entry["composite_score"] - mean) / stdev)
            if z > self.ZSCORE_THRESHOLD:
                anomalies.append(Anomaly(
                    index=i, timestamp=entry["timestamp"],
                    score=entry["composite_score"], z_score=round(z, 2),
                    severity="critical" if z > 3 else "warning",
                ))
        return anomalies

    def generate_report(self, fmt="markdown", days=7):
        """生成监控报告"""
        trend = self.analyze_trend(days)
        anomalies = self.detect_anomalies()
        recent = self._filter_recent(days)

        if fmt == "json":
            return json.dumps({
                "trend": trend.to_dict(),
                "anomalies": [a.to_dict() for a in anomalies],
                "recent_entries": len(recent),
            }, ensure_ascii=False, indent=2)

        # Markdown
        lines = ["# 📊 AI Deterministic Control - Monitor Report\n"]
        lines.append("**Status:** {}\n".format(trend.status.upper()))
        lines.append("**Mean Score:** {:.4f}".format(trend.mean_score))
        lines.append("**Std Dev:** {:.4f}".format(trend.stdev))
        lines.append("**Trend:** {}".format(trend.trend_direction))
        lines.append("**Data Points:** {}\n".format(trend.data_points))
        if anomalies:
            lines.append("## ⚠️ Anomalies\n")
            for a in anomalies:
                lines.append("- **[{}]** t={} score={:.4f} z={:.2f}".format(
                    a.severity.upper(), a.timestamp, a.score, a.z_score))
            lines.append("")
        if not anomalies:
            lines.append("✅ No anomalies detected.\n")
        return "\n".join(lines)

    def _filter_recent(self, days):
        from datetime import datetime, timezone, timedelta
        tz = timezone(timedelta(hours=8))
        cutoff = datetime.now(tz).timestamp() - days * 86400
        recent = []
        for e in self.history:
            try:
                ts = datetime.fromisoformat(e["timestamp"]).timestamp()
                if ts >= cutoff:
                    recent.append(e)
            except (ValueError, KeyError):
                recent.append(e)
        return recent[-self.WINDOW_SIZE:]

    def _calc_direction(self, scores):
        if len(scores) < 2:
            return "stable"
        half = len(scores) // 2
        first_half = scores[:half]
        second_half = scores[half:]
        mean_first = statistics.mean(first_half)
        mean_second = statistics.mean(second_half)
        diff = mean_second - mean_first
        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "declining"
        return "stable"

    def _load_history(self):
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_history(self):
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _now():
        from datetime import datetime, timezone, timedelta
        tz = timezone(timedelta(hours=8))
        return datetime.now(tz).isoformat()
