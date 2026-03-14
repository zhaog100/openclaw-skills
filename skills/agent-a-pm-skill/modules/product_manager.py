#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品管理模块

功能：
- 产品构思
- PRD编写
- 需求评审
"""

class ProductManager:
    """产品管理器"""
    
    def __init__(self):
        """初始化产品管理器"""
        self.products = {}
    
    def create_product(self, name, description):
        """创建产品"""
        product_id = f"prod_{len(self.products) + 1}"
        self.products[product_id] = {
            'id': product_id,
            'name': name,
            'description': description,
            'state': 'draft',
            'created_at': '2026-03-15 01:18'
        }
        return product_id
    
    def edit_product(self, product_id, updates):
        """编辑产品"""
        if product_id in self.products:
            self.products[product_id].update(updates)
            return True
        return False
    
    def delete_product(self, product_id):
        """删除产品"""
        if product_id in self.products:
            del self.products[product_id]
            return True
        return False
    
    def handle(self, parsed_message):
        """处理产品管理消息"""
        action = parsed_message.get('action')
        
        if action == 'create':
            name = parsed_message.get('name')
            desc = parsed_message.get('description')
            product_id = self.create_product(name, desc)
            return f"✅ 产品创建成功：{product_id}"
        
        elif action == 'edit':
            product_id = parsed_message.get('product_id')
            updates = parsed_message.get('updates', {})
            if self.edit_product(product_id, updates):
                return f"✅ 产品更新成功：{product_id}"
            return f"❌ 产品不存在：{product_id}"
        
        elif action == 'delete':
            product_id = parsed_message.get('product_id')
            if self.delete_product(product_id):
                return f"✅ 产品删除成功：{product_id}"
            return f"❌ 产品不存在：{product_id}"
        
        return "❌ 未知操作"
