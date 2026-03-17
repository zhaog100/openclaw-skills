# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""行动项提取模块 - 从会议文本中识别任务、负责人、截止日期和优先级"""

import re
import datetime
from typing import List, Dict, Any, Optional


def extract_actions(text: str, reference_date: Optional[datetime.date] = None) -> List[Dict[str, Any]]:
    """从会议文本中提取行动项。"""
    if reference_date is None:
        reference_date = datetime.date.today()

    sentences = _split_sentences(text)
    actions = []
    for sent in sentences:
        if not _is_action_sentence(sent):
            continue
        task = _extract_task(sent)
        assignee = _extract_assignee(sent)
        if not assignee:
            assignee = _extract_speaker(sent)
        deadline = _extract_deadline(sent, reference_date)
        priority = _infer_priority(sent)
        if task:
            actions.append({
                'task': task,
                'assignee': assignee,
                'deadline': deadline,
                'priority': priority,
            })
    return actions


def _split_sentences(text: str) -> List[str]:
    """按换行、句号等分割为句子"""
    blocks = re.split(r'[\n。！？]+', text)
    sents = []
    for block in blocks:
        block = block.strip()
        if not block or len(block) <= 2:
            continue
        if block.count('@') > 1:
            parts = re.split(r'(?=@)', block)
            sents.extend(p.strip() for p in parts if len(p.strip()) > 2)
        else:
            sents.append(block)
    return sents


def _is_action_sentence(sent: str) -> bool:
    """判断是否包含行动意图"""
    # 必须包含行动动词
    action_verbs = ['负责', '跟进', '完成', '提交', '整理', '确认', '沟通', '安排',
                    '协调', '准备', '反馈', '修改', '更新', '编写', '输出', '制作',
                    '推进', '落实', '对接', '调研', '评估', '审核', '通知', '部署',
                    '修复', '解决', '升级', '排好', '执行', '搞定', '做好']
    
    has_action = any(k in sent for k in action_verbs)
    if not has_action:
        return False
    
    # 排除纯信息性陈述（没有行动意图的描述）
    exclude_patterns = [
        r'大概需要\d+',           # "大概需要2周/3天" - 工时估算
        r'工作量大概',             # "工作量大概3天"
        r'不影响',                # "不影响现有功能"
        r'还没',                  # "还没修复" - 问题描述
        r'建议分',                # "建议分两期" - 建议
        r'(目前|现在)用的',       # "目前用的Java 8" - 现状描述
        r'总结一下',              # "总结一下" - 会议总结
        r'^的(会议|次|个|方面)',   # 残留截断文本
        r'主要讨论',              # "主要讨论" - 话题引入
    ]
    
    for p in exclude_patterns:
        if re.search(p, sent):
            return False
    
    # 排除纯评估/判断句（没有明确要做的事）
    if re.search(r'(评估|分析|了解|知道|发现|看到|听到|认为|觉得)\s*(大概|可能|应该|似乎)', sent):
        return False
    
    return True


def _extract_task(sent: str) -> str:
    """提取任务描述"""
    # 去掉说话人前缀
    task = re.sub(r'^[\u4e00-\u9fff]{1,4}[：:]\s*', '', sent)
    # 去掉@提及
    task = re.sub(r'@\S+\s*', '', task)
    # 去掉日期前缀
    task = re.sub(r'(\d{1,2}月\d{1,2}日?|下周[一二三四五六日天]|明天|后天|今天|本周五?|下周一?\s*前)\s*', '', task)
    # 去掉动词前缀（一次）
    task = re.sub(r'^(负责|跟进|完成|提交|整理|确认|沟通|安排|协调|准备|反馈|修改|更新|编写|输出|制作|推进|落实|对接|调研|评估|审核|通知|部署)\s*', '', task, count=1)
    # 去掉口语前缀
    task = re.sub(r'^(好的?|好呀|那|嗯|哦|行|对|是|可以)\s*[，,、;；]?\s*', '', task)
    task = task.strip('，。、；：,;:!?！？「」""\'\'')
    # 如果提取后太短，用原文（去掉说话人+口语+时间短语）
    if len(task) < 4:
        task = re.sub(r'^[\u4e00-\u9fff]{1,4}[：:]\s*', '', sent)
        task = re.sub(r'^[「"\'『]', '', task)
        task = re.sub(r'[」"\'』。！？]$', '', task)
        task = re.sub(r'^(好的?|那|嗯|行)\s*[，,]?\s*', '', task)
        task = re.sub(r'(下周一|本周内|本周|今天|明天|后天|这周)\s*前\s*', '', task)
        task = task.strip('，。、；：,;:!?！？')
    return task if len(task) >= 2 else sent.strip('，。、；：,;:')


