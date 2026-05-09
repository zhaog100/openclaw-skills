#!/usr/bin/env python3
"""
石油黄金相关性分析 - 核心逻辑
合并 report.py + report_card.py

Copyright (c) 2026 思捷娅科技 (SJYKJ)
Author: 思捷娅科技 (SJYKJ)/zhaog100
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analysis import load_data, run_all, interpret_correlation


def generate_report(period: str = "1y", window: int = 30) -> dict:
    """生成完整分析报告，返回结构化数据"""
    df = load_data(period)
    if df.empty:
        return {"error": "无法加载数据"}

    results = run_all(df, window)

    p = results["pearson"]
    s = results["spearman"]
    rc_now = results["rolling_current"]
    rc_range = results["rolling_range"]

    # 解读相关性
    interpretation = interpret_correlation(p["pearson_r"])

    # 趋势判断
    if rc_range[1] - rc_range[0] > 0.3:
        stability = "波动较大，相关关系不稳定"
    elif rc_range[1] - rc_range[0] > 0.15:
        stability = "存在一定波动"
    else:
        stability = "相对稳定"

    # Granger 因果检验
    causality = ""
    g = results.get("granger", {})
    for direction, result in g.items():
        if isinstance(result, dict) and result.get("significant"):
            if direction == "oil_causes_gold":
                causality += "原油价格变动对黄金有 Granger 因果影响（原油领先）；"
            elif direction == "gold_causes_oil":
                causality += "黄金价格变动对原油有 Granger 因果影响（黄金领先）；"

    return {
        "period": period,
        "window": window,
        "pearson_r": p["pearson_r"],
        "pearson_p": p["pearson_p"],
        "spearman_r": s["spearman_r"],
        "spearman_p": s["spearman_p"],
        "rolling_current": rc_now,
        "rolling_range": rc_range,
        "interpretation": interpretation,
        "stability": stability,
        "causality": causality,
        "significance": p["significance"]
    }


def format_text_report(data: dict) -> str:
    """将结构化数据格式化为文本报告"""
    if "error" in data:
        return f"❌ {data['error']}"

    lines = []
    lines.append("==================================================")
    lines.append("📊 石油-黄金相关性分析报告")
    lines.append("==================================================")
    lines.append(f"\n📅 数据范围: {data.get('period', 'N/A')}")
    lines.append(f"📈 样本窗口: {data.get('window', 30)} 天")
    lines.append("")

    # Pearson
    r = data.get("pearson_r", 0)
    p = data.get("pearson_p", 0)
    sig = "✅ 显著" if data.get("significance") else "❌ 不显著"
    lines.append(f"--- Pearson 相关系数 ---")
    lines.append(f"  r = {r:.4f} (p={p:.6f}) {sig}")
    lines.append(f"  解读: {data.get('interpretation', 'N/A')}")

    # Spearman
    lines.append("")
    lines.append("--- Spearman 秩相关 ---")
    sr = data.get("spearman_r", 0)
    sp = data.get("spearman_p", 0)
    ss = "✅ 显著" if sp < 0.05 else "❌ 不显著"
    lines.append(f"  ρ = {sr:.4f} (p={sp:.6f}) {ss}")

    # Rolling
    lines.append("")
    lines.append("--- 30日滚动相关系数 ---")
    lines.append(f"  当前: {data.get('rolling_current', 0):.4f}")
    lines.append(f"  区间: [{data.get('rolling_range', [0, 0])[0]:.4f}, {data.get('rolling_range', [0, 0])[1]:.4f}]")

    # Causality
    if data.get("causality"):
        lines.append("")
        lines.append("--- Granger 因果检验 ---")
        lines.append(f"  {data['causality']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="石油黄金相关性分析核心逻辑")
    parser.add_argument("--period", default="1y", help="数据周期 (1mo/3mo/6mo/1y/2y)")
    parser.add_argument("--window", type=int, default=30, help="滚动窗口天数")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")
    args = parser.parse_args()

    data = generate_report(args.period, args.window)

    if args.format == "json":
        import json
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(format_text_report(data))


if __name__ == "__main__":
    main()
