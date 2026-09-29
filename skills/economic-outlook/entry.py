#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — 唯一门面入口（Facade + 微技能）

用户只调两个函数：
- run(query)         问问题，返回 {summary, details, disclaimer}
- schedule(name)     注册/执行定时任务

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import sys, os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for p in [BASE_DIR, os.path.join(BASE_DIR, "shared")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from orchestrator.router import detect_workflow
from orchestrator.workflow import get_workflow
from orchestrator.executor import WorkflowExecutor
from shared.compliance import DISCLAIMER, filter_result


def run(query: str, verbose: bool = False) -> dict:
    """统一入口：问问题。"""
    workflow_name = detect_workflow(query)
    workflow = get_workflow(workflow_name)
    executor = WorkflowExecutor()
    result = executor.execute(workflow)

    output = {
        "workflow": workflow_name,
        "summary": _build_summary(result, workflow_name),
        "details": result.get("final_output", {}),
        "errors": result.get("errors", []),
        "timestamp": datetime.now().isoformat(),
    }
    if verbose:
        output["all_results"] = result.get("results", {})
    # 合规过滤
    output = filter_result(output, "macro")
    output["disclaimer"] = DISCLAIMER
    return output


def schedule(name: str) -> dict:
    """注册/执行定时任务。"""
    from orchestrator.scheduler import Scheduler
    return Scheduler().run_once(name)


def _build_summary(result: dict, workflow_name: str) -> str:
    final = result.get("final_output", {})
    if workflow_name == "stock_query":
        s = final
        return f"股票：{s.get('direction', 'N/A')} 评分 {s.get('score', 0):+.2f}\n{s.get('recommendation', '')}"
    if workflow_name == "employment_query":
        e = final
        inds = "、".join([i.get("name", i) if isinstance(i, dict) else i for i in e.get("industries", e.get("hot_industries", []))][:3])
        return f"就业热度行业：{inds}"
    if workflow_name == "quick_query":
        tr = final.get("results", [])
        fired = [t for t in tr if t.get("triggered")]
        if fired:
            return "\n".join(f"  {t['scenario_cn']}：{t['action']}" for t in fired)
        return "无触发信号"
    # full_report / weekly_report
    text = final.get("text", "")
    if text:
        return text[:800] + ("\n…（完整版见 details.text）" if len(text) > 800 else "")
    return "完整报告生成失败：" + str(result.get("errors", []))[:200]


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="经济决策门面入口 V3.1")
    p.add_argument("query", nargs="?", default="经济对股市、就业和创业有什么影响？")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--schedule", default="", help="执行定时任务名")
    args = p.parse_args()

    if args.schedule:
        r = schedule(args.schedule)
        print(r)
    else:
        r = run(args.query, args.verbose)
        print(f"工作流: {r['workflow']}")
        print(r["summary"])
        print("-" * 60)
        print(r["disclaimer"])
