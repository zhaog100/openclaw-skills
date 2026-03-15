#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent-b-dev-skill - 智能体B（Dev代理）技能包

版本: v1.0.0
创建者: 思捷娅科技 (SJYKJ)（Dev代理）
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

__version__ = '2.0.0'
__author__ = '思捷娅科技 (SJYKJ)'

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
        print(f"🚀 agent-b-dev-skill v{__version__} 启动...")

        # 监听GitHub Issue
        self.communicator.listen()

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
                print("  --start           启动GitHub监听")
                print("  --stop            停止监听")
                print("  --check           手动检查Issue")
                print("  --status          查看监听状态")
                print("  --send <issue> <message>  发送评论到Issue")
            elif '--start' in args:
                # 启动监听
                skill.communicator.listen()
                print("✅ 监听已启动（后台运行）")
            elif '--stop' in args:
                # 停止监听
                skill.communicator.stop()
            elif '--check' in args:
                # 手动检查
                skill.communicator.check_github_issues()
            elif '--status' in args:
                # 查看状态
                status = skill.communicator.handle({'action': 'status'})
                print(status)
            elif '--send' in args:
                # 发送评论
                if len(args) >= 3:
                    issue_number = args[args.index('--send') + 1]
                    message = ' '.join(args[args.index('--send') + 2:])
                    success, msg = skill.communicator.send_message(
                        'agent-a-pm', 
                        message, 
                        int(issue_number)
                    )
                    print(f"{'✅' if success else '❌'} {msg}")
                else:
                    print("❌ 用法: comm --send <issue_number> <message>")
            else:
                # 启动监听模式
                skill.run()
        else:
            print(f"❌ 未知操作: {command}")

if __name__ == '__main__':
    main()
