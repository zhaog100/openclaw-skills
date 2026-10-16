#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — 定时任务调度器

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import json, os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
SCHEDULES_PATH = BASE_DIR / "config" / "schedules.yaml"


class Scheduler:
    """定时任务调度器。"""

    def __init__(self):
        self.schedules = self._load_schedules()

    def _load_schedules(self) -> dict:
        if SCHEDULES_PATH.exists():
            try:
                import yaml
                with open(SCHEDULES_PATH, encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                return {}
        return {}

    def run_once(self, name: str) -> dict:
        """执行一次指定任务。"""
        from orchestrator.executor import WorkflowExecutor
        from orchestrator.workflow import get_workflow

        config = self.schedules.get(name, {})
        workflow_name = config.get("workflow", "full_report")
        workflow = get_workflow(workflow_name)
        if not workflow:
            return {"error": f"工作流不存在: {workflow_name}"}
        result = WorkflowExecutor().execute(workflow)

        output_dir = BASE_DIR / "data" / "reports"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        return {"task": name, "workflow": workflow_name,
                "output_file": str(output_file), "errors": result.get("errors", [])}


if __name__ == "__main__":
    import sys
    Scheduler().run_once(sys.argv[1] if len(sys.argv) > 1 else "weekly_report")
