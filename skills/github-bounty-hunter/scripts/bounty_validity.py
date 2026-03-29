#!/usr/bin/env python3
"""Bounty有效性预检 - 在认领前检查bounty是否仍然有效
2026-03-22 教训：ComfyUI bounty已停1年+，需提前检测"""
import requests, os, re, json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(os.path.expanduser('~/.openclaw/secrets/github-bounty-hunter.env'))

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}

# 仓库级黑名单：整个仓库的bounty都无效
REPO_BLACKLIST_FILE = Path(os.path.expanduser('~/.openclaw/workspace/data/bounty-repo-blacklist.txt'))

def load_repo_blacklist():
    """加载仓库级黑名单"""
    if REPO_BLACKLIST_FILE.exists():
        return set(line.strip().lower() for line in REPO_BLACKLIST_FILE.read_text().strip().split('\n') if line.strip() and not line.startswith('#'))
    return set()

def check_bounty_validity(owner, repo, number, body=''):
    """检查bounty是否有效。返回 (valid, reason)"""
    repo_key = f"{owner}/{repo}".lower()
    
    # 1. 仓库级黑名单
    blacklist = load_repo_blacklist()
    for blocked in blacklist:
        if blocked in repo_key:
            return False, f"仓库黑名单: {blocked}"
    
    # 2. 检查issue comments中是否有bounty失效声明
    try:
        r = requests.get(
            f'https://api.github.com/repos/{owner}/{repo}/issues/{number}/comments',
            headers=HEADERS, params={'per_page': 20}, timeout=10
        )
        if r.status_code == 200:
            for comment in r.json():
                body_text = (comment.get('body', '') or '').lower()
                # 关键失效信号
                invalid_signals = [
                    "don't do bounties",
                    "dont do bounties",
                    "no longer do bounties",
                    "bounty program ended",
                    "bounty program closed",
                    "stopped doing bounties",
                    "we don't offer bounties",
                    "not doing bounties anymore",
                    "bounty is cancelled",
                    "bounty revoked",
                    " bounty 已停",
                    "bounty已停",
                ]
                for signal in invalid_signals:
                    if signal in body_text:
                        return False, f"维护者声明bounty失效: {signal}"
    except:
        pass
    
    # 3. 检查issue body中的时间线索（bounty超1年可能失效）
    full_text = (body or '').lower()
    if 'bounty' in full_text:
        # 检查是否有"over 1 year"等失效提示
        stale_signals = [
            "over 1 year", "more than 1 year", "over a year",
            "not accepting", "no longer accepting",
            "closed bounty", "expired",
        ]
        for signal in stale_signals:
            if signal in full_text:
                return False, f"Issue包含失效信号: {signal}"
    
    return True, "OK"

if __name__ == '__main__':
    # CLI测试: python3 bounty_validity.py owner/repo number
    if len(sys.argv) >= 3:
        import sys
        parts = sys.argv[1].split('/')
        owner, repo = parts[0], parts[1]
        number = sys.argv[2]
        valid, reason = check_bounty_validity(owner, repo, number)
        print(f"{'✅' if valid else '❌'} {owner}/{repo}#{number}: {reason}")
