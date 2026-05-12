#!/usr/bin/env python3
"""
石油黄金投资建议模块
短期（1天~1周）为主 + 中长期（1月~6月）补充

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 思捷娅科技 (SJYKJ)

⚠️ 重要声明：本工具提供技术分析参考，不构成投资建议。
   市场有风险，投资需谨慎。所有分析结果仅供参考。

v2.0 更新：
- 多数据源支持（yfinance + AlphaVantage + Twelve Data + FRED）
- 智能数据源调度和故障转移
- 数据源健康监控
"""

import warnings
warnings.filterwarnings('ignore')

import sys
import time
import random
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

import numpy as np
import pandas as pd
from scipy import stats

# ==================== v2.0 多数据源配置 ====================

# 数据源配置
DATA_SOURCE_CONFIG = {
    "yfinance": {
        "enabled": True,
        "priority": 1,
        "rate_limit": 2000,  # 请求间隔（毫秒）
        "daily_limit": float('inf'),  # 无限制
    },
    "alphavantage": {
        "enabled": False,
        "priority": 2,
        "api_key": "",  # 需要用户配置
        "rate_limit": 5000,  # 免费版每天25次
        "daily_limit": 25,
    },
    "twelvedata": {
        "enabled": False,
        "priority": 3,
        "api_key": "",  # 需要用户配置
        "rate_limit": 12000,  # 免费版每天8次
        "daily_limit": 8,
    },
    "akshare": {
        "enabled": True,
        "priority": 4,
        "rate_limit": 1000,
        "daily_limit": float('inf'),
    },
    "fred": {
        "enabled": False,
        "priority": 5,
        "api_key": "",  # 需要用户配置
        "rate_limit": 1000,
        "daily_limit": float('inf'),
    },
}

# 品种符号映射
SYMBOL_MAPPING = {
    "GC=F": {"yfinance": "GC=F", "alphavantage": "GOLD", "twelvedata": "GC", "akshare": None},
    "CL=F": {"yfinance": "CL=F", "alphavantage": "OIL", "twelvedata": "CL", "akshare": None},
    "BZ=F": {"yfinance": "BZ=F", "alphavantage": "OIL", "twelvedata": "BRT", "akshare": None},
    "DX-Y.NYB": {"yfinance": "DX-Y.NYB", "alphavantage": "DXY", "twelvedata": "DXY", "akshare": None},
    "AU0": {"yfinance": None, "alphavantage": None, "twelvedata": None, "akshare": "AU0"},
    "SC0": {"yfinance": None, "alphavantage": None, "twelvedata": None, "akshare": "SC0"},
}


# ==================== v2.0 安全请求函数 ====================

def safe_yfinance_request(symbol: str, max_retries: int = 3, min_interval: float = 2.0, max_interval: float = 5.0) -> Optional[pd.DataFrame]:
    """安全的yfinance请求，带延迟和重试机制"""
    import yfinance as yf
    
    for attempt in range(max_retries):
        try:
            # 基础延迟（随机）
            delay = random.uniform(min_interval, max_interval) * (attempt + 1)
            print(f"    [yfinance] 等待 {delay:.1f}秒后请求 {symbol}...")
            time.sleep(delay)
            
            # 尝试使用Ticker.history()（更稳定）
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="3mo", interval="1d")
                if data is not None and len(data) >= 20:
                    print(f"    [yfinance] ✅ 通过Ticker.history()获取 {symbol} 成功 ({len(data)} 条数据)")
                    return data.dropna()
            except Exception as e1:
                print(f"    [yfinance] Ticker.history()失败: {e1}")
            
            # download fallback
            data = yf.download(symbol, period="3mo", interval="1d", progress=False)
            if data is not None and len(data) >= 20:
                if isinstance(data.columns, pd.MultiIndex):
                    data = data[symbol]
                print(f"    [yfinance] ✅ 通过download()获取 {symbol} 成功 ({len(data)} 条数据)")
                return data.dropna()
            
            raise ValueError("返回数据为空")
            
        except Exception as e:
            wait_time = 2 ** attempt  # 指数退避
            print(f"    [yfinance] ❌ 第{attempt+1}次尝试失败: {e}")
            if attempt < max_retries - 1:
                print(f"    [yfinance] ⏳ {wait_time}秒后重试...")
                time.sleep(wait_time)
            else:
                print(f"    [yfinance] ⚠️ {symbol} 获取失败，已达最大重试次数")
    
    return None


def retry_yfinance_request(symbol: str, max_retries: int = 3) -> Optional[pd.DataFrame]:
    """带指数退避的重试请求"""
    return safe_yfinance_request(symbol, max_retries=max_retries, min_interval=2.0, max_interval=5.0)


# ==================== v2.0 数据源类 ====================

class YFinanceSource:
    """yfinance数据源"""
    name = "yfinance"
    
    def fetch(self, symbol: str, period: str = "3mo") -> Optional[pd.DataFrame]:
        return safe_yfinance_request(symbol, max_retries=3)


class AlphaVantageSource:
    """AlphaVantage数据源"""
    name = "alphavantage"
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or DATA_SOURCE_CONFIG["alphavantage"].get("api_key", "")
    
    def fetch(self, symbol: str, period: str = "3mo") -> Optional[pd.DataFrame]:
        if not self.api_key:
            print(f"    [alphavantage] ⚠️ 未配置API Key，跳过")
            return None
        
        try:
            from alpha_vantage.timeseries import TimeSeries
            
            print(f"    [alphavantage] 请求 {symbol}...")
            ts = TimeSeries(key=self.api_key)
            
            # AlphaVantage的symbol映射
            av_symbol = SYMBOL_MAPPING.get(symbol, {}).get("alphavantage", symbol)
            if not av_symbol:
                return None
            
            # 获取日线数据
            data, metadata = ts.get_daily(symbol=av_symbol, outputsize="compact")
            
            if data:
                df = pd.DataFrame(data)
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                # 只保留需要的列
                df = df[['1. open', '2. high', '3. low', '4. close', '5. volume']]
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                print(f"    [alphavantage] ✅ 获取 {symbol} 成功 ({len(df)} 条数据)")
                return df
            
        except Exception as e:
            print(f"    [alphavantage] ❌ 获取 {symbol} 失败: {e}")
        
        return None


class TwelveDataSource:
    """Twelve Data数据源"""
    name = "twelvedata"
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or DATA_SOURCE_CONFIG["twelvedata"].get("api_key", "")
    
    def fetch(self, symbol: str, period: str = "3mo") -> Optional[pd.DataFrame]:
        if not self.api_key:
            print(f"    [twelvedata] ⚠️ 未配置API Key，跳过")
            return None
        
        try:
            from twelvedata import TDClient
            
            print(f"    [twelvedata] 请求 {symbol}...")
            td = TDClient(apikey=self.api_key)
            
            # Twelve Data的symbol映射
            td_symbol = SYMBOL_MAPPING.get(symbol, {}).get("twelvedata", symbol)
            if not td_symbol:
                return None
            
            # 获取时间序列
            ts = td.time_series(
                symbol=td_symbol,
                interval="1day",
                outputsize=30 if period == "3mo" else 365
            )
            
            data = ts.as_json()
            if data:
                df = pd.DataFrame(data)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
                df = df.sort_index()
                # 转换列名
                df = df.rename(columns={
                    'open': 'Open', 'high': 'High', 'low': 'Low', 
                    'close': 'Close', 'volume': 'Volume'
                })
                print(f"    [twelvedata] ✅ 获取 {symbol} 成功 ({len(df)} 条数据)")
                return df
            
        except Exception as e:
            print(f"    [twelvedata] ❌ 获取 {symbol} 失败: {e}")
        
        return None


