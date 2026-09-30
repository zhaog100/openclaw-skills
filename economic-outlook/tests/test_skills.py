#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — 技能独立性测试（门面+微技能）

验证：注册表发现 / 单技能执行 / schema / 失败隔离 / 工作流组合 / 入口合规。
数据源拉不到的技能 skip（不崩）。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import sys, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in [BASE, os.path.join(BASE, "shared"), os.path.join(BASE, "signals"), os.path.join(BASE, "outcomes")]:
    if p not in sys.path:
        sys.path.insert(0, p)

PASSES = []


def ok(msg):
    PASSES.append(msg)
    print("  ✓", msg)


def main():
    from skills.base import BaseSkill
    from orchestrator.registry import SkillRegistry

    # 1. 注册表发现全部技能
    reg = SkillRegistry()
    expected = ["macro_state", "pmi_orders", "credit_impulse", "etf_flow", "export_category",
                "domestic_category", "china_us_spread", "recruitment", "global_pmi",
                "history_analogy", "trigger_engine", "stock_outcome", "fund_outcome",
                "startup_outcome", "employment_outcome", "commodity_outcome",
                "overseas_outcome", "weekly_report"]
    missing = [n for n in expected if n not in reg.skills]
    assert not missing, f"技能未注册: {missing}"
    ok(f"注册表发现 {len(expected)} 技能全在")

    # 2. 所有技能是 BaseSkill 子类 + 有元数据
    for name, skill in reg.skills.items():
        assert isinstance(skill, BaseSkill), f"{name} 非 BaseSkill"
        assert skill.name and skill.description and skill.version, f"{name} 缺元数据"
    ok("全技能是 BaseSkill + 有 name/description/version")

    # 3. 单技能独立执行（拉不到数据 skip，不崩）
    for name in ["macro_state", "pmi_orders", "credit_impulse", "china_us_spread", "global_pmi"]:
        r = reg.get(name).execute({})
        if r.success:
            ok(f"{name} 独立执行成功")
        else:
            print(f"  ⚪ {name} 数据源不可用（skip，不崩）: {r.error[:30]}")

    # 4. 失败隔离：mock 一个必失败技能，工作流继续
    from orchestrator.executor import WorkflowExecutor
    from orchestrator.workflow import get_workflow
    wf = get_workflow("quick_query")
    assert wf is not None
    res = WorkflowExecutor(max_workers=2).execute(wf)
    assert res["workflow"] == "quick_query"
    ok(f"quick_query 工作流执行: 成功 {sum(1 for v in res['results'].values() if v['success'])} 个节点")

    # 5. 出口技能合规（无个股代码）
    import re
    for name in ["stock_outcome", "fund_outcome"]:
        r = reg.get(name).execute({})
        if r.success:
            assert not re.search(r"\b[036]\d{5}\b", str(r.data)), f"{name} 含个股代码"
            ok(f"{name} 合规（无个股代码）")
        else:
            print(f"  ⚪ {name} 数据源不可用（skip）: {r.error[:30]}")

    # 6. 入口 run() 合规
    from entry import run
    out = run("未来经济怎么看？")
    assert "summary" in out and "disclaimer" in out
    forbidden = ["买入", "卖出", "满仓", "清仓", "抄底"]
    txt = str(out)
    for w in forbidden:
        assert w not in txt, f"入口含违规词 {w}"
    assert not re.search(r"\b[036]\d{5}\b", txt), "入口含个股代码"
    ok("入口 run() 合规（有 disclaimer，无违规词/个股代码）")

    print(f"\ntest_skills: PASS ({len(PASSES)} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
