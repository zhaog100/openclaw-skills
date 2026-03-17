#!/usr/bin/env python3
"""
Algora 平台监控脚本 v2
- Algora.io 专业 Bounty 平台
- 高价值任务（$500-$10000）
- GitHub 原生集成

版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""

import os
import requests
from datetime import datetime
from pathlib import Path

class AlgoraMonitor:
    def __init__(self):
        self.notify_dir = Path('/tmp/github-bounty-notifies')
        self.notify_dir.mkdir(exist_ok=True)
        
        # Algora API（需要认证）
        self.api_url = "https://api.algora.io/v1/bounties"
        self.api_key = os.getenv('ALGORA_API_KEY', '')
        
        # GitHub 搜索 Algora 相关
        self.github_query = 'algora in:title,comments label:bounty is:issue is:open'
    
    def search_github(self, token):
        """通过 GitHub 搜索 Algora 任务"""
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f'https://api.github.com/search/issues?q={self.github_query}&sort=updated&order=desc&per_page=10'
        
        try:
            print('📡 通过 GitHub 搜索 Algora 任务...')
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                issues = data.get('items', [])
                print(f'✅ 找到 {len(issues)} 个 Algora 相关任务')
                return issues
            else:
                print(f'⚠️ API 返回：{response.status_code}')
                return []
        except Exception as e:
            print(f'❌ 搜索失败：{e}')
            return []
    
    def query_api(self):
        """通过 Algora API 查询（需要认证）"""
        if not self.api_key:
            print('⚠️  ALGORA_API_KEY 未配置，跳过 API 查询')
            return []
        
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        try:
            print('📡 通过 Algora API 查询...')
            response = requests.get(self.api_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                bounties = data.get('bounties', [])
                print(f'✅ 找到 {len(bounties)} 个 Algora 任务')
                return bounties
            else:
                print(f'⚠️ API 返回：{response.status_code}')
                return []
        except Exception as e:
            print(f'❌ API 查询失败：{e}')
            return []
    
    def notify(self, item, source='GitHub'):
        """通知新任务"""
        title = item.get('title', 'Unknown')[:60]
        url = item.get('html_url', item.get('url', 'Unknown'))
        updated = item.get('updated_at', item.get('createdAt', 'Unknown'))[:10]
        
        # 尝试提取奖金
        amount = '面议'
        body = item.get('body', '')
        import re
        money_match = re.search(r'[\$€£](\d+(,\d{3})*(\.\d+)?)', body)
        if money_match:
            amount = money_match.group(1)
        
        print("=" * 60)
        print(f"🎯 Algora 新任务！[{source}]")
        print(f"标题：{title}")
        print(f"奖金：${amount}")
        print(f"链接：{url}")
        print(f"更新：{updated}")
        print("=" * 60)
        
        # 保存通知
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        notify_file = self.notify_dir / f"algora_notify_{timestamp}.md"
        
        content = f"""# 🎯 Algora 新任务

**时间**: {datetime.now().isoformat()}
**来源**: {source}

## 详情

- **标题**: {title}
- **奖金**: ${amount}
- **链接**: {url}
- **更新**: {updated}

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
        print("🦞 Algora Monitor v2 启动！")
        print("📍 监控平台：Algora.io")
        print("💰 高价值任务（$500-$10000）")
        print("=" * 60)
        
        token = os.getenv('GITHUB_TOKEN', '')
        if not token:
            print("❌ GITHUB_TOKEN 未配置")
            return
        
        # GitHub 搜索
        issues = self.search_github(token)
        print()
        
        # API 查询
        api_bounties = self.query_api()
        print()
        
        all_items = []
        for issue in issues:
            all_items.append((issue, 'GitHub'))
        for bounty in api_bounties:
            all_items.append((bounty, 'API'))
        
        if all_items:
            print('=== 最新任务（前 5 个）===')
            print()
            for item, source in all_items[:5]:
                self.notify(item, source)
                print()
        else:
            print('⚠️  暂无 Algora 任务')
            print()
            print('💡 建议：')
            print('1. 访问官网：https://algora.io')
            print('2. 配置 ALGORA_API_KEY 获取专属任务')
            print('3. 高价值任务，值得重点关注')

if __name__ == "__main__":
    monitor = AlgoraMonitor()
    monitor.run()
