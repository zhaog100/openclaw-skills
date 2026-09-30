"""数据源适配器基类：所有适配器实现 fetch() 并返回统一格式。
版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
import time


@dataclass
class DataPoint:
    """统一数据点。"""
    indicator: str
    period: str
    value: float
    unit: str = ""
    source: str = ""
    updated_at: str = ""


class BaseAdapter(ABC):
    name = "base"

    def __init__(self, config: dict):
        self.config = config or {}
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        }

    @abstractmethod
    def fetch(self, indicator: str, **kwargs) -> list:
        ...

    def _sleep(self, seconds: float = 0.5):
        time.sleep(seconds)

    def _safe_get(self, session, url: str, **kwargs):
        for attempt in range(3):
            try:
                r = session.get(url, headers=self.headers, timeout=30, **kwargs)
                r.raise_for_status()
                return r
            except Exception as e:
                if attempt == 2:
                    raise
                self._sleep(1.5 * (attempt + 1))
