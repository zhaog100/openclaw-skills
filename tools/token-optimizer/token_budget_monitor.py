#!/usr/bin/env python3
"""
Token预算监控器 - 工具调用参数<200 tokens

基于Hazel_OC方法：减少冗余参数
"""

import json
from typing import Dict, List, Tuple

class TokenBudgetMonitor:
    """Token预算监控器"""

    def __init__(self, max_tokens: int = 200):
        """
        初始化

        Args:
            max_tokens: 最大token数（默认200）
        """
        self.max_tokens = max_tokens
        self.budget_alerts = []

    def estimate_tokens(self, text: str) -> int:
        """
        估算token数（粗略估算：1 token ≈ 4 字符）

        Args:
            text: 文本

        Returns:
            token估算数
        """
        if not text:
            return 0
        return len(str(text)) // 4

    def check_tool_call(self, tool_name: str, params: Dict) -> Tuple[bool, str]:
        """
        检查工具调用参数是否符合预算

        Args:
            tool_name: 工具名称
            params: 参数

        Returns:
            (是否通过, 消息)
        """
        # 计算参数总token数
        params_str = json.dumps(params, ensure_ascii=False)
        total_tokens = self.estimate_tokens(params_str)

        # 检查预算
        if total_tokens > self.max_tokens:
            message = f"⚠️ 工具调用 '{tool_name}' 参数超预算：{total_tokens} tokens > {self.max_tokens} tokens"
            self.budget_alerts.append({
                "tool_name": tool_name,
                "tokens": total_tokens,
                "max_tokens": self.max_tokens,
                "message": message
            })
            return False, message

        return True, f"✅ 工具调用 '{tool_name}' 参数符合预算：{total_tokens}/{self.max_tokens} tokens"

    def get_budget_alerts(self) -> List[Dict]:
        """
        获取预算警告列表

        Returns:
            警告列表
        """
        return self.budget_alerts

    def get_budget_stats(self) -> Dict:
        """
        获取预算统计

        Returns:
            统计信息
        """
        if not self.budget_alerts:
            return {
                "total_alerts": 0,
                "avg_over_budget": 0,
                "max_over_budget": 0
            }

        over_budget_tokens = [alert["tokens"] - self.max_tokens for alert in self.budget_alerts]

        return {
            "total_alerts": len(self.budget_alerts),
            "avg_over_budget": sum(over_budget_tokens) / len(over_budget_tokens),
            "max_over_budget": max(over_budget_tokens)
        }

    def suggest_optimization(self, tool_name: str, params: Dict) -> List[str]:
        """
        提供优化建议

        Args:
            tool_name: 工具名称
            params: 参数

        Returns:
            优化建议列表
        """
        suggestions = []

        # 检查冗余参数
        for key, value in params.items():
            if isinstance(value, str) and len(value) > 500:
                suggestions.append(f"参数 '{key}' 过长（{len(value)} 字符），考虑精简")

            if isinstance(value, (list, dict)) and len(json.dumps(value)) > 1000:
                suggestions.append(f"参数 '{key}' 复杂度过高，考虑简化")

        # 检查重复内容
        params_str = json.dumps(params, ensure_ascii=False)
        if params_str.count("query") > 1 or params_str.count("path") > 1:
            suggestions.append("参数中存在重复内容，考虑合并")

        return suggestions


if __name__ == "__main__":
    # 示例使用
    monitor = TokenBudgetMonitor(max_tokens=200)

    # 测试工具调用
    test_cases = [
        {
            "tool_name": "web_search",
            "params": {"query": "Token优化方法", "limit": 10}
        },
        {
            "tool_name": "file_read",
            "params": {
                "path": "/very/long/path/to/file.txt",
                "content": "这是一个非常长的内容" * 50  # 超长内容
            }
        }
    ]

    print("📊 Token预算监控测试：\n")

    for test in test_cases:
        is_valid, message = monitor.check_tool_call(test["tool_name"], test["params"])
        print(message)

        # 提供优化建议
        suggestions = monitor.suggest_optimization(test["tool_name"], test["params"])
        if suggestions:
            print("优化建议：")
            for suggestion in suggestions:
                print(f"  - {suggestion}")

        print()

    # 获取统计
    stats = monitor.get_budget_stats()
    print(f"📊 预算统计：{json.dumps(stats, ensure_ascii=False, indent=2)}")
