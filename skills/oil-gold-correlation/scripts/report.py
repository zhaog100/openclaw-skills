#!/usr/bin/env python3
"""
石油黄金分析报告生成器
输出自然语言分析结论

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) - AI Agent
"""
# 版本: v3.3 | 石油黄金白银相关性分析

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analysis import load_data, run_all, interpret_correlation


def generate_report(period: str = "1y", window: int = 30) -> str:
    """生成完整分析报告"""
    df = load_data(period)
    if df.empty:
        return "❌ 无法加载数据"

    results = run_all(df, window)

    p = results["pearson"]
    s = results["spearman"]
    rc_now = results["rolling_current"]
    rc_range = results["rolling_range"]

    # 解读
    interpretation = interpret_correlation(p["pearson_r"])

    # 趋势判断
    if rc_range[1] - rc_range[0] > 0.3:
        stability = "波动较大，相关关系不稳定"
    elif rc_range[1] - rc_range[0] > 0.15:
        stability = "存在一定波动"
    else:
        stability = "相对稳定"

    # 因果关系
    causality = ""
    g = results.get("granger", {})
    for direction, result in g.items():
        if isinstance(result, dict) and result.get("significant"):
            if direction == "oil_causes_gold":
                causality += "原油价格变动对黄金有 Granger 因果影响（原油领先）；"
            else:
                causality += "黄金价格变动对原油有 Granger 因果影响（黄金领先）；"

    # 协整
    cointegration_msg = ""
    ci = results.get("cointegration", {})
    if isinstance(ci, dict) and ci.get("cointegrated"):
        cointegration_msg = "两者存在长期均衡关系（协整），短期内偏离会回归。"

    # 投资启示
    if abs(p["pearson_r"]) > 0.5:
        investment = "⚠️ 强相关 → 同时持有黄金和原油的组合分散效果有限"
    elif abs(p["pearson_r"]) > 0.3:
        investment = "📊 中等相关 → 组合有一定分散效果，但需关注相关性变化"
    else:
        investment = "✅ 弱相关 → 黄金和原油组合能有效分散风险"

    report = f"""
📊 石油-黄金相关性分析报告
{'=' * 40}

📅 分析区间: {df.index[0].date()} ~ {df.index[-1].date()}
📈 样本数: {len(df)} 个交易日
🥇 黄金现价: ${df['gold'].iloc[-1]:,.2f}
🛢️ WTI现价: ${df['wti'].iloc[-1]:,.2f}

━━━ 相关性指标 ━━━

🔹 Pearson相关系数: {p['pearson_r']} {'✅' if p['significant'] else '❌'}
🔹 Spearman秩相关:  {s['spearman_r']}
🔹 解读: {interpretation}

━━━ 动态趋势 ━━━

🔹 当前{window}日滚动相关: {rc_now}
🔹 波动区间: [{rc_range[0]}, {rc_range[1]}]
🔹 稳定性: {stability}

━━━ 因果关系 ━━━

{causality if causality else '🔹 未发现显著 Granger 因果关系'}

━━━ 长期关系 ━━━

{cointegration_msg if cointegration_msg else '🔹 未发现协整关系（长期走势独立）'}

━━━ 投资启示 ━━━

{investment}

━━━ 分析方法 ━━━
本报告使用了 Pearson/Spearman/Kendall 相关系数、{window}日滚动窗口、
Granger 因果检验和 Engle-Granger 协整检验。

⚠️ 免责声明：本分析仅供参考，不构成投资建议。相关性不代表因果性，
市场状况变化可能导致相关性发生结构性变化。
"""

    print(report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成石油黄金分析报告")
    parser.add_argument("--period", default="1y")
    parser.add_argument("--window", type=int, default=30)
    args = parser.parse_args()

    generate_report(args.period, args.window)

# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
