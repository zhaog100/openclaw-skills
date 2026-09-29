#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对外统一入口（PRD §4 单入口）：./entry.py "你的问题"
支持: 纯宏观 / 加 --stock --fund --startup --employment 任意组合"""
import os, sys, logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from router import route

VALID_FLAGS = {'stock', 'fund', 'startup', 'employment'}

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = set(a.lstrip('-') for a in sys.argv[1:] if a.startswith('--'))
    query = " ".join(args) if args else "未来经济走势"
    force = flags & VALID_FLAGS  # flag 强制触发对应映射模块
    r = route(query, force=force)
    print(r['text'])
