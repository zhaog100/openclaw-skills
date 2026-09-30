"""数据源统一出口（PRD 文档 §七）：按 config/sources.yaml 路由到适配器。
官方源（NBS/海关/央行）不可用时优雅降级，不阻塞主流程。
版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)"""
from pathlib import Path
from .base import BaseAdapter, DataPoint
from .nbs import NBSAdapter
from .customs import CustomsAdapter
from .pboc import PBOCAdapter

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "sources.yaml"


def _load_config() -> dict:
    try:
        import yaml
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    except Exception:
        pass
    return {}


# 指标 → 适配器
ROUTING = {
    "gdp": "nbs", "cpi": "nbs", "ppi": "nbs",
    "社零": "nbs", "固投": "nbs", "失业率": "nbs",
    "出口": "customs", "出口_美国": "customs", "出口_欧盟": "customs",
    "社融": "pboc", "m1": "pboc", "m2": "pboc",
}


class SourceRouter:
    def __init__(self):
        config = _load_config()
        self.adapters = {
            "nbs": NBSAdapter(config),
            "customs": CustomsAdapter(config),
            "pboc": PBOCAdapter(config),
        }
        self.routing = dict(ROUTING)

    def fetch(self, indicator: str, **kwargs):
        """采集单个指标；官方源失败返回空（上层可降级 akshare）"""
        name = self.routing.get(indicator)
        if not name or name not in self.adapters:
            return []
        try:
            return self.adapters[name].fetch(indicator, **kwargs)
        except Exception as e:
            print(f"[{name}] 采集 {indicator} 失败: {e}")
            return []

    def fetch_all(self, indicators=None) -> dict:
        inds = indicators or list(self.routing.keys())
        return {i: self.fetch(i) for i in inds}


_router = None


def get_router() -> SourceRouter:
    global _router
    if _router is None:
        _router = SourceRouter()
    return _router


def fetch(indicator: str, **kwargs) -> list:
    return get_router().fetch(indicator, **kwargs)
