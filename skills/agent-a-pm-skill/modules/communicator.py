#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沟通协作模块

功能：
- 消息发送
- 消息接收
- 消息路由
"""

import json

class Communicator:
    """沟通协作器"""
    
    def __init__(self):
        """初始化沟通协作器"""
        self.handlers = {}
    
    def send_message(self, to, content):
        """发送消息"""
        message = {
            'from': 'agent-a-pm',
            'to': to,
            'content': content,
            'timestamp': '2026-03-15 01:20'
        }
        
        # 这里应该调用飞书API发送消息
        # 简化实现：直接打印
        print(f"📤 发送消息给 {to}：{content}")
        return True, f"消息已发送给 {to}"
    
    def receive_message(self):
        """接收消息"""
        # 这里应该监听飞书WebSocket接收消息
        # 简化实现：返回示例消息
        return {
            'from': '官家',
            'to': 'agent-a-pm',
            'content': '示例消息',
            'timestamp': '2026-03-15 01:20'
        }
    
    def parse_message(self, message):
        """解析消息"""
        content = message.get('content', '')
        
        # 简单解析逻辑
        if '产品' in content or 'PRD' in content:
            return {'type': 'product', 'content': content}
        elif 'Review' in content or '测试' in content:
            return {'type': 'review', 'content': content}
        elif '状态' in content:
            return {'type': 'state', 'content': content}
        else:
            return {'type': 'unknown', 'content': content}
    
    def route_message(self, message):
        """路由消息"""
        parsed = self.parse_message(message)
        msg_type = parsed['type']
        
        if msg_type in self.handlers:
            handler = self.handlers[msg_type]
            return handler(parsed)
        
        return "❌ 未知消息类型"
    
    def register_handler(self, msg_type, handler):
        """注册消息处理器"""
        self.handlers[msg_type] = handler
        print(f"✅ 注册处理器：{msg_type}")
    
    def listen(self, callback):
        """监听消息"""
        print("🎧 开始监听飞书消息...")
        
        # 简化实现：单次接收
        message = self.receive_message()
        result = callback(message)
        print(f"📥 处理结果：{result}")
        
        return result
    
    def handle(self, parsed_message):
        """处理沟通协作消息"""
        action = parsed_message.get('action')
        
        if action == 'send':
            to = parsed_message.get('to')
            content = parsed_message.get('content')
            success, msg = self.send_message(to, content)
            return f"✅ {msg}" if success else f"❌ {msg}"
        
        elif action == 'receive':
            message = self.receive_message()
            return f"📥 收到消息：{message}"
        
        elif action == 'route':
            message = parsed_message.get('message', {})
            result = self.route_message(message)
            return f"🔀 路由结果：{result}"
        
        return "❌ 未知操作"
