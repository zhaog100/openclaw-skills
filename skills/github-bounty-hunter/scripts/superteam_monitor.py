#!/usr/bin/env python3
"""
Superteam Earn 监控脚本
- 监控 Superteam 任务
- 支持 GitHub + 官网 API
- 自动通知

版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
GitHub: https://github.com/zhaog100/openclaw-skills
"""

import os
import requests
from datetime import datetime
from pathlib import Path

class SuperteamMonitor:
    def __init__(self):
        self.notify_dir = Path('/tmp/github-bounty-notifies')
        self.notify_dir.mkdir(exist_ok=True)
        
        # Superteam GitHub 组织
        self.github_orgs = [
            'superteamDAO',
            'superteam-financial',
            'superteam-earn'
        ]
        
        # 官网 API（待认证）
        self.api_url = "https://earn.superteam.fi/api/bounties"
        
    def search_github(self, token):
        """通过 GitHub 搜索 Superteam 任务"""
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        all_issues = []
        
        for org in self.github_orgs:
            query = f'org:{org} is:issue is:open label:bounty'
            url = f'https://api.github.com/search/issues?q={query}&sort=updated&order=desc&per_page=10'
            
            try:
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    issues = data.get('items', [])
                    all_issues.extend(issues)
            except Exception as e:
                print(f"⚠️ {org} 搜索失败：{e}")
        
        return all_issues
    
    def notify(self, issue):
        """通知新任务"""
        print("=" * 60)
        print(f"🎯 Superteam 新任务！")
        print(f"标题：{issue.get('title', 'Unknown')[:60]}")
        print(f"仓库：{'/'.join(issue.get('repository_url', '').split('/')[-2:])}")
        print(f"链接：{issue.get('html_url', '')}")
        print(f"更新：{issue.get('updated_at', '')[:10]}")
        print("=" * 60)
        
        # 保存通知
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        notify_file = self.notify_dir / f"superteam_notify_{timestamp}.md"
        
        content = f"""# 🎯 Superteam Earn 新任务

**时间**: {datetime.now().isoformat()}

## 详情

- **标题**: {issue.get('title', 'Unknown')}
- **仓库**: {'/'.join(issue.get('repository_url', '').split('/')[-2:])}
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
        print("🦞 Superteam Monitor 启动！")
        print("📍 监控平台：Superteam Earn")
        print("=" * 60)
        
        token = os.getenv('GITHUB_TOKEN', '')
        if not token:
            print("❌ GITHUB_TOKEN 未配置")
            return
        
        # GitHub 搜索
        issues = self.search_github(token)
        print(f"✅ 找到 {len(issues)} 个 Superteam 任务")
        print()
        
        if issues:
            print('=== 最新任务（前 5 个）===')
            print()
            for issue in issues[:5]:
                self.notify(issue)
                print()
        else:
            print('⚠️  暂无 Superteam 任务')
            print()
            print('💡 建议：')
            print('1. 访问官网：https://superteam.fi/earn')
            print('2. 加入 Discord：https://discord.gg/superteam')
            print('3. 关注 Twitter：@SuperteamDAO')

if __name__ == "__main__":
    monitor = SuperteamMonitor()
    monitor.run()
