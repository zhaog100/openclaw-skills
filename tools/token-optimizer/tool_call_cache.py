#!/usr/bin/env python3
"""
工具调用缓存 - 避免重复API请求

功能：
1. 缓存工具调用结果
2. 检查重复调用
3. 自动清理过期缓存
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional


class ToolCallCache:
    """工具调用缓存"""

    def __init__(self, cache_dir: str = ".cache/tool_calls", ttl: int = 3600):
        """
        初始化缓存

        Args:
            cache_dir: 缓存目录
            ttl: 缓存有效期（秒）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl

    def _get_cache_key(self, tool_name: str, params: Dict) -> str:
        """
        生成缓存键

        Args:
            tool_name: 工具名称
            params: 参数

        Returns:
            缓存键
        """
        param_str = json.dumps(params, sort_keys=True)
        hash_obj = hashlib.md5(f"{tool_name}:{param_str}".encode())
        return hash_obj.hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """
        获取缓存文件路径

        Args:
            cache_key: 缓存键

        Returns:
            文件路径
        """
        return self.cache_dir / f"{cache_key}.json"

    def get(self, tool_name: str, params: Dict) -> Optional[Dict]:
        """
        获取缓存结果

        Args:
            tool_name: 工具名称
            params: 参数

        Returns:
            缓存结果（如果存在且未过期）
        """
        cache_key = self._get_cache_key(tool_name, params)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)

            # 检查是否过期
            if time.time() - cached_data["timestamp"] > self.ttl:
                cache_path.unlink()  # 删除过期缓存
                return None

            return cached_data["result"]

        except (json.JSONDecodeError, KeyError):
            return None

    def set(self, tool_name: str, params: Dict, result: Dict):
        """
        设置缓存

        Args:
            tool_name: 工具名称
            params: 参数
            result: 结果
        """
        cache_key = self._get_cache_key(tool_name, params)
        cache_path = self._get_cache_path(cache_key)

        cached_data = {
            "tool_name": tool_name,
            "params": params,
            "result": result,
            "timestamp": time.time()
        }

        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cached_data, f, ensure_ascii=False, indent=2)

    def clear_expired(self):
        """清理过期缓存"""
        current_time = time.time()

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)

                if current_time - cached_data["timestamp"] > self.ttl:
                    cache_file.unlink()

            except (json.JSONDecodeError, KeyError):
                cache_file.unlink()

    def get_stats(self) -> Dict:
        """
        获取缓存统计

        Returns:
            统计信息
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            "total_entries": len(cache_files),
            "total_size_mb": total_size / (1024 * 1024),
            "cache_dir": str(self.cache_dir)
        }


if __name__ == "__main__":
    # 示例使用
    cache = ToolCallCache()

    # 模拟工具调用
    tool_name = "web_search"
    params = {"query": "test", "limit": 10}

    # 检查缓存
    cached_result = cache.get(tool_name, params)
    if cached_result:
        print("✅ 从缓存获取结果")
        print(cached_result)
    else:
        print("❌ 缓存未命中，执行工具调用...")
        # 模拟工具调用结果
        result = {"results": ["result1", "result2"]}
        cache.set(tool_name, params, result)
        print("✅ 结果已缓存")

    # 获取统计
    stats = cache.get_stats()
    print(f"\n📊 缓存统计：{stats}")
