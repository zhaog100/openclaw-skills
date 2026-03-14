#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成发布模块

功能：
- 发布准备
- 发布执行
- 发布验证
"""

class Publisher:
    """发布器"""
    
    def __init__(self):
        """初始化发布器"""
        self.releases = {}
    
    def prepare_release(self, project_id, version):
        """准备发布"""
        release_id = f"release_{len(self.releases) + 1}"
        
        self.releases[release_id] = {
            'id': release_id,
            'project_id': project_id,
            'version': version,
            'state': 'preparing',
            'checklist': {
                'code_review': False,
                'test_passed': False,
                'docs_updated': False
            }
        }
        
        return release_id
    
    def update_checklist(self, release_id, item, status):
        """更新检查清单"""
        if release_id not in self.releases:
            return False, "发布不存在"
        
        self.releases[release_id]['checklist'][item] = status
        return True, f"检查项已更新：{item} → {'✅' if status else '❌'}"
    
    def execute_release(self, release_id):
        """执行发布"""
        if release_id not in self.releases:
            return False, "发布不存在"
        
        release = self.releases[release_id]
        
        # 检查清单
        checklist = release['checklist']
        all_passed = all(checklist.values())
        
        if not all_passed:
            missing = [k for k, v in checklist.items() if not v]
            return False, f"检查清单未完成：{', '.join(missing)}"
        
        # 执行发布
        release['state'] = 'publishing'
        return True, f"发布中：{release_id}"
    
    def verify_release(self, release_id):
        """验证发布"""
        if release_id not in self.releases:
            return False, "发布不存在"
        
        release = self.releases[release_id]
        
        if release['state'] != 'publishing':
            return False, "发布未执行"
        
        # 简化验证
        release['state'] = 'published'
        return True, f"✅ 发布成功：{release_id} v{release['version']}"
    
    def handle(self, parsed_message):
        """处理发布消息"""
        action = parsed_message.get('action')
        
        if action == 'prepare':
            project_id = parsed_message.get('project_id')
            version = parsed_message.get('version', '1.0.0')
            release_id = self.prepare_release(project_id, version)
            return f"✅ 发布准备完成：{release_id}"
        
        elif action == 'checklist':
            release_id = parsed_message.get('release_id')
            item = parsed_message.get('item')
            status = parsed_message.get('status', True)
            success, msg = self.update_checklist(release_id, item, status)
            return f"✅ {msg}" if success else f"❌ {msg}"
        
        elif action == 'execute':
            release_id = parsed_message.get('release_id')
            success, msg = self.execute_release(release_id)
            return f"✅ {msg}" if success else f"❌ {msg}"
        
        elif action == 'verify':
            release_id = parsed_message.get('release_id')
            success, msg = self.verify_release(release_id)
            return msg if success else f"❌ {msg}"
        
        return "❌ 未知操作"
