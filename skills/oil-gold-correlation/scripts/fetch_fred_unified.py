#!/usr/bin/env python3
"""
FRED 数据获取统一接口 - 消除硬编码 fallback 值

提供获取宏观数据的标准接口，不再使用硬编码的默认值
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from fetch_fred import _latest


def get_consumer_confidence():
    """获取消费者信心数据"""
    val, change, pct = _latest("UMCSENT", 120)
    if val is not None:
        return {
            'value': round(val, 2),
            'change': round(change, 2) if change is not None else 0,
            'pct': round(pct, 2) if pct is not None else 0
        }
    return None


def get_vix():
    """获取 VIX 恐慌指数"""
    val, change, pct = _latest("VIXCLS", 90)
    if val is not None:
        return {
            'value': round(val, 2),
            'change': round(change, 2) if change is not None else 0,
            'pct': round(pct, 2) if pct is not None else 0
        }
    return None


def get_yield_spread():
    """获取收益率曲线利差"""
    val, change, pct = _latest("T10Y2Y", 90)
    if val is not None:
        return {
            'value': round(val, 3),
            'change': round(change, 3) if change is not None else 0,
            'pct': round(pct, 2) if pct is not None else 0
        }
    return None


def get_credit_spread():
    """获取信用利差"""
    val, change, pct = _latest("BAMLH0A0HYM2", 90)
    if val is not None:
        return {
            'value': round(val, 2),
            'change': round(change, 2) if change is not None else 0,
            'pct': round(pct, 2) if pct is not None else 0
        }
    return None


def get_all_macro_data():
    """获取所有宏观数据"""
    return {
        'consumer_confidence': get_consumer_confidence(),
        'vix': get_vix(),
        'spread': get_yield_spread(),
        'credit': get_credit_spread()
    }


if __name__ == "__main__":
    # 测试数据获取
    data = get_all_macro_data()
    print("宏观数据获取测试:")
    for key, value in data.items():
        if value:
            print(f"  {key}: {value['value']}")
        else:
            print(f"  {key}: [数据不可用]")