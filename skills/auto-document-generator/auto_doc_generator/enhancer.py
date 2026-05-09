#!/usr/bin/env python3
"""
AI 增强器 - 使用 AI 娡型增强文档内容

支持模型：
- Ollama（本地模型，Llama 3 / CodeLlama）
- Claude / GPT-4（云端模型，可选）

优先级：本地 > 云端
"""

import logging
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

# 日志配置
logger = logging.getLogger(__name__)


@dataclass
class AIConfig:
    """AI 配置"""
    provider: str = "ollama"
    model: str = "llama3"
    local: bool = True
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    timeout: int = 30


class AIEnhancer:
    """AI 增强器"""
    
    def __init__(self, config: Optional[AIConfig] = None):
        self.config = config or AIConfig()
        self.logger = logging.getLogger(__name__)
        
        # 初始化客户端
        self.client = self._init_client()
    
    def _init_client(self):
        """初始化 AI 客户端"""
        if self.config.local:
            try:
                import ollama
                return ollama
            except ImportError:
                self.logger.warning("Ollama not available, AI enhancement disabled")
                return None
        else:
            # 云端模型（OpenAI/Claude）
            try:
                import openai
                return openai
            except ImportError:
                self.logger.warning("OpenAI not available, AI enhancement disabled")
                return None
    
    def enhance_description(self, code: str, existing_doc: Optional[str] = None) -> str:
        """增强函数/类描述"""
        if not self.client:
            return existing_doc or ""
        
        prompt = f"""You are a technical documentation expert. Enhance the following code description:

Code:
```
{code}
```

Existing Description:
{existing_doc or "None"}

Generate a clear, concise description that:
1. Explains what the code does
2. Mentions important parameters or inputs
3. Describes the output or return value
4. Includes any important notes or warnings

Output only the enhanced description, no explanations."""

        try:
            if self.config.local and hasattr(self.client, 'chat'):
                response = self.client.chat(
                    model=self.config.model,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                return response['message']['content']
            else:
                # OpenAI 格式
                response = self.client.ChatCompletion.create(
                    model=self.config.model,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"AI enhancement failed: {e}")
            return existing_doc or ""
    
    def generate_examples(self, function_name: str, parameters: List, description: str) -> List[str]:
        """生成代码示例"""
        if not self.client:
            return []
        
        param_str = ", ".join([p.get('name', 'param') for p in parameters])
        
        prompt = f"""Generate 1-2 code examples for the following function:

Function: {function_name}
Parameters: {param_str}
Description: {description}

Examples should be:
1. Simple and easy to understand
2. Show typical usage
3. Include expected output

Output only the code examples, formatted as Markdown code blocks."""

        try:
            if self.config.local and hasattr(self.client, 'chat'):
                response = self.client.chat(
                    model=self.config.model,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                content = response['message']['content']
            else:
                response = self.client.ChatCompletion.create(
                    model=self.config.model,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                content = response.choices[0].message.content
            
            # 提取代码块
            examples = []
            import re
            code_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', content, re.DOTALL)
            for lang, code in code_blocks:
                examples.append(code.strip())
            
            return examples if examples else [content]
        except Exception as e:
            self.logger.error(f"Example generation failed: {e}")
            return []
    
    def improve_readability(self, doc: str) -> str:
        """改进文档可读性"""
        if not self.client:
            return doc
        
        prompt = f"""Improve the readability of the following documentation:

{doc}

Make it:
1. More concise
2. Better structured
3. Easier to understand

Output only the improved documentation."""

        try:
            if self.config.local and hasattr(self.client, 'chat'):
                response = self.client.chat(
                    model=self.config.model,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                return response['message']['content']
            else:
                response = self.client.ChatCompletion.create(
                    model=self.config.model,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Readability improvement failed: {e}")
            return doc
    
    def fill_missing_params(self, params: List[Dict], code: str) -> List[Dict]:
        """补充缺失的参数说明"""
        if not self.client:
            return params
        
        # 找出缺失描述的参数
        missing = [p for p in params if not p.get('description')]
        
        if not missing:
            return params
        
        prompt = f"""Generate descriptions for the following function parameters:

Code:
```
{code}
```

Parameters without descriptions:
{', '.join([p['name'] for p in missing])}

Output a JSON object with parameter names as keys and descriptions as values.
Example: {{"param1": "description1", "param2": "description2"}}"""

        try:
            if self.config.local and hasattr(self.client, 'chat'):
                response = self.client.chat(
                    model=self.config.model,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                content = response['message']['content']
            else:
                response = self.client.ChatCompletion.create(
                    model=self.config.model,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                content = response.choices[0].message.content
            
            # 解析 JSON
            import json
            import re
            
            # 提取 JSON
            json_match = re.search(r'\{[^}]+\}', content)
            if json_match:
                descriptions = json.loads(json_match.group())
                
                # 更新参数
                for param in params:
                    if param['name'] in descriptions:
                        param['description'] = descriptions[param['name']]
                
                return params
        except Exception as e:
            self.logger.error(f"Parameter filling failed: {e}")
            return params
        
        return params
