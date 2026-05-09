# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""文本解析模块 - 从原始会议文本提取结构化信息"""

import re
from typing import List, Dict, Any, Tuple


def parse_text(raw_text: str) -> Dict[str, Any]:
    """解析原始会议文本，提取议题、参与者、时间、地点、段落和讨论主题。"""
    lines = [l.strip() for l in raw_text.strip().split('\n') if l.strip()]

    # 先识别对话格式 vs 结构化格式
    is_dialogue = _detect_dialogue_format(raw_text)

    topic = _extract_topic(lines, is_dialogue)
    participants = _extract_participants(raw_text, is_dialogue)
    time_info = _extract_time(raw_text)
    location = _extract_location(raw_text)
    paragraphs = _split_paragraphs(raw_text)
    discussion_points = _extract_discussion_points(paragraphs, is_dialogue)
    summary_text = _extract_dialogue_summary(raw_text) if is_dialogue else ''

    return {
        'topic': topic,
        'participants': participants,
        'time': time_info,
        'location': location,
        'paragraphs': paragraphs,
        'discussion_points': discussion_points,
        'is_dialogue': is_dialogue,
        'dialogue_summary': summary_text,
    }


def _detect_dialogue_format(text: str) -> bool:
    """检测是否为对话格式（张三：xxx / 张三:xxx）"""
    lines = text.strip().split('\n')
    dialogue_lines = 0
    total_lines = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        total_lines += 1
        # 匹配 "中文名：内容" 格式
        if re.match(r'^[\u4e00-\u9fff]{1,4}[：:]', line):
            dialogue_lines += 1
    return total_lines > 0 and dialogue_lines / total_lines >= 0.3


def _parse_dialogue_lines(text: str) -> List[Tuple[str, str]]:
    """解析对话行，返回 [(说话人, 内容), ...]"""
    entries = []
    for line in text.strip().split('\n'):
        line = line.strip()
        m = re.match(r'^([\u4e00-\u9fff]{1,4})[：:]\s*(.+)', line)
        if m:
            entries.append((m.group(1), m.group(2)))
    return entries


def _extract_topic(lines: List[str], is_dialogue: bool) -> str:
    """提取议题"""
    # 优先找显式标记
    for line in lines:
        for pattern in [
            r'【议题[：:]?\s*】?\s*(.+)',
            r'议题[：:]\s*(.+)',
            r'会议[议题主题][：:]\s*(.+)',
        ]:
            m = re.match(pattern, line)
            if m:
                return m.group(1).strip()
    # 对话格式：从第一段内容中提取主题
    if is_dialogue and lines:
        first = re.sub(r'^[\u4e00-\u9fff]{1,4}[：:]\s*', '', lines[0])
        # 去掉语气词和引号
        first = re.sub(r'^[「"\'『]', '', first)
        first = re.sub(r'[」"\'』]$', '', first)
        # 如果太长，取前30字+省略
        if len(first) > 50:
            first = first[:50] + '……'
        return first if first else '未定议题'
    # 结构化格式 fallback
    if lines:
        first = re.sub(r'^[\d#*\-\[\s]+', '', lines[0]).strip()
        return first if first else '未定议题'
    return '未定议题'


def _extract_participants(text: str, is_dialogue: bool) -> List[str]:
    """提取参与者列表"""
    participants = []
    # 显式标记
    m = re.search(r'(?:参与者|参会人员|与会人员|出席)[：:]\s*(.+?)(?:\n|$)', text)
    if m:
        participants.extend(p.strip() for p in re.split(r'[、,，;；]', m.group(1)) if p.strip())
    # @提及
    for name in re.findall(r'@(\S+)', text):
        name = re.sub(r'[，。！？：；,\.!?:;]', '', name)
        if name and name not in participants:
            participants.append(name)
    # 对话格式：从说话人中提取
    if is_dialogue and not participants:
        entries = _parse_dialogue_lines(text)
        for speaker, _ in entries:
            if speaker not in participants and len(speaker) >= 2:
                participants.append(speaker)
    # "张三、李四参加"
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


def _extract_discussion_points(paragraphs: List[str], is_dialogue: bool) -> List[str]:
    """从段落中提取讨论要点"""
    points = []
    if is_dialogue:
        # 对话格式：按话题合并，而非逐句提取
        topic_transitions = ['另外', '第二点', '第三点', '接下来', '还有一点', '最后']
        current_topic = ''
        for para in paragraphs:
            for line in para.split('\n'):
                line = line.strip()
                m = re.match(r'^[\u4e00-\u9fff]{1,4}[：:]\s*(.+)', line)
                if not m:
                    continue
                content = m.group(1).strip()
                # 检查是否是话题切换
                is_transition = any(kw in content for kw in topic_transitions)
                if is_transition:
                    if current_topic and len(current_topic) > 5:
                        points.append(current_topic.strip('，。'))
                    current_topic = content
                else:
                    current_topic = content if not current_topic else current_topic + '；' + content
        if current_topic and len(current_topic) > 5:
            points.append(current_topic.strip('，。'))
    else:
        # 结构化格式：找编号列表
        for p in paragraphs:
            for line in p.split('\n'):
                line = line.strip()
                m = re.match(r'(?:\d+[.、)）]\s*|[一二三四五六七八九十]+[、.]\s*)', line)
                if m:
                    point = line[m.end():].strip()
                    if len(point) > 5:
                        points.append(point)
        if not points:
            for p in paragraphs:
                first = p.split('\n')[0].strip()
                first = re.sub(r'^[\d#*\-\[\s]+', '', first)
                if 10 < len(first) < 200:
                    points.append(first)
    return points


def _extract_complete_sentence(content: str, keyword: str) -> str:
    """从内容中提取包含关键词的完整句子"""
    # 找到关键词位置，向前找句首，向后找句尾
    idx = content.find(keyword)
    if idx < 0:
        return content[:60]
    # 句子边界
    before = max(0, content.rfind('。', 0, idx), content.rfind('；', 0, idx),
                 content.rfind('，', max(0, idx - 40), idx))
    if before == -1:
        before = 0
    else:
        before += 1
    after = content.find('。', idx)
    if after == -1:
        after = content.find('；', idx)
    if after == -1:
        after = len(content)
    else:
        after += 1
    sentence = content[before:after].strip()
    # 去掉引号
    sentence = re.sub(r'^[「"\'『，、]', '', sentence)
    return sentence if len(sentence) > 5 else content[:60]


def _extract_dialogue_summary(text: str) -> str:
    """从对话格式文本中提取总结性发言"""
    # 找"总结"、"总之"、"综上"等总结词
    for line in text.split('\n'):
        line = line.strip()
        m = re.match(r'^[\u4e00-\u9fff]{1,4}[：:]\s*(.+)', line)
        if m:
            content = m.group(1)
            if re.search(r'(?:总结|总之|综上|归纳|概括|汇总)', content):
                return content.strip('。').strip()
    # 找最后一段发言（通常是总结）
    entries = _parse_dialogue_lines(text)
    if entries:
        return entries[-1][1].strip('。').strip()
    return ''
