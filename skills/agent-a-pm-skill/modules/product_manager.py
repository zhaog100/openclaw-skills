#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品管理模块

功能：
- 产品构思
- PRD 编写
- 需求评审

日志：2026-03-15 米粒儿补充日志记录和输入验证
"""

import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ProductManager')


class ProductManager:
    """产品管理器"""
    
    def __init__(self):
        """初始化产品管理器"""
        self.products = {}
        logger.info("ProductManager 初始化完成")
    
    def create_product(self, name, description):
        """
        创建产品
        
        Args:
            name: 产品名称（必填，1-100 字符）
            description: 产品描述（必填，1-1000 字符）
        
        Returns:
            str: 产品 ID
            
        Raises:
            ValueError: 输入验证失败
        """
        # 输入验证
        if not name or not isinstance(name, str):
            logger.error("产品名称无效")
            raise ValueError("产品名称不能为空")
        if len(name) < 1 or len(name) > 100:
            logger.error(f"产品名称长度无效：{len(name)}")
            raise ValueError("产品名称长度必须在 1-100 字符之间")
        if not description or not isinstance(description, str):
            logger.error("产品描述无效")
            raise ValueError("产品描述不能为空")
        if len(description) < 1 or len(description) > 1000:
            logger.error(f"产品描述长度无效：{len(description)}")
            raise ValueError("产品描述长度必须在 1-1000 字符之间")
        
        product_id = f"prod_{len(self.products) + 1}"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.products[product_id] = {
            'id': product_id,
            'name': name,
            'description': description,
            'state': 'draft',
            'created_at': timestamp
        }
        logger.info(f"产品创建成功：{product_id} - {name}")
        return product_id
    
    def edit_product(self, product_id, updates):
        """
        编辑产品
        
        Args:
            product_id: 产品 ID
            updates: 更新内容（字典）
        
        Returns:
            bool: 是否成功
        """
        if not product_id or not isinstance(product_id, str):
            logger.error("产品 ID 无效")
            return False
        if not isinstance(updates, dict):
            logger.error("更新内容必须是字典")
            return False
        
        if product_id in self.products:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updates['updated_at'] = timestamp
            self.products[product_id].update(updates)
            logger.info(f"产品更新成功：{product_id}")
            return True
        
        logger.warning(f"产品不存在：{product_id}")
        return False
    
    def delete_product(self, product_id):
        """
        删除产品
        
        Args:
            product_id: 产品 ID
        
        Returns:
            bool: 是否成功
        """
        if not product_id or not isinstance(product_id, str):
            logger.error("产品 ID 无效")
            return False
        
        if product_id in self.products:
            del self.products[product_id]
            logger.info(f"产品删除成功：{product_id}")
            return True
        
        logger.warning(f"产品不存在：{product_id}")
        return False
    
    def handle(self, parsed_message):
        """处理产品管理消息"""
        action = parsed_message.get('action')
        
        if action == 'create':
            name = parsed_message.get('name')
            desc = parsed_message.get('description')
            try:
                product_id = self.create_product(name, desc)
                return f"✅ 产品创建成功：{product_id}"
            except ValueError as e:
                return f"❌ 创建失败：{str(e)}"
        
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
