#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
质量保障插件 - auto-pipeline 接口适配层

将 auto-pipeline 的 8 个 Bash 模块封装为 Python 调用接口，
供 agent-collab-platform 的 PM 代理使用。
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Optional


class PipelineConfig:
    """流水线配置"""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = str(
                Path(__file__).resolve().parent.parent.parent / "config" / "pipeline_config.json"
            )
        with open(config_path, "r", encoding="utf-8") as f:
            self._config = json.load(f)
        # pipeline_path 相对于配置文件目录解析
        pipeline_rel = self._config["pipeline_path"]
        config_dir = str(Path(config_path).resolve().parent)
        self.pipeline_path = str(Path(config_dir) / pipeline_rel)
        self.review_pass_score = self._config["review_pass_score"]
        self.max_fix_rounds = self._config["max_fix_rounds"]
        self.auto_publish = self._config["auto_publish"]

    @property
    def pipeline_sh(self) -> str:
        return str(Path(self.pipeline_path) / "pipeline.sh")


def _run_pipeline_cmd(
    pipeline_path: str,
    args: list[str],
    timeout: int = 300,
) -> tuple[int, str, str]:
    """执行 pipeline.sh 子命令"""
    cmd = ["bash", pipeline_path] + args
    env = os.environ.copy()
    env["PIPELINE_STATE_DIR"] = os.path.expanduser("~/.openclaw/pipeline")
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, env=env
    )
    return result.returncode, result.stdout, result.stderr