class AkshareSource:
    """akshare数据源（国内）"""
    name = "akshare"
    
    def fetch(self, symbol: str, period: str = "3mo") -> Optional[pd.DataFrame]:
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from fetch_data import fetch_data
            
            print(f"    [akshare] 请求 {symbol}...")
            raw = fetch_data(period=period)
            
            # 找到对应的akshare key
            ak_key = None
            for name, info in INSTRUMENTS.items():
                if info.get("symbol") == symbol:
                    ak_key = info.get("ak_key")
                    break
            
            if not ak_key or ak_key not in raw:
                print(f"    [akshare] ⚠️ 未找到 {symbol} 的数据")
                return None
            
            d = raw[ak_key]
            if d.get("close") and len(d["close"]) >= 20:
                df = pd.DataFrame({
                    "Open": d["open"],
                    "High": d["high"],
                    "Low": d["low"],
                    "Close": d["close"],
                    "Volume": d["volume"],
                }, index=pd.to_datetime(d["dates"]))
                print(f"    [akshare] ✅ 获取 {symbol} 成功 ({len(df)} 条数据)")
                return df
            
        except Exception as e:
            print(f"    [akshare] ❌ 获取 {symbol} 失败: {e}")
        
        return None


class FREDSource:
    """FRED宏观经济数据源"""
    name = "fred"
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or DATA_SOURCE_CONFIG["fred"].get("api_key", "")
    
    def fetch(self, series_id: str, period: str = "3mo") -> Optional[pd.DataFrame]:
        if not self.api_key:
            print(f"    [FRED] ⚠️ 未配置API Key，跳过")
            return None
        
        try:
            from fredapi import Fred
            
            print(f"    [FRED] 请求 {series_id}...")
            fred = Fred(api_key=self.api_key)
            
            # 获取数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90) if period == "3mo" else end_date - timedelta(days=365)
            
            data = fred.get_series(series_id, start_date, end_date)
            
            if data is not None and len(data) >= 20:
                df = pd.DataFrame({"Value": data})
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                print(f"    [FRED] ✅ 获取 {series_id} 成功 ({len(df)} 条数据)")
                return df
            
        except Exception as e:
            print(f"    [FRED] ❌ 获取 {series_id} 失败: {e}")
        
        return None


# ==================== v2.0 数据源管理器 ====================

class DataSourceManager:
    """智能数据源管理器"""
    
    def __init__(self):
        self.sources = {
            "yfinance": YFinanceSource(),
            "alphavantage": AlphaVantageSource(),
            "twelvedata": TwelveDataSource(),
            "akshare": AkshareSource(),
            "fred": FREDSource(),
        }
        
        # 按优先级排序的fallback顺序
        self.fallback_order = [
            "yfinance", "alphavantage", "twelvedata", "akshare", "fred"
        ]
        
        # 健康状态
        self.health_status = {name: "unknown" for name in self.sources}
        
        # 请求计数
        self.request_count = {name: 0 for name in self.sources}
    
    def get_data(self, symbol: str, priority: str = None, period: str = "3mo") -> Optional[pd.DataFrame]:
        """智能获取数据，优先使用指定源，失败则自动切换"""
        
        # 确定数据源尝试顺序
        if priority and priority in self.sources:
            sources_to_try = [priority] + [s for s in self.fallback_order if s != priority]
        else:
            sources_to_try = self.fallback_order.copy()
        
        # 按优先级排序
        sources_to_try = sorted(sources_to_try, 
                              key=lambda s: DATA_SOURCE_CONFIG.get(s, {}).get("priority", 99))
        
        last_error = None
        
        for source_name in sources_to_try:
            # 检查源是否启用
            if not DATA_SOURCE_CONFIG.get(source_name, {}).get("enabled", False):
                continue
            
            # 检查日限额
            if self.request_count.get(source_name, 0) >= DATA_SOURCE_CONFIG.get(source_name, {}).get("daily_limit", float('inf')):
                print(f"    [⚠️ {source_name}] 已达到日限额，跳过")
                continue
            
            source = self.sources.get(source_name)
            if not source:
                continue
            
            try:
                print(f"    [→] 尝试使用 {source_name} 获取 {symbol}...")
                self.request_count[source_name] = self.request_count.get(source_name, 0) + 1
                
                data = source.fetch(symbol, period)
                
                if data is not None and len(data) >= 20:
                    print(f"    [✅] 使用 {source_name} 成功获取 {symbol} ({len(data)} 条数据)")
                    self.health_status[source_name] = "healthy"
                    return data
                else:
                    print(f"    [⚠️] {source_name} 返回数据不足")
                    self.health_status[source_name] = "degraded"
                    
            except Exception as e:
                print(f"    [❌] {source_name} 获取 {symbol} 失败: {e}")
                self.health_status[source_name] = "down"
                last_error = e
                continue
        
        print(f"    [🚨] 所有数据源都无法获取 {symbol}")
        return None
    
    def check_health(self, source_name: str) -> str:
        """检查指定数据源健康状态"""
        if source_name not in self.sources:
            return "unknown"
        
        try:
            test_symbol = "AAPL"
            if source_name == "akshare":
                test_symbol = "000001"
            
            source = self.sources[source_name]
            data = source.fetch(test_symbol)
            
            if data is not None and len(data) >= 5:
                self.health_status[source_name] = "healthy"
                return "healthy"
            else:
                self.health_status[source_name] = "degraded"
                return "degraded"
                
        except Exception as e:
            print(f"    [🚨] {source_name} 健康检查失败: {e}")
            self.health_status[source_name] = "down"
            return "down"
    
    def check_all_health(self) -> Dict[str, str]:
        """检查所有数据源健康状态"""
        print("\n🔍 数据源健康检查:")
        for source_name in self.sources:
            status = self.check_health(source_name)
            emoji = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
            print(f"   {emoji} {source_name}: {status}")
        return self.health_status
    
    def get_healthy_sources(self) -> List[str]:
        """获取当前健康的数据源列表"""
        return [name for name, status in self.health_status.items() 
                if status == "healthy" and DATA_SOURCE_CONFIG.get(name, {}).get("enabled", False)]


# ==================== v2.0 数据源健康监控 ====================

