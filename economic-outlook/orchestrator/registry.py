#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — 技能注册表（自动发现 skills/ 下所有技能）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import importlib
import pkgutil
from pathlib import Path
from skills.base import BaseSkill


class SkillRegistry:
    """技能注册表：自动扫描 skills/ 目录注册 BaseSkill 子类。"""

    def __init__(self):
        self.skills: dict = {}
        self._discover()

    def _discover(self):
        skills_dir = Path(__file__).parent.parent / "skills"
        if not skills_dir.exists():
            return
        for module_info in pkgutil.iter_modules([str(skills_dir)]):
            module_name = module_info.name
            if module_name in ("base", "__init__"):
                continue
            try:
                mod = importlib.import_module(f"skills.{module_name}.skill")
            except (ImportError, ModuleNotFoundError):
                continue
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if (isinstance(attr, type) and issubclass(attr, BaseSkill)
                        and attr is not BaseSkill and not getattr(attr, "name", "") in self.skills):
                    try:
                        instance = attr()
                        self.skills[instance.name] = instance
                    except Exception:
                        continue

    def get(self, name: str) -> BaseSkill:
        return self.skills.get(name)

    def list_all(self) -> list:
        return [{"name": s.name, "description": s.description,
                 "version": s.version, "depends_on": s.depends_on}
                for s in self.skills.values()]


_registry = None


def get_registry() -> SkillRegistry:
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
    return _registry
