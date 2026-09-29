"""映射模块测试（PRD §21）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.state_vector import build_state_vector
from mappings import stock, fund, startup, employment


def test_stock_map():
    s = build_state_vector()
    r = stock.map(s)
    assert "cycle_position" in r and "hot_sectors" in r


def test_employment_map():
    s = build_state_vector()
    r = employment.map(s)
    assert "industry_heat" in r and "city_ranking" in r


def test_fund_map():
    s = build_state_vector()
    r = fund.map(s)
    assert "equity_vs_bond" in r


def test_startup_map():
    s = build_state_vector()
    r = startup.map(s)
    assert "industry_opportunity" in r


if __name__ == "__main__":
    test_stock_map(); test_employment_map(); test_fund_map(); test_startup_map()
    print("test_mappings: PASS")
