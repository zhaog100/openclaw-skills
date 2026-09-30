#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单文件缓存（PRD V3.1 §16）
shared/cache.py

官方数据发布后更新一次，其余时间读缓存。
支持 TTL 过期。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import json, time, pickle, os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CACHE_DIR = BASE_DIR / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# 默认 24h TTL（config/model_params.yaml 可覆盖）
TTL_SECONDS = 24 * 3600


def _resolve_ttl():
    """从 config/model_params.yaml 读 TTL（若存在）"""
    try:
        import yaml
        p = BASE_DIR / "config" / "model_params.yaml"
        if p.exists():
            with open(p, encoding='utf-8') as f:
                cfg = yaml.safe_load(f) or {}
            return int(cfg.get('cache', {}).get('ttl_seconds', TTL_SECONDS))
    except Exception:
        pass
    return TTL_SECONDS


def _json_path(key):
    return CACHE_DIR / f"{key}.json"


def _pkl_path(key):
    return CACHE_DIR / f"{key}.pkl"


def cache_get(key, ttl=None):
    """读缓存（JSON 或 pickle），过期返回 None"""
    ttl = ttl if ttl is not None else _resolve_ttl()
    jp = _json_path(key)
    if jp.exists():
        try:
            data = json.loads(jp.read_text(encoding='utf-8'))
            if time.time() - data.get('_ts', 0) > ttl:
                return None
            return data.get('value')
        except Exception:
            pass
    pp = _pkl_path(key)
    if pp.exists():
        if time.time() - pp.stat().st_mtime > ttl:
            return None
        try:
            with open(pp, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return None
    return None


def cache_set(key, value, binary=False):
    """写缓存"""
    if binary:
        with open(_pkl_path(key), 'wb') as f:
            pickle.dump(value, f)
    else:
        _json_path(key).write_text(
            json.dumps({'_ts': time.time(), 'value': value}, ensure_ascii=False, default=str),
            encoding='utf-8')


def invalidate(key):
    """删除缓存"""
    for p in (_json_path(key), _pkl_path(key)):
        if p.exists():
            p.unlink()


if __name__ == '__main__':
    cache_set('test', {'a': 1})
    print("cache_get:", cache_get('test'))
    cache_invalidate = invalidate
    invalidate('test')
    print("after invalidate:", cache_get('test'))
