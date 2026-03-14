#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
状态管理模块

功能：
- 状态流转
- 状态查询
- 状态通知
"""

# 产品状态定义（4阶段26状态）
PRODUCT_STATES = {
    # 产品构思阶段（6状态）
    'draft': {'next': ['pending_review'], 'desc': '草稿'},
    'pending_review': {'next': ['approved', 'rejected'], 'desc': '等待评审'},
    'approved': {'next': ['designing'], 'desc': '已通过'},
    'rejected': {'next': ['draft'], 'desc': '已拒绝'},
    'paused': {'next': ['draft'], 'desc': '已暂停'},
    'cancelled': {'next': [], 'desc': '已取消'},
    
    # 技术设计阶段（6状态）
    'designing': {'next': ['tech_review'], 'desc': '设计中'},
    'tech_review': {'next': ['tech_approved', 'tech_rejected'], 'desc': '技术评审中'},
    'tech_approved': {'next': ['developing'], 'desc': '技术已通过'},
    'tech_rejected': {'next': ['designing'], 'desc': '技术已拒绝'},
    'tech_paused': {'next': ['designing'], 'desc': '技术已暂停'},
    'tech_cancelled': {'next': [], 'desc': '技术已取消'},
    
    # 开发实现阶段（7状态）
    'developing': {'next': ['testing'], 'desc': '开发中'},
    'testing': {'next': ['dev_review'], 'desc': '测试中'},
    'dev_review': {'next': ['dev_approved', 'dev_rejected'], 'desc': '开发评审中'},
    'dev_approved': {'next': ['publishing'], 'desc': '开发已通过'},
    'dev_rejected': {'next': ['developing'], 'desc': '开发已拒绝'},
    'dev_paused': {'next': ['developing'], 'desc': '开发已暂停'},
    'dev_cancelled': {'next': [], 'desc': '开发已取消'},
    
    # 发布交付阶段（7状态）
    'publishing': {'next': ['published'], 'desc': '发布中'},
    'published': {'next': [], 'desc': '已发布'},
    'publish_paused': {'next': ['publishing'], 'desc': '发布已暂停'},
    'publish_cancelled': {'next': [], 'desc': '发布已取消'},
    'deleted': {'next': [], 'desc': '已删除'}
}

class StateManager:
    """状态管理器"""
    
    def __init__(self):
        """初始化状态管理器"""
        self.states = {}
    
    def transition(self, product_id, new_state):
        """状态流转"""
        if product_id not in self.states:
            return False, "产品不存在"
        
        current_state = self.states[product_id]
        
        # 检查状态流转是否合法
        if new_state not in PRODUCT_STATES[current_state]['next']:
            return False, f"不能从 {current_state} 流转到 {new_state}"
        
        # 更新状态
        self.states[product_id] = new_state
        return True, f"状态已更新：{current_state} → {new_state}"
    
    def query(self, product_id):
        """状态查询"""
        if product_id in self.states:
            state = self.states[product_id]
            return True, f"当前状态：{state} ({PRODUCT_STATES[state]['desc']})"
        return False, "产品不存在"
    
    def notify(self, product_id):
        """状态通知"""
        if product_id in self.states:
            state = self.states[product_id]
            return True, f"📢 状态通知：{product_id} → {state}"
        return False, "产品不存在"
    
    def handle(self, parsed_message):
        """处理状态管理消息"""
        action = parsed_message.get('action')
        
        if action == 'transition':
            product_id = parsed_message.get('product_id')
            new_state = parsed_message.get('new_state')
            success, msg = self.transition(product_id, new_state)
            if success:
                return f"✅ {msg}"
            return f"❌ {msg}"
        
        elif action == 'query':
            product_id = parsed_message.get('product_id')
            success, msg = self.query(product_id)
            return f"✅ {msg}" if success else f"❌ {msg}"
        
        elif action == 'notify':
            product_id = parsed_message.get('product_id')
            success, msg = self.notify(product_id)
            return msg if success else f"❌ {msg}"
        
        return "❌ 未知操作"
