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

def send_comment(repo, issue_number, body):
    """发送评论"""
    token = get_github_token()
    if not token:
        return False
    
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json'
    }
    
    try:
        print(f"🔄 发送评论到 {repo}#{issue_number}...")
        response = requests.post(
            url,
            headers=headers,
            json={'body': body},
            timeout=30
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ 评论已发送！")
            print(f"📎 URL: {data['html_url']}")
            return True
        else:
            print(f"❌ 发送失败: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
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
