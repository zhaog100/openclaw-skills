#!/usr/bin/env python3
"""
自动评论接单脚本
- 发现任务后自动评论申请
- 发送专业接单信息
- 支持多平台

版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
GitHub: https://github.com/zhaog100/openclaw-skills
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

class AutoApply:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Content-Type': 'application/json'
        }
        self.payment_address = os.getenv('PAYMENT_ADDRESS', 'TGu4W5T6q4KvLAbmXmZSRpUBNRCxr2aFTP')
    
    def apply_issue(self, repo_owner, repo_name, issue_number):
        """自动评论申请接单"""
        if not self.github_token:
            print("⚠️  未设置 GITHUB_TOKEN，跳过自动接单")
            return False
        
        try:
            # 评论内容
            comment = self._generate_comment()
            
            # 调用 GitHub API
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}/comments"
            data = {'body': comment}
            
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            
            if response.status_code == 201:
                print(f"✅ 接单成功：{repo_owner}/{repo_name}#{issue_number}")
                return True
            else:
                print(f"❌ 接单失败：{response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"❌ 异常：{e}")
            return False
    
    def apply_algora(self, bounty_id):
        """Algora 平台自动接单"""
        algora_key = os.getenv('ALGORA_API_KEY', '')
        if not algora_key:
            print("⚠️  未设置 ALGORA_API_KEY，跳过 Algora 接单")
            return False
        
        try:
            url = f"https://api.algora.io/v1/bounties/{bounty_id}/apply"
            headers = {
                'Authorization': f'Bearer {algora_key}',
                'Content-Type': 'application/json'
            }
            data = {
                'message': self._generate_algora_message(),
                'payment_address': self.payment_address
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code in [200, 201]:
                print(f"✅ Algora 接单成功：{bounty_id}")
                return True
            else:
                print(f"❌ Algora 接单失败：{response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 异常：{e}")
            return False
    
    def _generate_comment(self):
        """生成 GitHub 评论"""
        now = datetime.now().isoformat()
        return f"""## 🙋 申请接单

**申请者**: 小米辣 (AI Agent) 🌶️
**申请时间**: {now}

**优势**:
- ✅ 24/7 全天候工作
- ✅ 自动化开发 + 测试
- ✅ 快速交付（通常 2-8 小时）
- ✅ 开源项目经验丰富

**预计完成时间**: 24 小时内

**收款信息**:
- **平台**: OKX
- **币种**: USDT (TRC20)
- **地址**: `{self.payment_address}`

---
*由 github-bounty-hunter v1.3.0 自动发送 | 版权：思捷娅科技 (SJYKJ)*"""
    
    def _generate_algora_message(self):
        """生成 Algora 申请消息"""
        return f"""🙋 申请接单

我是小米辣，一个专业的 AI 开发代理，专注于快速交付高质量的开源代码。

**我的优势**:
- 24/7 全天候工作，无需休息
- 自动化开发 + 测试，保证质量
- 平均交付时间：2-8 小时
- 丰富的开源项目经验

**预计完成时间**: 24 小时内

**收款**: USDT (TRC20) - OKX 钱包

期待合作！🌶️"""
    
    def notify_qq(self, message):
        """QQ 通知（通过 OpenClaw 消息系统）"""
        try:
            # 使用 OpenClaw 内置消息发送
            from pathlib import Path
            notify_file = Path('/tmp/github-bounty-qq-notify.txt')
            
            with open(notify_file, 'w', encoding='utf-8') as f:
                f.write(f"🦞 GitHub Bounty Hunter\n\n{message}")
            
            print("✅ QQ 通知已准备（通过 OpenClaw 消息系统）")
            return True
            
        except Exception as e:
            print(f"❌ QQ 通知异常：{e}")
            return False

if __name__ == "__main__":
    # 测试
    applier = AutoApply()
    print("🦞 AutoApply 初始化完成")
    print(f"💰 收款地址：{applier.payment_address}")
    print("\n用法:")
    print("  applier.apply_issue('owner', 'repo', 123)")
    print("  applier.apply_algora('bounty_id')")
