# Copyright (c) 2026 思捷娅科技 (SJYKJ)

"""
ConfigManager — 确定性参数管理器
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List


@dataclass
class DeterministicConfig:
    """确定性控制核心配置"""
    temperature: float = 0.3
    top_p: float = 0.9
    seed: Optional[int] = None
    active_preset: Optional[str] = None

    def to_dict(self):
        d = {"temperature": self.temperature, "top_p": self.top_p}
        if self.seed is not None:
            d["seed"] = self.seed
        return d

    @classmethod
    def from_dict(cls, d):
        return cls(
            temperature=d.get("temperature", 0.3),
            top_p=d.get("top_p", 0.9),
            seed=d.get("seed"),
            active_preset=d.get("active_preset"),
        )


class ConfigManager:
    PRESETS_FILE = "default.json"
    CONFIG_FILE = "detcontrol_config.json"

    def __init__(self, skill_dir=None, config_dir=None):
        self.skill_dir = skill_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_dir = config_dir or self.skill_dir
        self.presets_path = os.path.join(self.skill_dir, "presets", self.PRESETS_FILE)
        self.config_path = os.path.join(self.config_dir, "data", self.CONFIG_FILE)
        self.presets = self._load_presets()
        self.config = self._load_config()

    def set_temperature(self, value):
        """设置温度，范围 [0.0, 2.0]"""
        clamped = max(0.0, min(2.0, value))
        warning = None
        if clamped != value:
            warning = "temperature clamped to [0.0, 2.0]"
        self.config["temperature"] = clamped
        self._save_config()
        result = {"status": "ok", "temperature": clamped}
        if warning:
            result["warning"] = warning
        return result

    def set_top_p(self, value):
        """设置 top_p，范围 [0.0, 1.0]"""
        clamped = max(0.0, min(1.0, value))
        warning = None
        if clamped != value:
            warning = "top_p clamped to [0.0, 1.0]"
        self.config["top_p"] = clamped
        self._save_config()
        result = {"status": "ok", "top_p": clamped}
        if warning:
            result["warning"] = warning
        return result

    def set_seed(self, value):
        """设置随机种子"""
        self.config["seed"] = int(value)
        self._save_config()
        return {"status": "ok", "seed": int(value)}

    def apply_preset(self, name):
        """应用场景预设"""
        if name not in self.presets:
            available = list(self.presets.keys())
            return {"status": "error", "message": f"preset '{name}' not found", "available": available}
        preset = self.presets[name]
        self.config["temperature"] = preset["temperature"]
        self.config["top_p"] = preset["top_p"]
        self.config["seed"] = preset.get("seed")
        self.config["active_preset"] = name
        self._save_config()
        return {"status": "ok", "preset": name, "config": self.config.copy()}

    def get_config(self):
        """获取当前配置"""
        return DeterministicConfig.from_dict(self.config)

    def list_presets(self):
        """列出所有预设"""
        result = {}
        for k, v in self.presets.items():
            result[k] = {"name": v.get("name", k), "temperature": v["temperature"],
                         "top_p": v["top_p"], "description": v.get("description", "")}
        return result

    def _load_presets(self):
        try:
            with open(self.presets_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("presets", {})
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _load_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"temperature": 0.3, "top_p": 0.9, "seed": None, "active_preset": None}
        except json.JSONDecodeError:
            return {"temperature": 0.3, "top_p": 0.9, "seed": None, "active_preset": None}

    def _save_config(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        self.config["last_modified"] = "auto"
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
