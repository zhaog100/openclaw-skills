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
    if len(sys.argv) < 2:
        # 没有参数，启动监听模式
        skill = AgentBDevSkill()
        skill.run()
    else:
        # 有参数，处理命令
        command = sys.argv[1]
        args = sys.argv[2:]
        
        skill = AgentBDevSkill()
        
        if command == 'tech':
            print(f"🎯 技术设计模式: {args}")
            # 调用技术设计模块
            skill.tech_designer.design(args)
        elif command == 'dev':
            print(f"💻 开发实现模式: {args}")
            # 调用开发实现模块
            skill.developer.develop(args)
        elif command == 'publish':
            print(f"🚀 集成发布模式: {args}")
            # 调用集成发布模块
            skill.publisher.publish(args)
        elif command == 'comm':
            if '--help' in args or '-h' in args:
                print("沟通协作模块帮助：")
                print("  --send <message>  发送消息")
                print("  --receive         接收消息")
                print("  --status          查看状态")
            elif '--send' in args:
                msg_idx = args.index('--send') + 1
                if msg_idx < len(args):
                    message = args[msg_idx]
                    print(f"📤 发送消息到小米辣: {message}")
                    # TODO: 实际发送消息
                else:
                    print("❌ 缺少消息内容")
            elif '--receive' in args:
                print("📥 接收消息中...")
                # TODO: 实际接收消息
            else:
                # 启动监听模式
                skill.run()
        else:
            print(f"❌ 未知操作: {command}")

if __name__ == '__main__':
    main()
