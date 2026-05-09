#!/usr/bin/env python3
"""
BountySource 监控脚本
- 开源项目 Bug 修复
- 奖金范围：$100-$2000
- 历史悠久，任务稳定

版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""

import os
import requests
from datetime import datetime
from pathlib import Path

class BountySourceMonitor:
    def __init__(self):
        self.notify_dir = Path('/tmp/github-bounty-notifies')
        self.notify_dir.mkdir(exist_ok=True)
        
        # GitHub 搜索 BountySource 相关
        self.github_query = 'bountysource in:title,comments OR "bounty" in:title label:bounty is:issue is:open'
    
    def search_github(self, token):
        """通过 GitHub 搜索 BountySource 任务"""
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f'https://api.github.com/search/issues?q={self.github_query}&sort=updated&order=desc&per_page=10'
        
        try:
            print('📡 搜索 BountySource 相关任务...')
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                issues = data.get('items', [])
                print(f'✅ 找到 {len(issues)} 个任务')
                return issues
            else:
                print(f'⚠️ API 返回：{response.status_code}')
                return []
        except Exception as e:
            print(f'❌ 搜索失败：{e}')
            return []
    
    def notify(self, issue):
        """通知新任务"""
        title = issue.get('title', 'Unknown')[:60]
        url = issue.get('html_url', 'Unknown')
        updated = issue.get('updated_at', 'Unknown')[:10]
        
        # 提取奖金
        amount = '面议'
        body = issue.get('body', '')
        import re
        money_match = re.search(r'[\$](\d+(,\d{3})*(\.\d+)?)', body)
        if money_match:
            amount = money_match.group(1)
        
        print("=" * 60)
        print(f"🎯 BountySource 新任务！")
        print(f"标题：{title}")
        print(f"奖金：${amount}")
        print(f"链接：{url}")
        print(f"更新：{updated}")
        print("=" * 60)
        
        # 保存通知
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        notify_file = self.notify_dir / f"bountysource_notify_{timestamp}.md"
        
        content = f"""# 🎯 BountySource 新任务

**时间**: {datetime.now().isoformat()}

## 详情

- **标题**: {title}
- **奖金**: ${amount}
- **链接**: {url}
- **更新**: {updated}

## 建议操作

1. 查看 BountySource 详情
2. 评估技术可行性
3. 申请任务

---
*由 github-bounty-hunter v1.3.0 自动发送 | 版权：思捷娅科技 (SJYKJ)*"""
        
        with open(notify_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 通知已保存：{notify_file}")
    
    def run(self):
        """运行监控"""
        print("🦞 BountySource Monitor 启动！")
        print("📍 监控平台：BountySource")
        print("💰 Bug 修复（$100-$2000）")
        print("=" * 60)
        
        token = os.getenv('GITHUB_TOKEN', '')
        if not token:
            print("❌ GITHUB_TOKEN 未配置")
            return
        
        issues = self.search_github(token)
        print()
        
        if issues:
            print('=== 最新任务（前 5 个）===')
            print()
            for issue in issues[:5]:
                self.notify(issue)
                print()
        else:
            print('⚠️  暂无 BountySource 任务')
            print()
            print('💡 建议：')
            print('1. 访问官网：https://www.bountysource.com')
            print('2. 关注热门开源项目')
            print('3. Bug 修复为主，技术门槛较低')

if __name__ == "__main__":
    monitor = BountySourceMonitor()
    monitor.run()
