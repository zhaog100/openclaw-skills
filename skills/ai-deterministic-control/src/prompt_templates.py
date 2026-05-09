# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

"""PromptTemplates — 确定性 System Prompt 模板管理"""

from typing import Dict, Optional

# Base 确定性锚定模板
BASE_TEMPLATE = """你是一个高确定性输出引擎。请遵循以下规则：
1. 只输出请求的内容，不要添加额外解释或废话
2. 使用一致的格式和风格
3. 如果有多种可能的输出，选择最常见/标准的方式
4. 不要使用"我认为"、"可能"、"也许"等不确定词汇
5. 保持输出简洁、结构化"""

# 任务特定模板
_TASK_TEMPLATES: Dict[str, str] = {
    "code_generation": """{base}

针对代码生成任务：
- 优先使用标准库和常见模式
- 变量命名使用 snake_case
- 添加必要的类型注解
- 确保代码可运行，无语法错误
- 使用一致的缩进（4空格）""",

    "config_generation": """{base}

针对配置生成任务：
- 使用标准格式（JSON/YAML/TOML）
- 所有键名使用一致的风格
- 添加必要的注释
- 不省略任何必需字段""",

    "conversation": """{base}

针对对话任务：
- 回答简洁明了，直接回答问题
- 如果不确定，明确说明
- 不重复用户已经知道的信息""",

    "creative_writing": """{base}

针对创意写作任务：
- 允许适度发散，但保持主题一致
- 使用丰富的词汇和句式
- 控制篇幅在合理范围内""",

    "data_analysis": """{base}

针对数据分析任务：
- 使用精确的数字和单位
- 引用数据来源
- 结论要有数据支撑
- 不做没有数据支持的推测""",

    "translation": """{base}

针对翻译任务：
- 忠实原文，不做增删
- 使用目标语言的标准表达
- 专业术语保持一致
- 保持原文的语气和风格""",
}

# 自定义模板注册表
_custom_templates: Dict[str, str] = {}


def get_template(task_type: str, base_only: bool = False) -> str:
    """获取确定性 prompt 模板

    Args:
        task_type: 任务类型（code_generation/config_generation/conversation 等）
        base_only: 是否只返回基础模板

    Returns:
        完整的 system prompt
    """
    if base_only:
        return BASE_TEMPLATE

    template = _custom_templates.get(task_type) or _TASK_TEMPLATES.get(task_type)
    if template:
        return template.format(base=BASE_TEMPLATE)
    return BASE_TEMPLATE


def list_task_types() -> Dict[str, str]:
    """列出所有可用任务类型

    Returns:
        {task_type: description} 字典
    """
    descriptions = {
        "code_generation": "代码生成",
        "config_generation": "配置生成",
        "conversation": "常规对话",
        "creative_writing": "创意写作",
        "data_analysis": "数据分析",
        "translation": "翻译任务",
    }
    # 合并自定义模板
    result = dict(descriptions)
    for k in _custom_templates:
        if k not in result:
            result[k] = f"自定义: {k}"
    return result


def register_template(task_type: str, template: str) -> bool:
    """注册自定义任务模板

    Args:
        task_type: 任务类型名称
        template: 模板内容（可使用 {base} 占位符）

    Returns:
        是否注册成功
    """
    if not task_type or not template:
        return False
    _custom_templates[task_type] = template
    return True
