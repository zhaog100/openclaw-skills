#!/usr/bin/env python3
"""
Oil-Gold Correlation MCP 服务器 - 提供跨框架支持
基于 MCP (Model Context Protocol) 标准
"""

import json
import sys
import asyncio
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

class OilGoldMCP:
    """Oil-Gold Correlation MCP 服务器"""
    
    def __init__(self, framework: str = 'openclaw'):
        self.framework = framework
        self.data_sources = ['akshare', 'yfinance', 'fred', 'alphavantage']
        self.default_period = '1y'
        self.cache_ttl = 300  # 5分钟
    
    async def fetch_data(self, symbols: List[str], period: str = None) -> Dict[str, Any]:
        """获取石油黄金数据"""
        if period is None:
            period = self.default_period
        
        results = {}
        
        for symbol in symbols:
            # 尝试多个数据源
            for source in self.data_sources:
                try:
                    data = await self.fetch_from_source(source, symbol, period)
                    if data:
                        results[symbol] = {
                            'source': source,
                            'data': data
                        }
                        break
                except Exception as e:
                    continue
        
        return results
    
    async def fetch_from_source(self, source: str, symbol: str, period: str) -> Optional[Dict]:
        """从指定数据源获取数据"""
        # 这里简化处理，实际应该调用相应的数据获取模块
        if source == 'akshare':
            return await self._fetch_akshare(symbol, period)
        elif source == 'yfinance':
            return await self._fetch_yfinance(symbol, period)
        elif source == 'fred':
            return await self._fetch_fred(symbol, period)
        return None
    
    async def _fetch_akshare(self, symbol: str, period: str) -> Optional[Dict]:
        """从akshare获取数据"""
        try:
            import akshare as ak
            
            # 映射符号
            symbol_map = {
                'AU0': 'AU0',  # 黄金期货
                'SC0': 'SC0',  # 原油期货
                'CL=F': 'SC0',  # WTI原油
                'GC=F': 'AU0'   # COMEX黄金
            }
            
            ak_symbol = symbol_map.get(symbol, symbol)
            
            # 获取数据
            df = ak.futures_main_sina(symbol=ak_symbol)
            
            if df is not None and not df.empty:
                return {
                    'dates': df['日期'].tolist(),
                    'open': df['开盘价'].tolist(),
                    'high': df['最高价'].tolist(),
                    'low': df['最低价'].tolist(),
                    'close': df['收盘价'].tolist(),
                    'volume': df['成交量'].tolist()
                }
        except Exception as e:
            print(f"akshare 获取 {symbol} 失败: {e}")
        
        return None
    
    async def _fetch_yfinance(self, symbol: str, period: str) -> Optional[Dict]:
        """从yfinance获取数据"""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            
            if not df.empty:
                return {
                    'dates': df.index.strftime('%Y-%m-%d').tolist(),
                    'open': df['Open'].tolist(),
                    'high': df['High'].tolist(),
                    'low': df['Low'].tolist(),
                    'close': df['Close'].tolist(),
                    'volume': df['Volume'].tolist()
                }
        except Exception as e:
            print(f"yfinance 获取 {symbol} 失败: {e}")
        
        return None
    
    async def _fetch_fred(self, symbol: str, period: str) -> Optional[Dict]:
        """从FRED获取数据"""
        try:
            from fredapi import Fred
            
            fred = Fred()
            data = fred.get_series(symbol)
            
            if data is not None:
                return {
                    'dates': data.index.strftime('%Y-%m-%d').tolist(),
                    'values': data.tolist()
                }
        except Exception as e:
            print(f"FRED 获取 {symbol} 失败: {e}")
        
        return None
    
    async def analyze_correlation(self, symbols: List[str], period: str = None) -> Dict[str, Any]:
        """分析相关性"""
        data = await self.fetch_data(symbols, period)
        
        if len(data) < 2:
            return {"error": "数据不足，无法分析相关性"}
        
        # 提取黄金和原油数据
        gold_data = None
        oil_data = None
        
        for symbol, item in data.items():
            if 'AU' in symbol or 'GC' in symbol:
                gold_data = item['data']
            elif 'SC' in symbol or 'CL' in symbol or 'BZ' in symbol:
                oil_data = item['data']
        
        if not gold_data or not oil_data:
            return {"error": "需要黄金和原油数据才能分析相关性"}
        
        # 计算相关性
        try:
            import pandas as pd
            import numpy as np
            
            # 对齐日期
            gold_df = pd.DataFrame({
                'date': gold_data['dates'],
                'gold_close': gold_data['close']
            })
            oil_df = pd.DataFrame({
                'date': oil_data['dates'],
                'oil_close': oil_data['close']
            })
            
            merged = pd.merge(gold_df, oil_df, on='date', how='inner')
            
            if len(merged) < 2:
                return {"error": "重叠数据不足"}
            
            # 计算收益率
            merged['gold_return'] = merged['gold_close'].pct_change()
            merged['oil_return'] = merged['oil_close'].pct_change()
            
            # 计算相关性
            gold_returns = merged['gold_return'].dropna()
            oil_returns = merged['oil_return'].dropna()
            
            if len(gold_returns) < 2 or len(oil_returns) < 2:
                return {"error": "收益率数据不足"}
            
            correlation = gold_returns.corr(oil_returns)
            
            return {
                "correlation": correlation,
                "data_points": len(merged),
                "period": period,
                "symbols": symbols
            }
            
        except Exception as e:
            return {"error": f"分析失败: {e}"}
    
    async def generate_report(self, symbols: List[str], period: str = None) -> str:
        """生成分析报告"""
        correlation_data = await self.analyze_correlation(symbols, period)
        
        if "error" in correlation_data:
            return f"错误: {correlation_data['error']}"
        
        corr = correlation_data['correlation']
        
        # 解释相关性
        if corr > 0.7:
            relation = "强正相关"
            interpretation = "黄金和原油价格同向变动趋势明显"
        elif corr > 0.3:
            relation = "中等正相关"
            interpretation = "黄金和原油价格有一定同向趋势"
        elif corr > -0.3:
            relation = "弱相关"
            interpretation = "黄金和原油价格关联性较弱"
        elif corr > -0.7:
            relation = "中等负相关"
            interpretation = "黄金和原油价格有反向趋势"
        else:
            relation = "强负相关"
            interpretation = "黄金和原油价格反向变动明显"
        
        report = f"""
石油黄金相关性分析报告
======================

数据期间: {correlation_data['period']}
数据点数量: {correlation_data['data_points']}
相关品种: {', '.join(correlation_data['symbols'])}

分析结果:
- 相关系数: {corr:.4f}
- 相关类型: {relation}
- 解读: {interpretation}

投资启示:
"""
        
        if corr > 0.5:
            report += "- 两者同向变动，可考虑对冲策略\n- 关注宏观经济因素对两者的共同影响"
        elif corr < -0.5:
            report += "- 两者反向变动，可作为投资组合的平衡工具\n- 一个品种的上涨可能预示另一个品种的下跌"
        else:
            report += "- 两者关联性不强，需要分别分析各自的影响因素\n- 可独立制定投资策略"
        
        report += "\n\n⚠️ 免责声明: 本分析仅供参考，不构成投资建议。市场有风险，投资需谨慎。"
        
        return report

