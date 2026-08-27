# Copyright (c) 2026 思捷娅科技 (SJYKJ)

"""
ModelBridge — OpenClaw 模型参数桥接
"""

import json
import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict

from config_manager import DeterministicConfig


class ModelBridge:
    OPENCLAW_CONFIG = "~/.openclaw/openclaw.json"

    def __init__(self, config_path=None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path(self.OPENCLAW_CONFIG).expanduser()
        self._backup_path = None

    def inject_params(self, config, dry_run=False):
        """将确定性参数注入所有模型"""
        self._backup_config()
        data = self._read_config()
        try:
            for model_name in data.get("models", {}):
                self._inject_to_model(data["models"][model_name], config)
            if not dry_run:
                json.dumps(data, ensure_ascii=False)
                self._write_config(data)
        except (json.JSONDecodeError, Exception) as e:
            self._restore_config()
            raise RuntimeError("写入失败，已恢复备份: {}".format(e))
        return data

    def inject_model_params(self, model_name, config):
        """只注入指定模型"""
        self._backup_config()
        data = self._read_config()
        try:
            if model_name in data.get("models", {}):
                self._inject_to_model(data["models"][model_name], config)
            json.dumps(data, ensure_ascii=False)
            self._write_config(data)
        except Exception as e:
            self._restore_config()
            raise RuntimeError("写入失败，已恢复备份: {}".format(e))
        return data

    def read_current(self):
        """读取当前配置"""
        return self._read_config()

    def reset_params(self, targets=None):
        """恢复默认参数"""
        defaults = {"temperature": 0.3, "top_p": 0.9, "seed": None}
        if targets is None:
            targets = list(defaults.keys())
        self._backup_config()
        data = self._read_config()
        try:
            for model_name in data.get("models", {}):
                params = data["models"][model_name].get("parameters", {})
                for key in targets:
                    if key in defaults:
                        params[key] = defaults[key]
                data["models"][model_name]["parameters"] = params
            json.dumps(data, ensure_ascii=False)
            self._write_config(data)
        except Exception as e:
            self._restore_config()
            raise RuntimeError("重置失败，已恢复备份: {}".format(e))
        return data

    def _inject_to_model(self, model_cfg, config):
        if "parameters" not in model_cfg:
            model_cfg["parameters"] = {}
        model_cfg["parameters"]["temperature"] = config.temperature
        model_cfg["parameters"]["top_p"] = config.top_p
        if config.seed is not None:
            model_cfg["parameters"]["seed"] = config.seed

    def _backup_config(self):
        if self.config_path.exists():
            self._backup_path = self.config_path.with_suffix(".json.bak")
            shutil.copy2(str(self.config_path), str(self._backup_path))

    def _restore_config(self):
        if self._backup_path and self._backup_path.exists():
            shutil.copy2(str(self._backup_path), str(self.config_path))

    def _read_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"models": {}}
        except json.JSONDecodeError:
            return {"models": {}}

    def _write_config(self, data):
        os.makedirs(self.config_path.parent, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
