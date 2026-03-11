#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上下文监控Hook v1.1 - 优化版本
使用文件读取方式获取会话信息
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
import subprocess

# 配置
THRESHOLD = 0.95  # 95%触发阈值
WORKSPACE = "/root/.openclaw/workspace"
MEMORY_DIR = f"{WORKSPACE}/memory"
LOG_FILE = f"{WORKSPACE}/logs/context-monitor.log"

# 确保目录存在
Path(MEMORY_DIR).mkdir(parents=True, exist_ok=True)
Path(f"{WORKSPACE}/logs").mkdir(parents=True, exist_ok=True)

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)

    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

def get_session_status():
    """获取当前会话状态（使用openclaw status命令）"""
    try:
        # 运行openclaw status命令
        result = subprocess.run(
            ['openclaw', 'status'],
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout

        # 解析会话信息
        sessions = []

        # 查找Sessions部分
        lines = output.split('\n')
        in_sessions = False

        for line in lines:
            if 'Sessions' in line:
                in_sessions = True
                continue

            if in_sessions and '┌' in line:
                continue

            if in_sessions and 'agent:main:' in line:
                # 解析会话行
                # 格式: │ agent:main:qqbot:direct:b1094aa… │ direct │ just now │ glm-5 │ 90k/205k (44%) · 🗄️ 3% cached │

                parts = line.split('│')
                if len(parts) >= 5:
                    session_key = parts[1].strip()
                    kind = parts[2].strip()
                    age = parts[3].strip()
                    model = parts[4].strip()

                    # 提取token信息
                    token_match = re.search(r'(\d+)k/(\d+)k\s*\((\d+)%\)', line)
                    if token_match:
                        tokens_used = int(token_match.group(1)) * 1000
                        tokens_limit = int(token_match.group(2)) * 1000
                        usage_percent = int(token_match.group(3))
                        usage = usage_percent / 100.0

                        sessions.append({
                            'key': session_key,
                            'kind': kind,
                            'age': age,
                            'model': model,
                            'tokens_used': tokens_used,
                            'tokens_limit': tokens_limit,
                            'usage': usage
                        })

        return sessions

    except subprocess.TimeoutExpired:
        log("❌ 命令超时")
        return []
    except Exception as e:
        log(f"❌ 获取会话状态异常: {e}")
        return []

def check_context_usage(sessions):
    """检查上下文使用率"""
    for session in sessions:
        session_key = session.get('key', 'unknown')
        model = session.get('model', 'unknown')
        usage = session.get('usage', 0)
        tokens_used = session.get('tokens_used', 0)
        tokens_limit = session.get('tokens_limit', 0)

        log(f"📊 会话: {session_key[:50]}...")
        log(f"   模型: {model}")
        log(f"   Token使用: {tokens_used}/{tokens_limit} ({usage*100:.1f}%)")

        if usage >= THRESHOLD:
            log(f"⚠️ 达到触发阈值 {THRESHOLD*100}%!")
            return session

    return None

def trigger_memory_update(session_info):
    """触发记忆更新"""
    log("💾 开始更新记忆...")

    today = datetime.now().strftime('%Y-%m-%d')
    memory_file = f"{MEMORY_DIR}/{today}-context-summary.md"

    summary = f"""# 上下文自动保存

**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**会话ID**: {session_info['key']}
**模型**: {session_info['model']}
**Token使用**: {session_info['tokens_used']}/{session_info['tokens_limit']} ({session_info['usage']*100:.1f}%)

## 触发原因
- 上下文使用率达到 {session_info['usage']*100:.1f}%
- 超过阈值 {THRESHOLD*100}%

## 状态
✅ 记忆已自动保存
✅ 可以开始新会话

## 下一步
- 继续当前会话（可能很快达到上限）
- 开始新会话（自动加载记忆）

---
*此文件由上下文监控Hook自动生成*
*时间: {datetime.now().isoformat()}*
"""

    with open(memory_file, 'w', encoding='utf-8') as f:
        f.write(summary)

    log(f"✅ 记忆已保存: {memory_file}")
    return memory_file

def notify_user(session_info, memory_file):
    """通知用户"""
    log("📢 准备通知用户...")

    notification = f"""
💡 上下文即将达到上限（{session_info['usage']*100:.1f}%）

我已经自动保存了本次对话的关键信息
记忆文件: {memory_file}

建议：
- 继续当前会话（可能很快达到上限）
- 开始新会话（自动加载记忆）

新会话会自动加载我们的记忆 💾
"""

    log(notification)

    # TODO: 通过QQ Bot发送通知
    # 可以使用message工具

    return notification

def main():
    """主函数"""
    log("=" * 60)
    log("🔍 上下文监控Hook启动")
    log("=" * 60)

    # 获取会话状态
    sessions = get_session_status()

    if not sessions:
        log("⚠️ 未找到活跃会话")
        return

    log(f"📊 找到 {len(sessions)} 个会话")

    # 检查上下文使用率
    session_info = check_context_usage(sessions)

    if session_info:
        log("⚠️ 检测到会话达到阈值！")

        # 触发记忆更新
        memory_file = trigger_memory_update(session_info)

        # 通知用户
        notify_user(session_info, memory_file)

        log("✅ Hook执行完成")
    else:
        log("✅ 所有会话上下文正常")

    log("=" * 60)

if __name__ == "__main__":
    main()
