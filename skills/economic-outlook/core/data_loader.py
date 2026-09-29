#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据采集与加载（PRD V2.0 §8）
core/data_loader.py

通过 shared.sources 统一取数，映射模块不直接写 API 调用。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys, logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'shared'))

import sources


def load_indicator(name, freq='M'):
    """读取单个指标历史序列（DataFrame）"""
    src = sources.get_source(name)
    if src is None:
        return None
    try:
        return src.fetch(name, freq)
    except Exception:
        return None


def load_all():
    """一次拉取全部数据源，返回 dict"""
    return sources.load_all()


if __name__ == '__main__':
    data = load_all()
    ok = [k for k, v in data.items() if v is not None]
    print(f"加载 {len(ok)} 源: {ok}")
