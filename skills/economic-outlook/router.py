#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""意图路由（PRD §7）：关键词识别 宏观/股票/基金/创业/就业，并行调用映射模块"""
import os, sys, re, logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'core'))
sys.path.insert(0, os.path.join(BASE_DIR, 'mappings'))
sys.path.insert(0, os.path.join(BASE_DIR, 'shared'))

import state_vector
import stock, fund, startup, employment
import compliance as comp

INTENTS = {
    'stock': [r'股票', r'股市', r'行业', r'景气', r'板块', r'个股'],
    'fund': [r'基金', r'债', r'配置', r'股债'],
    'startup': [r'创业', r'融资', r'机会'],
    'employment': [r'就业', r'求职', r'招聘', r'薪资', r'岗位'],
    'macro': [r'经济', r'宏观', r'GDP', r'CPI', r'预测', r'走势', r'形势'],
}


def detect_intents(query):
    hits = set()
    for intent, pats in INTENTS.items():
        if any(re.search(p, query) for p in pats):
            hits.add(intent)
    return hits


def route(query):
    """
    路由入口：返回 { 'state': 宏观向量, 'modules': {意图: 合规过滤后结果}, 'text': 纯文本 }
    """
    intents = detect_intents(query) or {'macro'}
    state = state_vector.build_state_vector()
    modules = {'macro': state}

    if 'stock' in intents:
        modules['stock'] = comp.filter_result(stock.map(state), 'stock')
    if 'fund' in intents:
        modules['fund'] = comp.filter_result(fund.map(state), 'fund')
    if 'startup' in intents:
        modules['startup'] = comp.filter_result(startup.map(state), 'startup')
    if 'employment' in intents:
        modules['employment'] = comp.filter_result(employment.map(state), 'employment')

    import shared.formatters as fmt
    lines = [f"📊 宏观经济（综合 {state.get('total_score')} 分）",
             f"  驱动: {'、'.join(state.get('drivers', [])[:5])}",
             ""]
    if 'stock' in modules:
        lines.append(fmt.stock_report(modules['stock']))
    if 'fund' in modules:
        lines.append(fmt.fund_report(modules['fund']))
    if 'startup' in modules:
        lines.append(fmt.startup_report(modules['startup']))
    if 'employment' in modules:
        lines.append(fmt.employment_report(modules['employment']))
    lines.append("\n⚠️ 仅供参考，不构成投资建议/商业决策依据。")
    return {'state': state, 'modules': modules, 'text': "\n".join(lines)}


if __name__ == '__main__':
    q = sys.argv[1] if len(sys.argv) > 1 else "未来一年经济和股市怎么看"
    r = route(q)
    print(r['text'])
