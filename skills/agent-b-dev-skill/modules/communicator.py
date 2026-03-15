#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沟通协作模块 v2.0 - GitHub Issue协作

功能：
- GitHub Issue评论监听
- 自动识别小米辣回复
- 状态流转触发
"""

import json
import subprocess
import time
import threading
from datetime import datetime

class Communicator:
    """沟通协作器 - GitHub Issue模式"""
    
    def __init__(self):
        """初始化沟通协作器"""
        self.handlers = {}
        self.identity = 'agent-b-dev'  # 智能体B（Dev代理）
        self.github_repo = 'zhaog100/openclaw-skills'
        self.running = False
        self.check_interval = 30  # 30秒检查一次
        self.last_check_time = None
        
        # 记录已处理的Issue评论
        self.processed_comments = set()
    
    def send_message(self, to, content, issue_number=None):
        """发送消息（通过GitHub Issue评论）"""
        try:
            if issue_number:
                # 发送到指定Issue
                cmd = [
                    'gh', 'issue', 'comment', str(issue_number),
                    '--body', content
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ [{self.identity}] 发送评论到Issue #{issue_number}")
                    return True, f"评论已发送到Issue #{issue_number}"
                else:
                    print(f"❌ [{self.identity}] 发送失败: {result.stderr}")
                    return False, f"发送失败: {result.stderr}"
            else:
                # 打印消息（测试用）
                print(f"📤 [{self.identity}] 发送消息给 {to}：{content}")
                return True, f"消息已发送给 {to}"
        except Exception as e:
            print(f"❌ [{self.identity}] 发送异常: {e}")
            return False, f"发送异常: {e}"
    
    def check_github_issues(self):
        """检查GitHub Issue评论"""
        try:
            # 1. 获取最近的Issue（按更新时间排序）
            cmd = [
                'gh', 'issue', 'list',
                '--repo', self.github_repo,
                '--state', 'open',
                '--limit', '10',
                '--json', 'number,title,updatedAt'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ [{self.identity}] 获取Issue失败: {result.stderr}")
                return
            
            issues = json.loads(result.stdout)
            
            # 2. 检查每个Issue的最新评论
            for issue in issues:
                issue_number = issue['number']
                issue_title = issue['title']
                
                # 获取评论
                comments_cmd = [
                    'gh', 'issue', 'view', str(issue_number),
                    '--repo', self.github_repo,
                    '--json', 'comments'
                ]
                
                comments_result = subprocess.run(comments_cmd, capture_output=True, text=True)
                
                if comments_result.returncode == 0:
                    issue_data = json.loads(comments_result.stdout)
                    comments = issue_data.get('comments', [])
                    
                    # 检查最新评论
                    if comments:
                        latest_comment = comments[-1]
                        comment_id = latest_comment['id']
                        comment_user = latest_comment['author']['login']
                        comment_body = latest_comment['body']
                        comment_time = latest_comment['createdAt']
                        
                        # 跳过已处理的评论
                        if comment_id in self.processed_comments:
                            continue
                        
                        # 跳过自己的评论（小米粒）
                        if '小米粒' in comment_body or 'Dev' in comment_body:
                            continue
                        
                        # 识别小米辣的回复（GitHub用户名：zhaog100，且包含小米辣或PM标识）
                        if comment_user == 'zhaog100' and ('小米辣' in comment_body or 'PM' in comment_body):
                            print(f"\n🔔 [{self.identity}] 发现小米辣回复！")
                            print(f"   Issue #{issue_number}: {issue_title}")
                            print(f"   评论时间: {comment_time}")
                            print(f"   评论内容: {comment_body[:100]}...")
                            
                            # 标记为已处理
                            self.processed_comments.add(comment_id)
                            
                            # 触发处理
                            self.handle_xiaomila_reply(issue_number, issue_title, comment_body)
            
            self.last_check_time = datetime.now()
            
        except Exception as e:
            print(f"❌ [{self.identity}] 检查Issue异常: {e}")
    
    def handle_xiaomila_reply(self, issue_number, issue_title, comment_body):
        """处理小米辣的回复"""
        # 解析评论内容，识别任务类型
        if 'PRD' in issue_title or '产品构思' in comment_body:
            # 触发技术设计流程
            print(f"🎯 [{self.identity}] 触发技术设计流程")
            self.trigger_tech_design(issue_number)
        
        elif '技术设计' in comment_body or 'tech design' in comment_body.lower():
            # 触发开发实现流程
            print(f"💻 [{self.identity}] 触发开发实现流程")
            self.trigger_development(issue_number)
        
        elif '开发完成' in comment_body or 'Review' in comment_body:
            # 触发发布流程
            print(f"🚀 [{self.identity}] 触发发布流程")
            self.trigger_publish(issue_number)
        
        else:
            # 通用回复
            print(f"📝 [{self.identity}] 收到小米辣回复，准备响应")
            self.send_message(
                'agent-a-pm',
                f"🌾 小米粒（Dev）收到！\n\nIssue #{issue_number} 已确认，准备处理...",
                issue_number
            )
    
    def trigger_tech_design(self, issue_number):
        """触发技术设计"""
        print(f"📋 [{self.identity}] 开始技术设计...")
        
        # 获取Issue内容（PRD）
        cmd = [
            'gh', 'issue', 'view', str(issue_number),
            '--repo', self.github_repo,
            '--json', 'title,body'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            issue_data = json.loads(result.stdout)
            prd_title = issue_data['title']
            prd_body = issue_data['body']
            
            # 调用技术设计模块
            from tech_designer import TechDesigner
            tech_designer = TechDesigner()
            
            design_id, design_data = tech_designer.create_design(
                issue_number,
                prd_title,
                prd_body
            )
            
            # 提交到GitHub
            tech_designer.submit_to_github(design_id, design_data)
    
    def trigger_development(self, issue_number):
        """触发开发实现"""
        print(f"💻 [{self.identity}] 开始开发实现...")
        # TODO: 获取技术设计，开始开发
        pass
    
    def trigger_publish(self, issue_number):
        """触发发布流程"""
        print(f"🚀 [{self.identity}] 开始发布流程...")
        # TODO: 验证开发完成，开始发布
        pass
    
    def listen_github(self):
        """监听GitHub Issue（后台线程）"""
        print(f"🎧 [{self.identity}] 开始监听GitHub Issue...")
        print(f"   仓库: {self.github_repo}")
        print(f"   检查间隔: {self.check_interval}秒")
        
        while self.running:
            try:
                self.check_github_issues()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"❌ [{self.identity}] 监听异常: {e}")
                time.sleep(5)
    
    def listen(self, callback=None):
        """启动监听"""
        if self.running:
            print(f"⚠️ [{self.identity}] 监听已在运行")
            return
        
        self.running = True
        
        # 启动GitHub监听线程
        github_thread = threading.Thread(target=self.listen_github, daemon=True)
        github_thread.start()
        
        print(f"✅ [{self.identity}] GitHub监听已启动")
    
    def stop(self):
        """停止监听"""
        self.running = False
        print(f"⏹️ [{self.identity}] 监听已停止")
    
    def parse_message(self, message):
        """解析消息"""
        content = message.get('content', '')
        
        # 简单解析逻辑（Dev代理专用）
        if '技术设计' in content or 'tech design' in content.lower():
            return {'type': 'tech_design', 'content': content, 'message': message}
        elif '开发' in content or 'develop' in content.lower():
            return {'type': 'develop', 'content': content, 'message': message}
        elif '发布' in content or 'publish' in content.lower():
            return {'type': 'publish', 'content': content, 'message': message}
        else:
            return {'type': 'unknown', 'content': content, 'message': message}
    
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
        print(f"✅ [{self.identity}] 注册处理器：{msg_type}")
    
    def handle(self, parsed_message):
        """处理沟通协作消息"""
        action = parsed_message.get('action')
        
        if action == 'send':
            to = parsed_message.get('to')
            content = parsed_message.get('content')
            issue_number = parsed_message.get('issue_number')
            success, msg = self.send_message(to, content, issue_number)
            return f"✅ {msg}" if success else f"❌ {msg}"
        
        elif action == 'check':
            # 手动检查
            self.check_github_issues()
            return "✅ 检查完成"
        
        elif action == 'start':
            # 启动监听
            self.listen()
            return "✅ 监听已启动"
        
        elif action == 'stop':
            # 停止监听
            self.stop()
            return "✅ 监听已停止"
        
        elif action == 'status':
            # 查看状态
            status = "运行中" if self.running else "已停止"
            last_check = self.last_check_time.strftime("%H:%M:%S") if self.last_check_time else "未检查"
            return f"📊 监听状态: {status}\n   上次检查: {last_check}\n   检查间隔: {self.check_interval}秒"
        
        return "❌ 未知操作"
