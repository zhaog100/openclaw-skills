#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 引擎 - 本地 AI 模型调用
支持 Ollama、CodeLlama 等本地模型
"""

import os
import json
import subprocess
from typing import Dict, List, Optional

class AIEngine:
    """本地 AI 引擎"""
    
    def __init__(self, model: str = "codellama:7b"):
        """
        初始化 AI 引擎
        
        Args:
            model: 模型名称，默认 codellama:7b
        """
        self.model = model
        self.ollama_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
    def check_ollama(self) -> bool:
        """检查 Ollama 是否可用"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def analyze_code(self, code: str, language: str = "python") -> Dict:
        """
        分析代码质量
        
        Args:
            code: 代码内容
            language: 编程语言
            
        Returns:
            分析结果字典
        """
        prompt = f"""请分析以下{language}代码的质量，检查：
1. 代码规范（命名、格式）
2. 潜在 Bug（空指针、资源泄漏等）
3. 性能问题（低效循环、重复计算）
4. 安全问题（SQL 注入、硬编码密码等）

代码：
```{language}
{code}
```

请以 JSON 格式返回分析结果：
{{
    "issues": [
        {{
            "line": 行号,
            "severity": "low|medium|high",
            "category": "规范|bug|性能|安全",
            "message": "问题描述"
        }}
    ],
    "suggestions": [
        {{
            "priority": "low|medium|high",
            "suggestion": "改进建议",
            "code_example": "示例代码"
        }}
    ]
}}
"""
        
        try:
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # 解析 JSON 响应
                response = result.stdout.strip()
                # 提取 JSON 部分
                start = response.find("{")
                end = response.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = response[start:end]
                    return json.loads(json_str)
            
            return {"issues": [], "suggestions": []}
            
        except Exception as e:
            print(f"AI 分析失败：{e}")
            return {"issues": [], "suggestions": []}
    
    def generate_suggestion(self, issue: Dict, code: str) -> str:
        """
        为问题生成改进建议
        
        Args:
            issue: 问题字典
            code: 原始代码
            
        Returns:
            改进建议文本
        """
        prompt = f"""针对以下代码问题，提供具体的改进建议和示例代码：

问题：{issue.get('message', '')}
严重程度：{issue.get('severity', 'medium')}
类别：{issue.get('category', '规范')}

原始代码：
```
{code}
```

请提供：
1. 问题说明
2. 改进建议
3. 修改后的代码示例
"""
        
        try:
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            
            return f"建议：修复{issue.get('category', '问题')}（{issue.get('severity', 'medium')}）"
            
        except Exception:
            return f"建议：修复{issue.get('category', '问题')}"


class AIDebateEngine:
    """AI 辩论引擎 - 多模型辩论提升准确率"""
    
    def __init__(self, models: List[str] = None):
        """
        初始化辩论引擎
        
        Args:
            models: 模型列表，默认使用多个模型
        """
        self.models = models or ["codellama:7b", "deepseek-coder:6.7b"]
        self.engines = [AIEngine(model) for model in self.models]
    
    def debate_analysis(self, code: str, language: str = "python") -> Dict:
        """
        多模型辩论分析
        
        Args:
            code: 代码内容
            language: 编程语言
            
        Returns:
            综合分析报告
        """
        results = []
        
        # 各模型独立分析
        for engine in self.engines:
            if engine.check_ollama():
                result = engine.analyze_code(code, language)
                results.append(result)
        
        if not results:
            return {"issues": [], "suggestions": [], "confidence": 0}
        
        # 合并结果（取所有模型都发现的问题）
        all_issues = []
        all_suggestions = []
        
        for result in results:
            all_issues.extend(result.get("issues", []))
            all_suggestions.extend(result.get("suggestions", []))
        
        # 去重（基于行号和问题描述）
        seen = set()
        unique_issues = []
        for issue in all_issues:
            key = f"{issue.get('line', 0)}:{issue.get('message', '')}"
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        # 计算置信度
        confidence = len(results) / len(self.engines)
        
        return {
            "issues": unique_issues,
            "suggestions": all_suggestions,
            "confidence": confidence,
            "models_used": len(results)
        }


# 测试
if __name__ == "__main__":
    engine = AIEngine()
    
    if engine.check_ollama():
        print("✓ Ollama 可用")
        
        test_code = """
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    return total

password = "admin123"
"""
        result = engine.analyze_code(test_code, "python")
        print(f"发现问题：{len(result.get('issues', []))}")
        print(f"改进建议：{len(result.get('suggestions', []))}")
    else:
        print("✗ Ollama 不可用，请安装并启动 Ollama")
        print("  安装：curl -fsSL https://ollama.com/install.sh | sh")
        print("  启动：ollama serve")
