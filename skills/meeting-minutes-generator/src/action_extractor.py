# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""行动项提取模块 - 从会议文本中识别任务、负责人、截止日期和优先级"""

import re
import datetime
from typing import List, Dict, Any, Optional


def extract_actions(text: str, reference_date: Optional[datetime.date] = None) -> List[Dict[str, Any]]:
    """从会议文本中提取行动项。

    Args:
        text: 会议文本
        reference_date: 参考日期（用于相对日期计算），默认今天

    Returns:
        行动项列表，每项包含 task, assignee, deadline, priority
    """
    if reference_date is None:
        reference_date = datetime.date.today()

    sentences = _split_sentences(text)
    actions = []
    for sent in sentences:
        if not _is_action_sentence(sent):
            continue
        action = {
            'task': _extract_task(sent),
            'assignee': _extract_assignee(sent),
            'deadline': _extract_deadline(sent, reference_date),
            'priority': _infer_priority(sent),
        }
        if action['task']:
            actions.append(action)
    return actions


def _split_sentences(text: str) -> List[str]:
    sents = re.split(r'[。！？\n]+', text)
    return [s.strip() for s in sents if len(s.strip()) > 2]


def _is_action_sentence(sent: str) -> bool:
    """判断是否包含行动意图"""
    keywords = ['负责', '跟进', '完成', '提交', '整理', '确认', '沟通', '安排',
                '协调', '准备', '反馈', '修改', '更新', '编写', '输出', '制作',
                '推进', '落实', '对接', '调研', '评估', '审核', '通知', '部署',
                '需要', '要求', '待办', 'TODO', 'todo', '修复', '搞定', '解决']
    return any(k in sent for k in keywords)


def _extract_task(sent: str) -> str:
    """提取任务描述"""
    # 去掉@提及和日期前缀
    task = re.sub(r'@\S+\s*', '', sent)
    task = re.sub(r'(\d{1,2}月\d{1,2}日?|下周[一二三四五六日天]|明天|后天|今天|本周五?|下周一?\s*前)\s*', '', task)
    task = re.sub(r'(负责|跟进|完成|提交|整理|确认|沟通|安排|协调|准备|反馈|修改|更新|编写|输出|制作|推进|落实|对接|调研|评估|审核|通知|部署)\s*', '', task, count=1)
    task = task.strip('，。、；：,;:')
    return task if len(task) >= 2 else sent.strip('，。、；：,;:')


def _extract_assignee(sent: str) -> str:
    """提取负责人"""
    # xxx负责
    m = re.search(r'([\u4e00-\u9fff]{2,4})负责', sent)
    if m:
        return m.group(1)

    # 由xxx (name is 2-4 chars, followed by verb)
    m = re.search(r'由([\u4e00-\u9fff]{2,4}?)(?:负责|协调|跟进|完成|提交|整理|审核|推进|落实|对接|调研|通知|安排|处理)', sent)
    if m:
        return m.group(1)

    # 交给xxx
    m = re.search(r'(?:交给|指派给|分配给)([\u4e00-\u9fff]{2,4}?)(?:审核|负责|跟进|完成|处理|编写)', sent)
    if m:
        return m.group(1)

    # @xxx followed by space/punctuation/end (most common in chat)
    m = re.search(r'@([\u4e00-\u9fffA-Za-z0-9_]{2,10})(?:[\s，。！？：；,\.!?:;]|$)', sent)
    if m:
        return m.group(1)
    # @xxx+verb (e.g., @张三负责)
    m = re.search(r'@([\u4e00-\u9fff]{2,4})(负责|跟进|完成|提交|整理|协调|审核)', sent)
    if m:
        return m.group(1)

    return ''


def _extract_deadline(sent: str, ref: datetime.date) -> str:
    """提取截止日期，返回可读字符串"""
    today_weekday = ref.weekday()  # 0=Mon

    # 绝对日期: 3月20日 / 2026-03-20 / 2026/03/20
    m = re.search(r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})日?', sent)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.search(r'(\d{1,2})月(\d{1,2})日?', sent)
    if m:
        return f"{ref.year}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"

    # 相对日期
    weekday_map = {'一': 0, '二': 1, '三': 2, '四': 3, '五': 4, '六': 5, '日': 6, '天': 6}

    m = re.search(r'今天', sent)
    if m:
        return ref.isoformat()

    m = re.search(r'明天', sent)
    if m:
        d = ref + datetime.timedelta(days=1)
        return d.isoformat()

    m = re.search(r'后天', sent)
    if m:
        d = ref + datetime.timedelta(days=2)
        return d.isoformat()

    # 下周X
    m = re.search(r'下周([一二三四五六日天])', sent)
    if m:
        target = weekday_map.get(m.group(1), 0)
        days_to_next_monday = (0 - today_weekday) % 7 or 7
        days_ahead = days_to_next_monday + target
        d = ref + datetime.timedelta(days=days_ahead)
        return d.isoformat()

    # 本周X
    m = re.search(r'本周([一二三四五六日天])', sent)
    if m:
        target = weekday_map.get(m.group(1), 0)
        days_ahead = (target - today_weekday) % 7
        if days_ahead == 0:
            days_ahead = 0
        d = ref + datetime.timedelta(days=days_ahead)
        return d.isoformat()

    # N天后
    m = re.search(r'(\d+)\s*天后', sent)
    if m:
        d = ref + datetime.timedelta(days=int(m.group(1)))
        return d.isoformat()

    return ''


def _infer_priority(sent: str) -> str:
    """推断优先级"""
    high_keywords = ['紧急', '立即', '尽快', '重要', '优先', '必须', '务必', '马上', '今日内']
    low_keywords = ['有空', '不急', '慢慢', '后续', '视情况', '可选']

    for k in high_keywords:
        if k in sent:
            return '高'
    for k in low_keywords:
        if k in sent:
            return '低'
    return '中'
