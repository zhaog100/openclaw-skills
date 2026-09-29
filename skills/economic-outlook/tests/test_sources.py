"""数据源适配器测试（PRD 文档 §十一）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.sources import get_router, DataPoint


def test_router_init():
    router = get_router()
    for k in ("nbs", "customs", "pboc"):
        assert k in router.adapters, f"缺少适配器 {k}"


def test_fetch_cpi():
    router = get_router()
    points = router.fetch("cpi", start="202401", end="202609")
    assert isinstance(points, list)  # cid 未填时返回空，不抛异常


def test_fetch_social_financing():
    router = get_router()
    points = router.fetch("社融")  # 央行失败会优雅返回 []
    assert isinstance(points, list)


def test_fetch_export():
    router = get_router()
    points = router.fetch("出口_美国")
    assert isinstance(points, list)


if __name__ == "__main__":
    test_router_init()
    test_fetch_cpi()
    test_fetch_social_financing()
    test_fetch_export()
    print("test_sources: PASS")