def _extract_speaker(sent: str) -> str:
    """从对话格式提取说话人"""
    m = re.match(r'^([\u4e00-\u9fff]{1,4})[：:]', sent)
    if m:
        return m.group(1)
    return ''


def _extract_assignee(sent: str) -> str:
    """提取负责人"""
    # 由xxx负责
    m = re.search(r'由([\u4e00-\u9fff]{2,4}?)(?:负责|协调|跟进|完成|提交|整理|审核|推进|落实|对接|调研|通知|安排|处理)', sent)
    if m:
        return m.group(1)

    # xxx负责
    m = re.search(r'([\u4e00-\u9fff]{2,4})负责', sent)
    if m:
        name = m.group(1)
        # 避免匹配到"开发负责"、"测试负责"等
        if name not in ['开发', '测试', '运维', '产品', '前端', '后端', '项目']:
            return name

    # 交给xxx
    m = re.search(r'(?:交给|指派给|分配给)([\u4e00-\u9fff]{2,4}?)(?:审核|负责|跟进|完成|处理|编写)', sent)
    if m:
        return m.group(1)

    # @xxx（独立@格式，后跟空格+内容）
    m = re.search(r'@([\u4e00-\u9fff]{2,4})\s', sent)
    if m:
        return m.group(1)

    # @xxx+verb
    m = re.search(r'@([\u4e00-\u9fff]{2,4})(负责|跟进|完成|提交|整理|协调|审核)', sent)
    if m:
        return m.group(1)

    return ''


def _extract_deadline(sent: str, ref: datetime.date) -> str:
    """提取截止日期"""
    today_weekday = ref.weekday()

    # 绝对日期
    m = re.search(r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})日?', sent)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.search(r'(\d{1,2})月(\d{1,2})日?', sent)
    if m:
        return f"{ref.year}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"

    weekday_map = {'一': 0, '二': 1, '三': 2, '四': 3, '五': 4, '六': 5, '日': 6, '天': 6}

    # 这周内/本周内
    m = re.search(r'(?:这周|本周)内', sent)
    if m:
        return f"{ref.isoformat()}（本周内）"

    # 下周X前
    m = re.search(r'下周([一二三四五六日天])\s*前', sent)
    if m:
        target = weekday_map.get(m.group(1), 0)
        days_to_next_monday = (0 - today_weekday) % 7 or 7
        days_ahead = days_to_next_monday + target
        d = ref + datetime.timedelta(days=days_ahead)
        return d.isoformat()

    # 下周X
    m = re.search(r'下周([一二三四五六日天])', sent)
    if m:
        target = weekday_map.get(m.group(1), 0)
        days_to_next_monday = (0 - today_weekday) % 7 or 7
        days_ahead = days_to_next_monday + target
        d = ref + datetime.timedelta(days=days_ahead)
        return d.isoformat()

    # 今天
    if '今天' in sent:
        return ref.isoformat()

    # 明天
    if '明天' in sent:
        return (ref + datetime.timedelta(days=1)).isoformat()

    # 后天
    if '后天' in sent:
        return (ref + datetime.timedelta(days=2)).isoformat()

    # 本月25号
    m = re.search(r'本月(\d{1,2})号', sent)
    if m:
        day = int(m.group(1))
        try:
            d = ref.replace(day=day)
            return d.isoformat()
        except ValueError:
            return ''

    # N天后
    m = re.search(r'(\d+)\s*天后', sent)
    if m:
        d = ref + datetime.timedelta(days=int(m.group(1)))
        return d.isoformat()

    return ''


def _infer_priority(sent: str) -> str:
    """推断优先级"""
    high_keywords = ['紧急', '立即', '尽快', '重要', '高优先级', '必须', '务必', '马上', '今日内', 'P0']
    low_keywords = ['有空', '不急', '慢慢', '后续', '视情况', '可选', '低优先级']

    for k in high_keywords:
        if k in sent:
            return '高'
    for k in low_keywords:
        if k in sent:
            return '低'
    return '中'
