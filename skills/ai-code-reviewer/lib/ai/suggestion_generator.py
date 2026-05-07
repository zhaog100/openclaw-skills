#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进建议生成器（SuggestionGenerator）

基于 AI 生成改进建议，支持 AI 辩论机制减少误报

**版本**：v1.0
**创建时间**：2026-03-15 23:45
**创建者**：小米粒（Dev 代理）🌾
"""

import json
from typing import Dict, List, Any


class SuggestionGenerator:
    """改进建议生成器"""
    
    def __init__(self, ai_engine=None):
        """
        初始化建议生成器
        
        Args:
            ai_engine: AI 引擎（可选，Phase 2 集成）
        """
        self.ai_engine = ai_engine
    
    def generate_suggestions(self, issues: Dict[str, List[Dict]]) -> List[Dict]:
        """
        为所有问题生成改进建议
        
        Args:
            issues: 问题列表（来自 CodeQualityDetector）
        
        Returns:
            改进建议列表
        """
        suggestions = []
        
        # Phase 1：基于规则的简单建议
        for category, issue_list in issues.items():
            for issue in issue_list:
                suggestion = self._generate_rule_based_suggestion(issue)
                if suggestion:
                    suggestions.append(suggestion)
        
        # Phase 2：AI 生成建议（待集成）
        # if self.ai_engine:
        #     suggestions = self._generate_ai_suggestions(issues)
        
        return suggestions
    
    def _generate_rule_based_suggestion(self, issue: Dict) -> Dict:
        """
        基于规则生成建议（Phase 1）
        
        Args:
            issue: 问题字典
        
        Returns:
            建议字典
        """
        issue_type = issue.get('type', '')
        subtype = issue.get('subtype', '')
        
        # 安全检查建议
        if issue_type == 'security':
            if subtype == 'sql_injection':
                return {
                    'issue': issue,
                    'suggestion': '使用参数化查询代替字符串拼接',
                    'example': '''# 错误示例
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# 正确示例
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))''',
                    'priority': 'high'
                }
            elif subtype == 'xss':
                return {
                    'issue': issue,
                    'suggestion': '对用户输入进行 HTML 转义',
                    'example': '''# 使用 html.escape() 转义用户输入
import html
safe_content = html.escape(user_input)''',
                    'priority': 'high'
                }
            elif subtype == 'hardcoded_password':
                return {
                    'issue': issue,
                    'suggestion': '使用环境变量或配置文件存储密码',
                    'example': '''# 错误示例
password = "admin123"

# 正确示例
import os
password = os.getenv('DB_PASSWORD')''',
                    'priority': 'high'
                }
        
        # 规范检查建议
        elif issue_type == 'standards':
            if subtype == 'line_length':
                return {
                    'issue': issue,
                    'suggestion': '将长行拆分为多行',
                    'example': '''# 使用括号隐式续行
result = (
    long_function_name(
        arg1, arg2, arg3
    )
)''',
                    'priority': 'low'
                }
        
        # 默认建议
        return {
            'issue': issue,
            'suggestion': f'修复{issue_type}问题：{issue.get("message", "")}',
            'example': '# 请根据具体问题修复',
            'priority': issue.get('severity', 'medium')
        }
    
    def _generate_ai_suggestions(self, issues: Dict) -> List[Dict]:
        """
        基于 AI 生成建议（Phase 2 待实现）
        
        Args:
            issues: 问题列表
        
        Returns:
            AI 生成的建议列表
        """
        # TODO: Phase 2 集成 AI 引擎
        # 1. 调用 AI 引擎生成建议
        # 2. AI 辩论机制验证
        # 3. 返回最终建议
        return []
    
    def debate_verify(self, suggestion_a: Dict, suggestion_b: Dict) -> Dict:
        """
        AI 辩论验证（Phase 2 待实现）
        
        Args:
            suggestion_a: 模型 A 的建议
            suggestion_b: 模型 B 的建议
        
        Returns:
            最终建议
        """
        # TODO: Phase 2 实现 AI 辩论机制
        return suggestion_a


# 测试入口
if __name__ == '__main__':
    # 测试数据
    test_issues = {
        'security': [
            {
                'type': 'security',
                'subtype': 'sql_injection',
                'line': 10,
                'message': '检测到 SQL 查询，建议使用参数化查询',
                'severity': 'high'
            }
        ],
        'standards': [
            {
                'type': 'standards',
                'subtype': 'line_length',
                'line': 25,
                'message': '行长度超过 120 字符',
                'severity': 'low'
            }
        ]
    }
    
    # 生成建议
    generator = SuggestionGenerator()
    suggestions = generator.generate_suggestions(test_issues)
    
    # 输出结果
    print(json.dumps(suggestions, indent=2, ensure_ascii=False))