def _source_and_call(
    pipeline_path: str,
    func_name: str,
    args: list[str],
    timeout: int = 300,
) -> tuple[int, str, str]:
    """通过 source 脚本后直接调用函数"""
    src_dir = str(Path(pipeline_path).parent / "src")
    modules = [
        "status_manager.sh",
        "prd_reader.sh",
        "plan_reviewer.sh",
        "review_engine.sh",
        "fix_engine.sh",
        "publish_engine.sh",
    ]
    source_lines = [f'source "{src_dir}/{m}"' for m in modules]
    bash_script = (
        "set -euo pipefail\n"
        + "\n".join(source_lines) + "\n"
        + f"{func_name} {' '.join(args)}\n"
    )
    result = subprocess.run(
        ["bash", "-c", bash_script],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr


def read_prd(prd_path: str, config: Optional[PipelineConfig] = None) -> dict[str, Any]:
    """调用 prd_reader.sh，解析 PRD 返回结构化任务

    Args:
        prd_path: PRD 文件路径
        config: 流水线配置

    Returns:
        结构化任务字典（包含 tasks 列表）
    """
    cfg = config or PipelineConfig()
    _, stdout, stderr = _source_and_call(cfg.pipeline_path, "prd_read", [prd_path])
    return json.loads(stdout.strip())


def plan_review(tasks: Any, config: Optional[PipelineConfig] = None) -> dict[str, Any]:
    """调用 plan_reviewer.sh，审查任务声明

    Args:
        tasks: 结构化任务（dict 或 JSON 字符串）
        config: 流水线配置

    Returns:
        审查后的任务声明
    """
    cfg = config or PipelineConfig()
    tasks_json = json.dumps(tasks) if isinstance(tasks, dict) else tasks
    _, stdout, stderr = _source_and_call(cfg.pipeline_path, "plan_review", [tasks_json])
    return json.loads(stdout.strip())


def review(
    skill_dir: str,
    approved_tasks: Any,
    config: Optional[PipelineConfig] = None,
) -> dict[str, Any]:
    """调用 review_engine.sh，返回 12 维度评分

    Args:
        skill_dir: 技能目录路径
        approved_tasks: 审查后的任务声明（dict 或 JSON 字符串）
        config: 流水线配置

    Returns:
        评分结果（total_score, dimensions, issues, passed）
    """
    cfg = config or PipelineConfig()
    skill_name = Path(skill_dir).name
    tasks_json = json.dumps(approved_tasks) if isinstance(approved_tasks, dict) else approved_tasks
    _, stdout, stderr = _source_and_call(
        cfg.pipeline_path, "review", [tasks_json, skill_name, skill_dir]
    )
    return json.loads(stdout.strip())


def fix(
    skill_dir: str,
    issues: Any,
    review_result: Any,
    config: Optional[PipelineConfig] = None,
) -> str:
    """调用 fix_engine.sh，生成修复 prompt

    Args:
        skill_dir: 技能目录路径
        issues: 问题列表（dict 或 JSON 字符串）
        review_result: 评分结果（dict 或 JSON 字符串）
        config: 流水线配置

    Returns:
        修复 prompt 字符串
    """
    cfg = config or PipelineConfig()
    skill_name = Path(skill_dir).name
    issues_json = json.dumps(issues) if isinstance(issues, (dict, list)) else issues
    review_json = json.dumps(review_result) if isinstance(review_result, dict) else review_result
    _, stdout, stderr = _source_and_call(
        cfg.pipeline_path, "fix_issues", [skill_name, issues_json, skill_dir, review_json]
    )
    return stdout.strip()


def publish(
    skill_dir: str,
    review_result: Any,
    config: Optional[PipelineConfig] = None,
) -> dict[str, Any]:
    """调用 publish_engine.sh，执行发布

    Args:
        skill_dir: 技能目录路径
        review_result: 评分结果
        config: 流水线配置

    Returns:
        发布结果
    """
    cfg = config or PipelineConfig()
    skill_name = Path(skill_dir).name
    review_json = json.dumps(review_result) if isinstance(review_result, dict) else review_result
    _, stdout, stderr = _source_and_call(
        cfg.pipeline_path, "publish", [skill_name, review_json, skill_dir]
    )
    return json.loads(stdout.strip())


def check_status(
    skill_name: str,
    config: Optional[PipelineConfig] = None,
) -> dict[str, Any]:
    """调用 status_manager.sh，查询技能状态

    Args:
        skill_name: 技能名称
        config: 流水线配置

    Returns:
        状态信息
    """
    cfg = config or PipelineConfig()
    _, stdout, stderr = _source_and_call(cfg.pipeline_path, "status_detail", [skill_name])
    return json.loads(stdout.strip())


def run_quality_gate(
    skill_dir: str,
    prd_path: Optional[str] = None,
    config: Optional[PipelineConfig] = None,
) -> dict[str, Any]:
    """执行完整质量检查流程

    流程: read_prd → plan_review → review → (不通过则) fix → (≥pass_score则) publish

    Args:
        skill_dir: 技能目录路径
        prd_path: PRD 文件路径（可选）
        config: 流水线配置

    Returns:
        质量检查结果
    """
    cfg = config or PipelineConfig()
    result = {
        "skill_dir": skill_dir,
        "passed": False,
        "total_score": 0,
        "fix_rounds": 0,
        "published": False,
        "review_result": None,
    }

    # 阶段1: PRD 解析
    if prd_path and os.path.exists(prd_path):
        tasks = read_prd(prd_path, cfg)
        approved_tasks = plan_review(tasks, cfg)
    else:
        approved_tasks = {}

    # 阶段2: Review
    review_result = review(skill_dir, approved_tasks, cfg)
    score = review_result.get("total_score", 0)
    result["review_result"] = review_result
    result["total_score"] = score

    # 阶段3: 修复循环
    for round_num in range(1, cfg.max_fix_rounds + 1):
        if score >= cfg.review_pass_score:
            break
        issues = review_result.get("issues", [])
        if not issues:
            break
        fix(skill_dir, issues, review_result, cfg)
        result["fix_rounds"] = round_num
        # 重新 review
        review_result = review(skill_dir, approved_tasks, cfg)
        score = review_result.get("total_score", 0)
        result["review_result"] = review_result
        result["total_score"] = score

    result["passed"] = score >= cfg.review_pass_score

    # 阶段4: 发布
    if result["passed"] and cfg.auto_publish:
        try:
            publish(skill_dir, review_result, cfg)
            result["published"] = True
        except Exception as e:
            result["publish_error"] = str(e)

    return result
