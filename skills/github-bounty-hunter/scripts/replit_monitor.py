#!/usr/bin/env python3
"""
Replit Bounties 监控脚本
- 监控 Replit 平台的 bounty 任务
- 快速现金流（$50-$500）
- 自动通知

版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
GitHub: https://github.com/zhaog100/openclaw-skills
"""

import os
import requests
from datetime import datetime
from pathlib import Path

class ReplitMonitor:
    def __init__(self):
        self.notify_dir = Path('/tmp/github-bounty-notifies')
        self.notify_dir.mkdir(exist_ok=True)
        
        # Replit 官网
        self.base_url = "https://replit.com"
        self.bounties_url = "https://replit.com/bounties"
        
        # GitHub 搜索 Replit 相关任务
        self.github_query = 'replit in:title,comments label:bounty is:issue is:open'
        
    def search_github(self, token):
        """通过 GitHub 搜索 Replit 相关任务"""
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f'https://api.github.com/search/issues?q={self.github_query}&sort=updated&order=desc&per_page=10'
        
        try:
            print('📡 通过 GitHub 搜索 Replit 任务...')
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                issues = data.get('items', [])
                print(f'✅ 找到 {len(issues)} 个 Replit 相关任务')
                return issues
            else:
                print(f'⚠️ API 返回状态码：{response.status_code}')
                return []
                
        except Exception as e:
            print(f'❌ 搜索失败：{e}')
            return []
    
    def notify(self, issue):
        """通知新任务"""
        print("=" * 60)
        print(f"🎯 Replit 新任务！")
        print(f"标题：{issue.get('title', 'Unknown')[:60]}")
        repo_url = issue.get('repository_url', '')
        if repo_url:
            print(f"仓库：{'/'.join(repo_url.split('/')[-2:])}")
        print(f"链接：{issue.get('html_url', '')}")
        print(f"更新：{issue.get('updated_at', '')[:10]}")
        
        # 尝试提取奖金
        body = issue.get('body', '')
        import re
        money_match = re.search(r'[\$](\d+(,\d{3})*(\.\d+)?)', body)
        if money_match:
            amount = money_match.group(1)
            print(f"奖金：${amount}")
        else:
            print("奖金：面议")
        
        print("=" * 60)
        
        # 保存通知
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        notify_file = self.notify_dir / f"replit_notify_{timestamp}.md"
        
        content = f"""# 🎯 Replit Bounties 新任务

**时间**: {datetime.now().isoformat()}

## 详情

- **标题**: {issue.get('title', 'Unknown')}
- **仓库**: {'/'.join(issue.get('repository_url', '').split('/')[-2:]) if issue.get('repository_url') else 'N/A'}
- **链接**: {issue.get('html_url', '')}
- **更新**: {issue.get('updated_at', '')[:10]}

## 建议操作

1. 查看任务详情
2. 评估技术可行性
3. 申请任务

---
*由 github-bounty-hunter v1.3.0 自动发送 | 版权：思捷娅科技 (SJYKJ)*"""
        
        with open(notify_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 通知已保存：{notify_file}")
    
    def run(self):
        """运行监控"""
        print("🦞 Replit Monitor 启动！")
        print("📍 监控平台：Replit Bounties")
        print("💰 快速现金流（$50-$500/任务）")
        print("=" * 60)
        
        token = os.getenv('GITHUB_TOKEN', '')
        if not token:
            print("❌ GITHUB_TOKEN 未配置")
            return
        
        # GitHub 搜索
        issues = self.search_github(token)
        print()
        
        if issues:
            print('=== 最新任务（前 5 个）===')
            print()
            for issue in issues[:5]:
                self.notify(issue)
                print()
        else:
            print('⚠️  暂无 Replit 任务')
            print()
            print('💡 建议：')
            print('1. 访问官网：https://replit.com/bounties')
            print('2. 快速现金流，适合练手')
            print('3. 奖金范围：$50-$500')

if __name__ == "__main__":
    monitor = ReplitMonitor()
    monitor.run()
