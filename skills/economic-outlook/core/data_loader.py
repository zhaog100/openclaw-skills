"""数据采集与加载（PRD 文档 §八）：官方源优先，失败降级 akshare。
版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)"""
import os, sys, logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "shared"))
sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))

import sources


def load_indicator(name, **kwargs):
    """读取单个指标历史序列（官方源 DataPoint 列表；不可用返回空）。"""
    return sources.fetch(name, **kwargs)


def load_all():
    """加载全部宏观数据（akshare 21 源，主力；官方源作补充）。"""
    import fetch_macro
    return fetch_macro.fetch_all(timeout=180)


def to_series(points):
    """DataPoint 列表 → 按时间排序的数值列表。"""
    if not points:
        return []
    return [p.value for p in sorted(points, key=lambda p: p.period)]


if __name__ == "__main__":
    router = sources.get_router()
    pts = router.fetch("社融")
    print(f"官方源社融: {len(pts)} 条（不可用则降级 akshare）")
