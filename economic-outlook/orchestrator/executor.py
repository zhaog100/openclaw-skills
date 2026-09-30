#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — 执行引擎（拓扑排序 + 并行 + 失败隔离）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from skills.base import SkillResult
from orchestrator.registry import get_registry
from orchestrator.workflow import Workflow


class WorkflowExecutor:
    """工作流执行引擎。"""

    def __init__(self, max_workers: int = 4):
        self.registry = get_registry()
        self.max_workers = max_workers

    def execute(self, workflow: Workflow) -> dict:
        results = {}
        errors = []
        remaining = list(workflow.nodes)

        while remaining:
            ready = [n for n in remaining if all(d in results for d in n.depends_on)]
            if not ready:
                for n in remaining:
                    missing = [d for d in n.depends_on if d not in results]
                    errors.append(f"{n.skill} 依赖未满足: {missing}")
                break

            # 并行组分组
            parallel_groups = {}
            for node in ready:
                group = node.parallel_group or node.skill
                parallel_groups.setdefault(group, []).append(node)

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {}
                for group, nodes in parallel_groups.items():
                    for node in nodes:
                        ctx = self._build_context(node, results)
                        skill = self.registry.get(node.skill)
                        if not skill:
                            errors.append(f"技能不存在: {node.skill}")
                            remaining.remove(node)
                            continue
                        futures[executor.submit(skill.execute, ctx)] = node
                for future in as_completed(futures):
                    node = futures[future]
                    result = future.result()
                    results[node.skill] = result
                    if not result.success and not node.optional:
                        errors.append(f"{node.skill}: {result.error}")
                    remaining.remove(node)

        final = results.get(workflow.output)
        return {
            "workflow": workflow.name,
            "results": {k: {"success": v.success, "data": v.data, "error": v.error}
                        for k, v in results.items()},
            "final_output": final.data if final and final.success else {},
            "errors": errors,
        }

    def _build_context(self, node, results: dict) -> dict:
        ctx = {}
        for dep in node.depends_on:
            if dep in results and results[dep].success:
                ctx[dep] = results[dep].data
        return ctx
