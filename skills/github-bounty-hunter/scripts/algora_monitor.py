#!/usr/bin/env python3
"""
Algora Bounty 监控脚本（v2.0 - 使用 /attempt 命令）

根据小米粒实战经验更新：
- Claim 不是在 Algora 平台点按钮
- 而是在 GitHub issue 评论区发 `/attempt`
- Algora bot 会自动扫描并关联到 Algora 账户
- 提交 PR 后自动关联，无需手动提交审核

功能：
- 自动扫描 Algora 相关 bounty 任务
- 低竞争任务优先（评论<10）
- 自动发送 /attempt 评论
- 统一追踪 Claim 状态

版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
GitHub: https://github.com/zhaog100/openclaw-skills
ClawHub: https://clawhub.com
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
STATE_FILE = Path('/tmp/algora-bounty-state.json')
LOG_DIR = Path('/home/zhaog/.openclaw/workspace/skills/github-bounty-hunter/logs')
LOG_FILE = LOG_DIR / 'algora_monitor.log'

# 创建日志目录
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 钱包地址（可选配置，Claim 时填写也可以）
WALLET_ADDRESS = os.getenv('ALGORA_WALLET_ADDRESS', '')

# 如果没有配置，Claim 时会提示手动填写
NEED_WALLET_CONFIG = not WALLET_ADDRESS or WALLET_ADDRESS == '0x...'

class AlgoraMonitor:
    def __init__(self):
        self.headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Content-Type': 'application/json'
        }
        self.state = self.load_state()
    
    def load_state(self):
        """加载 STATE.json"""
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        return {'status': 'pending', 'tasks': [], 'claimed': []}
    
    def save_state(self):
        """保存 STATE.json"""
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def log(self, message):
        """日志记录"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        print(log_entry.strip())
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
    
    def scan_bounties(self, limit=20):
        """
        扫描 Algora bounty 任务
        
        注意：Algora 任务实际在 GitHub 上执行
        - Algora 平台：Claim 任务 + 填写钱包 + 收款
        - GitHub 平台：实际工作 + 提交 PR
        """
        self.log("=== 开始扫描 Algora Bounty ===")
        self.log("💡 提示：Algora 任务在 GitHub 上执行，Claim 在 Algora 平台")
        
        try:
            # 使用 GitHub 搜索 Algora 相关任务
            # 注意：Algora 任务可能没有 label:algora，所以用多种关键词搜索
            url = "https://api.github.com/search/issues"
            params = {
                'q': 'bounty Algora OR "algora.io" in:title,body is:issue is:open created:>=2026-01-01',
                'sort': 'comments',  # 按评论数排序（低竞争优先）
                'order': 'asc',      # 升序
                'per_page': limit
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            bounties = data.get('items', [])
            
            self.log(f"找到 {len(bounties)} 个 Algora bounty 任务")
            
            # 过滤低竞争任务（评论<10）
            low_competition = [b for b in bounties if b.get('comments', 0) < 10]
            self.log(f"低竞争任务：{len(low_competition)} 个")
            
            # 显示任务信息
            for i, bounty in enumerate(low_competition[:5], 1):
                title = bounty.get('title', '')[:50]
                repo = '/'.join(bounty.get('repository_url', '').split('/')[-2:])
                comments = bounty.get('comments', 0)
                html_url = bounty.get('html_url', '')
                self.log(f"{i}. {title}... ({repo}) - {comments} 评论")
                self.log(f"   GitHub: {html_url}")
            
            return low_competition
            
        except Exception as e:
            self.log(f"❌ 扫描失败：{e}")
            return []
    
    def claim_bounty(self, bounty):
        """
        Claim bounty 任务（使用 Algora 官方 /attempt 命令）
        
        根据小米粒实战经验：
        - Claim 不是在 Algora 平台点按钮
        - 而是在 GitHub issue 评论区发 `/attempt`
        - Algora bot 会自动扫描并关联到 Algora 账户
        """
        issue_number = bounty.get('number')
        repo = bounty.get('repository_url', '').split('/')[-2:]
        repo_name = '/'.join(repo)
        
        self.log(f"=== Claim 任务 #{issue_number} ({repo_name}) ===")
        self.log("💡 使用 Algora 官方 /attempt 命令")
        
        try:
            # 提交 /attempt 评论（Algora 官方方式）
            url = f"https://api.github.com/repos/{repo_name}/issues/{issue_number}/comments"
            
            # 使用 Algora 官方的 /attempt 命令
            comment_body = """/attempt

**Plan:**
1. Review the requirements
2. Start working on the task
3. Submit PR when complete

Ready to work! 🚀

---
*Claimed via Algora Monitor - GitHub Bounty Hunter*
"""
            
            data = {'body': comment_body}
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            comment_id = result.get('id')
            comment_url = result.get('html_url')
            
            self.log(f"✅ /attempt 成功！评论 ID: {comment_id}")
            self.log(f"链接：{comment_url}")
            self.log("💡 Algora bot 会自动检测并关联到你的 Algora 账户")
            
            # 更新状态
            self.state['claimed'].append({
                'issue_number': issue_number,
                'repo': repo_name,
                'claimed_at': datetime.now().isoformat(),
                'comment_id': comment_id,
                'comment_url': comment_url,
                'method': '/attempt'
            })
            self.save_state()
            
            return True
            
        except Exception as e:
            self.log(f"❌ Claim 失败：{e}")
            return False
    
    def run(self, max_claims=5):
        """运行监控"""
        self.log("🚀 Algora Monitor 启动")
        
        # 扫描任务
        bounties = self.scan_bounties(limit=20)
        
        if not bounties:
            self.log("⚠️ 没有找到合适的任务")
            return
        
        # Claim 低竞争任务
        claimed_count = 0
        for bounty in bounties:
            if claimed_count >= max_claims:
                self.log(f"已达到最大 Claim 数量 ({max_claims})")
                break
            
            # 检查是否已 Claim
            issue_number = bounty.get('number')
            already_claimed = any(
                t['issue_number'] == issue_number 
                for t in self.state.get('claimed', [])
            )
            
            if already_claimed:
                self.log(f"⏭️  任务 #{issue_number} 已 Claim，跳过")
                continue
            
            # Claim 任务
            success = self.claim_bounty(bounty)
            if success:
                claimed_count += 1
                # 避免速率限制
                time.sleep(5)
        
        self.log(f"📊 本次运行 Claim 了 {claimed_count} 个任务")
        self.log("✅ Algora Monitor 完成")


if __name__ == '__main__':
    monitor = AlgoraMonitor()
    monitor.run(max_claims=5)
