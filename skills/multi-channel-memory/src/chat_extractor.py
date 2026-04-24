#!/usr/bin/env python3
"""
多通道对话提取器 - Multi-Channel Chat Extractor
================================================

功能:
1. 读取所有会话记录 (sessions/*.jsonl)
2. 过滤 user/assistant 角色的消息
3. UTC 时间戳转换为北京时间 (Asia/Shanghai +8h)
4. 清理元数据 (message_id, sender metadata 等)
5. 按时间排序，标注通道来源
6. 输出到 memory/chat-YYYY-MM-DD.md

用法:
    python chat_extractor.py [--date YYYY-MM-DD] [--output-dir memory/]
"""

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# 配置
SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
OUTPUT_DIR = Path.home() / ".openclaw" / "workspace" / "memory"
TIMEZONE_OFFSET = timedelta(hours=8)  # Asia/Shanghai


def load_sessions() -> Dict:
    """读取 sessions.json 获取所有会话"""
    sessions_file = SESSIONS_DIR / "sessions.json"
    if not sessions_file.exists():
        print(f"❌ Sessions file not found: {sessions_file}")
        return {}
    
    with open(sessions_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_jsonl_session(file_path: Path) -> List[Dict]:
    """解析 .jsonl 会话文件"""
    messages = []
    if not file_path.exists():
        return messages
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get('type') == 'message':
                    msg_data = entry.get('message', {})
                    role = msg_data.get('role', 'unknown')
                    
                    # 提取内容（支持多种格式）
                    content_list = msg_data.get('content', [])
                    text_content = ''
                    if isinstance(content_list, list):
                        for item in content_list:
                            if isinstance(item, dict):
                                if item.get('type') == 'text':
                                    text_content += item.get('text', '') + '\n'
                                elif item.get('type') == 'thinking':
                                    pass  # 跳过 thinking
                    elif isinstance(content_list, str):
                        text_content = content_list
                    
                    if text_content and role in ['user', 'assistant']:
                        messages.append({
                            'role': role,
                            'content': text_content.strip(),
                            'createdAt': entry.get('timestamp', '')
                        })
            except json.JSONDecodeError:
                continue
    return messages


def extract_channel(session_data: Dict) -> str:
    """从会话元数据提取通道"""
    channel = session_data.get('lastChannel', 'unknown')
    origin = session_data.get('origin', {})
    if isinstance(origin, dict):
        channel = origin.get('channel', channel)
    
    channel_map = {
        'qqbot': 'QQ',
        'feishu': '飞书',
        'wechat': '微信',
        'telegram': 'Telegram',
        'discord': 'Discord',
        'terminal': '终端',
        'web': 'Web',
        'webchat': 'Web',
        'cron': '定时任务',
        'heartbeat': '心跳',
        'unknown': '未知'
    }
    
    return channel_map.get(channel, channel.title())


def utc_to_cst(utc_timestamp) -> datetime:
    """UTC 时间戳转换为北京时间"""
    try:
        # 支持毫秒时间戳（整数）或 ISO 字符串
        if isinstance(utc_timestamp, (int, float)):
            # 毫秒时间戳
            utc_dt = datetime.fromtimestamp(utc_timestamp / 1000)
        else:
            # ISO 字符串
            utc_dt = datetime.fromisoformat(str(utc_timestamp).replace('Z', '+00:00'))
        cst_dt = utc_dt + TIMEZONE_OFFSET
        return cst_dt
    except Exception as e:
        print(f"⚠️ 时间戳解析失败：{utc_timestamp} - {e}")
        return datetime.now()


def clean_message_content(content: str) -> str:
    """清理消息内容中的元数据"""
    if not content:
        return ""
    
    # 移除 Conversation info JSON 块
    content = re.sub(
        r'Conversation info \(untrusted metadata\):.*?```json.*?```',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 移除 Sender metadata JSON 块
    content = re.sub(
        r'Sender \(untrusted metadata\):.*?```json.*?```',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 移除 [QQBot] 等标记
    content = re.sub(r'\[QQBot\].*?\n', '', content)
    content = re.sub(r'message_id.*?\n', '', content)
    content = re.sub(r'sender_id.*?\n', '', content)
    
    # 移除工具调用标记
    content = re.sub(r'\[non-text content:.*?\]', '', content)
    content = re.sub(r'\[toolCall.*?\]', '', content)
    
    # 移除多余空行
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.strip()


def extract_messages_for_date(sessions_data: Dict, target_date: str) -> List[Dict]:
    """提取指定日期的所有消息"""
    all_messages = []
    target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
    
    # 获取所有 jsonl 文件
    jsonl_files = list(SESSIONS_DIR.glob('*.jsonl'))
    
    for jsonl_file in jsonl_files:
        # 跳过 checkpoint 文件
        if '.checkpoint.' in jsonl_file.name:
            continue
        
        # 提取 session ID（文件名去掉 .jsonl）
        session_id = jsonl_file.stem
        
        # 查找匹配的会话数据
        session_data = None
        channel = 'unknown'
        for key, data in sessions_data.items():
            if data.get('sessionId') == session_id or key == session_id:
                session_data = data
                channel = extract_channel(data)
                break
        
        if not session_data:
            session_data = {'key': session_id}
            channel = 'unknown'
        
        # 解析消息
        messages = parse_jsonl_session(jsonl_file)
        
        for msg in messages:
            timestamp = msg.get('createdAt', '')
            if not timestamp:
                continue
            
            cst_dt = utc_to_cst(timestamp)
            msg_date = cst_dt.date()
            
            if msg_date != target_date_obj:
                continue
            
            role = msg.get('role', 'unknown')
            if role not in ['user', 'assistant']:
                continue
            
            content = msg.get('content', '')
            if not content:
                continue
            
            clean_content = clean_message_content(content)
            if not clean_content:
                continue
            
            all_messages.append({
                'timestamp': cst_dt,
                'channel': channel,
                'role': role,
                'content': clean_content,
                'session_id': session_id
            })
    
    all_messages.sort(key=lambda x: x['timestamp'])
    return all_messages


def format_chat_log(messages: List[Dict], target_date: str) -> str:
    """格式化聊天日志为 Markdown"""
    lines = []
    lines.append(f"# 多通道对话记录 - {target_date}\n")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S CST')}\n")
    lines.append(f"**通道数量**: {len(set(m['channel'] for m in messages))}\n")
    lines.append(f"**消息总数**: {len(messages)}\n")
    lines.append("---\n")
    
    current_hour = None
    
    for msg in messages:
        msg_hour = msg['timestamp'].hour
        if msg_hour != current_hour:
            current_hour = msg_hour
            lines.append(f"\n## {msg_hour:02d}:00 - {msg_hour:02d}:59\n")
        
        time_str = msg['timestamp'].strftime('%H:%M:%S')
        role_map = {'user': '用户', 'assistant': 'AI'}
        role_str = role_map.get(msg['role'], msg['role'])
        
        lines.append(f"### {time_str} [{msg['channel']}] {role_str}\n")
        lines.append(f"{msg['content']}\n")
        lines.append("---\n")
    
    return '\n'.join(lines)


def main():
    target_date = datetime.now().strftime('%Y-%m-%d')
    output_dir = OUTPUT_DIR
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--date' and i + 1 < len(args):
            target_date = args[i + 1]
            i += 2
        elif args[i] == '--output-dir' and i + 1 < len(args):
            output_dir = Path(args[i + 1])
            i += 2
        else:
            i += 1
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🔍 加载会话列表...")
    sessions_data = load_sessions()
    print(f"✅ 找到 {len(sessions_data)} 个会话")
    
    print(f"📅 提取日期：{target_date}")
    messages = extract_messages_for_date(sessions_data, target_date)
    print(f"✅ 提取到 {len(messages)} 条消息")
    
    if not messages:
        print("⚠️ 没有找到消息")
        return
    
    print(f"📝 格式化聊天日志...")
    chat_log = format_chat_log(messages, target_date)
    
    output_file = output_dir / f"chat-{target_date}.md"
    with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
        f.write(chat_log)
    
    print(f"✅ 已保存到：{output_file}")
    print(f"📊 统计:")
    print(f"   - 通道数：{len(set(m['channel'] for m in messages))}")
    print(f"   - 消息数：{len(messages)}")
    print(f"   - 用户消息：{sum(1 for m in messages if m['role'] == 'user')}")
    print(f"   - AI 消息：{sum(1 for m in messages if m['role'] == 'assistant')}")


if __name__ == '__main__':
    main()
