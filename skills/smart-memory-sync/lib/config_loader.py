#!/usr/bin/env python3
"""
共享配置加载器
优先级：环境变量 > config.json > config.example.json > 默认值
"""
import json
import os
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
DEFAULT_WORKSPACE = Path.home() / '.openclaw' / 'workspace'

DEFAULTS = {
    'thresholds': {'remind': 50, 'auto_sync': 75, 'auto_switch': 85},
    'intervals': {'check': 300, 'sync': 3600},
    'paths': {
        'workspace': '',
        'memory': 'MEMORY.md',
        'memory_lite': 'MEMORY-LITE.md',
        'daily_log': 'memory/',
        'knowledge': 'knowledge/',
    },
    'integrations': {
        'context_manager': {'enabled': True, 'skill': 'context-manager'},
        'qmd': {'enabled': True, 'collection': 'knowledge'},
        'git': {'enabled': True, 'auto_push': False},
    },
    'notifications': {
        'qqbot': {'enabled': True, 'target': ''},
    },
}

# 环境变量映射
ENV_MAP = {
    'SMS_THRESHOLD_REMIND': ('thresholds', 'remind', int),
    'SMS_THRESHOLD_SYNC': ('thresholds', 'auto_sync', int),
    'SMS_THRESHOLD_SWITCH': ('thresholds', 'auto_switch', int),
    'SMS_INTERVAL_CHECK': ('intervals', 'check', int),
    'SMS_INTERVAL_SYNC': ('intervals', 'sync', int),
    'SMS_WORKSPACE': ('paths', 'workspace', str),
    'SMS_QMD_COLLECTION': ('integrations', 'qmd', 'collection'),
    'SMS_GIT_AUTO_PUSH': ('integrations', 'git', 'auto_push'),
    'SMS_QQBOT_TARGET': ('notifications', 'qqbot', 'target'),
}


def _deep_get(d, keys):
    """安全获取嵌套字典值"""
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k, {})
        else:
            return None
    return d


def _deep_set(d, keys, value):
    """安全设置嵌套字典值"""
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = value


def _deep_merge(base, override):
    """深度合并字典"""
    result = base.copy()
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def _load_json(path):
    """加载JSON文件"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def load_config():
    """加载配置：config.json > config.example.json > 默认值，再叠加环境变量"""
    config = _deep_merge(DEFAULTS, _load_json(SKILL_ROOT / 'config.example.json'))
    config = _deep_merge(config, _load_json(SKILL_ROOT / 'config.json'))

    # 环境变量覆盖
    for env_key, path in ENV_MAP.items():
        val = os.environ.get(env_key)
        if val is not None:
            *keys, field = path
            if len(keys) == 2:
                # e.g. ('integrations', 'qmd', 'collection') - last is the leaf field
                _deep_set(config, keys, val)
            elif len(keys) == 1:
                _deep_set(config, keys, val)

    # 特殊处理：workspace 路径展开
    ws = config['paths'].get('workspace', '')
    config['paths']['_resolved_workspace'] = Path(ws).expanduser() if ws else DEFAULT_WORKSPACE

    return config


def get_workspace(config=None):
    """获取workspace绝对路径"""
    if config is None:
        config = load_config()
    return config['paths']['_resolved_workspace']


def get_log_path():
    """获取日志路径"""
    return SKILL_ROOT / 'logs' / 'monitor.log'