class DataSourceMonitor:
    """数据源健康监控"""
    
    def __init__(self):
        self.health_log = Path(__file__).parent.parent / "cache" / "datasource_health.json"
        self.health_log.parent.mkdir(parents=True, exist_ok=True)
        self.load_health_log()
    
    def load_health_log(self):
        """加载历史健康日志"""
        if self.health_log.exists():
            try:
                with open(self.health_log, 'r') as f:
                    self.log = json.load(f)
            except:
                self.log = {}
        else:
            self.log = {}
    
    def save_health_log(self):
        """保存健康日志"""
        try:
            with open(self.health_log, 'w') as f:
                json.dump(self.log, f, indent=2, default=str)
        except Exception as e:
            print(f"    [⚠️] 保存健康日志失败: {e}")
    
    def record_health(self, source_name: str, status: str, error: str = None):
        """记录数据源健康状态"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if today not in self.log:
            self.log[today] = {}
        
        self.log[today][source_name] = {
            "status": status,
            "error": str(error) if error else None,
            "timestamp": datetime.now().isoformat()
        }
        
        self.save_health_log()
    
    def get_availability(self, source_name: str, days: int = 7) -> float:
        """计算数据源可用性百分比"""
        availability_count = 0
        total_count = 0
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            if date in self.log and source_name in self.log[date]:
                total_count += 1
                if self.log[date][source_name].get("status") == "healthy":
                    availability_count += 1
        
        return (availability_count / total_count * 100) if total_count > 0 else 0
    
    def send_alert(self, source_name: str, status: str):
        """发送告警通知"""
        if status == "down":
            print(f"\n🚨【告警】数据源 {source_name} 不可用！")
            print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   建议: 检查API配置或切换备用数据源")


# 全局数据源管理器实例
_data_source_manager = None

def get_data_source_manager() -> DataSourceManager:
    """获取全局数据源管理器实例"""
    global _data_source_manager
    if _data_source_manager is None:
        _data_source_manager = DataSourceManager()
    return _data_source_manager


# ==================== 品种定义 =====
# 自动检测可用数据源，国际品种和国内品种自动切换
INSTRUMENTS = {
    # 国际品种（主力，美元计价）
    "黄金期货": {"symbol": "GC=F", "type": "期货", "exchange": "COMEX", "currency": "USD", "source": "yfinance"},
    "WTI原油": {"symbol": "CL=F", "type": "期货", "exchange": "NYMEX", "currency": "USD", "source": "yfinance"},
    "布伦特原油": {"symbol": "BZ=F", "type": "期货", "exchange": "ICE", "currency": "USD", "source": "yfinance"},
    "白银期货": {"symbol": "SI=F", "type": "期货", "exchange": "COMEX", "currency": "USD", "source": "yfinance"},
    "美元指数": {"symbol": "DX-Y.NYB", "type": "指数", "exchange": "ICE", "currency": "USD", "source": "yfinance"},
    # 国内品种（辅助，人民币计价）
    "沪金期货": {"symbol": "AU0", "type": "期货", "exchange": "上海期货交易所", "currency": "CNY", "source": "akshare", "ak_key": "gold"},
    "沪油期货": {"symbol": "SC0", "type": "期货", "exchange": "上海国际能源交易中心", "currency": "CNY", "source": "akshare", "ak_key": "wti"},
    "沪银期货": {"symbol": "AG0", "type": "期货", "exchange": "上海期货交易所", "currency": "CNY", "source": "akshare", "ak_key": "silver"},
}


# ==================== 批量数据下载（v2.0 智能多数据源）====================

def batch_download(symbols: List[str], period: str = "3mo", interval: str = "1d", max_retries: int = 3) -> pd.DataFrame:
    """批量下载数据，使用智能数据源管理器"""
    import yfinance as yf
    
    # 获取数据源管理器
    manager = get_data_source_manager()
    
    # 自动选择可用数据源批量下载
    for attempt in range(max_retries):
        try:
            print(f"[批量下载] 第{attempt+1}次尝试下载 {len(symbols)} 个品种...")
            
            # 先尝试yfinance批量下载
            data = yf.download(
                symbols, 
                period=period, 
                interval=interval,
                group_by="ticker", 
                progress=False,
                threads=True
            )
            
            if data is not None and not data.empty:
                # 检查数据完整性
                valid_count = 0
                for sym in symbols:
                    try:
                        if isinstance(data.columns, pd.MultiIndex):
                            if sym in data.columns.get_level_values(0):
                                valid_count += 1
                        elif sym in data.columns:
                            valid_count += 1
                    except:
                        pass
                
                if valid_count >= len(symbols) * 0.5:
                    print(f"[批量下载] ✅ 成功获取 {valid_count}/{len(symbols)} 个品种数据")
                    return data
                    
        except Exception as e:
            print(f"[批量下载] ❌ 批量下载失败: {e}")
        
        # 指数退避
        if attempt < max_retries - 1:
            wait_time = 3 * (attempt + 1)
            print(f"[批量下载] ⏳ {wait_time}秒后重试...")
            time.sleep(wait_time)
    
    # 批量下载失败，尝试逐个下载
    print(f"[批量下载] ⚠️ 批量下载失败，尝试逐个下载...")
    
    result_dfs = {}
    for sym in symbols:
        # 自动选择可用数据源
        data = safe_yfinance_request(sym, max_retries=2, min_interval=1.0, max_interval=2.0)
        
        if data is not None and len(data) >= 20:
            result_dfs[sym] = data
        else:
            # 尝试其他数据源
            manager = get_data_source_manager()
            data = manager.get_data(sym, period=period)  # 自动选择可用源
            if data is not None:
                result_dfs[sym] = data
    
    if result_dfs:
        print(f"[批量下载] ✅ 通过多数据源获取 {len(result_dfs)}/{len(symbols)} 个品种数据")
        # 合并数据
        combined = pd.concat(result_dfs, axis=1)
        return combined
    else:
        print(f"[批量下载] ❌ 所有数据源都无法获取数据")
        return pd.DataFrame()


# ==================== 技术指标函数 ====================

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])


def calc_macd(series):
    ema12 = series.ewm(span=12).mean()
    ema26 = series.ewm(span=26).mean()
    dif = ema12 - ema26
    dea = dif.ewm(span=9).mean()
    macd_hist = (dif - dea) * 2

    if len(dif) < 2:
        return {
            "dif": round(float(dif.iloc[-1]), 2),
            "dea": round(float(dea.iloc[-1]), 2),
            "macd": round(float(macd_hist.iloc[-1]), 2),
            "signal": "数据不足",
        }

    dif_v, dea_v = float(dif.iloc[-1]), float(dea.iloc[-1])
    dif_prev, dea_prev = float(dif.iloc[-2]), float(dea.iloc[-2])

    if dif_v > dea_v and dif_prev <= dea_prev:
        sig = "金叉↗"
    elif dif_v < dea_v and dif_prev >= dea_prev:
        sig = "死叉↘"
    elif dif_v > dea_v:
        sig = "多头"
    else:
        sig = "空头"

    return {
        "dif": round(dif_v, 2), "dea": round(dea_v, 2),
        "macd": round(float(macd_hist.iloc[-1]), 2), "signal": sig,
    }


def calc_bollinger(series, period=20):
    ma = series.rolling(period).mean()
    std = series.rolling(period).std()
    upper = ma + 2 * std
    lower = ma - 2 * std
    price = float(series.iloc[-1])
    u, m, l = float(upper.iloc[-1]), float(ma.iloc[-1]), float(lower.iloc[-1])
    pct = (price - l) / (u - l) * 100 if u != l else 50
    return {
        "upper": round(u, 2), "middle": round(m, 2), "lower": round(l, 2),
        "pct": round(pct, 1),
        "position": "上轨上方(超买)" if price > u else
                    "下轨下方(超卖)" if price < l else
                    f"中轨上方({pct:.0f}%位)" if price > m else f"中轨下方({pct:.0f}%位)",
    }


def calc_stoch(high, low, close, period=14):
    """标准 KDJ 随机指标（使用 High/Low/Close）"""
    hh = high.rolling(period).max()
    ll = low.rolling(period).min()
    k = (close - ll) / (hh - ll) * 100
    d = k.rolling(3).mean()
    j = 3 * k - 2 * d
    k_val, d_val, j_val = float(k.iloc[-1]), float(d.iloc[-1]), float(j.iloc[-1])
    return {
        "K": round(k_val, 1), "D": round(d_val, 1), "J": round(j_val, 1),
        "signal": "超卖金叉" if k_val < 20 and k_val > d_val else
                  "超买死叉" if k_val > 80 and k_val < d_val else
                  "金叉上行" if k_val > d_val else "死叉下行",
    }


def calc_atr(high, low, close, period=14):
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    return float(atr.iloc[-1])


def calc_obv(close, volume):
    """OBV（能量潮）+ 量价背离判断"""
    try:
        direction = close.diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
        obv = (direction * volume).cumsum()
        obv_val = float(obv.iloc[-1])
        obv_5ago = float(obv.iloc[-6]) if len(obv) > 5 else obv_val
        price_5ago = float(close.iloc[-6]) if len(close) > 5 else float(close.iloc[-1])
        price_now = float(close.iloc[-1])

        price_up = price_now > price_5ago
        obv_up = obv_val > obv_5ago

        if price_up and not obv_up:
            divergence = "量价顶背离⚠️（看跌信号）"
            score_impact = -15
        elif not price_up and obv_up:
            divergence = "量价底背离✅（看涨信号）"
            score_impact = 15
        elif price_up and obv_up:
            divergence = "量价齐升（健康上涨）"
            score_impact = 5
        else:
            divergence = "量价齐跌（弱势）"
            score_impact = -5

        return {
            "obv": round(obv_val, 0),
            "obv_change_5d": round((obv_val - obv_5ago) / abs(obv_5ago) * 100, 1) if obv_5ago != 0 else 0,
            "divergence": divergence,
            "score_impact": score_impact,
        }
    except Exception:
        return {"obv": 0, "obv_change_5d": 0, "divergence": "计算失败", "score_impact": 0}


def calc_gold_oil_ratio(gold_price, oil_price):
    """黄金-原油比率分析"""
    try:
        if oil_price <= 0:
            return None
        ratio = gold_price / oil_price

        if ratio > 30:
            level = "极度偏高🔴（原油相对便宜/避险情绪极强）"
            score_impact = 10
        elif ratio > 25:
            level = "偏高🟠（避险情绪较强）"
            score_impact = 5
        elif ratio > 20:
            level = "正常范围🟢"
            score_impact = 0
        elif ratio > 15:
            level = "偏低🟠（原油相对贵/风险偏好高）"
            score_impact = -5
        else:
            level = "极度偏低🔴（风险偏好极高）"
            score_impact = -10

        return {
            "ratio": round(ratio, 2),
            "level": level,
            "score_impact": score_impact,
        }
    except Exception:
        return None


def calc_fibonacci(high, low, current_price):
    """Fibonacci 回撤位计算"""
    try:
        diff = high - low
        if diff <= 0:
            return None
        fib_levels = {
            "23.6%": round(high - diff * 0.236, 2),
            "38.2%": round(high - diff * 0.382, 2),
            "50.0%": round(high - diff * 0.5, 2),
            "61.8%": round(high - diff * 0.618, 2),
            "78.6%": round(high - diff * 0.786, 2),
        }

        sorted_levels = sorted(fib_levels.items(), key=lambda x: x[1], reverse=True)
        zone = "高位"
        for i, (name, price) in enumerate(sorted_levels):
            if current_price >= price:
                zone = f"{name}附近" if i == 0 else f"{name}~{sorted_levels[i-1][0]}区间"
                break
        else:
            zone = f"{sorted_levels[-1][0]}以下（深度回调）"

        return {
            "high": round(high, 2),
            "low": round(low, 2),
            "levels": fib_levels,
            "zone": zone,
            "score_impact": 5 if current_price <= fib_levels["38.2%"] else -5 if current_price >= fib_levels["23.6%"] else 0,
        }
    except Exception:
        return None


def calc_support_resistance(close, high_series, low_series, boll_upper, boll_lower, current_price):
    """支撑/阻力位计算"""
    try:
        recent_high = float(high_series.tail(30).max())
        recent_low = float(low_series.tail(30).min())

        magnitude = 10 ** (len(str(int(current_price))) - 1)
        unit = magnitude // 10 if magnitude >= 10 else 1
        psych_support = round((current_price // unit) * unit, 2)
        psych_resistance = round((current_price // unit + 1) * unit, 2)

        supports = sorted([s for s in [recent_low, boll_lower, psych_support] if s < current_price], reverse=True)
        resistances = sorted([r for r in [recent_high, boll_upper, psych_resistance] if r > current_price])

        nearest_support = round(supports[0], 2) if supports else round(recent_low, 2)
        nearest_resistance = round(resistances[0], 2) if resistances else round(recent_high, 2)

        return {
            "support1": nearest_support,
            "support2": round(supports[1], 2) if len(supports) > 1 else None,
            "resistance1": nearest_resistance,
            "resistance2": round(resistances[1], 2) if len(resistances) > 1 else None,
        }
    except Exception:
        return None


def calc_multi_timeframe(symbol, batch_3mo=None, batch_1y=None):
    """多时间框架分析"""
    result = {}
    try:
        if batch_1y is not None and symbol in batch_1y:
            data_1y = batch_1y[symbol].dropna()
            if len(data_1y) >= 40:
                close_1y = data_1y["Close"] if "Close" in data_1y else data_1y.iloc[:, 0]
                weekly = close_1y.iloc[::5]
                if len(weekly) >= 5:
                    w_ma5 = float(weekly.tail(5).mean())
                    w_now = float(weekly.iloc[-1])
                    result["weekly"] = "偏多↗" if w_now > w_ma5 else "偏空↘" if w_now < w_ma5 else "震荡→"
                    result["weekly_score"] = 10 if w_now > w_ma5 else -10 if w_now < w_ma5 else 0
    except Exception:
        result["weekly"] = "数据不足"
        result["weekly_score"] = 0

    try:
        if batch_3mo is not None and symbol in batch_3mo:
            data_3mo = batch_3mo[symbol].dropna()
            if len(data_3mo) >= 10:
                close_3mo = data_3mo["Close"] if "Close" in data_3mo else data_3mo.iloc[:, 0]
                ma5_now = float(close_3mo.tail(5).mean())
                ma5_prev = float(close_3mo.iloc[-10:-5].mean()) if len(close_3mo) >= 10 else ma5_now
                result["daily"] = "短线上行" if ma5_now > ma5_prev else "短线下行" if ma5_now < ma5_prev else "短线横盘"
                result["daily_score"] = 5 if ma5_now > ma5_prev else -5 if ma5_now < ma5_prev else 0
    except Exception:
        result["daily"] = "数据不足"
        result["daily_score"] = 0

    return result


def calc_ma_system(series):
    """均线系统（中长期用）"""
    ma20 = float(series.rolling(20).mean().iloc[-1])
    ma60 = float(series.rolling(60).mean().iloc[-1]) if len(series) >= 60 else None
    ma120 = float(series.rolling(120).mean().iloc[-1]) if len(series) >= 120 else None
    price = float(series.iloc[-1])

    trend = "震荡"
    if ma60 and ma120:
        if ma20 > ma60 > ma120:
            trend = "多头排列（长线看涨）"
        elif ma20 < ma60 < ma120:
            trend = "空头排列（长线看跌）"
        else:
            trend = "均线粘合（方向不明）"
    elif ma60:
        trend = "偏多" if price > ma60 else "偏空"

    return {"ma20": round(ma20, 2), "ma60": round(ma60, 2) if ma60 else None,
            "ma120": round(ma120, 2) if ma120 else None, "trend": trend}


def calc_trend_strength(series):
    """趋势强度（上涨日占比）"""
    ret = series.pct_change().dropna()
    if len(ret) < 20:
        return 0
    up_days = (ret > 0).rolling(20).sum().iloc[-1]
    return round(float(up_days) / 20 * 100, 0)


def calc_adx(high, low, close, period=14):
    """ADX 趋势强度指标 - 区分趋势/震荡行情"""
    high = pd.Series(high).reset_index(drop=True)
    low = pd.Series(low).reset_index(drop=True)
    close = pd.Series(close).reset_index(drop=True)

    if len(close) < period * 2:
        return 20.0, "震荡"

    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    up_move = high - high.shift(1)
    down_move = low.shift(1) - low
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

    atr = tr.rolling(period).mean()
    plus_di = 100 * pd.Series(plus_dm).rolling(period).mean() / atr
    minus_di = 100 * pd.Series(minus_dm).rolling(period).mean() / atr

    di_diff = abs(plus_di - minus_di)
    di_sum = plus_di + minus_di
    dx = 100 * di_diff / di_sum.replace(0, np.nan)
    adx = dx.rolling(period).mean()

    adx_val = float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 20.0

    if adx_val > 50:
        regime = "强趋势"
    elif adx_val > 25:
        regime = "趋势"
    elif adx_val > 20:
        regime = "弱趋势"
    else:
        regime = "震荡"

    return round(adx_val, 1), regime


def calc_williams_r(high, low, close, period=14):
    """Williams %R - 超买超卖辅助指标"""
    hh = pd.Series(high).rolling(period).max()
    ll = pd.Series(low).rolling(period).min()
    close_s = pd.Series(close)
    wr = -100 * (hh - close_s) / (hh - ll).replace(0, np.nan)
    wr_val = float(wr.iloc[-1]) if not pd.isna(wr.iloc[-1]) else -50.0

    if wr_val > -20:
        signal = "超买"
    elif wr_val < -80:
        signal = "超卖"
    else:
        signal = "中性"

    return round(wr_val, 1), signal


def calc_ichimoku_signal(high, low, close):
    """一目均衡表简化信号 - 趋势+支撑阻力"""
    high_s = pd.Series(high)
    low_s = pd.Series(low)
    close_s = pd.Series(close)

    if len(close_s) < 52:
        return None

    tenkan = (high_s.rolling(9).max() + low_s.rolling(9).min()) / 2
    kijun = (high_s.rolling(26).max() + low_s.rolling(26).min()) / 2
    senkou_a = (tenkan + kijun) / 2
    senkou_b = (high_s.rolling(52).max() + low_s.rolling(52).min()) / 2

    price = float(close_s.iloc[-1])
    cloud_top = float(max(senkou_a.iloc[-1], senkou_b.iloc[-1]))
    cloud_bottom = float(min(senkou_a.iloc[-1], senkou_b.iloc[-1]))
    tenkan_val = float(tenkan.iloc[-1])
    kijun_val = float(kijun.iloc[-1])

    if price > cloud_top:
        trend = "多头（云上方）"
        score = 15
    elif price < cloud_bottom:
        trend = "空头（云下方）"
        score = -15
    else:
        trend = "震荡（云层内）"
        score = 0

    if tenkan_val > kijun_val:
        tk_signal = "转换线>基准线(多头)"
        score += 10
    else:
        tk_signal = "转换线<基准线(空头)"
        score -= 10

    return {
        "trend": trend, "tk_signal": tk_signal,
        "cloud_top": round(cloud_top, 2),
        "cloud_bottom": round(cloud_bottom, 2),
        "score_impact": score,
    }


# ==================== v1.3.0 智能建议引擎 ====================

def calc_dynamic_weights(macd_result, boll, atr, price):
    """根据市场环境动态调整指标权重"""
    weights = {
        "rsi": 1.0, "kdj": 1.0, "macd": 1.0,
        "bollinger": 1.0, "obv": 0.8, "fibonacci": 0.6,
    }

    boll_width = (boll["upper"] - boll["lower"]) / boll["middle"] * 100 if boll["middle"] != 0 else 5
    macd_hist = abs(macd_result.get("macd", 0))
    volatility = atr / price * 100 if price > 0 else 2

    is_trending = macd_hist > 0.5 and boll_width > 4
    is_ranging = boll_width < 3 and macd_hist < 0.3
    is_volatile = volatility > 3

    if is_trending:
        weights["macd"] = 1.5; weights["rsi"] = 0.7; weights["kdj"] = 0.7; weights["obv"] = 1.0
        regime = "趋势行情"
    elif is_ranging:
        weights["rsi"] = 1.4; weights["kdj"] = 1.4; weights["macd"] = 0.6
        regime = "震荡行情"
    elif is_volatile:
        for k in weights: weights[k] = 0.9
        regime = "高波动行情"
    else:
        regime = "常规行情"

    return weights, regime


def resolve_conflicts(signals):
    """处理信号冲突，分类多空信号并计算一致度"""
    bullish, bearish, neutral = [], [], []
    trend_keywords = ["MACD", "均线", "趋势", "周线", "布林"]

    for sig in signals:
        sl = sig.lower()
        is_bull = any(w in sl for w in ["超卖", "金叉", "多头", "底背离", "齐升", "上行", "偏多", "看涨"])
        is_bear = any(w in sl for w in ["超买", "死叉", "空头", "顶背离", "齐跌", "下行", "偏空", "看跌"])
        is_trend = any(k in sig for k in trend_keywords)

        if is_bull and not is_bear:
            bullish.append({"signal": sig, "is_trend": is_trend})
        elif is_bear and not is_bull:
            bearish.append({"signal": sig, "is_trend": is_trend})
        else:
            neutral.append(sig)

    total = len(bullish) + len(bearish)
    if total == 0:
        return {"bullish": bullish, "bearish": bearish, "neutral": neutral,
                "ratio": 0.5, "consensus": "无信号", "consensus_pct": 50}

    ratio = len(bullish) / total
    if ratio > 0.8 or ratio < 0.2:
        consensus_pct = max(ratio, 1 - ratio) * 100
        consensus = "高确信"
    elif ratio >= 0.5:
        consensus_pct = ratio * 100; consensus = "偏多"
    else:
        consensus_pct = (1 - ratio) * 100; consensus = "偏空"

    return {
        "bullish": bullish, "bearish": bearish, "neutral": neutral,
        "ratio": ratio, "consensus": consensus, "consensus_pct": round(consensus_pct, 0),
    }


def calc_confidence(score, signals, weights, conflict_result):
    """计算置信度评分"""
    consensus_pct = conflict_result["consensus_pct"]
    score_strength = min(abs(score) / 50 * 100, 100)
    signal_count_score = min(len(signals) / 8 * 100, 100)
    confidence = consensus_pct * 0.4 + score_strength * 0.3 + signal_count_score * 0.3

    if confidence > 75: level, emoji = "HIGH", "🟢"
    elif confidence > 50: level, emoji = "MEDIUM", "🟡"
    else: level, emoji = "LOW", "🔴"

    return {"level": level, "emoji": emoji, "pct": round(confidence, 0),
            "consensus": conflict_result["consensus"]}


def calc_sl_tp(price, atr, fib_levels, support_resistance, direction):
    """计算止损止盈价位"""
    if direction == "buy":
        sl_atr = round(price - 1.5 * atr, 2)
        sl_support = support_resistance.get("support1", sl_atr) if support_resistance else sl_atr
        sl = max(sl_atr, sl_support)
        if fib_levels:
            tp1 = max(round(price + 2.0 * atr, 2), fib_levels.get("38.2%", round(price + 2 * atr, 2)))
            tp2 = max(round(price + 3.0 * atr, 2), fib_levels.get("50.0%", round(price + 3 * atr, 2)))
        else:
            tp1 = round(price + 2.0 * atr, 2); tp2 = round(price + 3.0 * atr, 2)
        risk = price - sl; reward1 = tp1 - price; reward2 = tp2 - price
    else:
        sl_atr = round(price + 1.5 * atr, 2)
        sl_resist = support_resistance.get("resistance1", sl_atr) if support_resistance else sl_atr
        sl = min(sl_atr, sl_resist)
        if fib_levels:
            tp1 = min(round(price - 2.0 * atr, 2), fib_levels.get("38.2%", round(price - 2 * atr, 2)))
            tp2 = min(round(price - 3.0 * atr, 2), fib_levels.get("50.0%", round(price - 3 * atr, 2)))
        else:
            tp1 = round(price - 2.0 * atr, 2); tp2 = round(price - 3.0 * atr, 2)
        risk = sl - price; reward1 = price - tp1; reward2 = price - tp2

    if risk <= 0: return None
    return {
        "sl": sl, "tp1": tp1, "tp2": tp2,
        "risk_pct": round(risk / price * 100, 1),
        "reward1_pct": round(reward1 / price * 100, 1),
        "reward2_pct": round(reward2 / price * 100, 1),
        "rr1": round(reward1 / risk, 1), "rr2": round(reward2 / risk, 1),
        "tradable": round(reward1 / risk, 1) >= 2.0,
    }


def calc_position(confidence, price, sl, account_size=100000, contract_multiplier=1):
    """计算建议仓位"""
    if confidence["level"] == "LOW":
        return {"lots": 0, "reason": "置信度低，不建议开仓"}

    risk_pct = 0.02 if confidence["level"] == "HIGH" else 0.01
    dollar_risk = account_size * risk_pct
    per_lot_risk = abs(price - sl) * contract_multiplier

    if per_lot_risk <= 0:
        return {"lots": 0, "reason": "止损计算异常"}

    lots = max(1, int(dollar_risk / per_lot_risk))
    return {"lots": lots, "risk_pct": risk_pct * 100,
            "dollar_risk": round(dollar_risk, 0), "per_lot_risk": round(per_lot_risk, 2)}


# ==================== 短期分析（1天~1周）====================

def analyze_short_term(symbol, days=3, batch_data=None):
    """短期分析，支持批量数据传入避免重复下载"""
    if batch_data is not None and symbol in batch_data:
        data = batch_data[symbol].dropna()
    else:
        import yfinance as yf
        data = yf.download(symbol, period="3mo", interval="1d", progress=False)
        # 减少延迟，因为已经有缓存机制

    if data.empty or len(data) < 20:
        return None

    close = data["Close"].dropna() if "Close" in data else data.iloc[:, 0].dropna()
    high = data["High"].dropna() if "High" in data else close
    low = data["Low"].dropna() if "Low" in data else close

    price = float(close.iloc[-1])
    prev = float(close.iloc[-2]) if len(close) > 1 else price
    prev5 = float(close.iloc[-6]) if len(close) > 5 else prev
    change_1d = ((price - prev) / prev) * 100
    change_5d = ((price - prev5) / prev5) * 100

    rsi = calc_rsi(close)
    macd = calc_macd(close)
    boll = calc_bollinger(close)
    stoch = calc_stoch(high, low, close)
    atr = calc_atr(high, low, close)

    volume = data["Volume"].dropna() if "Volume" in data else None
    obv = calc_obv(close, volume) if volume is not None and len(volume) > 5 else None
    fib = calc_fibonacci(float(high.tail(30).max()), float(low.tail(30).min()), price)
    sr = calc_support_resistance(close, high, low, boll["upper"], boll["lower"], price)

    adx_val, adx_regime = calc_adx(high, low, close)
    williams_r, wr_signal = calc_williams_r(high, low, close)
    ichimoku = calc_ichimoku_signal(high, low, close)

    stop_loss = round(price - 1.5 * atr, 2)
    take_profit = round(price + 2.0 * atr, 2)
    if sr:
        stop_loss = min(stop_loss, sr["support1"])
        take_profit = max(take_profit, sr["resistance1"])

    score = 0
    signals = []

    if rsi < 25: score += 35; signals.append("RSI严重超卖")
    elif rsi < 35: score += 20; signals.append("RSI超卖")
    elif rsi > 75: score -= 35; signals.append("RSI严重超买")
    elif rsi > 65: score -= 20; signals.append("RSI超买")
    else: signals.append(f"RSI中性({rsi:.0f})")

    if stoch["signal"] == "超卖金叉": score += 30; signals.append("KDJ超卖金叉")
    elif stoch["signal"] == "金叉上行": score += 15; signals.append("KDJ金叉上行")
    elif stoch["signal"] == "超买死叉": score -= 30; signals.append("KDJ超买死叉")
    elif stoch["signal"] == "死叉下行": score -= 15; signals.append("KDJ死叉下行")

    if macd["signal"] == "金叉↗": score += 25; signals.append("MACD金叉")
    elif macd["signal"] == "多头": score += 10; signals.append("MACD多头")
    elif macd["signal"] == "死叉↘": score -= 25; signals.append("MACD死叉")
    elif macd["signal"] == "空头": score -= 10; signals.append("MACD空头")

    if "超卖" in boll["position"]: score += 20; signals.append("布林下轨")
    elif "超买" in boll["position"]: score -= 20; signals.append("布林上轨")

    if change_5d > 3: score += 10
    elif change_5d < -3: score -= 10

    if obv:
        score += obv["score_impact"]
        signals.append(obv["divergence"])

    if fib:
        score += fib["score_impact"]
        signals.append(f"Fib区间: {fib['zone']}")

    if adx_val > 50:
        if macd["signal"] in ("金叉↗", "多头"):
            score += 10
            signals.append(f"ADX={adx_val}(强趋势)+MACD共振")
        elif macd["signal"] in ("死叉↘", "空头"):
            score -= 10
            signals.append(f"ADX={adx_val}(强趋势)+MACD空头共振")
    elif adx_val < 20:
        signals.append(f"ADX={adx_val}(震荡市→RSI/KDJ优先)")
        if rsi < 30: score += 5
        elif rsi > 70: score -= 5

    if wr_signal == "超买" and rsi > 65:
        score -= 8
        signals.append(f"W%R={williams_r}+RSI={rsi:.0f}双超买")
    elif wr_signal == "超卖" and rsi < 35:
        score += 8
        signals.append(f"W%R={williams_r}+RSI={rsi:.0f}双超卖")
    elif wr_signal == "超买" and rsi < 50:
        signals.append(f"W%R超买但RSI未确认→分歧")
    elif wr_signal == "超卖" and rsi > 50:
        signals.append(f"W%R超卖但RSI未确认→分歧")

    if ichimoku:
        score += ichimoku["score_impact"]
        signals.append(f"一目: {ichimoku['trend']}")

    volatility = atr / price * 100
    pred_low = round(price * (1 - volatility * days / 100), 2)
    pred_high = round(price * (1 + volatility * days / 100), 2)

    if score >= 50: advice, action, strategy = "🟢🟢 强烈买入", "STRONG_BUY", f"今日逢低买入，目标${take_profit}"
    elif score >= 25: advice, action, strategy = "🟢 建议买入", "BUY", f"本周逢低建仓，目标${take_profit}"
    elif score >= 10: advice, action, strategy = "🟢 轻仓试探", "LIGHT_BUY", "小仓试探，观察1-2天"
    elif score <= -50: advice, action, strategy = "🔴🔴 强烈卖出", "STRONG_SELL", f"今日减仓，止损${stop_loss}"
    elif score <= -25: advice, action, strategy = "🔴 建议卖出", "SELL", f"本周减仓，止损${stop_loss}"
    elif score <= -10: advice, action, strategy = "🔴 轻仓减仓", "LIGHT_SELL", "减部分仓位观察"
    else: advice, action, strategy = "🟡 观望等待", "HOLD", "信号不明，等待1-2天"

    return {
        "price": round(price, 2), "change_1d": round(change_1d, 2), "change_5d": round(change_5d, 2),
        "rsi": round(rsi, 1), "macd": macd, "bollinger": boll, "stoch": stoch,
        "atr": round(atr, 2), "stop_loss": stop_loss, "take_profit": take_profit,
        "score": score, "signals": signals, "advice": advice, "action": action,
        "strategy": strategy, "pred_low": pred_low, "pred_high": pred_high,
        "volatility": round(volatility, 2),
        "obv": obv, "fibonacci": fib, "support_resistance": sr,
        "adx": adx_val, "adx_regime": adx_regime,
        "williams_r": williams_r, "wr_signal": wr_signal,
        "ichimoku": ichimoku,
    }


# ==================== 中长期分析（1月~6月）====================

def analyze_medium_long_term(symbol, batch_data=None):
    """中长期分析，支持批量数据传入"""
    if batch_data is not None and symbol in batch_data:
        data = batch_data[symbol].dropna()
    else:
        import yfinance as yf
        data = yf.download(symbol, period="1y", interval="1d", progress=False)
        # 减少延迟，因为已经有缓存机制

    if data.empty or len(data) < 60:
        return None

    close = data["Close"].dropna() if "Close" in data else data.iloc[:, 0].dropna()
    price = float(close.iloc[-1])
    prev_1m = float(close.iloc[-22]) if len(close) > 22 else price
    prev_3m = float(close.iloc[-66]) if len(close) > 66 else price
    prev_6m = float(close.iloc[-132]) if len(close) > 132 else price
    change_1m = ((price - prev_1m) / prev_1m) * 100
    change_3m = ((price - prev_3m) / prev_3m) * 100
    change_6m = ((price - prev_6m) / prev_6m) * 100

    ma = calc_ma_system(close)
    rsi = calc_rsi(close)
    macd = calc_macd(close)
    boll = calc_bollinger(close)
    trend_strength = calc_trend_strength(close)

    score = 0
    signals = []

    if "多头" in ma["trend"]: score += 30; signals.append("均线多头排列")
    elif "空头" in ma["trend"]: score -= 30; signals.append("均线空头排列")
    else: signals.append("均线粘合")

    if change_1m > 5: score += 15; signals.append(f"月涨{change_1m:+.1f}%")
    elif change_1m < -5: score -= 15; signals.append(f"月跌{change_1m:+.1f}%")

    if change_3m > 10: score += 15; signals.append(f"季涨{change_3m:+.1f}%")
    elif change_3m < -10: score -= 15; signals.append(f"季跌{change_3m:+.1f}%")

    if trend_strength > 65: score += 10; signals.append("上涨趋势强")
    elif trend_strength < 35: score -= 10; signals.append("下跌趋势强")

    if rsi < 35: score += 15; signals.append("RSI偏低(中期买入机会)")
    elif rsi > 65: score -= 15; signals.append("RSI偏高(中期注意回调)")

    if macd["signal"] in ("金叉↗", "多头"): score += 10
    elif macd["signal"] in ("死叉↘", "空头"): score -= 10

    if boll["pct"] < 20: score += 10; signals.append("价格处于低位区间")
    elif boll["pct"] > 80: score -= 10; signals.append("价格处于高位区间")

    if score >= 40: advice = "🟢 中长线看多，可分批建仓"
    elif score >= 15: advice = "🟢 中长线偏多，可持有观望"
    elif score <= -40: advice = "🔴 中长线看空，建议减仓"
    elif score <= -15: advice = "🔴 中长线偏空，谨慎持有"
    else: advice = "🟡 中长线方向不明，观望"

    recent_60 = close.tail(60)
    support = round(float(recent_60.min()), 2)
    resistance = round(float(recent_60.max()), 2)

    return {
        "price": round(price, 2),
        "change_1m": round(change_1m, 2), "change_3m": round(change_3m, 2),
        "change_6m": round(change_6m, 2),
        "ma": ma, "rsi": round(rsi, 1), "macd": macd,
        "trend_strength": trend_strength, "score": score,
        "signals": signals, "advice": advice,
        "support": support, "resistance": resistance,
    }


# ==================== 每日推送报告 ====================

def generate_daily_report(days=3):
    """生成每日推送报告：批量下载 → 短期为主 + 中长期补充"""
    horizon = f"{days}天"
    now = datetime.now()

    print("=" * 50)
    print(f"💰 石油黄金每日投资参考")
    print(f"📅 {now.strftime('%Y-%m-%d %H:%M')} | 短期{horizon} + 中长期")
    print("=" * 50)

    # v2.0: 数据源健康检查
    print("\n🔍 数据源健康状态:")
    manager = get_data_source_manager()
    healthy = manager.get_healthy_sources()
    print(f"   健康数据源: {', '.join(healthy) if healthy else '无'}")

    unique_symbols = list(set(info["symbol"] for info in INSTRUMENTS.values()))

    print("  批量下载数据...", flush=True)
    batch_3mo = batch_download(unique_symbols, period="3mo", interval="1d")
    # 减少延迟，因为已经有缓存机制
    batch_1y = batch_download(unique_symbols, period="1y", interval="1d")

    short_results = {}
    long_results = {}
    mtf_results = {}

    for name, info in INSTRUMENTS.items():
        sym = info["symbol"]
        mtf_results[name] = calc_multi_timeframe(sym, batch_3mo=batch_3mo, batch_1y=batch_1y)

    for name, info in INSTRUMENTS.items():
        sym = info["symbol"]
        print(f"  分析 {name}...", end=" ", flush=True)
        try:
            sr = analyze_short_term(sym, days, batch_data=batch_3mo)
            if sr:
                short_results[name] = {**info, **sr}
                lr = analyze_medium_long_term(sym, batch_data=batch_1y)
                if lr:
                    long_results[name] = {**info, **lr}
                print(f"${sr['price']:,.2f} ({sr['change_1d']:+.2f}%) {sr['advice']}")
            else:
                print("数据不足")
        except Exception as e:
            print(f"失败: {e}")

    if not short_results:
        print("❌ 未获取到数据")
        return

    lines = []

    lines.append(f"\n{'━' * 50}")
    lines.append(f"⚡ 一，今日操作摘要（短期{horizon}）")
    lines.append(f"{'━' * 50}")

    buys = {k: v for k, v in short_results.items() if "BUY" in v.get("action", "")}
    sells = {k: v for k, v in short_results.items() if "SELL" in v.get("action", "")}
    holds = {k: v for k, v in short_results.items() if v.get("action") == "HOLD"}

    if buys:
        lines.append(f"\n  🟢 买入: {', '.join(buys.keys())}")
        for n, r in buys.items():
            lines.append(f"     {n}: 现价${r['price']:,.2f} → 目标${r['take_profit']} 止损${r['stop_loss']}")
    if sells:
        lines.append(f"\n  🔴 卖出: {', '.join(sells.keys())}")
        for n, r in sells.items():
            lines.append(f"     {n}: 现价${r['price']:,.2f} → 止损${r['stop_loss']}")
    if holds:
        lines.append(f"\n  🟡 观望: {', '.join(holds.keys())}")

    gold_price = None
    oil_price = None
    for name, r in short_results.items():
        if "黄金期货" in name:
            gold_price = r["price"]
        elif "WTI" in name or "布伦特" in name:
            oil_price = r["price"]
    if gold_price is None:
        for name, r in short_results.items():
            if "黄金" in name:
                gold_price = r["price"]
                break
    if oil_price is None:
        for name, r in short_results.items():
            if "原油" in name:
                oil_price = r["price"]
                break
    gold_oil_ratio = calc_gold_oil_ratio(gold_price, oil_price) if gold_price and oil_price else None

    if gold_oil_ratio:
        lines.append(f"\n  ⚖️ 黄金/原油比率: {gold_oil_ratio['ratio']:.1f} - {gold_oil_ratio['level']}")
        lines.append(f"     （历史均值20-25，>30原油便宜/<15原油贵）")

    lines.append(f"\n  📏 多时间框架:")
    for name in INSTRUMENTS:
        mtf = mtf_results.get(name, {})
        w = mtf.get("weekly", "-")
        d = mtf.get("daily", "-")
        if w != "数据不足" or d != "数据不足":
            lines.append(f"     {name}: 周线{w} | {d}")

    lines.append(f"\n{'━' * 50}")
    lines.append(f"📊 二、短期分析（{horizon}，主报告）")
    lines.append(f"{'━' * 50}")

    for name, r in short_results.items():
        lines.append(f"\n  【{name}】({r['symbol']} · {r['type']})")
        lines.append(f"    💵 ${r['price']:,.2f} | 日{r['change_1d']:+.2f}% | 5日{r['change_5d']:+.2f}%")
        lines.append(f"    📈 RSI {r['rsi']} | KDJ K={r['stoch']['K']} D={r['stoch']['D']} ({r['stoch']['signal']})")
        lines.append(f"    📉 MACD {r['macd']['signal']} | 布林 {r['bollinger']['position']}")
        lines.append(f"    📏 {horizon}预测: ${r['pred_low']} ~ ${r['pred_high']} (波动{r['volatility']:.1f}%)")
        if r.get('obv'):
            lines.append(f"    📊 OBV: {r['obv']['divergence']}")
        if r.get('fibonacci'):
            lines.append(f"    🔮 Fib: {r['fibonacci']['zone']}")
        if r.get('support_resistance'):
            sr = r['support_resistance']
            lines.append(f"    📐 支撑: ${sr['support1']} | 阻力: ${sr['resistance1']}")
        lines.append(f"    🎯 {r['advice']} - {r['strategy']}")

    lines.append(f"\n{'━' * 50}")
    lines.append("📐 三、中长期趋势（参考）")
    lines.append(f"{'━' * 50}")

    for name, r in long_results.items():
        lines.append(f"\n  【{name}】")
        lines.append(f"    📊 月{r['change_1m']:+.2f}% | 季{r['change_3m']:+.2f}% | 半年{r['change_6m']:+.2f}%")
        lines.append(f"    📏 均线: {r['ma']['trend']} | 趋势强度: {r['trend_strength']:.0f}%")
        lines.append(f"    📐 支撑: ${r['support']} | 阻力: ${r['resistance']}")
        lines.append(f"    🎯 {r['advice']}")

    # ... (后续省略，与原版相同)

    report = "\n".join(lines)
    print(report)
    return report


def _analyze_instrument(instrument_name, period="90d", horizon=3):
    """
    分析单个金融工具（黄金/原油）
    返回技术指标和评分
    用于 report_text.py 生成双消息报告
    """
    try:
        # 找到对应的金融工具
        info = None
        for name, data in INSTRUMENTS.items():
            if instrument_name in name:
                info = data
                break
        
        if not info:
            return None
        
        # 获取数据
        from fetch_data import fetch_data
        raw_data = fetch_data(period=period)
        
        # 根据数据来源选择键
        if info.get("ak_key") and info.get("ak_key") in raw_data:
            data = raw_data[info.get("ak_key")]
        else:
            # 如果没有ak_key，尝试使用symbol
            symbol = info.get("symbol", "")
            if symbol == "AU0":
                data = raw_data.get("gold")
            elif symbol == "SC0":
                data = raw_data.get("wti")
            else:
                return None
        
        # 转换为DataFrame
        if not data or 'close' not in data:
            return None
            
        import pandas as pd
        from datetime import datetime
        dates = pd.to_datetime(data['date']) if 'date' in data else pd.date_range(end=datetime.now(), periods=len(data['close']), freq='D')
        df = pd.DataFrame({
            'Close': data['close'],
            'Open': data.get('open', data['close']),
            'High': data.get('high', data['close']),
            'Low': data.get('low', data['close']),
            'Volume': data.get('volume', [0]*len(data['close']))
        }, index=dates)
        
        if df is None or len(df) < 20:
            return None
        
        # 获取最新价格
        latest_price = df["Close"].iloc[-1]
        
        # 计算技术指标
        close = df["Close"]
        high = df["High"]
        low = df["Low"]
        
        rsi = calc_rsi(close)
        macd = calc_macd(close)
        boll = calc_bollinger(close)
        kdj = calc_stoch(high, low, close)
        
        # 计算综合评分
        tech_score = 0
        
        # 均线系统
        ma20 = close.rolling(20).mean().iloc[-1]
        ma60 = close.rolling(60).mean().iloc[-1] if len(close) >= 60 else None
        
        if ma60:
            if ma20 > ma60:
                tech_score += 20
            elif ma20 < ma60:
                tech_score -= 20
        
        # RSI
        if rsi < 30:
            tech_score += 15
        elif rsi > 70:
            tech_score -= 15
        
        # MACD
        if macd["signal"] in ("金叉↗", "多头"):
            tech_score += 10
        elif macd["signal"] in ("死叉↘", "空头"):
            tech_score -= 10
        
        # 布林带
        if boll["pct"] < 20:
            tech_score += 10
        elif boll["pct"] > 80:
            tech_score -= 10
        
        # 信号标签
        if tech_score >= 60:
            signal_label = "建议买入"
        elif tech_score >= 40:
            signal_label = "可考虑"
        elif tech_score >= 20:
            signal_label = "观望"
        else:
            signal_label = "建议回避"
        
        return {
            "score": tech_score,
            "tech_score": tech_score,
            # "macro_score": 50,  # 暂时注释掉硬编码的宏观评分
            "signal_label": signal_label,
            "latest": latest_price
        }
        
    except Exception as e:
        print(f"    [_analyze_instrument] 分析 {instrument_name} 失败: {e}")
        return None


if __name__ == "__main__":
    generate_daily_report(3)