# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""核心调度模块 - 一键生成会议纪要"""

try:
    from .minutes_parser import parse_text
    from .action_extractor import extract_actions
    from .summary_generator import generate_summary
    from .formatter import format_markdown, format_plain, format_json
except ImportError:
    from minutes_parser import parse_text
    from action_extractor import extract_actions
    from summary_generator import generate_summary
    from formatter import format_markdown, format_plain, format_json


def generate_minutes(raw_text: str = None, fmt: str = "markdown",
                      audio_path: str = None, stt_engine=None) -> str:
    """一键生成会议纪要。

    支持两种入口:
    1. 文本输入: generate_minutes(raw_text="会议文本...")
    2. 音频输入: generate_minutes(audio_path="meeting.mp3", stt_engine=engine)

    Args:
        raw_text: 原始会议文本（与audio_path二选一）
        fmt: 输出格式，支持 markdown / plain / json
        audio_path: 音频文件路径（可选，需配合stt_engine）
        stt_engine: STT引擎实例（可选，实现BaseSTTEngine接口）

    Returns:
        格式化后的会议纪要字符串
    """
    # 音频转文字
    if audio_path:
        if stt_engine is None:
            try:
                from stt_interface import get_available_engine
            except ImportError:
                from src.stt_interface import get_available_engine
            stt_engine = get_available_engine()
        if stt_engine is None:
            raise RuntimeError(
                "STT未配置。请安装Whisper(pip install openai-whisper) "
                "或设置OPENAI_API_KEY/SENSEVOICE_API_KEY环境变量。"
            )
        raw_text = stt_engine.transcribe(audio_path)

    if not raw_text:
        return ""
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
