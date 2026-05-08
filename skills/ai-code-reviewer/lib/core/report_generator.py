#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Review 报告生成器（ReportGenerator）

生成 Markdown 格式的代码审查报告

**版本**：v1.0
**创建时间**：2026-03-15 23:45
**创建者**：小米粒（Dev 代理）🌾
"""

import json
from datetime import datetime
from typing import Dict, List, Any


class ReportGenerator:
    """Review 报告生成器"""
    
    def __init__(self, template_path: str = None):
        """
        初始化报告生成器
        
        Args:
            template_path: 报告模板路径（可选）
        """
        self.template_path = template_path
        self.template = self._load_template()
    
    def _load_template(self) -> Dict:
        """加载报告模板"""
        return {
            'title': '# 代码审查报告',
            'summary': '## 摘要',
            'issues': '## 详细问题',
            'suggestions': '## 改进建议',
            'statistics': '## 统计数据'
        }
    
    def generate(self, issues: Dict, suggestions: List[Dict], file_path: str) -> str:
        """
        生成完整的审查报告
        
        Args:
            issues: 问题列表（来自 CodeQualityDetector）
            suggestions: 建议列表（来自 SuggestionGenerator）
            file_path: 审查的文件路径
        
        Returns:
            Markdown 格式报告
        """
        report = []
        
        # 标题
        report.append(self.template['title'])
        report.append('')
        report.append(f'**审查时间**：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        report.append(f'**审查文件**：{file_path}')
        report.append('')
        
        # 摘要
        report.append(self.template['summary'])
        report.append('')
        summary = self._generate_summary(issues)
        report.append(summary)
        report.append('')
        
        # 详细问题
        report.append(self.template['issues'])
        report.append('')
        for category, issue_list in issues.items():
            if issue_list:
                report.append(f'### {self._get_category_name(category)}（{len(issue_list)}个）')
                report.append('')
                for i, issue in enumerate(issue_list, 1):
                    report.append(f'**{i}. {issue.get("message", "未知问题")}**')
                    report.append(f'- 行号：{issue.get("line", "N/A")}')
                    report.append(f'- 严重程度：{issue.get("severity", "medium")}')
                    report.append('')
        
        # 改进建议
        report.append(self.template['suggestions'])
        report.append('')
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                report.append(f'**{i}. {suggestion.get("suggestion", "无建议")}**')
                report.append(f'- 优先级：{suggestion.get("priority", "medium")}')
                if suggestion.get('example'):
                    report.append('')
                    report.append('```python')
                    report.append(suggestion['example'])
                    report.append('```')
                report.append('')
        else:
            report.append('暂无改进建议')
            report.append('')
        
        # 统计数据
        report.append(self.template['statistics'])
        report.append('')
        statistics = self._generate_statistics(issues)
        report.append(statistics)
        report.append('')
        
        return '\n'.join(report)
    
    def _generate_summary(self, issues: Dict) -> str:
        """生成摘要"""
        total_issues = sum(len(issue_list) for issue_list in issues.values())
        
        # 统计各严重程度
        severity_count = {'high': 0, 'medium': 0, 'low': 0}
        for issue_list in issues.values():
            for issue in issue_list:
                severity = issue.get('severity', 'medium')
                severity_count[severity] = severity_count.get(severity, 0) + 1
        
        # 确定整体严重程度
        if severity_count['high'] > 0:
            overall_severity = '高'
        elif severity_count['medium'] > 0:
            overall_severity = '中'
        else:
            overall_severity = '低'
        
        return f'''- **文件数**：1
- **问题总数**：{total_issues}
- **严重程度**：{overall_severity}
- **高优先级**：{severity_count['high']}
- **中优先级**：{severity_count['medium']}
- **低优先级**：{severity_count['low']}'''
    
    def _generate_statistics(self, issues: Dict) -> str:
        """生成统计数据"""
        stats = []
        for category, issue_list in issues.items():
            if issue_list:
                stats.append(f'- **{self._get_category_name(category)}**：{len(issue_list)}个')
        
        if not stats:
            return '- 无问题'
        
        return '\n'.join(stats)
    
    def _get_category_name(self, category: str) -> str:
        """获取分类的中文名称"""
        category_map = {
            'syntax': '语法问题',
            'standards': '规范问题',
            'logic': '逻辑问题',
            'performance': '性能问题',
            'security': '安全问题'
        }
        return category_map.get(category, category)
    
    def save_report(self, report: str, output_path: str) -> bool:
        """
        保存报告到文件
        
        Args:
            report: 报告内容
            output_path: 输出文件路径
        
        Returns:
            是否成功
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            return True
        except Exception as e:
            print(f'保存报告失败：{e}')
            return False


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
    
    test_suggestions = [
        {
            'suggestion': '使用参数化查询代替字符串拼接',
            'priority': 'high',
            'example': 'cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))'
        }
    ]
    
    # 生成报告
    generator = ReportGenerator()
    report = generator.generate(test_issues, test_suggestions, 'test.py')
    
    # 输出报告
    print(report)
    
    # 保存报告
    # generator.save_report(report, 'code_review_report.md')
