#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开发实现模块

功能：
- 代码编写
- 单元测试
- 代码集成
"""

class Developer:
    """开发者"""
    
    def __init__(self):
        """初始化开发者"""
        self.projects = {}
    
    def develop_feature(self, design_id, feature_name):
        """开发功能"""
        project_id = f"dev_{len(self.projects) + 1}"
        
        self.projects[project_id] = {
            'id': project_id,
            'design_id': design_id,
            'feature': feature_name,
            'state': 'developing',
            'progress': 0,
            'created_at': '2026-03-15 01:11'
        }
        
        return project_id
    
    def write_code(self, project_id, code):
        """编写代码"""
        if project_id not in self.projects:
            return False, "项目不存在"
        
        # 简化代码编写
        lines_of_code = len(code.split('\n'))
        self.projects[project_id]['lines'] = lines_of_code
        
        return True, f"编写代码：{lines_of_code} 行"
    
    def test_code(self, project_id, test_cases):
        """测试代码"""
        if project_id not in self.projects:
            return False, "项目不存在"
        
        # 简化测试
        passed = sum(1 for tc in test_cases if tc.get('expected') == tc.get('actual'))
        failed = len(test_cases) - passed
        
        self.projects[project_id]['test_passed'] = passed
        self.projects[project_id]['test_failed'] = failed
        
        return True, f"测试结果：{passed} 通过，{failed} 失败"
    
    def integrate(self, project_id):
        """集成代码"""
        if project_id not in self.projects:
            return False, "项目不存在"
        
        self.projects[project_id]['state'] = 'testing'
        return True, f"代码集成完成：{project_id}"
    
    def handle(self, parsed_message):
        """处理开发消息"""
        action = parsed_message.get('action')
        
        if action == 'develop':
            design_id = parsed_message.get('design_id')
            feature = parsed_message.get('feature')
            project_id = self.develop_feature(design_id, feature)
            return f"✅ 开发项目创建：{project_id}"
        
        elif action == 'write_code':
            project_id = parsed_message.get('project_id')
            code = parsed_message.get('code', '')
            success, msg = self.write_code(project_id, code)
            return f"✅ {msg}" if success else f"❌ {msg}"
        
        elif action == 'test':
            project_id = parsed_message.get('project_id')
            test_cases = parsed_message.get('test_cases', [])
            success, msg = self.test_code(project_id, test_cases)
            return f"🧪 {msg}" if success else f"❌ {msg}"
        
        elif action == 'integrate':
            project_id = parsed_message.get('project_id')
            success, msg = self.integrate(project_id)
            return f"✅ {msg}" if success else f"❌ {msg}"
        
        return "❌ 未知操作"
