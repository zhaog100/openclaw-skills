#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合规过滤（FR-18，PRD §10）：强制过滤个股代码、买卖点、基金推荐、收益承诺"""
import re

# 个股代码模式（6 位数字、SH/SZ 前缀等）
STOCK_PATTERNS = [
    r'\b[036]\d{5}\b',          # 沪深 6 位代码
    r'SH\d{6}', r'SZ\d{6}', r'HK\d{4,5}',
    r'(买|卖)(入|出)?点', r'(加仓|减仓|清仓|割肉|抄底|逃顶)',
    r'涨停|跌停|满仓|空仓',
]
# 基金/收益承诺
FUND_PATTERNS = [
    r'(推荐|买入)基金[【\[]?\w*基金编号|基金代码\s*[:：]?\d{6}',
    r'收益[达到保证必含]\d*%', r'(年化|回报|收益)承诺',
]
# 创业/就业承诺
PROMISE_PATTERNS = [
    r'(保证|确保|承诺)(成功|薪资|录用|回本)',
]


def filter_text(text, mode='generic', add_disclaimer=True):
    """
    过滤文本中的合规违规内容
    mode: stock/fund/startup/employment/generic
    add_disclaimer: 是否追加免责声明（字段级过滤时应为 False，避免反复追加）
    返回: (cleaned_text, removed_count)
    """
    removed = 0
    cleaned = text

    patterns = []
    if mode in ('stock', 'generic'):
        patterns += STOCK_PATTERNS
    if mode in ('fund', 'generic'):
        patterns += FUND_PATTERNS
    if mode in ('startup', 'employment', 'generic'):
        patterns += PROMISE_PATTERNS

    for p in patterns:
        matches = re.findall(p, cleaned)
        if matches:
            removed += len(matches)
            cleaned = re.sub(p, '[已过滤]', cleaned)

    # 追加免责声明（若缺失且要求追加）
    if add_disclaimer and '不构成' not in cleaned and '免责' not in cleaned:
        cleaned += "\n\n⚠️ 本内容仅供参考，不构成投资建议/商业决策依据。"
    return cleaned, removed


def filter_result(result, mode):
    """对映射模块输出 dict 做合规过滤（过滤敏感词，不在每个字段追加免责尾巴）"""
    out = {}
    for k, v in result.items():
        if isinstance(v, str):
            out[k], _ = filter_text(v, mode, add_disclaimer=False)
        elif isinstance(v, list):
            out[k] = [filter_text(x, mode, add_disclaimer=False)[0] if isinstance(x, str) else x for x in v]
        else:
            out[k] = v
    out.setdefault('_compliance', f'{mode} 模式合规过滤完成')
    return out
