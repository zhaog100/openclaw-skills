#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — 技能基类（单一职责技能标准接口）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SkillResult:
    """技能输出标准格式。"""
    skill_name: str
    success: bool
    data: dict = field(default_factory=dict)
    error: str = ""
    duration_ms: int = 0
    timestamp: str = ""


class BaseSkill(ABC):
    """技能基类：所有 Skill 必须实现 run()。"""
    name: str = "base"
    description: str = ""
    version: str = "1.0.0"
    depends_on: list = []
    inputs_schema: dict = {}
    outputs_schema: dict = {}

    def __init__(self, config: dict = None):
        self.config = config or {}

    @abstractmethod
    def run(self, context: dict) -> dict:
        """执行技能。context = 上游技能输出 + 全局上下文。"""
        ...

    def validate_inputs(self, context: dict) -> tuple:
        """校验输入。"""
        missing = [k for k in self.inputs_schema if k not in context]
        return (len(missing) == 0, missing)

    def execute(self, context: dict) -> SkillResult:
        """执行技能并包装结果（失败隔离）。"""
        start = datetime.now()
        try:
            ok, missing = self.validate_inputs(context)
            if not ok:
                return SkillResult(skill_name=self.name, success=False,
                                   error=f"缺少输入：{missing}",
                                   timestamp=datetime.now().isoformat())
            data = self.run(context)
            duration = int((datetime.now() - start).total_seconds() * 1000)
            return SkillResult(skill_name=self.name, success=True, data=data or {},
                               duration_ms=duration, timestamp=datetime.now().isoformat())
        except Exception as e:
            duration = int((datetime.now() - start).total_seconds() * 1000)
            return SkillResult(skill_name=self.name, success=False, error=str(e),
                               duration_ms=duration, timestamp=datetime.now().isoformat())
