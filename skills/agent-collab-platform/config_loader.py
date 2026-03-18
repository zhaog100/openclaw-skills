"""统一配置加载器 - 环境变量优先，配置文件次之"""
import json
import os

_CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
_CONFIG_FILE = os.path.join(_CONFIG_DIR, 'config.json')

_cache = {}

def get(key, default=None):
    if not _cache and os.path.isfile(_CONFIG_FILE):
        with open(_CONFIG_FILE) as f:
            _cache.update(json.load(f))
    return os.environ.get(key.upper(), _cache.get(key, default))

def get_repo():
    return get('github_repo', 'zhaog100/openclaw-skills')

def get_interval():
    return int(get('check_interval', 30))
