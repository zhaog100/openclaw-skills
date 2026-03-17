# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""文本解析模块 - 从原始会议文本提取结构化信息"""

import re
from typing import List, Dict, Any


def parse_text(raw_text: str) -> Dict[str, Any]:
    """解析原始会议文本，提取议题、参与者、时间、地点、段落和讨论主题。

    Args:
        raw_text: 原始会议文本

    Returns:
        包含 topic, participants, time, location, paragraphs, discussion_points 的字典
    """
    lines = [l.strip() for l in raw_text.strip().split('\n') if l.strip()]

    topic = _extract_topic(lines)
    participants = _extract_participants(raw_text)
    time_info = _extract_time(raw_text)
    location = _extract_location(raw_text)
    paragraphs = _split_paragraphs(raw_text)
    discussion_points = _extract_discussion_points(paragraphs)

    return {
        'topic': topic,
        'participants': participants,
        'time': time_info,
        'location': location,
        'paragraphs': paragraphs,
        'discussion_points': discussion_points,
    }


def _extract_topic(lines: List[str]) -> str:
    """从首行或【议题】标记提取议题"""
    for line in lines:
        m = re.match(r'【议题[：:]?\s*】?\s*(.+)', line)
        if m:
            return m.group(1).strip()
        m = re.match(r'议题[：:]\s*(.+)', line)
        if m:
            return m.group(1).strip()
        m = re.match(r'会议[议题主题][：:]\s*(.+)', line)
        if m:
            return m.group(1).strip()
    # fallback: 第一行非空
    if lines:
        return re.sub(r'^[\d#*\-\[\s]+', '', lines[0]).strip() or '未定议题'
    return '未定议题'


def _extract_participants(text: str) -> List[str]:
    """提取参与者列表"""
    participants = []
    # 模式1: 参与者：张三、李四、王五
    m = re.search(r'(?:参与者|参会人员|与会人员|出席)[：:]\s*(.+?)(?:\n|$)', text)
    if m:
        raw = m.group(1)
        participants.extend(p.strip() for p in re.split(r'[、,，;；]', raw) if p.strip())
    # @提及
    at_mentions = re.findall(r'@(\S+)', text)
    for name in at_mentions:
        name = re.sub(r'[，。！？：；,\.!?:;]', '', name)
        if name and name not in participants:
            participants.append(name)
    # 模式2: 张三、李四参加
    if not participants:
        m = re.search(r'([\u4e00-\u9fff]{2,4}(?:[、,，][\u4e00-\u9fff]{2,4})+)\s*(?:参加|出席|参会)', text)
        if m:
            participants.extend(p.strip() for p in re.split(r'[、,，]', m.group(1)) if p.strip())
    return participants


def _extract_time(text: str) -> str:
    """提取会议时间"""
    patterns = [
        r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?\s*\d{0,2}[:：]?\d{0,2})',
        r'(?:会议时间|时间)[：:]\s*(.+?)(?:\n|$)',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1).strip()
    # fallback
    m = re.search(r'(\d{1,2}月\d{1,2}日)', text)
    if m:
        return m.group(1)
    return ''


def _extract_location(text: str) -> str:
    """提取会议地点"""
    patterns = [
        r'(?:会议地点|地点|会议室)[：:]\s*(.+?)(?:\n|$)',
        r'在(.{2,20}(?:会议室|办公室|大厅|楼层))',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1).strip()
    return ''


def _split_paragraphs(text: str) -> List[str]:
    """将文本按段落拆分"""
    blocks = re.split(r'\n\s*\n', text.strip())
    return [b.strip() for b in blocks if b.strip()]


def _extract_discussion_points(paragraphs: List[str]) -> List[str]:
    """从段落中提取讨论要点"""
    points = []
    for p in paragraphs:
        # 带编号的行
        for line in p.split('\n'):
            line = line.strip()
            m = re.match(r'(?:\d+[.、)）]\s*|[一二三四五六七八九十]+[、.]\s*)', line)
            if m:
                point = line[m.end():].strip()
                if len(point) > 5:
                    points.append(point)
    # fallback: 每段首句
    if not points:
        for p in paragraphs:
            first = p.split('\n')[0].strip()
            first = re.sub(r'^[\d#*\-\[\s【】]+', '', first)
            if 10 < len(first) < 200:
                points.append(first)
    return points
