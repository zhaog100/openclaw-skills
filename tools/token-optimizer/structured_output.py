#!/usr/bin/env python3
"""
结构化输出模板 - 减少JSON错误

基于Hazel_OC方法：错误率从14个/7天 → 2个/7天（↓85%）
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path

class StructuredOutputTemplate:
    """结构化输出模板"""

    def __init__(self, templates_dir: str = None):
        """
        初始化

        Args:
            templates_dir: 模板目录（可选）
        """
        self.templates_dir = Path(templates_dir) if templates_dir else None
        self.success_patterns = {}  # 成功的JSON模式

    def register_success_pattern(self, tool_name: str, pattern: Dict):
        """
        注册成功的JSON模式

        Args:
            tool_name: 工具名称
            pattern: 成功的JSON模式
        """
        self.success_patterns[tool_name] = pattern

    def generate_output(self, tool_name: str, **kwargs) -> Dict:
        """
        生成结构化输出

        Args:
            tool_name: 工具名称
            **kwargs: 参数

        Returns:
            结构化输出
        """
        if tool_name not in self.success_patterns:
            return {"error": f"未找到工具 {tool_name} 的模板"}

        template = self.success_patterns[tool_name].copy()

        # 填充参数
        for key, value in kwargs.items():
            if key in template:
                template[key] = value

        return template

    def validate_output(self, tool_name: str, output: Dict) -> bool:
        """
        验证输出是否符合模板

        Args:
            tool_name: 工具名称
            output: 输出数据

        Returns:
            是否有效
        """
        if tool_name not in self.success_patterns:
            return False

        template = self.success_patterns[tool_name]

        # 检查必需字段
        for key in template.keys():
            if key not in output:
                return False

        return True

    def get_common_tools(self) -> Dict[str, Dict]:
        """
        获取常用工具的模板

        Returns:
            工具模板字典
        """
        return {
            "web_search": {
                "query": "",
                "limit": 10,
                "results": []
            },
            "file_read": {
                "path": "",
                "offset": 0,
                "limit": 1000
            },
            "git_commit": {
                "message": "",
                "files": []
            },
            "api_call": {
                "endpoint": "",
                "method": "GET",
                "params": {},
                "response": None
            }
        }


if __name__ == "__main__":
    # 示例使用
    template_engine = StructuredOutputTemplate()

    # 注册常用工具模板
    common_tools = template_engine.get_common_tools()
    for tool_name, pattern in common_tools.items():
        template_engine.register_success_pattern(tool_name, pattern)

    # 生成结构化输出
    output = template_engine.generate_output(
        "web_search",
        query="Token优化",
        limit=5
    )

    print("✅ 生成的结构化输出：")
    print(json.dumps(output, ensure_ascii=False, indent=2))

    # 验证输出
    is_valid = template_engine.validate_output("web_search", output)
    print(f"\n✅ 输出验证: {'通过' if is_valid else '失败'}")
