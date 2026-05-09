#!/usr/bin/env python3
"""
发送 GitHub Issue 评论
"""
import requests
import sys
import time
from pathlib import Path

# GitHub Token
TOKEN_FILE = Path.home() / '.git-credentials'

def get_github_token():
    """从 git-credentials 提取 Token"""
    try:
        with open(TOKEN_FILE) as f:
            for line in f:
                if 'github.com' in line:
                    # 格式: https://user:token@github.com
                    parts = line.strip().split(':')
                    if len(parts) >= 3:
                        token = parts[2].split('@')[0]
                        return token
    except Exception as e:
        print(f"❌ 读取 Token 失败: {e}")
    return None

def send_comment(repo, issue_number, body, max_retries=3):
    """发送评论（带重试）"""
    token = get_github_token()
    if not token:
        return False
    
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'Mozilla/5.0 (compatible; OpenClaw/1.0)'
    }
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                wait_time = 2 ** attempt  # 指数退避
                print(f"⏳ 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            
            print(f"🔄 发送评论到 {repo}#{issue_number}...（尝试 {attempt + 1}/{max_retries}）")
            response = requests.post(
                url,
                headers=headers,
                json={'body': body},
                timeout=60  # 增加超时时间
            )
            
            if response.status_code == 201:
                data = response.json()
                print(f"✅ 评论已发送！")
                print(f"📎 URL: {data['html_url']}")
                return True
            elif response.status_code == 403:
                print(f"⚠️  API 限流，等待 60 秒...")
                time.sleep(60)
                continue
            else:
                print(f"❌ 发送失败: {response.status_code}")
                print(f"   {response.text}")
                if attempt < max_retries - 1:
                    continue
                return False
                
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
            if attempt < max_retries - 1:
                continue
            return False
        except requests.exceptions.ConnectionError as e:
            print(f"❌ 连接错误: {e}")
            if attempt < max_retries - 1:
                continue
            return False
        except Exception as e:
            print(f"❌ 错误: {e}")
            if attempt < max_retries - 1:
                continue
            return False
    
    return False

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("用法: python3 github_comment.py <repo> <issue_number> <comment>")
        sys.exit(1)
    
    repo = sys.argv[1]
    issue_number = sys.argv[2]
    comment = sys.argv[3]
    
    success = send_comment(repo, issue_number, comment)
    sys.exit(0 if success else 1)
