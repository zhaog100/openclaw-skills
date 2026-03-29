#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置加载器 - 统一配置管理
环境变量优先级高于 config.json
敏感信息（token/cookie）仅通过环境变量传入
"""

import json
import os
from pathlib import Path


# 环境变量名映射（env_var -> config_key）
ENV_MAP = {
    # 推送配置
    "WOOL_SERVERCHAN_KEY": ("push_config", "serverchan_key"),
    "WOOL_PUSHPLUS_TOKEN": ("push_config", "pushplus_token"),
    "WOOL_DINGTALK_TOKEN": ("push_config", "dingtalk_token"),
    "WOOL_DINGTALK_SECRET": ("push_config", "dingtalk_secret"),
    # 邮件配置
    "WOOL_EMAIL_SMTP": ("push_config", "email_config", "smtp_server"),
    "WOOL_EMAIL_PORT": ("push_config", "email_config", "smtp_port"),
    "WOOL_EMAIL_FROM": ("push_config", "email_config", "from_addr"),
    "WOOL_EMAIL_PASSWORD": ("push_config", "email_config", "password"),
    "WOOL_EMAIL_TO": ("push_config", "email_config", "to_addr"),
    # 数据库
    "WOOL_DB_PATH": ("db_path",),
    # 通用
    "WOOL_THRESHOLD": ("threshold",),
}

# Skill 根目录
SKILL_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = SKILL_ROOT / "config.json"
DATA_DIR = SKILL_ROOT / "data"


def _deep_get(d, keys):
    """深度获取嵌套字典值"""
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k)
        else:
            return None
    return d


def _deep_set(d, keys, value):
    """深度设置嵌套字典值"""
    for k in keys[:-1]:
        if k not in d or not isinstance(d[k], dict):
            d[k] = {}
        d = d[k]
    d[keys[-1]] = value


def load_config(config_path=None):
    """
    加载配置，环境变量优先级高于 config.json

    Args:
        config_path: 自定义配置文件路径，默认使用 skill 根目录的 config.json

    Returns:
        dict: 合并后的配置
    """
    path = Path(config_path) if config_path else CONFIG_PATH

    # 默认配置
    config = {
        "db_path": str(DATA_DIR / "price_history.db"),
        "threshold": 0.8,
        "items": [],
        "push_config": {
            "enabled": False,
            "serverchan_enabled": False,
            "serverchan_key": "",
            "pushplus_enabled": False,
            "pushplus_token": "",
            "dingtalk_enabled": False,
            "dingtalk_token": "",
            "dingtalk_secret": "",
            "email_enabled": False,
            "email_config": {},
        },
        "price_monitor": {"enabled": True, "interval": 3600, "history_days": 30},
    }

    # 从文件加载
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                file_config = json.load(f)
            _merge(config, file_config)
        except Exception:
            pass

    # 环境变量覆盖
    for env_var, keys in ENV_MAP.items():
        val = os.environ.get(env_var)
        if val is not None:
            # 端口号转 int
            if env_var == "WOOL_EMAIL_PORT":
                try:
                    val = int(val)
                except ValueError:
                    continue
            _deep_set(config, keys, val)

    # 确保数据目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    return config


def _merge(base, override):
    """深度合并字典，override 覆盖 base"""
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _merge(base[k], v)
        else:
            base[k] = v
