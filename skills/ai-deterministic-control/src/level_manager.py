# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

"""LevelManager — 确定性等级管理 (L0-L4)"""

from typing import Dict, List, Optional

_LEVELS = {
    "L0": {
        "level": "L0",
        "name": "完全随机",
        "temperature": 1.0,
        "top_p": 1.0,
        "seed": None,
        "strategy": "none",
        "description": "无任何确定性控制，完全自由输出",
        "use_cases": ["头脑风暴", "创意写作", "故事生成"],
    },
    "L1": {
        "level": "L1",
        "name": "轻度约束",
        "temperature": 0.7,
        "top_p": 0.95,
        "seed": None,
        "strategy": "prompt",
        "description": "仅降低温度，适合需要一定创意但要求一致的场景",
        "use_cases": ["常规对话", "问答", "内容改写"],
    },
    "L2": {
        "level": "L2",
        "name": "中度约束",
        "temperature": 0.3,
        "top_p": 0.9,
        "seed": 42,
        "strategy": "seed",
        "description": "固定种子+低温度，适合代码生成等任务",
        "use_cases": ["代码生成", "数据分析", "翻译"],
    },
    "L3": {
        "level": "L3",
        "name": "高度约束",
        "temperature": 0.1,
        "top_p": 0.8,
        "seed": 42,
        "strategy": "seed+prompt",
        "description": "种子+模板+低温度，适合配置生成等精确任务",
        "use_cases": ["配置生成", "API响应", "数据提取", "测试用例"],
    },
    "L4": {
        "level": "L4",
        "name": "极度约束",
        "temperature": 0.0,
        "top_p": 0.5,
        "seed": 42,
        "strategy": "seed+prompt+vote",
        "description": "最高确定性：种子+模板+多数投票，适合安全关键任务",
        "use_cases": ["数学计算", "格式转换", "安全相关输出"],
    },
}

# 自动检测关键词映射
_TASK_KEYWORDS = {
    "L0": ["brainstorm", "creative", "story", "poem", "imagin", "fiction", "art"],
    "L1": ["chat", "discuss", "explain", "summarize", "rewrite", "paraphrase", "opinion"],
    "L2": ["code", "function", "program", "algorithm", "translate", "translation", "analyze"],
    "L3": ["config", "json", "yaml", "api", "schema", "test case", "extract", "format"],
    "L4": ["math", "calculate", "formula", "exact", "precise", "safety", "security", "regex"],
}


def get_level_config(level: str) -> Dict:
    """获取等级的完整参数配置

    Args:
        level: L0-L4

    Returns:
        {level, name, temperature, top_p, seed, strategy, description, use_cases}
    """
    level = level.upper()
    if level not in _LEVELS:
        raise ValueError(f"未知等级: {level}，有效值: {list(_LEVELS.keys())}")
    return dict(_LEVELS[level])


def list_levels() -> List[Dict]:
    """列出所有确定性等级

    Returns:
        等级配置列表
    """
    return [dict(cfg) for cfg in _LEVELS.values()]


def auto_detect_level(task_description: str) -> str:
    """根据任务描述自动推荐确定性等级

    Args:
        task_description: 任务描述文本

    Returns:
        推荐等级（L0-L4）
    """
    if not task_description:
        return "L1"  # 默认

    desc_lower = task_description.lower()
    scores = {}

    for level, keywords in _TASK_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in desc_lower)
        scores[level] = score

    if max(scores.values()) == 0:
        return "L1"  # 无匹配关键词，默认L1

    return max(scores, key=scores.get)
