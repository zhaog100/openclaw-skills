# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""格式化输出模块 - Markdown / 纯文本 / JSON"""

import json
from typing import Dict, Any


def format_markdown(minutes: Dict[str, Any]) -> str:
    """格式化为Markdown"""
    info = minutes.get('meeting_info', {})
    lines = []

    lines.append(f"# 会议纪要：{info.get('topic', '未定议题')}")
    lines.append("")

    # 基本信息
    lines.append("## 基本信息")
    if info.get('time'):
        lines.append(f"- **时间**：{info['time']}")
    if info.get('location'):
        lines.append(f"- **地点**：{info['location']}")
    if info.get('participants'):
        lines.append(f"- **参会人员**：{'、'.join(info['participants'])}")
    lines.append("")

    # 概述
    if minutes.get('summary'):
        lines.append("## 会议概述")
        lines.append(minutes['summary'])
        lines.append("")

    # 讨论要点
    points = minutes.get('discussion_points', [])
    if points:
        lines.append("## 讨论要点")
        for i, p in enumerate(points, 1):
            lines.append(f"{i}. {p}")
        lines.append("")

    # 决策记录
    decisions = minutes.get('decisions', [])
    if decisions:
        lines.append("## 决策记录")
        for i, d in enumerate(decisions, 1):
            lines.append(f"{i}. {d}")
        lines.append("")

    # 总结性发言
    dialogue_summary = minutes.get('dialogue_summary', '')
    if dialogue_summary:
        lines.append("## 会议总结")
        lines.append(dialogue_summary)
        lines.append("")

    # 行动项
    actions = minutes.get('action_items', [])
    if actions:
        lines.append("## 行动项")
        for i, a in enumerate(actions, 1):
            assignee = a.get('assignee', '待定')
            deadline = a.get('deadline', '待定')
            priority = a.get('priority', '中')
            lines.append(f"{i}. {a['task']}（负责人：{assignee}，截止：{deadline}，优先级：{priority}）")
        lines.append("")

    return '\n'.join(lines)


def format_plain(minutes: Dict[str, Any]) -> str:
    """格式化为纯文本"""
    info = minutes.get('meeting_info', {})
    lines = []

    lines.append(f"会议纪要：{info.get('topic', '未定议题')}")
    lines.append("=" * 40)

    if info.get('time'):
        lines.append(f"时间：{info['time']}")
    if info.get('location'):
        lines.append(f"地点：{info['location']}")
    if info.get('participants'):
        lines.append(f"参会人员：{'、'.join(info['participants'])}")
    lines.append("")

    if minutes.get('summary'):
        lines.append(f"概述：{minutes['summary']}")
        lines.append("")

    points = minutes.get('discussion_points', [])
    if points:
        lines.append("讨论要点：")
        for i, p in enumerate(points, 1):
            lines.append(f"  {i}. {p}")
        lines.append("")

    decisions = minutes.get('decisions', [])
    if decisions:
        lines.append("决策记录：")
        for i, d in enumerate(decisions, 1):
            lines.append(f"  {i}. {d}")
        lines.append("")

    actions = minutes.get('action_items', [])
    if actions:
        lines.append("行动项：")
        for i, a in enumerate(actions, 1):
            assignee = a.get('assignee', '待定')
            deadline = a.get('deadline', '待定')
            priority = a.get('priority', '中')
            lines.append(f"  {i}. {a['task']} (负责人:{assignee}, 截止:{deadline}, 优先级:{priority})")
        lines.append("")

    return '\n'.join(lines)


def format_json(minutes: Dict[str, Any]) -> str:
    """格式化为JSON字符串"""
    return json.dumps(minutes, ensure_ascii=False, indent=2)
