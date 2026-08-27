# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/usr/bin/env python3
"""
Context Manager MCP 服务器 - 提供跨框架支持
基于 MCP (Model Context Protocol) 标准
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# MCP 标准导入
try:
    from mcp.server import Server
    from mcp.types import Tool, Content, TextContent
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("⚠️  MCP 库未安装，使用兼容模式")
    # 简单的 MCP 兼容层
    class Server:
        def __init__(self, name: str):
            self.name = name
            self.tools = {}
        
        def tool(self):
            def decorator(func):
                self.tools[func.__name__] = func
                return func
            return decorator
        
        async def run(self, stdin, stdout):
            pass
    
    class TextContent:
        def __init__(self, text: str):
            self.text = text

class ContextManagerMCP:
    """Context Manager MCP 服务器"""
    
    def __init__(self, framework: str = 'openclaw'):
        self.framework = framework
        self.adapter = self.get_adapter()
        self.threshold = 70
        self.cooldown = 3600
        self.last_switch = 0
    
    def get_adapter(self):
        """获取框架适配器"""
        if self.framework == 'openclaw':
            return OpenClawAdapter()
        elif self.framework == 'claude-code':
            return ClaudeCodeAdapter()
        elif self.framework == 'cursor':
            return CursorAdapter()
        else:
            return OpenClawAdapter()
    
    class OpenClawAdapter:
        """OpenClaw 框架适配器"""
        
        @staticmethod
        def get_context_usage() -> float:
            """获取 OpenClaw 上下文使用率"""
            try:
                from openclaw import session_status
                status = session_status()
                tokens = status.get('tokens', {})
                total = tokens.get('total', 0)
                context = tokens.get('context', 0)
                return (context / total) * 100 if total > 0 else 0
            except:
                return 0
        
        @staticmethod
        def create_new_session():
            """创建新会话"""
            try:
                from openclaw import agentTurn
                return agentTurn()
            except:
                return None
    
    class ClaudeCodeAdapter:
        """Claude Code 框架适配器"""
        
        @staticmethod
        def get_context_usage() -> float:
            """获取 Claude Code 上下文使用率"""
            # 实现Claude Code的上下文获取逻辑
            return 0
        
        @staticmethod
        def create_new_session():
            """创建新会话"""
            # 实现Claude Code的会话创建逻辑
            return None
    
    class CursorAdapter:
        """Cursor 框架适配器"""
        
        @staticmethod
        def get_context_usage() -> float:
            """获取 Cursor 上下文使用率"""
            # 实现Cursor的上下文获取逻辑
            return 0
        
        @staticmethod
        def create_new_session():
            """创建新会话"""
            # 实现Cursor的会话创建逻辑
            return None
    
    def should_switch(self) -> bool:
        """判断是否需要切换会话"""
        import time
        now = time.time()
        
        # 检查冷却期
        if now - self.last_switch < self.cooldown:
            return False
        
        # 获取上下文使用率
        usage = self.adapter.get_context_usage()
        
        # 检查阈值
        if usage >= self.threshold:
            self.last_switch = now
            return True
        
        return False
    
    def switch_session(self):
        """执行会话切换"""
        if self.should_switch():
            return self.adapter.create_new_session()
        return None

# MCP 服务器定义
app = Server("context-manager-mcp")

@app.tool()
async def check_context() -> Dict[str, Any]:
    """检查当前上下文使用率"""
    manager = ContextManagerMCP()
    usage = manager.adapter.get_context_usage()
    should_switch = manager.should_switch()
    
    return {
        "usage": usage,
        "threshold": manager.threshold,
        "should_switch": should_switch,
        "framework": manager.framework
    }

@app.tool()
async def switch_session() -> Dict[str, Any]:
    """手动触發会话切换"""
    manager = ContextManagerMCP()
    result = manager.switch_session()
    
    return {
        "success": result is not None,
        "framework": manager.framework
    }

@app.tool()
async def set_threshold(threshold: int) -> Dict[str, Any]:
    """设置上下文切换阈值"""
    manager = ContextManagerMCP()
    manager.threshold = threshold
    
    return {
        "success": True,
        "threshold": threshold
    }

@app.tool()
async def get_status() -> Dict[str, Any]:
    """获取Context Manager状态"""
    return {
        "framework": "openclaw",
        "version": "2.7.0",
        "threshold": 70,
        "cooldown": 3600,
        "mcp_enabled": True
    }

async def main():
    """启动MCP服务器"""
    if HAS_MCP:
        from mcp.server.stdio import stdio_server
        async with stdio_server(sys.stdin.buffer, sys.stdout.buffer) as (read_stream, write_stream):
            await app.run(read_stream, write_stream)
    else:
        # 兼容模式：通过stdio提供简单API
        for line in sys.stdin:
            try:
                data = json.loads(line.strip())
                command = data.get('command')
                
                if command == 'check':
                    result = await check_context()
                elif command == 'switch':
                    result = await switch_session()
                elif command == 'status':
                    result = await get_status()
                else:
                    result = {"error": "Unknown command"}
                
                sys.stdout.write(json.dumps(result) + '\n')
                sys.stdout.flush()
            except json.JSONDecodeError:
                sys.stdout.write(json.dumps({"error": "Invalid JSON"}) + '\n')
                sys.stdout.flush()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())