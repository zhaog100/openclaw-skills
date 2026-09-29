"""核心引擎测试（PRD §21）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.state_vector import build_state_vector


def test_state_vector_keys():
    s = build_state_vector()
    for k in ["horizon", "total_score", "drivers", "scenario_prob", "forecast_q"]:
        assert k in s, f"缺少 {k}"


def test_forecast_8q():
    s = build_state_vector()
    assert len(s["forecast_q"]) == 8, "应为 8 季度"


if __name__ == "__main__":
    test_state_vector_keys()
    test_forecast_8q()
    print("test_core: PASS")
