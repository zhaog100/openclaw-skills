#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合规过滤（FR-18，PRD V3.1 §17/§19）
shared/compliance.py

从 config/compliance.yaml 读规则（缺省用内置），强制过滤个股/买卖点/基金推荐/收益承诺。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YAML_PATH = os.path.join(BASE_DIR, 'config', 'compliance.yaml')

DISCLAIMER = (
    "本内容仅用于宏观研究与信息参考，不构成投资建议。"
    "预测存在不确定性，基金相关需持牌机构提供。"
    "创业与就业参考不构成商业决策唯一依据。"
)

# 内置默认（yaml 缺省时用）
DEFAULT_RULES = {
    'stock': ['买入', '卖出', '满仓', '清仓', '抄底', '逃顶', '割肉', '涨停', '跌停'],
    'fund': ['必涨', '稳赚', '保本', '推荐基金'],
    'startup': ['保证成功', '稳赚', '必赚'],
    'employment': ['保证录用', '保证薪资', '包分配'],
}
STOCK_CODE = re.compile(r'\b[036]\d{5}\b|\b(?:SH|SZ)\d{6}\b|\bHK\d{4,5}\b')


def load_rules():
    """读 config/compliance.yaml，缺省回退内置"""
    rules = {k: list(v) for k, v in DEFAULT_RULES.items()}
    try:
        import yaml
        if os.path.exists(YAML_PATH):
            with open(YAML_PATH, encoding='utf-8') as f:
                cfg = yaml.safe_load(f) or {}
            for mode in rules:
                if mode in cfg and isinstance(cfg[mode].get('forbidden'), list):
                    rules[mode] = list(cfg[mode]['forbidden'])
    except Exception:
        pass
    return rules


def filter_text(text, mode='generic'):
    """过滤单个字符串。返回 (cleaned, removed)"""
    if not isinstance(text, str):
        return text, 0
    rules = load_rules()
    words = []
    if mode in ('stock', 'generic'):
        words += rules.get('stock', [])
    if mode in ('fund', 'generic'):
        words += rules.get('fund', [])
    if mode in ('startup', 'generic'):
        words += rules.get('startup', [])
    if mode in ('employment', 'generic'):
        words += rules.get('employment', [])

    cleaned = text
    removed = 0
    for w in words:
        if w and w in cleaned:
            removed += cleaned.count(w)
            cleaned = cleaned.replace(w, '[已过滤]')
    # 个股代码
    hits = STOCK_CODE.findall(cleaned)
    if hits:
        removed += len(hits)
        cleaned = STOCK_CODE.sub('[代码已过滤]', cleaned)
    return cleaned, removed


def filter_output(result):
    """递归过滤 dict/list（PRD §17 的 _walk 语义）"""
    def walk(obj, mode):
        if isinstance(obj, dict):
            return {k: walk(v, mode) for k, v in obj.items()}
        if isinstance(obj, list):
            return [walk(x, mode) for x in obj]
        if isinstance(obj, str):
            cleaned, _ = filter_text(obj, mode)
            return cleaned
        return obj

    mode = result.get('_compliance_mode', 'generic') if isinstance(result, dict) else 'generic'
    out = walk(result, mode)
    if isinstance(out, dict):
        out.setdefault('disclaimer', DISCLAIMER)
    return out


def filter_result(result, mode):
    """对映射模块输出做合规过滤（标记 mode 后走 filter_output）"""
    out = dict(result)
    out['_compliance_mode'] = mode
    return filter_output(out)


if __name__ == '__main__':
    c, n = filter_text("推荐 600519 买入满仓，必涨保本", 'stock')
    print(c, "| removed:", n)
