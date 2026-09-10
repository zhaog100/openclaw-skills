#!/usr/bin/env python3
"""
小米椒内容助手 - Ollama API 集成项目
基于 qwen2.5:0.5b 的本地文案生成与优化工具
作者：小米椒 🌶️🔥
"""

import sys
import json
import time
import argparse
from typing import Optional
from dataclasses import dataclass, asdict

# 配置
OLLAMA_API = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:0.5b"


@dataclass
class GenerationResult:
    model: str
    prompt: str
    response: str
    latency_ms: int
    success: bool
    error: Optional[str] = None


class ContentAssistant:
    """内容助手核心类"""
    
    def __init__(self, model: str = DEFAULT_MODEL, api_url: str = OLLAMA_API):
        self.model = model
        self.api_url = api_url
        self.session = None
    
    def _call_ollama(self, prompt: str, stream: bool = False) -> tuple[str, float, Optional[str]]:
        """调用 Ollama API"""
        import requests
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": 0.7,
                "num_predict": 512
            }
        }
        
        start = time.time()
        try:
            resp = requests.post(
                f"{self.api_url}/api/generate",
                json=payload,
                timeout=60
            )
            elapsed = (time.time() - start) * 1000
            
            if resp.status_code == 200:
                data = resp.json()
                return data.get("response", ""), elapsed, None
            else:
                return "", elapsed, f"HTTP {resp.status_code}"
        except Exception as e:
            return "", elapsed, str(e)
    
    def generate_copy(self, topic: str, style: str = "小红书", 
                      length: str = "short", tone: str = "活泼") -> GenerationResult:
        """生成文案"""
        prompt = f"""你是一个专业的{style}内容创作者，擅长撰写{tone}风格的文案。

请为以下主题创作一篇{style}风格的推广文案：
主题：{topic}

要求：
- 标题要有吸引力，使用emoji
- 正文包含：亮点介绍+个人体验+推荐理由
- 结尾加上5个相关热门标签
- 语气{tone}，像朋友推荐一样自然
- 风格符合{style}平台特点"""
        
        if length == "short":
            prompt += "\n- 字数控制在80字以内"
        elif length == "medium":
            prompt += "\n- 字数控制在150字以内"
        else:
            prompt += "\n- 字数控制在300字以内"
        
        response, latency, error = self._call_ollama(prompt)
        
        return GenerationResult(
            model=self.model,
            prompt=prompt[:100],
            response=response,
            latency_ms=int(latency),
            success=error is None,
            error=error
        )
    
    def optimize_copy(self, original: str, platform: str = "小红书") -> GenerationResult:
        """优化文案"""
        prompt = f"""你是一位经验丰富的{platform}内容运营专家，擅长优化文案。

请优化以下文案，使其更符合{platform}平台的传播特点：

【原文】
{original}

【优化要求】
1. 标题更吸引人，加入emoji
2. 结构更清晰，层次分明
3. 语言更生动，有感染力
4. 加入适当的互动引导
5. 添加5-8个热门标签

请直接输出优化后的完整文案："""
        
        response, latency, error = self._call_ollama(prompt)
        
        return GenerationResult(
            model=self.model,
            prompt=prompt[:100],
            response=response,
            latency_ms=int(latency),
            success=error is None,
            error=error
        )
    
    def explain_concept(self, concept: str, audience: str = "普通人") -> GenerationResult:
        """解释概念"""
        prompt = f"""请用{audience}能听懂的方式解释以下概念：

概念：{concept}

要求：
1. 使用简单易懂的语言
2. 用生活中的例子帮助理解
3. 避免专业术语
4. 控制在100字以内"""
        
        response, latency, error = self._call_ollama(prompt)
        
        return GenerationResult(
            model=self.model,
            prompt=prompt[:100],
            response=response,
            latency_ms=int(latency),
            success=error is None,
            error=error
        )
    
    def chat(self, message: str, context: list[str] = None) -> GenerationResult:
        """对话模式"""
        if context:
            history = "\n".join([f"用户: {m}" if i % 2 == 0 else f"助手: {m}" 
                                 for i, m in enumerate(context)])
            prompt = f"{history}\n用户: {message}\n助手:"
        else:
            prompt = message
        
        response, latency, error = self._call_ollama(prompt)
        
        return GenerationResult(
            model=self.model,
            prompt=prompt[:100],
            response=response,
            latency_ms=int(latency),
            success=error is None,
            error=error
        )


def print_result(result: GenerationResult):
    """打印结果"""
    print("\n" + "=" * 50)
    print(f"🌶️ 小米椒内容助手 | 模型: {result.model}")
    print("=" * 50)
    
    if result.success:
        print(f"\n✅ 响应时间: {result.latency_ms}ms")
        print(f"\n📝 输出内容:\n{result.response}")
    else:
        print(f"\n❌ 错误: {result.error}")
    
    print("\n" + "-" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="🌶️ 小米椒内容助手 - Ollama API 集成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成小红书文案
  python assistant.py generate --topic "新开的咖啡馆" --style 小红书
  
  # 优化现有文案
  python assistant.py optimize --text "这家店不错" --platform 小红书
  
  # 解释概念
  python assistant.py explain --concept "区块链" --audience 小学生
  
  # 对话模式
  python assistant.py chat --message "你好"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="生成文案")
    gen_parser.add_argument("--topic", required=True, help="文案主题")
    gen_parser.add_argument("--style", default="小红书", 
                          choices=["小红书", "朋友圈", "微博", "抖音"],
                          help="平台风格")
    gen_parser.add_argument("--length", default="short",
                          choices=["short", "medium", "long"],
                          help="篇幅长度")
    gen_parser.add_argument("--tone", default="活泼",
                          choices=["活泼", "正式", "幽默", "温馨"],
                          help="语气风格")
    
    # optimize 命令
    opt_parser = subparsers.add_parser("optimize", help="优化文案")
    opt_parser.add_argument("--text", required=True, help="待优化的原文案")
    opt_parser.add_argument("--platform", default="小红书",
                          choices=["小红书", "朋友圈", "微博"],
                          help="目标平台")
    
    # explain 命令
    exp_parser = subparsers.add_parser("explain", help="解释概念")
    exp_parser.add_argument("--concept", required=True, help="要解释的概念")
    exp_parser.add_argument("--audience", default="普通人",
                          help="目标受众")
    
    # chat 命令
    chat_parser = subparsers.add_parser("chat", help="对话模式")
    chat_parser.add_argument("--message", required=True, help="输入消息")
    
    # 版本信息
    ver_parser = subparsers.add_parser("version", help="显示版本")
    
    args = parser.parse_args()
    
    if args.command == "version":
        print("🌶️ 小米椒内容助手 v1.0.0")
        print(f"模型: {DEFAULT_MODEL}")
        print(f"API: {OLLAMA_API}")
        return
    
    if not args.command:
        parser.print_help()
        return
    
    # 初始化助手
    assistant = ContentAssistant()
    
    # 执行命令
    if args.command == "generate":
        result = assistant.generate_copy(
            topic=args.topic,
            style=args.style,
            length=args.length,
            tone=args.tone
        )
    elif args.command == "optimize":
        result = assistant.optimize_copy(
            original=args.text,
            platform=args.platform
        )
    elif args.command == "explain":
        result = assistant.explain_concept(
            concept=args.concept,
            audience=args.audience
        )
    elif args.command == "chat":
        result = assistant.chat(message=args.message)
    
    # 打印结果
    print_result(result)
    
    # 返回码
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