# MCP 服务器定义
app = Server("oil-gold-correlation-mcp")

@app.tool()
async def fetch_data(symbols: List[str], period: str = "1y") -> Dict[str, Any]:
    """获取石油黄金数据"""
    manager = OilGoldMCP()
    return await manager.fetch_data(symbols, period)

@app.tool()
async def analyze_correlation(symbols: List[str], period: str = "1y") -> Dict[str, Any]:
    """分析石油黄金相关性"""
    manager = OilGoldMCP()
    return await manager.analyze_correlation(symbols, period)

@app.tool()
async def generate_report(symbols: List[str], period: str = "1y") -> str:
    """生成石油黄金分析报告"""
    manager = OilGoldMCP()
    return await manager.generate_report(symbols, period)

@app.tool()
async def get_status() -> Dict[str, Any]:
    """获取服务状态"""
    return {
        "service": "oil-gold-correlation-mcp",
        "version": "2.1.4",
        "framework": "openclaw",
        "mcp_enabled": True,
        "data_sources": ["akshare", "yfinance", "fred", "alphavantage"]
    }

async def main():
    """启动MCP服务器"""
    if HAS_MCP:
        from mcp.server.stdio import stdio_server
        async with stdio_server(sys.stdin.buffer, sys.stdout.buffer) as (read_stream, write_stream):
            await app.run(read_stream, write_stream)
    else:
        # 兼容模式
        for line in sys.stdin:
            try:
                data = json.loads(line.strip())
                command = data.get('command')
                params = data.get('params', {})
                
                if command == 'fetch':
                    result = await fetch_data(**params)
                elif command == 'analyze':
                    result = await analyze_correlation(**params)
                elif command == 'report':
                    result = await generate_report(**params)
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
    asyncio.run(main())