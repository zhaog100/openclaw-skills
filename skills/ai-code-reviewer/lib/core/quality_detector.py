#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码质量检测器（CodeQualityDetector）

5 层代码质量检查：
1. 语法检查（tree-sitter）
2. 代码规范（命名、格式）
3. 逻辑检查（潜在 bug、死代码）
4. 性能检查（时间复杂度、内存泄漏）
5. 安全检查（SQL 注入、XSS 漏洞）

**版本**：v1.0
**创建时间**：2026-03-15 22:45
**创建者**：小米粒（Dev 代理）🌾
"""

import os
import json
from typing import Dict, List, Any


class CodeQualityDetector:
    """代码质量检测器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化检测器
        
        Args:
            config_path: 配置文件路径（YAML 格式）
        """
        self.config_path = config_path
        self.rules = self._load_rules(config_path) if config_path else {}
        self.parser = None  # tree-sitter 解析器（后续集成）
    
    def _load_rules(self, config_path: str) -> Dict:
        """加载规则配置"""
        # TODO: 使用 PyYAML 加载 rules.yaml
        return {
            'naming': {
                'function': r'^[a-z][a-zA-Z0-9_]*$',
                'variable': r'^[a-z][a-zA-Z0-9_]*$',
                'class': r'^[A-Z][a-zA-Z0-9]*$'
            },
            'security': {
                'sql_injection': ['SELECT * FROM', 'DROP TABLE'],
                'xss': ['<script>', 'javascript:']
            }
        }
    
    def detect(self, file_path: str) -> Dict[str, List[Dict]]:
        """
        执行 5 层代码质量检查
        
        Args:
            file_path: 代码文件路径
        
        Returns:
            问题列表（JSON 格式）
            {
                'syntax': [...],
                'standards': [...],
                'logic': [...],
                'performance': [...],
                'security': [...]
            }
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在：{file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        results = {
            'syntax': self._check_syntax(code, file_path),
            'standards': self._check_standards(code, file_path),
            'logic': self._check_logic(code, file_path),
            'performance': self._check_performance(code, file_path),
            'security': self._check_security(code, file_path)
        }
        
        return results
    
    def _check_syntax(self, code: str, file_path: str) -> List[Dict]:
        """
        第 1 层：语法检查（tree-sitter）
        
        TODO: 集成 tree-sitter 进行语法解析
        """
        issues = []
        # TODO: 使用 tree-sitter 解析语法错误
        # self.parser = TreeSitterParser()
        # errors = self.parser.parse(code)
        # for error in errors:
        #     issues.append({
        #         'type': 'syntax',
        #         'line': error.line,
        #         'column': error.column,
        #         'message': error.message,
        #         'severity': 'high'
        #     })
        return issues
    
    def _check_standards(self, code: str, file_path: str) -> List[Dict]:
        """
        第 2 层：代码规范检查
        
        检查项：
        - 命名规范（函数、变量、类）
        - 格式规范（缩进、空行、行长度）
        """
        issues = []
        lines = code.split('\n')
        
        # 检查行长度（最大 120 字符）
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append({
                    'type': 'standards',
                    'subtype': 'line_length',
                    'line': i,
                    'message': f'行长度超过 120 字符（当前{len(line)}字符）',
                    'severity': 'low'
                })
        
        # 检查命名规范（简单示例）
        # TODO: 使用正则表达式检查函数、变量、类命名
        
        return issues
    
    def _check_logic(self, code: str, file_path: str) -> List[Dict]:
        """
        第 3 层：逻辑检查
        
        检查项：
        - 潜在 bug（空指针、资源泄漏）
        - 死代码（未使用的变量、不可达代码）
        """
        issues = []
        # TODO: 使用 AST 分析逻辑问题
        return issues
    
    def _check_performance(self, code: str, file_path: str) -> List[Dict]:
        """
        第 4 层：性能检查
        
        检查项：
        - 时间复杂度（嵌套循环）
        - 内存泄漏（未释放资源）
        - 低效操作（重复计算）
        """
        issues = []
        # TODO: 分析性能问题
        return issues
    
    def _check_security(self, code: str, file_path: str) -> List[Dict]:
        """
        第 5 层：安全检查
        
        检查项：
        - SQL 注入
        - XSS 漏洞
        - 硬编码密码
        """
        issues = []
        
        # 检查 SQL 注入
        if 'SELECT * FROM' in code:
            issues.append({
                'type': 'security',
                'subtype': 'sql_injection',
                'line': 0,
                'message': '检测到 SQL 查询，建议使用参数化查询',
                'severity': 'high'
            })
        
        # 检查 XSS
        if '<script>' in code:
            issues.append({
                'type': 'security',
                'subtype': 'xss',
                'line': 0,
                'message': '检测到 script 标签，注意 XSS 风险',
                'severity': 'high'
            })
        
        # 检查硬编码密码
        if 'password' in code.lower() and '=' in code:
            issues.append({
                'type': 'security',
                'subtype': 'hardcoded_password',
                'line': 0,
                'message': '检测到硬编码密码，建议使用配置文件',
                'severity': 'high'
            })
        
        return issues
    
    def detect_directory(self, dir_path: str, extensions: List[str] = None) -> Dict[str, Dict]:
        """
        递归扫描目录中的所有代码文件
        
        Args:
            dir_path: 目录路径
            extensions: 文件扩展名列表（默认：['.py', '.sh', '.js']）
        
        Returns:
            所有文件的问题列表
        """
        if extensions is None:
            extensions = ['.py', '.sh', '.js']
        
        results = {}
        
        for root, dirs, files in os.walk(dir_path):
            # 跳过隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    try:
                        results[file_path] = self.detect(file_path)
                    except Exception as e:
                        results[file_path] = {'error': str(e)}
        
        return results


# 测试入口
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python quality_detector.py <文件路径>")
        sys.exit(1)
    
    detector = CodeQualityDetector()
    results = detector.detect(sys.argv[1])
    
    # 输出 JSON 格式结果
    print(json.dumps(results, indent=2, ensure_ascii=False))
