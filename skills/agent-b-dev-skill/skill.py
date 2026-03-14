#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent-b-dev-skill - 智能体B（Dev代理）技能包

版本: v1.0.0
创建者: 小米粒（Dev代理）
创建时间: 2026-03-15
"""

import sys
import os

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from tech_designer import TechDesigner
from developer import Developer
from publisher import Publisher
from communicator import Communicator

__version__ = '1.0.0'
__author__ = '小米粒 (miliger)'

class AgentBDevSkill:
    """智能体B（Dev代理）技能包主类"""
    
    def __init__(self):
        """初始化技能包"""
        self.tech_designer = TechDesigner()
        self.developer = Developer()
        self.publisher = Publisher()
        self.communicator = Communicator()
    
    def handle_message(self, message):
        """处理消息"""
        # 1. 解析消息
        parsed = self.communicator.parse_message(message)
        
        # 2. 路由到对应模块
        if parsed['type'] == 'tech_design':
            return self.tech_designer.handle(parsed)
        elif parsed['type'] == 'develop':
            return self.developer.handle(parsed)
        elif parsed['type'] == 'publish':
            return self.publisher.handle(parsed)
        else:
            return self.communicator.handle(parsed)
    
    def run(self):
        """运行技能包"""
        print("🚀 agent-b-dev-skill v1.0.0 启动...")
        
        # 监听飞书消息
        self.communicator.listen(self.handle_message)

def main():
    """主入口"""
    skill = AgentBDevSkill()
    skill.run()

if __name__ == '__main__':
    main()
