# Copyright (c) 2026 思捷娅科技 (SJYKJ)

"""
ConsistencyChecker — 输出一致性检查器
"""

from dataclasses import dataclass, field
from typing import Optional, List, Callable, Dict
from enum import Enum

from algorithms import levenshtein_similarity, tfidf_cosine_similarity, composite_score
from config_manager import DeterministicConfig


class AlertLevel(Enum):
    OK = "ok"
    WARN = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    level: AlertLevel
    message: str
    threshold: float
    actual: float

    def to_dict(self):
        return {"level": self.level.value, "message": self.message,
                "threshold": self.threshold, "actual": self.actual}


@dataclass
class ConsistencyReport:
    samples: List[str]
    char_similarity: float
    semantic_similarity: float
    composite_score: float
    alert: Optional[Alert] = None

    def to_dict(self):
        d = {
            "samples": self.samples,
            "char_similarity": round(self.char_similarity, 4),
            "semantic_similarity": round(self.semantic_similarity, 4),
            "composite_score": round(self.composite_score, 4),
        }
        if self.alert:
            d["alert"] = self.alert.to_dict()
        return d


class ConsistencyChecker:
    CHAR_WEIGHT = 0.4
    SEMANTIC_WEIGHT = 0.6
    DEFAULT_SAMPLES = 5

    def __init__(self, config=None):
        self.config = config or DeterministicConfig()

    def check(self, prompt, sampler_fn=None, n_samples=None):
        """一致性检查主流程"""
        if n_samples is None:
            n_samples = self.DEFAULT_SAMPLES
        if sampler_fn is None:
            sampler_fn = self.default_sampler

        config_dict = self.config.to_dict()
        samples = []
        for _ in range(n_samples):
            try:
                s = sampler_fn(prompt, config_dict)
                samples.append(str(s))
            except Exception:
                samples.append("[error]")

        if len(samples) < 2:
            return ConsistencyReport(
                samples=samples, char_similarity=0.0,
                semantic_similarity=0.0, composite_score=0.0,
                alert=Alert(AlertLevel.CRITICAL, "insufficient samples", 0.8, 0.0),
            )

        char_scores, sem_scores = [], []
        for i in range(len(samples)):
            for j in range(i + 1, len(samples)):
                cs = levenshtein_similarity(samples[i], samples[j])
                ss = tfidf_cosine_similarity(samples[i], samples[j])
                char_scores.append(cs)
                sem_scores.append(ss)

        avg_char = sum(char_scores) / len(char_scores)
        avg_sem = sum(sem_scores) / len(sem_scores)
        comp = composite_score(avg_char, avg_sem, self.CHAR_WEIGHT, self.SEMANTIC_WEIGHT)
        alert = self._check_threshold(comp)
        return ConsistencyReport(
            samples=samples, char_similarity=avg_char,
            semantic_similarity=avg_sem, composite_score=comp, alert=alert,
        )

    def _check_threshold(self, score):
        if score >= 0.8:
            return None
        elif score >= 0.6:
            return Alert(AlertLevel.WARN, "moderate consistency", 0.8, score)
        else:
            return Alert(AlertLevel.CRITICAL, "low consistency", 0.6, score)

    @staticmethod
    def default_sampler(prompt, config):
        """
        默认采样函数：openclaw CLI → HTTP API → mock 降级
        """
        import subprocess
        try:
            result = subprocess.run(
                ["openclaw", "message", "--model", config.get("model", "glm-5-turbo"),
                 "--temperature", str(config.get("temperature", 0.3)),
                 "--no-stream", prompt],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass
        return "[mock] {}".format(abs(hash(prompt)) % 10000)
