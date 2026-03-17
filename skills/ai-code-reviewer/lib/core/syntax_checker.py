#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语法检查器（SyntaxChecker）

使用 tree-sitter 进行语法解析和检查

**版本**：v1.0
**创建时间**：2026-03-16 00:20
**创建者**：小米粒（Dev 代理）🌾
"""

from tree_sitter import Language, Parser
import tree_sitter_python
import tree_sitter_bash
from typing import Dict, List, Any


class SyntaxChecker:
    """语法检查器"""
    
    def __init__(self):
        """初始化语法检查器"""
        self.parsers = {
            'python': Parser(Language(tree_sitter_python.language())),
            'bash': Parser(Language(tree_sitter_bash.language()))
        }
    
    def check(self, code: str, file_path: str) -> List[Dict]:
        """
        检查语法错误
        
        Args:
            code: 代码内容
            file_path: 文件路径
        
        Returns:
            语法错误列表
        """
        issues = []
        
        # 检测文件类型
        if file_path.endswith('.py'):
            lang = 'python'
        elif file_path.endswith('.sh'):
            lang = 'bash'
        else:
            return issues
        
        # 解析代码
        parser = self.parsers.get(lang)
        if not parser:
            return issues
        
        tree = parser.parse(bytes(code, 'utf8'))
        
        # 检查语法错误
        if tree.root_node.has_error:
            issues.append({
                'type': 'syntax',
                'subtype': 'syntax_error',
                'line': tree.root_node.start_point[0] + 1,
                'message': '语法错误，请检查代码',
                'severity': 'high'
            })
        
        return issues


# 测试入口
if __name__ == '__main__':
    checker = SyntaxChecker()
    
    # 测试正确代码
    correct_code = '''
def hello():
    print("Hello, World!")
'''
    issues = checker.check(correct_code, 'test.py')
    print(f"正确代码：{len(issues)} 个问题")
    
    # 测试错误代码
    error_code = '''
def hello(
    print("Hello, World!")
'''
    issues = checker.check(error_code, 'test.py')
    print(f"错误代码：{len(issues)} 个问题")
    for issue in issues:
        print(f"  - {issue['message']}")
