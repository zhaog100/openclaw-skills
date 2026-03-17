# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""纪要生成模块 - 整合解析结果和行动项，生成结构化会议纪要"""

import re
from typing import Dict, Any, List


def generate_summary(parsed: Dict[str, Any], actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """生成结构化会议纪要。

    Args:
        parsed: parse_text() 的输出
        actions: extract_actions() 的输出

    Returns:
        结构化纪要字典
    """
    return {
        'meeting_info': {
            'topic': parsed.get('topic', ''),
            'time': parsed.get('time', ''),
            'location': parsed.get('location', ''),
            'participants': parsed.get('participants', []),
        },
        'summary': _build_overview(parsed),
        'discussion_points': parsed.get('discussion_points', []),
        'decisions': _extract_decisions(parsed),
        'action_items': actions,
        'raw_paragraphs': parsed.get('paragraphs', []),
    }


def _build_overview(parsed: Dict[str, Any]) -> str:
    """生成会议概述"""
    topic = parsed.get('topic', '未定议题')
    parts = [parsed.get('participants', [])]
    points = parsed.get('discussion_points', [])
    n_points = len(points)

    overview = f"本次会议围绕「{topic}」展开讨论"
    if n_points > 0:
        overview += f"，共涉及{n_points}个讨论要点"
    if parts[0]:
        overview += f"，参会人员包括{'、'.join(parts[0])}"
    overview += "。"
    return overview


def _extract_decisions(parsed: Dict[str, Any]) -> List[str]:
    """从文本中提取决策记录"""
    decisions = []
    for p in parsed.get('paragraphs', []):
        lines = p.split('\n')
        for line in lines:
            line = line.strip()
            # 带决策标记的行
            if re.search(r'(?:决定|决策|决议|确认|同意|批准|通过|敲定)[：:：]', line):
                after = re.split(r'(?:决定|决策|决议|确认|同意|批准|通过|敲定)[：:：]', line, 1)
                if len(after) > 1 and len(after[1].strip()) > 2:
                    decisions.append(after[1].strip().rstrip('。'))
            # 决定做某事
            elif re.match(r'.*(?:决定|确认|同意)\s*(?:采用|使用|选择|执行|启动)', line):
                decisions.append(line.strip().rstrip('。'))
    return decisions
