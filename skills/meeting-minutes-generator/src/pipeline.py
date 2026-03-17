# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""核心调度模块 - 一键生成会议纪要"""

from .minutes_parser import parse_text
from .action_extractor import extract_actions
from .summary_generator import generate_summary
from .formatter import format_markdown, format_plain, format_json


def generate_minutes(raw_text: str, fmt: str = "markdown") -> str:
    """一键生成会议纪要。

    Args:
        raw_text: 原始会议文本
        fmt: 输出格式，支持 markdown / plain / json

    Returns:
        格式化后的会议纪要字符串
    """
    parsed = parse_text(raw_text)
    actions = extract_actions(raw_text)
    minutes = generate_summary(parsed, actions)

    formatters = {
        'markdown': format_markdown,
        'plain': format_plain,
        'json': format_json,
    }
    formatter = formatters.get(fmt.lower(), format_markdown)
    return formatter(minutes)
