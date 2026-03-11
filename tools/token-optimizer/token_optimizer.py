#!/usr/bin/env python3
"""
Token优化器 - 基于Hazel_OC方法

功能：
1. 分类统计输出（人类/机器）
2. 识别浪费点
3. 生成优化建议
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class TokenOptimizer:
    """Token优化器"""

    def __init__(self):
        self.categories = {
            "human": 0,      # 给人类的输出
            "tool_orchestration": 0,  # 工具编排（JSON/API）
            "agent_delegation": 0,     # 代理委托
            "community": 0,   # 社区互动（Moltbook等）
            "logs": 0         # 日志和记忆文件
        }
        self.total_tokens = 0
        self.waste_points = []
        self.optimization_suggestions = []

    def classify_output(self, content: str, context: str) -> str:
        """
        分类输出内容

        Args:
            content: 输出内容
            context: 上下文（tool/human/agent/community/log）

        Returns:
            分类名称
        """
        content_lower = content.lower()

        # 工具编排
        if any(keyword in content_lower for keyword in
               ['json', 'api', 'function', 'tool', 'execute', 'curl', 'git']):
            return "tool_orchestration"

        # 代理委托
        if any(keyword in content_lower for keyword in
               ['spawn', 'sub-agent', 'delegate', 'task description']):
            return "agent_delegation"

        # 社区互动
        if any(keyword in content_lower for keyword in
               ['moltbook', 'post', 'comment', 'community']):
            return "community"

        # 日志和记忆
        if any(keyword in content_lower for keyword in
               ['memory', 'log', 'state', 'tracking']):
            return "logs"

        # 默认：给人类
        return "human"

    def count_tokens(self, text: str) -> int:
        """
        粗略估算token数量（按空格分词）

        Args:
            text: 文本内容

        Returns:
            token数量估算
        """
        # 粗略估算：中文按字符，英文按空格分词
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        english_words = len(text.split())
        return chinese_chars + english_words

    def identify_waste(self, category: str, content: str, token_count: int):
        """
        识别浪费点

        Args:
            category: 分类
            content: 内容
            token_count: token数量
        """
        # 工具编排：检查JSON错误风险
        if category == "tool_orchestration":
            if 'json' in content.lower() and token_count > 200:
                self.waste_points.append({
                    "type": "large_json",
                    "tokens": token_count,
                    "suggestion": "使用结构化输出模板，减少参数冗余"
                })

        # 代理委托：检查开销比
        if category == "agent_delegation":
            if token_count > 150:
                self.waste_points.append({
                    "type": "high_overhead",
                    "tokens": token_count,
                    "suggestion": "简化任务描述，避免过度委托"
                })

    def generate_suggestions(self) -> List[Dict]:
        """
        生成优化建议

        Returns:
            优化建议列表
        """
        suggestions = []

        # 工具编排优化
        if self.categories["tool_orchestration"] > self.total_tokens * 0.25:
            suggestions.append({
                "category": "tool_orchestration",
                "priority": "high",
                "suggestion": "实现结构化输出模板",
                "expected_saving": "30%"
            })

        # 代理委托优化
        if self.categories["agent_delegation"] > self.total_tokens * 0.15:
            suggestions.append({
                "category": "agent_delegation",
                "priority": "medium",
                "suggestion": "减少不必要的委托，简化任务描述",
                "expected_saving": "20%"
            })

        # 重复调用检查
        if len(self.waste_points) > 5:
            suggestions.append({
                "category": "caching",
                "priority": "high",
                "suggestion": "实现工具调用缓存",
                "expected_saving": "15%"
            })

        return suggestions

    def generate_report(self) -> Dict:
        """
        生成报告

        Returns:
            完整报告
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tokens": self.total_tokens,
                "categories": self.categories,
                "percentages": {
                    cat: (count / self.total_tokens * 100) if self.total_tokens > 0 else 0
                    for cat, count in self.categories.items()
                }
            },
            "waste_points": self.waste_points,
            "suggestions": self.generate_suggestions(),
            "comparison": {
                "hazel_oc": {
                    "human": 38,
                    "tool_orchestration": 27,
                    "agent_delegation": 19,
                    "community": 11,
                    "logs": 5
                },
                "current": {
                    cat: (count / self.total_tokens * 100) if self.total_tokens > 0 else 0
                    for cat, count in self.categories.items()
                }
            }
        }

        return report

    def save_report(self, filepath: str = None):
        """
        保存报告

        Args:
            filepath: 文件路径
        """
        if filepath is None:
            filepath = f"token_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report = self.generate_report()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return filepath


if __name__ == "__main__":
    # 示例使用
    optimizer = TokenOptimizer()

    # 模拟输出
    test_outputs = [
        ("这是一段给人类的回复", "human"),
        ('{"command": "git status"}', "tool"),
        ("Spawn sub-agent to handle task", "agent"),
        ("Moltbook post content", "community"),
        ("Memory log entry", "log")
    ]

    for content, context in test_outputs:
        category = optimizer.classify_output(content, context)
        tokens = optimizer.count_tokens(content)
        optimizer.categories[category] += tokens
        optimizer.total_tokens += tokens
        optimizer.identify_waste(category, content, tokens)

    # 生成报告
    report_path = optimizer.save_report()
    print(f"报告已保存到：{report_path}")

    # 打印摘要
    print("\n📊 Token分类统计：")
    for cat, count in optimizer.categories.items():
        percentage = (count / optimizer.total_tokens * 100) if optimizer.total_tokens > 0 else 0
        print(f"  {cat}: {count} tokens ({percentage:.1f}%)")
