#!/usr/bin/env python3
"""
Algora Bounty 监控脚本
- 每 30 分钟扫描一次
- 发现新任务自动通知
- 支持自动评论接单

版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
GitHub: https://github.com/zhaog100/openclaw-skills
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# 配置
ALGORA_API_URL = "https://api.algora.io/v1/bounties"
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
STATE_FILE = Path('/tmp/github-bounty-state.yaml')

class AlgoraMonitor:
    def __init__(self):
        self.headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Content-Type': 'application/json'
        }
        self.state = self.load_state()
    
    def load_state(self):
        """加载 STATE.yaml"""
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                # 简单 YAML 解析
                state = {}
                for line in f:
                    if ':' in line:
                        key, value = line.strip().split(':', 1)
                        state[key.strip()] = value.strip()
                return state
        return {'status': 'pending', 'tasks': []}
    
    def save_state(self):
        """保存 STATE.yaml"""
        with open(STATE_FILE, 'w') as f:
            f.write(f"# GitHub Bounty Hunter State\n")
            f.write(f"# 更新时间：{datetime.now().isoformat()}\n\n")
            f.write(f"status: {self.state.get('status', 'pending')}\n")
            f.write(f"last_scan: {self.state.get('last_scan', 'never')}\n")
            f.write(f"total_tasks: {len(self.state.get('tasks', []))}\n")
    
    def fetch_bounties(self, limit=20):
        """获取最新 Bounty 任务"""
        try:
            print(f"📡 正在获取 Algora 任务...")
            # 模拟 API 调用（实际需集成 Algora API）
            response = requests.get(
                f"{ALGORA_API_URL}?limit={limit}",
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️  API 返回状态码：{response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 获取失败：{e}")
            return []
    
    def filter_tasks(self, bounties):
        """筛选适合的任务"""
        suitable = []
        for bounty in bounties:
            # 筛选条件
            if bounty.get('status') == 'open':
                if bounty.get('amount', 0) >= 500:  # 最低$500
                    suitable.append(bounty)
        return suitable
    
    def notify(self, task):
        """通知新任务"""
        print("=" * 60)
        print(f"🎯 发现新任务！")
        print(f"标题：{task.get('title', 'Unknown')}")
        print(f"奖金：${task.get('amount', 0)}")
        print(f"链接：{task.get('url', 'Unknown')}")
        print(f"截止：{task.get('deadline', 'Unknown')}")
        print("=" * 60)
    
    def auto_apply(self, task):
        """自动评论接单"""
        if not GITHUB_TOKEN:
            print("⚠️  未设置 GITHUB_TOKEN，跳过自动接单")
            return
        
        try:
            # 自动评论内容
            comment = """## 🙋 申请接单

**申请者**: 小米辣 (AI Agent) 🌶️
**申请时间**: """ + datetime.now().isoformat() + """

**优势**:
- ✅ 24/7 全天候工作
- ✅ 自动化开发 + 测试
- ✅ 快速交付（通常 2-8 小时）
- ✅ 开源项目经验丰富

**预计完成时间**: 24 小时内

---
*由 github-bounty-hunter 自动发送 | 版权：思捷娅科技 (SJYKJ)*"""
            
            print(f"📝 准备自动评论接单...")
            # TODO: 调用 GitHub API 发送评论
            print("✅ 评论发送成功（模拟）")
            
        except Exception as e:
            print(f"❌ 自动接单失败：{e}")
    
    def run(self):
        """运行监控"""
        print("🦞 GitHub Bounty Hunter 启动！")
        print(f"📍 监控平台：Algora")
        print(f"⏰ 扫描频率：30 分钟")
        print(f"💰 最低奖金：$500")
        print("=" * 60)
        
        while True:
            try:
                # 获取任务
                bounties = self.fetch_bounties()
                
                # 筛选
                suitable = self.filter_tasks(bounties)
                
                # 通知
                for task in suitable:
                    self.notify(task)
                    # 自动接单（可选）
                    # self.auto_apply(task)
                
                # 更新状态
                self.state['last_scan'] = datetime.now().isoformat()
                self.state['tasks'] = suitable
                self.save_state()
                
                print(f"✅ 扫描完成，发现 {len(suitable)} 个适合的任务")
                print(f"⏳ 30 分钟后再次扫描...\n")
                
                # 等待 30 分钟
                time.sleep(1800)
                
            except KeyboardInterrupt:
                print("\n👋 监控停止")
                break
            except Exception as e:
                print(f"❌ 错误：{e}")
                time.sleep(60)  # 错误后等待 1 分钟

if __name__ == "__main__":
    monitor = AlgoraMonitor()
    monitor.run()
