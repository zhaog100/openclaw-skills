#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 统一入口（V3.1 信号驱动多出口决策）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import sys, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "signals"))
sys.path.insert(0, os.path.join(BASE_DIR, "outcomes"))

from signals.aggregator import SignalAggregator
from signals.comprehensive_output import generate_comprehensive_report
from signals.matrix_view import build_decision_matrix, print_matrix
from outcomes.report import generate_outcome_report


def run(query: str = "", verbose: bool = False) -> dict:
    """对外唯一入口。"""
    agg = SignalAggregator()
    report = generate_comprehensive_report(agg)
    outcome_report = generate_outcome_report(agg)

    result = {
        "query": query,
        "date": report["date"],
        "signals": report["signals"],
        "outcomes": report["outcomes"],
        "summary": report["summary"],
        "outcome_text": outcome_report["text"],
        "outcome_detail": outcome_report["outcomes"],
    }

    if verbose:
        df = build_decision_matrix(agg)
        result["matrix"] = df.to_dict()
        result["matrix_text"] = df.to_string()

    return result


def main():
    import argparse
    p = argparse.ArgumentParser(description="经济分析 Skill V3.1")
    p.add_argument("query", nargs="?", default="", help="自然语言查询")
    p.add_argument("--verbose", action="store_true", help="输出决策矩阵")
    args = p.parse_args()

    r = run(args.query, args.verbose)
    print(r["summary"])
    print()
    print(r["outcome_text"])
    if args.verbose:
        print()
        print(r["matrix_text"])


if __name__ == "__main__":
    main()
