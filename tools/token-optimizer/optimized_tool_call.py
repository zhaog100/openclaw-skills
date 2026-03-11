#!/usr/bin/env python3
"""
Token优化集成 - 工具调用包装器

功能：
1. 调用前检查预算
2. 检查缓存
3. 记录统计
4. 缓存结果
"""

import sys
sys.path.append('/root/.openclaw/workspace/tools/token-optimizer')

from token_budget_monitor import TokenBudgetMonitor
from tool_call_cache import ToolCallCache
from token_optimizer import TokenOptimizer
from typing import Dict, Any, Optional


class OptimizedToolCall:
    """优化的工具调用包装器"""

    def __init__(self):
        self.monitor = TokenBudgetMonitor(max_tokens=200)
        self.cache = ToolCallCache(ttl_seconds=3600)
        self.optimizer = TokenOptimizer()

    def call(self, tool_name: str, params: Dict, executor=None) -> Optional[Dict]:
        """
        优化的工具调用

        Args:
            tool_name: 工具名称
            params: 参数
            executor: 执行函数（可选）

        Returns:
            结果
        """
        # 1. 检查预算
        is_valid, message = self.monitor.check_tool_call(tool_name, params)
        if not is_valid:
            print(f"⚠️ {message}")
            suggestions = self.monitor.suggest_optimization(tool_name, params)
            for suggestion in suggestions:
                print(f"  💡 {suggestion}")
            return None

        # 2. 检查缓存
        cached_result = self.cache.get(tool_name, params)
        if cached_result:
            print(f"✅ 从缓存获取结果: {tool_name}")
            return cached_result

        # 3. 执行工具调用
        print(f"⚙️ 执行工具调用: {tool_name}")
        if executor:
            result = executor(**params)
        else:
            # 模拟结果
            result = {"status": "success", "data": "mock_result"}

        # 4. 缓存结果
        self.cache.set(tool_name, params, result)
        print(f"✅ 结果已缓存: {tool_name}")

        # 5. 记录统计
        self._track_usage(tool_name, params, result)

        return result

    def _track_usage(self, tool_name: str, params: Dict, result: Dict):
        """
        记录使用统计

        Args:
            tool_name: 工具名称
            params: 参数
            result: 结果
        """
        # 分类工具调用
        context = "tool"  # 默认工具编排
        content = str(params) + str(result)

        category = self.optimizer.classify_output(content, context)
        tokens = self.optimizer.count_tokens(content)

        self.optimizer.categories[category] += tokens
        self.optimizer.total_tokens += tokens

    def get_stats(self) -> Dict:
        """
        获取统计信息

        Returns:
            统计信息
        """
        return {
            "token_stats": self.optimizer.get_category_stats(),
            "cache_stats": self.cache.get_stats(),
            "budget_stats": self.monitor.get_budget_stats()
        }


# 全局实例
_global_optimizer = None


def get_optimizer() -> OptimizedToolCall:
    """
    获取全局优化器实例

    Returns:
        优化器实例
    """
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = OptimizedToolCall()
    return _global_optimizer


# 示例使用
if __name__ == "__main__":
    optimizer = OptimizedToolCall()

    # 测试工具调用
    test_cases = [
        {
            "tool_name": "web_search",
            "params": {"query": "Token优化", "limit": 10}
        },
        {
            "tool_name": "file_read",
            "params": {"path": "/test/file.txt", "offset": 0, "limit": 100}
        },
        {
            "tool_name": "web_search",  # 重复调用，应该从缓存获取
            "params": {"query": "Token优化", "limit": 10}
        }
    ]

    print("📊 测试优化工具调用：\n")

    for test in test_cases:
        result = optimizer.call(test["tool_name"], test["params"])
        print()

    # 获取统计
    stats = optimizer.get_stats()
    print("\n📊 统计信息：")
    print(f"缓存统计: {stats['cache_stats']}")
    print(f"预算统计: {stats['budget_stats']}")
