#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一入口（PRD V2.0 §3/§22）
china-econ-skill / entry.py

用法：
  python entry.py "未来一年经济和股市怎么看"
  from entry import run
  result = run("未来一年股市怎么看？")
  print(result["summary"])

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys, logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from router import route

VALID_FLAGS = {'stock', 'fund', 'startup', 'employment'}


def run(query: str, flags: set = None, verbose: bool = False) -> dict:
    """
    对外唯一入口。

    Args:
        query: 用户自然语言问题
        flags: 强制触发的映射模块（如 {'stock','employment'}）
        verbose: 返回完整 details

    Returns:
        {
            "summary": str,
            "details": dict,
            "disclaimer": str
        }
    """
    result = route(query, force=flags)
    if not verbose:
        return {
            'summary': result.get('summary', result.get('text', '')),
            'details': {k: v for k, v in result.items() if k not in ('summary', 'text')},
            'disclaimer': result.get('disclaimer', ''),
        }
    return result


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flagset = set(a.lstrip('-') for a in sys.argv[1:] if a.startswith('--'))
    query = ' '.join(args) if args else '未来一年经济和股市怎么看'
    force = flagset & VALID_FLAGS
    out = run(query, flags=force, verbose=True)
    print(out['summary'])
    print('-' * 60)
    print(out['disclaimer'])
