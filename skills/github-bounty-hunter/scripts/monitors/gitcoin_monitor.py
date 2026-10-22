# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/usr/bin/env python3
"""
Gitcoin Bounty 监控脚本
- 扫描 Gitcoin 上的 bounty 任务
- 支持 GraphQL API
- 自动通知

版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
GitHub: https://github.com/your_username/openclaw-skills
"""

import os
import tempfile
import json
import requests
from datetime import datetime
from pathlib import Path

class GitcoinMonitor:
    def __init__(self):
        self.api_url = "https://api.gitcoin.co/graphql"
        self.state_file = Path(tempfile.gettempdir()) / 'gitcoin-bounty-state.yaml'
        self.notify_dir = Path(tempfile.gettempdir()) / 'github-bounty-notifies'
        self.notify_dir.mkdir(exist_ok=True)
        
    def query_bounties(self, limit=20):
        """查询 Gitcoin bounty 任务"""
        query = """
        query GetBounties($limit: Int!) {
            bounties(first: $limit, orderBy: "-createdAt") {
                id
                title
                description
                tokenAmount
                tokenAddress
                issuer {
                    address
                    username
                }
                repository {
                    url
                    name
                }
                createdAt
                status
            }
        }
        """
        
        variables = {"limit": limit}
        
        try:
<<<<<<< HEAD
            logger.info("📡 查询 Gitcoin Bounties...")
=======
            print("📡 查询 Gitcoin Bounties...")
