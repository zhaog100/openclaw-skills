#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — 工作流定义（技能组合成 DAG）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from dataclasses import dataclass, field


@dataclass
class WorkflowNode:
    """工作流节点。"""
    skill: str
    depends_on: list = field(default_factory=list)
    optional: bool = False
    parallel_group: str = ""


@dataclass
class Workflow:
    """工作流定义。"""
    name: str
    description: str
    nodes: list
    output: str


# 用 config/workflows.yaml 优先（缺失 fallback 内置）
def _load_workflow_defs() -> dict:
    """从 config/workflows.yaml 读工作流，缺失用内置默认。"""
    import os
    try:
        import yaml
        cfg = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "workflows.yaml")
        if os.path.exists(cfg):
            with open(cfg) as f:
                d = yaml.safe_load(f) or {}
            defs = d.get("workflows", d)
            if defs:
                return defs
    except Exception:
        pass
    return {}


WORKFLOWS = {
    "quick_query": Workflow("quick_query", "快速查询，只跑核心信号", [
        WorkflowNode("macro_state"),
        WorkflowNode("pmi_orders", parallel_group="signals"),
        WorkflowNode("credit_impulse", parallel_group="signals"),
        WorkflowNode("china_us_spread", parallel_group="signals"),
        WorkflowNode("trigger_engine", depends_on=["pmi_orders", "credit_impulse"]),
    ], "trigger_engine"),
    "full_report": Workflow("full_report", "完整周报，跑所有信号和出口", [
        WorkflowNode("macro_state"),
        WorkflowNode("pmi_orders", parallel_group="signals"),
        WorkflowNode("credit_impulse", parallel_group="signals"),
        WorkflowNode("etf_flow", parallel_group="signals", optional=True),
        WorkflowNode("export_category", parallel_group="signals", optional=True),
        WorkflowNode("domestic_category", parallel_group="signals", optional=True),
        WorkflowNode("china_us_spread", parallel_group="signals"),
        WorkflowNode("recruitment", parallel_group="signals", optional=True),
        WorkflowNode("global_pmi", parallel_group="signals"),
        WorkflowNode("history_analogy", depends_on=["pmi_orders", "credit_impulse", "china_us_spread", "global_pmi"]),
        WorkflowNode("trigger_engine", depends_on=["pmi_orders", "credit_impulse", "china_us_spread", "global_pmi"]),
        WorkflowNode("stock_outcome", depends_on=["trigger_engine"], parallel_group="outcomes"),
        WorkflowNode("fund_outcome", depends_on=["trigger_engine"], parallel_group="outcomes"),
        WorkflowNode("startup_outcome", depends_on=["export_category", "domestic_category"], parallel_group="outcomes"),
        WorkflowNode("employment_outcome", depends_on=["recruitment", "export_category"], parallel_group="outcomes"),
        WorkflowNode("commodity_outcome", depends_on=["global_pmi", "credit_impulse"], parallel_group="outcomes"),
        WorkflowNode("overseas_outcome", depends_on=["china_us_spread", "global_pmi"], parallel_group="outcomes"),
        WorkflowNode("weekly_report", depends_on=["history_analogy", "trigger_engine"]),
    ], "weekly_report"),
    "stock_query": Workflow("stock_query", "股票专用查询", [
        WorkflowNode("macro_state"),
        WorkflowNode("pmi_orders", parallel_group="signals"),
        WorkflowNode("credit_impulse", parallel_group="signals"),
        WorkflowNode("etf_flow", parallel_group="signals", optional=True),
        WorkflowNode("china_us_spread", parallel_group="signals"),
        WorkflowNode("stock_outcome", depends_on=["pmi_orders", "credit_impulse", "etf_flow", "china_us_spread"]),
    ], "stock_outcome"),
    "employment_query": Workflow("employment_query", "就业专用查询", [
        WorkflowNode("recruitment", parallel_group="signals", optional=True),
        WorkflowNode("export_category", parallel_group="signals", optional=True),
        WorkflowNode("domestic_category", parallel_group="signals", optional=True),
        WorkflowNode("employment_outcome", depends_on=["recruitment", "export_category", "domestic_category"]),
    ], "employment_outcome"),
}


def get_workflow(name: str):
    """获取工作流（支持 yaml 覆盖）。"""
    yaml_defs = _load_workflow_defs().get(name)
    if yaml_defs:
        nodes = [WorkflowNode(n.get("skill", n.get("name", "")),
                               depends_on=n.get("depends_on", []),
                               optional=n.get("optional", False),
                               parallel_group=n.get("parallel_group", ""))
                 for n in yaml_defs.get("nodes", [])]
        return Workflow(name, yaml_defs.get("description", name), nodes, yaml_defs.get("output", ""))
    return WORKFLOWS.get(name)
