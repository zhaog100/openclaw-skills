#!/usr/bin/env python3
"""
Algora Bounty 监控脚本（v2.1 - 增强健壮性）

根据小米粒实战经验更新：
- Claim 不是在 Algora 平台点按钮
- 而是在 GitHub issue 评论区发 `/attempt`
- Algora bot 会自动扫描并关联到 Algora 账户
- 提交 PR 后自动关联，无需手动提交审核

增强功能：
- ✅ PID 文件管理（防止重复启动）
- ✅ 信号处理（优雅退出）
- ✅ 异常处理（带重试机制）
- ✅ 速率限制处理（自动等待）
- ✅ 状态持久化（STATE.json）

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
import sys
import json
import time
import signal
import requests
from datetime import datetime
from pathlib import Path

# 配置
ALGORA_API_URL = "https://api.algora.io/v1/bounties"
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
STATE_FILE = Path('/tmp/algora-bounty-state.json')
LOG_DIR = Path('/home/zhaog/.openclaw/workspace/skills/github-bounty-hunter/logs')
LOG_FILE = LOG_DIR / 'algora_monitor.log'
PID_FILE = Path('/home/zhaog/.openclaw/workspace/skills/github-bounty-hunter/algora_monitor.pid')

# 创建日志目录
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 钱包地址（可选配置，Claim 时填写也可以）
WALLET_ADDRESS = os.getenv('ALGORA_WALLET_ADDRESS', '')

# 如果没有配置，Claim 时会提示手动填写
NEED_WALLET_CONFIG = not WALLET_ADDRESS or WALLET_ADDRESS == '0x...'

# 全局变量
monitor = None

def log_message(message):
    """日志记录（可在信号处理中使用）"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
    except:
        pass

# 优雅退出处理
def signal_handler(signum, frame):
    """处理 SIGINT/SIGTERM 信号，优雅退出"""
    log_message("收到退出信号，正在保存状态并退出...")
    if monitor:
        monitor.save_state()
    # 清理 PID 文件
    if PID_FILE.exists():
        PID_FILE.unlink()
    sys.exit(0)

# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# 检查是否已在运行
def check_running():
    """检查是否已在运行，防止重复启动"""
    if PID_FILE.exists():
        try:
            with open(PID_FILE, 'r') as f:
                old_pid = int(f.read().strip())
            # 检查进程是否还在运行
            os.kill(old_pid, 0)
            log_message(f"❌ 脚本已在运行（PID: {old_pid}），请勿重复启动")
            sys.exit(1)
        except (ProcessLookupError, ValueError):
            # 进程已不存在，删除旧的 PID 文件
            PID_FILE.unlink()
            log_message("检测到上次异常退出，清理旧 PID 文件")
    
    # 写入当前 PID
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    log_message(f"✅ 脚本启动（PID: {os.getpid()}）")


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
        log_message(message)
    
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
            
        except Exception as e:  # RateLimitError
            if '403' in str(e) or 'rate limit' in str(e).lower():
                self.log("❌ 触发 GitHub API 速率限制，请等待 60 秒后重试")
            elif 'timeout' in str(e).lower():
                self.log("❌ 请求超时，请检查网络连接")
            else:
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
            
        except Exception as e:  # RateLimitError
            if '403' in str(e) or 'rate limit' in str(e).lower():
                self.log("❌ 触发 GitHub API 速率限制")
            elif 'timeout' in str(e).lower():
                self.log("❌ 请求超时")
            else:
                self.log(f"❌ Claim 失败：{e}")
            return False
    
    def run(self, max_claims=5):
        """运行监控（增强版 - 带异常处理）"""
        try:
            self.log("🚀 Algora Monitor 启动")
            
            # 扫描任务
            bounties = self.scan_bounties(limit=20)
            
            if not bounties:
                self.log("⚠️  没有找到合适的任务")
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
                
                # Claim 任务（带重试机制）
                success = False
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        success = self.claim_bounty(bounty)
                        if success:
                            break
                    except Exception as e:  # RateLimitError
                        if '403' in str(e) or 'rate limit' in str(e).lower():
                            wait_time = 60 * (attempt + 1)
                            self.log(f"⚠️  触发速率限制，等待 {wait_time} 秒后重试...")
                            time.sleep(wait_time)
                        else:
                            self.log(f"⚠️  Claim 失败（尝试 {attempt+1}/{max_retries}）：{e}")
                            if attempt < max_retries - 1:
                                time.sleep(10)
                
                if success:
                    claimed_count += 1
                    # 避免速率限制
                    time.sleep(5)
            
            self.log(f"📊 本次运行 Claim 了 {claimed_count} 个任务")
            self.log("✅ Algora Monitor 完成")
            
        except KeyboardInterrupt:
            self.log("⚠️  用户中断，正在退出...")
        except Exception as e:
            self.log(f"❌ 运行异常：{e}")
            # 保存当前状态
            self.save_state()
        finally:
            # 清理 PID 文件
            if PID_FILE.exists():
                PID_FILE.unlink()


if __name__ == '__main__':
    # 检查是否已在运行
    check_running()
    
    # 创建监控实例
    monitor = AlgoraMonitor()
    
    # 运行监控
    monitor.run(max_claims=5)