>>>>>>> skills/main
            response = requests.post(
                self.api_url,
                json={'query': query, 'variables': variables},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'bounties' in data['data']:
                    return data['data']['bounties']
            else:
<<<<<<< HEAD
                logger.warning(f"⚠️ API 返回状态码：{response.status_code}")
=======
                print(f"⚠️ API 返回状态码：{response.status_code}")
>>>>>>> skills/main
                
            return []
            
        except Exception as e:
<<<<<<< HEAD
            logger.error(f"❌ 查询失败：{e}")
=======
            print(f"❌ 查询失败：{e}")
>>>>>>> skills/main
            return []
    
    def filter_bounties(self, bounties, min_amount=10):
        """筛选适合的 bounty"""
        suitable = []
        
        for bounty in bounties:
            try:
                amount = float(bounty.get('tokenAmount', 0))
                if amount >= min_amount and bounty.get('status') == 'active':
                    suitable.append(bounty)
            except:
                continue
                
        return suitable
    
    def notify(self, bounty):
        """通知新 bounty"""
<<<<<<< HEAD
        logger.info("=" * 60)
        logger.info(f"🎯 发现新 Bounty！")
        logger.info(f"标题：{bounty.get('title', 'Unknown')}")
        logger.info(f"奖金：{bounty.get('tokenAmount', 0)} {bounty.get('tokenAddress', 'Unknown')}")
        logger.info(f"发布者：{bounty.get('issuer', {}).get('username', 'Unknown')}")
        logger.info(f"仓库：{bounty.get('repository', {}).get('url', 'Unknown')}")
        logger.info(f"创建：{bounty.get('createdAt', 'Unknown')}")
        logger.info("=" * 60)
=======
        print("=" * 60)
        print(f"🎯 发现新 Bounty！")
        print(f"标题：{bounty.get('title', 'Unknown')}")
        print(f"奖金：{bounty.get('tokenAmount', 0)} {bounty.get('tokenAddress', 'Unknown')}")
        print(f"发布者：{bounty.get('issuer', {}).get('username', 'Unknown')}")
        print(f"仓库：{bounty.get('repository', {}).get('url', 'Unknown')}")
        print(f"创建：{bounty.get('createdAt', 'Unknown')}")
        print("=" * 60)
>>>>>>> skills/main
        
        # 写入通知文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        notify_file = self.notify_dir / f"gitcoin_notify_{timestamp}.md"
        
        content = f"""# 🎯 Gitcoin Bounty 发现

**时间**: {datetime.now().isoformat()}

## 详情

- **标题**: {bounty.get('title', 'Unknown')}
- **奖金**: {bounty.get('tokenAmount', 0)} {bounty.get('tokenAddress', 'Unknown')}
- **发布者**: {bounty.get('issuer', {}).get('username', 'Unknown')}
- **仓库**: {bounty.get('repository', {}).get('url', 'Unknown')}
- **创建**: {bounty.get('createdAt', 'Unknown')}

## 建议操作

1. 查看任务详情
2. 评估技术可行性
3. 申请任务

---
*由 github-bounty-hunter v7.5.6 自动发送 | 版权：思捷娅科技 (SJYKJ)*"""
        
        with open(notify_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
<<<<<<< HEAD
        logger.info(f"✅ 通知已保存：{notify_file}")
=======
        print(f"✅ 通知已保存：{notify_file}")
>>>>>>> skills/main
    
    def save_state(self, bounties):
        """保存状态"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            f.write(f"# Gitcoin Bounty State\n")
            f.write(f"# 更新时间：{datetime.now().isoformat()}\n\n")
            f.write(f"total_bounties: {len(bounties)}\n")
            f.write(f"last_scan: {datetime.now().isoformat()}\n")
    
    def run(self):
        """运行监控"""
<<<<<<< HEAD
        logger.info("🦞 Gitcoin Monitor 启动！")
        logger.info(f"📍 监控平台：Gitcoin")
        logger.info(f"⏰ 扫描频率：30 分钟")
        logger.info("=" * 60)
        
        # 查询
        bounties = self.query_bounties(limit=20)
        logger.info(f"✅ 获取到 {len(bounties)} 个 Bounties")
        
        # 筛选
        suitable = self.filter_bounties(bounties, min_amount=10)
        logger.info(f"✅ 筛选出 {len(suitable)} 个适合的任务")
=======
        print("🦞 Gitcoin Monitor 启动！")
        print(f"📍 监控平台：Gitcoin")
        print(f"⏰ 扫描频率：30 分钟")
        print("=" * 60)
        
        # 查询
        bounties = self.query_bounties(limit=20)
        print(f"✅ 获取到 {len(bounties)} 个 Bounties")
        
        # 筛选
        suitable = self.filter_bounties(bounties, min_amount=10)
        print(f"✅ 筛选出 {len(suitable)} 个适合的任务")
>>>>>>> skills/main
        
        # 通知
        for bounty in suitable[:5]:  # 最多通知 5 个
            self.notify(bounty)
<<<<<<< HEAD
            logger.info()
=======
            print()
>>>>>>> skills/main
        
        # 保存状态
        self.save_state(bounties)
        
<<<<<<< HEAD
        logger.info("🎉 扫描完成！")
        logger.info("⏳ 30 分钟后再次扫描...")
=======
        print("🎉 扫描完成！")
        print("⏳ 30 分钟后再次扫描...")
>>>>>>> skills/main

def search_gitcoin_github():
    """通过 GitHub 搜索 Gitcoin 相关 bounty（主要方式）"""
    token = os.getenv('GITHUB_TOKEN', '')
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # 搜索带 gitcoin 标签的 Issue
    query = 'gitcoin in:title,comments label:bounty is:issue is:open'
    url = f'https://api.github.com/search/issues?q={query}&sort=updated&order=desc&per_page=10'
    
<<<<<<< HEAD
    logger.info('📡 通过 GitHub 搜索 Gitcoin 任务...')
=======
    print('📡 通过 GitHub 搜索 Gitcoin 任务...')
>>>>>>> skills/main
    response = requests.get(url, headers=headers, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
<<<<<<< HEAD
        logger.info(f'✅ 找到 {len(items)} 个 Gitcoin 相关任务')
        logger.info()
        
        if items:
            logger.info('=== Gitcoin Bounty 任务（前 5 个）===')
            logger.info()
            for i, item in enumerate(items[:5], 1):
                logger.info(f'{i}. 📌 {item.get("title", "")[:60]}')
                logger.info(f'   仓库：{"/".join(item.get("repository_url", "").split("/")[-2:])}')
                logger.info(f'   链接：{item.get("html_url", "")}')
                logger.info(f'   更新：{item.get("updated_at", "")[:10]}')
                logger.info()
        else:
            logger.warning('⚠️  暂无 Gitcoin 相关任务')
    else:
        logger.error(f'❌ 搜索失败：{response.status_code}')
        logger.info(response.text[:300])
=======
        print(f'✅ 找到 {len(items)} 个 Gitcoin 相关任务')
        print()
        
        if items:
            print('=== Gitcoin Bounty 任务（前 5 个）===')
            print()
            for i, item in enumerate(items[:5], 1):
                print(f'{i}. 📌 {item.get("title", "")[:60]}')
                print(f'   仓库：{"/".join(item.get("repository_url", "").split("/")[-2:])}')
                print(f'   链接：{item.get("html_url", "")}')
                print(f'   更新：{item.get("updated_at", "")[:10]}')
                print()
        else:
            print('⚠️  暂无 Gitcoin 相关任务')
    else:
        print(f'❌ 搜索失败：{response.status_code}')
        print(response.text[:300])
>>>>>>> skills/main


def search_gitcoin_github():
    """通过 GitHub 搜索 Gitcoin 相关 bounty"""
    import requests
    
    token = os.getenv('GITHUB_TOKEN', '')
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # 搜索带 gitcoin 标签的 Issue
    query = 'gitcoin in:title,comments label:bounty is:issue is:open'
    url = f'https://api.github.com/search/issues?q={query}&sort=updated&order=desc&per_page=10'
    
<<<<<<< HEAD
    logger.info('📡 通过 GitHub 搜索 Gitcoin 任务...')
=======
    print('📡 通过 GitHub 搜索 Gitcoin 任务...')
>>>>>>> skills/main
    response = requests.get(url, headers=headers, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
<<<<<<< HEAD
        logger.info(f'✅ 找到 {len(items)} 个 Gitcoin 相关任务')
        logger.info()
        
        if items:
            logger.info('=== Gitcoin Bounty 任务（前 5 个）===')
            logger.info()
            for i, item in enumerate(items[:5], 1):
                logger.info(f'{i}. 📌 {item.get("title", "")[:60]}')
                logger.info(f'   仓库：{"/".join(item.get("repository_url", "").split("/")[-2:])}')
                logger.info(f'   链接：{item.get("html_url", "")}')
                logger.info(f'   更新：{item.get("updated_at", "")[:10]}')
                logger.info()
        else:
            logger.warning('⚠️  暂无 Gitcoin 相关任务')
    else:
        logger.error(f'❌ 搜索失败：{response.status_code}')
        logger.info(response.text[:300])
=======
        print(f'✅ 找到 {len(items)} 个 Gitcoin 相关任务')
        print()
        
        if items:
            print('=== Gitcoin Bounty 任务（前 5 个）===')
            print()
            for i, item in enumerate(items[:5], 1):
                print(f'{i}. 📌 {item.get("title", "")[:60]}')
                print(f'   仓库：{"/".join(item.get("repository_url", "").split("/")[-2:])}')
                print(f'   链接：{item.get("html_url", "")}')
                print(f'   更新：{item.get("updated_at", "")[:10]}')
                print()
        else:
            print('⚠️  暂无 Gitcoin 相关任务')
    else:
        print(f'❌ 搜索失败：{response.status_code}')
        print(response.text[:300])
>>>>>>> skills/main


if __name__ == "__main__":
    # 优先使用 GitHub 搜索（不需要额外 API Key）
<<<<<<< HEAD
    logger.info("🦞 Gitcoin Monitor - GitHub 搜索模式")
    logger.info("=" * 60)
=======
    print("🦞 Gitcoin Monitor - GitHub 搜索模式")
    print("=" * 60)
>>>>>>> skills/main
    search_gitcoin_github()
    
    # 如果配置了 Gitcoin API Key，再尝试 API 查询
    if os.getenv('GITCOIN_API_KEY'):
<<<<<<< HEAD
        logger.info()
        logger.info("=" * 60)
        logger.info("📡 尝试 Gitcoin API 查询...")
        monitor = GitcoinMonitor()
        monitor.run()
    else:
        logger.info()
        logger.warning("⚠️  未配置 GITCOIN_API_KEY，跳过 API 查询")
        logger.info("💡 提示：配置 API Key 可以获取更多 Gitcoin 专属任务")
=======
        print()
        print("=" * 60)
        print("📡 尝试 Gitcoin API 查询...")
        monitor = GitcoinMonitor()
        monitor.run()
    else:
        print()
        print("⚠️  未配置 GITCOIN_API_KEY，跳过 API 查询")
        print("💡 提示：配置 API Key 可以获取更多 Gitcoin 专属任务")
>>>>>>> skills/main
