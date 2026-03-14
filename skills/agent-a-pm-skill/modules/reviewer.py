#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Review验证模块

功能：
- 代码审查
- 测试验证
- 发布评审
"""

class Reviewer:
    """Review验证器"""
    
    def __init__(self):
        """初始化Review验证器"""
        self.reviews = {}
    
    def review_code(self, pr_number, code):
        """代码审查"""
        review_id = f"review_{len(self.reviews) + 1}"
        
        # 简化审查逻辑
        issues = []
        
        # 检查代码长度
        if len(code) > 10000:
            issues.append("代码过长，建议拆分")
        
        # 检查TODO注释
        if 'TODO' in code:
            issues.append("发现TODO注释，请完善")
        
        # 检查错误处理
        if 'try' not in code and 'except' not in code:
            issues.append("缺少错误处理")
        
        self.reviews[review_id] = {
            'id': review_id,
            'type': 'code',
            'pr_number': pr_number,
            'issues': issues,
            'status': 'approved' if len(issues) == 0 else 'needs_work',
            'created_at': '2026-03-15 01:20'
        }
        
        return review_id, issues
    
    def review_test(self, test_result):
        """测试验证"""
        review_id = f"test_review_{len(self.reviews) + 1}"
        
        passed = test_result.get('passed', 0)
        failed = test_result.get('failed', 0)
        
        self.reviews[review_id] = {
            'id': review_id,
            'type': 'test',
            'passed': passed,
            'failed': failed,
            'status': 'approved' if failed == 0 else 'needs_fix',
            'created_at': '2026-03-15 01:20'
        }
        
        return review_id, passed, failed
    
    def review_publish(self, version, checklist):
        """发布评审"""
        review_id = f"pub_review_{len(self.reviews) + 1}"
        
        # 检查发布清单
        missing = []
        required_items = ['changelog', 'tests_passed', 'docs_updated']
        
        for item in required_items:
            if item not in checklist or not checklist[item]:
                missing.append(item)
        
        self.reviews[review_id] = {
            'id': review_id,
            'type': 'publish',
            'version': version,
            'missing': missing,
            'status': 'approved' if len(missing) == 0 else 'needs_work',
            'created_at': '2026-03-15 01:20'
        }
        
        return review_id, missing
    
    def handle(self, parsed_message):
        """处理Review消息"""
        action = parsed_message.get('action')
        
        if action == 'review_code':
            pr_number = parsed_message.get('pr_number')
            code = parsed_message.get('code', '')
            review_id, issues = self.review_code(pr_number, code)
            
            if len(issues) == 0:
                return f"✅ 代码审查通过：PR #{pr_number}"
            return f"⚠️ 代码需要改进：\n" + "\n".join(f"- {issue}" for issue in issues)
        
        elif action == 'review_test':
            test_result = parsed_message.get('test_result', {})
            review_id, passed, failed = self.review_test(test_result)
            
            if failed == 0:
                return f"✅ 测试全部通过：{passed}个"
            return f"❌ 测试失败：{passed}个通过，{failed}个失败"
        
        elif action == 'review_publish':
            version = parsed_message.get('version')
            checklist = parsed_message.get('checklist', {})
            review_id, missing = self.review_publish(version, checklist)
            
            if len(missing) == 0:
                return f"✅ 发布评审通过：v{version}"
            return f"⚠️ 发布清单缺失：\n" + "\n".join(f"- {item}" for item in missing)
        
        return "❌ 未知操作"
