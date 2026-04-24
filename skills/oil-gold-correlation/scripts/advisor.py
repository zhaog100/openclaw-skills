#!/usr/bin/env python3
"""
石油黄金投资建议模块
短期（1天~1周）为主 + 中长期（1月~6月）补充

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) - AI Agent
"""

import warnings
warnings.filterwarnings('ignore')

import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from scipy import stats

# ===== 品种定义 =====
# 优先使用国际品种（yfinance），国内品种（akshare）作为辅助
INSTRUMENTS = {
    # 国际品种（主力，美元计价）
    "黄金期货": {"symbol": "GC=F", "type": "期货", "exchange": "COMEX", "currency": "USD", "source": "yfinance"},
    "白银期货": {"symbol": "SI=F", "type": "期货", "exchange": "COMEX", "currency": "USD", "source": "yfinance"},
    "WTI原油": {"symbol": "CL=F", "type": "期货", "exchange": "NYMEX", "currency": "USD", "source": "yfinance"},
    "布伦特原油": {"symbol": "BZ=F", "type": "期货", "exchange": "ICE", "currency": "USD", "source": "yfinance"},
    "美元指数": {"symbol": "DX-Y.NYB", "type": "指数", "exchange": "ICE", "currency": "USD", "source": "yfinance"},
    # 国内品种（辅助，人民币计价）
    "沪金期货": {"symbol": "AU0", "type": "期货", "exchange": "上海期货交易所", "currency": "CNY", "source": "akshare", "ak_key": "gold"},
    "沪银期货": {"symbol": "AG0", "type": "期货", "exchange": "上海期货交易所", "currency": "CNY", "source": "akshare", "ak_key": "silver"},
    "沪油期货": {"symbol": "SC0", "type": "期货", "exchange": "上海国际能源交易中心", "currency": "CNY", "source": "akshare", "ak_key": "wti"},
}


# ==================== 批量数据下载（避免限速）====================

def batch_download(symbols, period="3mo", interval="1d", max_retries=3):
    """批量下载数据，带重试"""
    import yfinance as yf
    for attempt in range(max_retries):
        try:
            data = yf.download(symbols, period=period, interval=interval,
                               group_by="ticker", progress=False)
            return data
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 3 * (attempt + 1)
                print(f"[重试] 批量下载第{attempt+1}次失败，{wait}秒后重试...")
                time.sleep(wait)
            else:
                print(f"❌ 批量下载失败: {e}")
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
            score_impact = 10  # 利多黄金
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

        # 判断当前价格在哪个 Fib 区间
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
            "score_impact": 5 if current_price <= fib_levels["38.2%"] else
                           -5 if current_price >= fib_levels["23.6%"] else 0,
        }
    except Exception:
        return None


def calc_support_resistance(close, high_series, low_series, boll_upper, boll_lower, current_price):
    """支撑/阻力位计算"""
    try:
        # 近期高低点
        recent_high = float(high_series.tail(30).max())
        recent_low = float(low_series.tail(30).min())

        # 整数关口（心理价位）
        magnitude = 10 ** (len(str(int(current_price))) - 1)
        unit = magnitude // 10 if magnitude >= 10 else 1
        psych_support = round((current_price // unit) * unit, 2)
        psych_resistance = round((current_price // unit + 1) * unit, 2)

        # 综合取最近的支撑/阻力
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
        # 周线趋势（从1年数据取周线）
        if batch_1y is not None and symbol in batch_1y:
            data_1y = batch_1y[symbol].dropna()
            if len(data_1y) >= 40:
                close_1y = data_1y["Close"] if "Close" in data_1y else data_1y.iloc[:, 0]
                # 简化周线：每5天取一次
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
        # 日线趋势（5日均线方向）
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
    """ADX 趋势强度指标 - 区分趋势/震荡行情
    ADX > 25: 趋势行情，趋势指标有效
    ADX < 20: 震荡行情，震荡指标有效
    ADX > 50: 强趋势，可重仓
    """
    high = pd.Series(high).reset_index(drop=True)
    low = pd.Series(low).reset_index(drop=True)
    close = pd.Series(close).reset_index(drop=True)

    if len(close) < period * 2:
        return 20.0, "震荡"

    # True Range
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # +DM / -DM
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

    # Smoothed
    atr = tr.rolling(period).mean()
    plus_di = 100 * pd.Series(plus_dm).rolling(period).mean() / atr
    minus_di = 100 * pd.Series(minus_dm).rolling(period).mean() / atr

    # DX → ADX
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
    """Williams %R - 超买超卖辅助指标
    %R > -20: 超买区
    %R < -80: 超卖区
    """
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
    """一目均衡表简化信号 - 趋势+支撑阻力
    价格在云上方: 多头
    价格在云下方: 空头
    """
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

    # 转换线 vs 基准线
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
    else:  # sell
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
        time.sleep(1)  # 避免限速

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
    stoch = calc_stoch(high, low, close)  # 标准KDJ用H/L/C
    atr = calc_atr(high, low, close)

    # === 新增指标 ===
    volume = data["Volume"].dropna() if "Volume" in data else None
    obv = calc_obv(close, volume) if volume is not None and len(volume) > 5 else None
    fib = calc_fibonacci(float(high.tail(30).max()), float(low.tail(30).min()), price)
    sr = calc_support_resistance(close, high, low, boll["upper"], boll["lower"], price)

    # === v1.5.4 增强指标 ===
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

    # === v1.5.4 ADX 趋势强度加权 ===
    if adx_val > 50:
        # 强趋势：趋势指标权重加大
        if macd["signal"] in ("金叉↗", "多头"):
            score += 10  # 强趋势中 MACD 多头加成
            signals.append(f"ADX={adx_val}(强趋势)+MACD共振")
        elif macd["signal"] in ("死叉↘", "空头"):
            score -= 10
            signals.append(f"ADX={adx_val}(强趋势)+MACD空头共振")
    elif adx_val < 20:
        # 震荡市：降低趋势指标权重，RSI/KDJ 更重要
        signals.append(f"ADX={adx_val}(震荡市→RSI/KDJ优先)")
        # 震荡市中 RSI 信号加权
        if rsi < 30:
            score += 5  # 震荡超卖更可靠
        elif rsi > 70:
            score -= 5

    # === v1.5.4 Williams %R 交叉验证 ===
    if wr_signal == "超买" and rsi > 65:
        score -= 8  # 双超买确认，加空
        signals.append(f"W%R={williams_r}+RSI={rsi:.0f}双超卖")
    elif wr_signal == "超卖" and rsi < 35:
        score += 8  # 双超卖确认，加多
        signals.append(f"W%R={williams_r}+RSI={rsi:.0f}双超卖")
    elif wr_signal == "超买" and rsi < 50:
        signals.append(f"W%R超买但RSI未确认→分歧")
    elif wr_signal == "超卖" and rsi > 50:
        signals.append(f"W%R超卖但RSI未确认→分歧")

    # === v1.5.4 一目均衡表 ===
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
        time.sleep(1)

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
    """v1.4.0 多数据源报告：akshare优先 → yfinance备用 → 机遇扫描 → 永不返回None"""
    horizon = f"{days}天"
    now = datetime.now()
    lines = []

    lines.append("=" * 50)
    lines.append("💰 石油黄金每日投资参考 v1.4.0")
    lines.append(f"📅 {now.strftime('%Y-%m-%d %H:%M')} | 短期{horizon} + 中长期")

    # ━━━ 数据获取：多源 + 永不失败 ━━━
    short_results = {}
    long_results = {}
    raw_data = {}
    source_report = []
    currencies = set()

    # --- 阶段1: akshare 国内品种（CNY，最稳定）---
    ak_names = {k: v for k, v in INSTRUMENTS.items() if v.get("source") == "akshare"}
    for name, info in ak_names.items():
        print(f"  [akshare] 获取 {name}...", end=" ", flush=True)
        try:
            ak_key = info.get("ak_key", "")
            df = _fetch_akshare_single(ak_key, "90d")
            if df is not None and len(df) >= 20:
                raw_data[name] = df
                sr = _analyze_from_df(name, info, df, days)
                if sr:
                    short_results[name] = sr
                    currencies.add(info["currency"])
                    source_report.append(f"✅ {name}({info['symbol']}) [{info['currency']}]")
                    print(f"✅ {info['currency']}{sr['price']:,.2f} ({sr['change_1d']:+.2f}%)")
                else:
                    print("分析失败")
            else:
                print("数据不足")
        except Exception as e:
            print(f"失败: {e}")

    # --- 阶段2: yfinance 国际品种（USD，可能被限流）---
    yf_available = _check_yfinance()
    yf_names = {k: v for k, v in INSTRUMENTS.items() if v.get("source") == "yfinance"}

    if yf_available:
        yf_symbols = {k: v["symbol"] for k, v in yf_names.items()}
        unique_syms = list(set(yf_symbols.values()))

        print("  [yfinance] 批量下载国际品种...", flush=True)
        batch_3mo = batch_download(unique_syms, period="3mo", interval="1d")
        time.sleep(1)
        batch_1y = batch_download(unique_syms, period="1y", interval="1d")

        for name, info in yf_names.items():
            sym = info["symbol"]
            print(f"  [yfinance] 分析 {name}...", end=" ", flush=True)
            try:
                sr = analyze_short_term(sym, days, batch_data=batch_3mo)
                if sr:
                    short_results[name] = {**info, **sr}
                    currencies.add(info["currency"])
                    if batch_3mo is not None and sym in batch_3mo:
                        raw_data[name] = batch_3mo[sym].dropna()
                    source_report.append(f"✅ {name}({sym}) [USD]")
                    lr = analyze_medium_long_term(sym, batch_data=batch_1y)
                    if lr:
                        long_results[name] = {**info, **lr}
                    print(f"${sr['price']:,.2f} ({sr['change_1d']:+.2f}%) {sr['advice']}")
                else:
                    print("数据不足")
                    source_report.append(f"⚠️ {name}({sym}) 数据不足")
            except Exception as e:
                print(f"失败: {e}")
                source_report.append(f"❌ {name}({sym}) 失败")
    else:
        for name in yf_names:
            source_report.append(f"⚠️ {name} — 国际品种因数据源限速暂缺")

    # --- 阶段3: 只要有任何品种成功就输出报告 ---
    if not short_results:
        lines.append("")
        lines.append("❌ 所有数据源均不可用，报告无法生成")
        lines.append("  • akshare 服务异常")
        lines.append("  • yfinance 被限流")
        lines.append("  • 建议稍后重试")
        report = "\n".join(lines)
        print(report)
        return report

    currency_str = "/".join(sorted(currencies)) if currencies else "N/A"
    lines.append(f"📊 数据来源: {currency_str} | {' | '.join(source_report)}")
    lines.append("=" * 50)

    # ━━━ 一、快速摘要 ━━━
    lines.append(f"\n{'━' * 50}")
    lines.append(f"⚡ 一、今日操作摘要（短期{horizon}）")
    lines.append(f"{'━' * 50}")

    buys = {k: v for k, v in short_results.items() if "BUY" in str(v.get("action", ""))}
    sells = {k: v for k, v in short_results.items() if "SELL" in str(v.get("action", ""))}
    holds = {k: v for k, v in short_results.items() if "HOLD" in str(v.get("action", "HOLD"))}

    if buys:
        lines.append(f"\n  🟢 买入: {', '.join(buys.keys())}")
        for n, r in buys.items():
            cur = r.get('currency', 'USD')
            sym = '¥' if cur == 'CNY' else '$'
            lines.append(f"     {n}: 现价{sym}{r.get('price', r.get('latest', 0)):,.2f} → 目标{sym}{r.get('take_profit', '-')} 止损{sym}{r.get('stop_loss', '-')}")
    if sells:
        lines.append(f"\n  🔴 卖出: {', '.join(sells.keys())}")
    if holds:
        lines.append(f"\n  🟡 观望: {', '.join(holds.keys())}")

    # 黄金-原油比率
    gold_price = None
    oil_price = None
    for name, r in short_results.items():
        if "黄金" in name and gold_price is None:
            gold_price = r.get("price", r.get("latest"))
        if ("原油" in name or "WTI" in name) and oil_price is None:
            oil_price = r.get("price", r.get("latest"))
    gold_oil_ratio = calc_gold_oil_ratio(gold_price, oil_price) if gold_price and oil_price else None
    if gold_oil_ratio:
        lines.append(f"\n  ⚖️ 黄金/原油比率: {gold_oil_ratio['ratio']:.1f} — {gold_oil_ratio['level']}")

    # ━━━ 二、短期详细 ━━━
    lines.append(f"\n{'━' * 50}")
    lines.append(f"📊 二、短期分析（{horizon}，主报告）")
    lines.append(f"{'━' * 50}")

    for name, r in short_results.items():
        cur = r.get('currency', 'USD')
        sym = '¥' if cur == 'CNY' else '$'
        price = r.get('price', r.get('latest', 0))
        lines.append(f"\n  【{name}】({r.get('symbol', '')} · {r.get('type', '')})")
        lines.append(f"    💵 {sym}{price:,.2f} | 日{r.get('change_1d', 0):+.2f}% | 5日{r.get('change_5d', 0):+.2f}%")
        if r.get('rsi'):
            lines.append(f"    📈 RSI {r['rsi']}")
        if r.get('stoch'):
            lines.append(f"    📈 KDJ K={r['stoch']['K']} D={r['stoch']['D']} ({r['stoch']['signal']})")
        if r.get('macd') and isinstance(r['macd'], dict):
            lines.append(f"    📉 MACD {r['macd']['signal']} | 布林 {r.get('bollinger', {}).get('position', '-')}")
        if r.get('volatility'):
            lines.append(f"    📏 预测: {sym}{r.get('pred_low', '-')} ~ {sym}{r.get('pred_high', '-')} (波动{r['volatility']:.1f}%)")
        if r.get('obv'):
            lines.append(f"    📊 OBV: {r['obv']['divergence']}")
        if r.get('fibonacci'):
            lines.append(f"    🔮 Fib: {r['fibonacci']['zone']}")
        if r.get('support_resistance'):
            sr = r['support_resistance']
            lines.append(f"    📐 支撑: {sym}{sr['support1']} | 阻力: {sym}{sr['resistance1']}")
        lines.append(f"    🎯 {r.get('advice', '-')}")

    # ━━━ 三、中长期 ━━━
    if long_results:
        lines.append(f"\n{'━' * 50}")
        lines.append("📐 三、中长期趋势（参考）")
        lines.append(f"{'━' * 50}")
        for name, r in long_results.items():
            lines.append(f"\n  【{name}】")
            lines.append(f"    📊 月{r.get('change_1m', 0):+.2f}% | 季{r.get('change_3m', 0):+.2f}%")
            lines.append(f"    📏 均线: {r.get('ma', {}).get('trend', '-')}")
            lines.append(f"    🎯 {r.get('advice', '-')}")

    # ━━━ 四、综合建议 ━━━
    gold_dict = {k: v for k, v in short_results.items() if "黄金" in k or "沪金" in k}
    silver_dict = {k: v for k, v in short_results.items() if "白银" in k or "沪银" in k}
    oil_dict = {k: v for k, v in short_results.items() if "原油" in k or "WTI" in k or "布伦特" in k or "沪油" in k}
    dxy_dict = {k: v for k, v in short_results.items() if "美元" in k}

    lines.append(f"\n{'━' * 50}")
    lines.append("🎯 四、综合建议")
    lines.append(f"{'━' * 50}")

    if gold_dict:
        gs = np.mean([v.get("score", 50) for v in gold_dict.values()])
        lines.append(f"\n  🥇 黄金: 短期评分{gs:+.0f}")
    if oil_dict:
        os_val = np.mean([v.get("score", 50) for v in oil_dict.values()])
        lines.append(f"\n  🛢️ 原油: 短期评分{os_val:+.0f}")
    if dxy_dict:
        dxy_r = list(dxy_dict.values())[0]
        dxy_dir = "偏强⚠️利空商品" if dxy_r.get("score", 0) > 10 else "偏弱✅利好商品" if dxy_r.get("score", 0) < -10 else "中性"
        lines.append(f"\n  💵 美元: {dxy_dir}")

    # ━━━ 五、国际形势 ━━━
    geo_score = 0
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from geopolitics import generate_geopolitical_section
        geo_lines, geo_score = generate_geopolitical_section()
        lines.extend(geo_lines)
    except Exception:
        lines.append(f"\n{'━' * 50}")
        lines.append("🌍 五、国际形势（获取失败）")

    # ━━━ 六、综合投资建议 ━━━
    lines.append(f"\n{'━' * 50}")
    lines.append("🎯 六、综合投资建议（智能引擎 v1.4.0）")
    lines.append(f"{'━' * 50}")

    asset_groups = [("🥇 黄金", gold_dict, 0.3), ("🥈 白银", silver_dict, 0.25), ("🛢️ 原油", oil_dict, 0.2)]

    for emoji_name, asset_dict, geo_weight in asset_groups:
        if not asset_dict:
            continue

        primary = list(asset_dict.values())[0]
        score = np.mean([v.get("score", 50) for v in asset_dict.values()])
        price = primary.get("price", primary.get("latest", 0))
        atr = primary.get("atr", 0)
        macd_r = primary.get("macd", {})
        boll = primary.get("bollinger", {})
        signals = primary.get("signals", [])
        fib = primary.get("fibonacci")
        sr_data = primary.get("support_resistance")

        if isinstance(macd_r, dict) and isinstance(boll, dict):
            weights, regime = calc_dynamic_weights(macd_r, boll, atr, price)
        else:
            weights, regime = {}, "常规行情"

        conflict = resolve_conflicts(signals) if signals else {"bullish": [], "bearish": [], "neutral": [], "ratio": 0.5, "consensus": "无信号", "consensus_pct": 50}

        final_score = score + geo_score * geo_weight
        if gold_oil_ratio and emoji_name.startswith("🥇"):
            final_score += gold_oil_ratio.get("score_impact", 0)

        confidence = calc_confidence(final_score, signals, weights, conflict)
        direction = "buy" if final_score >= 10 else "sell" if final_score <= -10 else None

        sltp = None
        if direction and sr_data and isinstance(macd_r, dict):
            fib_levels = fib["levels"] if fib and isinstance(fib, dict) else None
            sltp = calc_sl_tp(price, atr, fib_levels, sr_data, direction)

        sep = "═" * 42
        cur = primary.get('currency', 'USD')
        csym = '¥' if cur == 'CNY' else '$'

        lines.append(f"\n  {sep}")
        lines.append(f"  📊 综合投资建议：{emoji_name}")
        lines.append(f"  {sep}")
        lines.append(f"  🌊 市场环境：{regime}")
        if direction == "buy": lines.append(f"  🎯 方向：做多（买入）")
        elif direction == "sell": lines.append(f"  🎯 方向：做空（卖出）")
        else: lines.append(f"  🎯 方向：观望")
        lines.append(f"  📐 置信度：{confidence['emoji']} {confidence['level']} ({confidence['pct']:.0f}%)")
        lines.append(f"  📈 评分：{final_score:+.0f}/100")

        if conflict.get("bullish") or conflict.get("bearish"):
            lines.append(f"\n  📋 信号汇总：")
            bull_desc = "、".join(s["signal"] for s in conflict.get("bullish", []))
            bear_desc = "、".join(s["signal"] for s in conflict.get("bearish", [])[:4])
            if conflict.get("bullish"): lines.append(f"    看多({len(conflict['bullish'])})：{bull_desc}")
            if conflict.get("bearish"): lines.append(f"    看空({len(conflict['bearish'])})：{bear_desc}")
            lines.append(f"    一致度：{conflict.get('consensus_pct', 50):.0f}%")

        if direction and sltp:
            lines.append(f"\n  💰 操作建议：")
            lines.append(f"    入场：{csym}{price:,.2f} | 止损：{csym}{sltp['sl']:,.2f} | 目标：{csym}{sltp['tp1']:,.2f}")
            lines.append(f"    风险回报比：1:{sltp['rr1']:.1f}")
        elif not direction:
            lines.append(f"\n  💰 操作建议：观望等待")
        lines.append(f"  {sep}")

    # ━━━ 七、🔍 隐藏机遇扫描 ━━━
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from opportunity_scanner import OpportunityScanner

        scanner = OpportunityScanner()

        # 内外盘背离
        gold_domestic = raw_data.get("沪金期货")
        gold_intl = raw_data.get("黄金期货")
        if gold_domestic is not None and gold_intl is not None:
            scanner.scan_divergence(gold_domestic, gold_intl, "沪金", "国际金")
        oil_domestic = raw_data.get("沪油期货")
        oil_intl = raw_data.get("WTI原油")
        if oil_domestic is not None and oil_intl is not None:
            scanner.scan_divergence(oil_domestic, oil_intl, "沪油", "国际油")

        # 跨品种
        gold_any = raw_data.get("黄金期货") or raw_data.get("沪金期货")
        oil_any = raw_data.get("WTI原油") or raw_data.get("沪油期货")
        if gold_any is not None and oil_any is not None:
            scanner.scan_cross_commodity(gold_any, oil_any)

        # 量价背离
        for name, df in raw_data.items():
            scanner.scan_volume_price(df, name)

        opp_lines = scanner.generate_opportunity_report()
        opp_impact = scanner.get_total_score_impact()

        lines.append(f"\n{'━' * 50}")
        lines.append("🔍 七、隐藏机遇扫描（v1.4.0）")
        lines.append(f"{'━' * 50}")
        for ol in opp_lines:
            lines.append(ol)
        if opp_impact != 0:
            lines.append(f"  📊 综合影响: {opp_impact:+d}分")
    except Exception as e:
        lines.append(f"\n  ⚠️ 机遇扫描暂不可用: {e}")

    # ━━━ 风险提示 ━━━
    lines.append(f"\n{'━' * 50}")
    lines.append("⚠️ 风险提示")
    lines.append(f"{'━' * 50}")
    lines.append("  • 技术分析+地缘分析仅供参考，不构成投资建议")
    lines.append("  • 期货有杠杆风险，新手从ETF开始")
    lines.append("  • 单品种仓位 ≤ 10%，总仓位 ≤ 30%")
    lines.append("  • v1.4.0: 多源交叉验证 + 隐藏机遇扫描")

    report = "\n".join(lines)
    print(report)
    return report


def _check_yfinance():
    """检测 yfinance 是否可用"""
    try:
        import yfinance as yf
        t = yf.Ticker("AAPL")
        hist = t.history(period="5d")
        return hist is not None and not hist.empty
    except Exception:
        return False


def _analyze_from_df(name, info, df, days=3):
    """从 DataFrame 分析品种（统一入口，用于 akshare 数据）"""
    try:
        close = df["Close"] if "Close" in df.columns else df.iloc[:, 0]
        high = df["High"] if "High" in df.columns else close
        low = df["Low"] if "Low" in df.columns else close
        volume = df["Volume"] if "Volume" in df.columns else None

        if len(close) < 20:
            return None

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

        obv = calc_obv(close, volume) if volume is not None and len(volume) > 5 else None
        fib = calc_fibonacci(float(high.tail(30).max()), float(low.tail(30).min()), price)
        sr = calc_support_resistance(close, high, low, boll["upper"], boll["lower"], price)

        score = 0
        signals = []
        if rsi < 25: score += 35; signals.append("RSI严重超卖")
        elif rsi < 35: score += 20; signals.append("RSI超卖")
        elif rsi > 75: score -= 35; signals.append("RSI严重超买")
        elif rsi > 65: score -= 20; signals.append("RSI偏高")

        if macd["signal"] == "金叉↗": score += 25; signals.append("MACD金叉")
        elif macd["signal"] == "多头": score += 10; signals.append("MACD多头")
        elif macd["signal"] == "死叉↘": score -= 25; signals.append("MACD死叉")
        elif macd["signal"] == "空头": score -= 10; signals.append("MACD空头")

        if obv:
            score += obv.get("score_impact", 0)
            signals.append(obv.get("divergence", ""))

        volatility = atr / price * 100 if price > 0 else 0
        pred_low = round(price * (1 - volatility * days / 100), 2)
        pred_high = round(price * (1 + volatility * days / 100), 2)

        stop_loss = round(price - 1.5 * atr, 2)
        take_profit = round(price + 2.0 * atr, 2)
        if sr:
            stop_loss = min(stop_loss, sr["support1"])
            take_profit = max(take_profit, sr["resistance1"])

        if score >= 50: advice, action = "🟢🟢 强烈买入", "STRONG_BUY"
        elif score >= 25: advice, action = "🟢 建议买入", "BUY"
        elif score >= 10: advice, action = "🟢 轻仓试探", "LIGHT_BUY"
        elif score <= -50: advice, action = "🔴🔴 强烈卖出", "STRONG_SELL"
        elif score <= -25: advice, action = "🔴 建议卖出", "SELL"
        elif score <= -10: advice, action = "🔴 轻仓减仓", "LIGHT_SELL"
        else: advice, action = "🟡 观望等待", "HOLD"

        return {
            **info, "price": round(price, 2), "latest": round(price, 2),
            "change_1d": round(change_1d, 2), "change_5d": round(change_5d, 2),
            "rsi": round(rsi, 1), "macd": macd, "bollinger": boll, "stoch": stoch,
            "atr": round(atr, 2), "stop_loss": stop_loss, "take_profit": take_profit,
            "score": score, "signals": signals, "advice": advice, "action": action,
            "pred_low": pred_low, "pred_high": pred_high,
            "volatility": round(volatility, 2),
            "obv": obv, "fibonacci": fib, "support_resistance": sr,
        }
    except Exception:
        return None


if __name__ == "__main__OLD":
    import argparse
    parser = argparse.ArgumentParser(description="石油黄金每日投资参考")
    parser.add_argument("--days", type=int, default=3, help="短期预测天数")
    args = parser.parse_args()
    generate_daily_report(args.days)


# ==================== akshare 数据适配器 ====================

def _fetch_yfinance_single(symbol, period="90d"):
    """获取单个 yfinance 品种数据 - Ticker.history() 优先，download fallback"""
    try:
        import yfinance as yf
        # 方法 1: Ticker.history()（最稳定）
        try:
            t = yf.Ticker(symbol)
            df = t.history(period=period, interval="1d")
            if df is not None and len(df) >= 20:
                return df.dropna()
        except Exception:
            pass
        # 方法 2: download fallback
        try:
            df = yf.download(symbol, period=period, interval="1d", progress=False)
            if df is not None and len(df) >= 20:
                if isinstance(df.columns, pd.MultiIndex):
                    df = df[symbol]
                return df.dropna()
        except Exception:
            pass
    except Exception:
        pass
    return None


def _fetch_akshare_single(ak_key, period="90d"):
    """获取单个 akshare 品种数据"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from fetch_data import fetch_data
        raw = fetch_data(period=period)
        d = raw.get(ak_key, {})
        if d.get("close") and len(d["close"]) >= 20:
            return pd.DataFrame({
                "Open": d["open"], "High": d["high"],
                "Low": d["low"], "Close": d["close"],
                "Volume": d["volume"],
            }, index=pd.to_datetime(d["dates"]))
    except Exception as e:
        pass
    return None


def _analyze_instrument(name, period="90d", horizon=3):
    """分析单个品种：国际yfinance优先 → 国内akshare备用"""
    info = INSTRUMENTS.get(name, {})
    source = info.get("source", "yfinance")
    currency = info.get("currency", "USD")
    sym = info.get("symbol", "")
    ak_key = info.get("ak_key", "")

    # 获取数据：主力源优先，失败则尝试备用
    df = None
    actual_currency = currency

    if source == "yfinance":
        df = _fetch_yfinance_single(sym, period)
        if df is None and ak_key:
            df = _fetch_akshare_single(ak_key, period)
            actual_currency = "CNY"
    else:
        df = _fetch_akshare_single(ak_key, period)
        if df is None:
            df = _fetch_yfinance_single(sym, period)
            actual_currency = "USD"

    if df is None or len(df) < 20:
        return None

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]
    latest = float(close.iloc[-1])
    cur_sym = "¥" if actual_currency == "CNY" else "$"

    # RSI
    rsi = calc_rsi(close)
    # Bollinger
    boll = calc_bollinger(close)
    # KDJ
    stoch = calc_stoch(high, low, close)
    # ATR
    atr_val = calc_atr(high, low, close)
    # MACD
    macd_data = calc_macd(close)
    # OBV
    obv_data = calc_obv(close, volume)
    # Fibonacci
    try:
        fib_data = calc_fibonacci(high, low, latest)
    except:
        fib_data = None
    # Support/Resistance
    try:
        boll_lo = float(boll['lower']) if isinstance(boll, dict) else float(boll[0])
        boll_hi = float(boll['upper']) if isinstance(boll, dict) else float(boll[2])
        sr_data = calc_support_resistance(close, high, low, boll_hi, boll_lo, latest)
    except Exception as e:
        sr_data = None

    # === v1.5.4 增强指标 ===
    adx_val, adx_regime = calc_adx(high, low, close)
    williams_r, wr_signal = calc_williams_r(high, low, close)
    ichimoku = calc_ichimoku_signal(high, low, close)

    # 均线系统
    ma_system = calc_ma_system(close)

    # Scoring
    score = 50
    signals = []

    if rsi < 25: score += 35; signals.append("RSI严重超卖")
    elif rsi < 35: score += 20; signals.append("RSI超卖")
    elif rsi > 75: score -= 35; signals.append("RSI严重超买")
    elif rsi > 65: score -= 20; signals.append("RSI偏高")

    if boll is not None:
        if isinstance(boll, dict):
            if latest < boll["lower"]: score += 15; signals.append("跌破布林下轨")
            elif latest > boll["upper"]: score -= 15; signals.append("突破布林上轨")
        else:
            boll_lo, boll_mid, boll_hi = boll
            if latest < boll_lo: score += 15; signals.append("跌破布林下轨")
            elif latest > boll_hi: score -= 15; signals.append("突破布林上轨")

    if stoch is not None:
        if isinstance(stoch, dict):
            k, d = stoch["K"], stoch["D"]
        else:
            k, d = stoch
        if k < 20 and d < 20: score += 15; signals.append("KDJ超卖区")
        elif k > 80 and d > 80: score -= 15; signals.append("KDJ超卖区")
        if k > d and k < 50: score += 5; signals.append("KDJ金叉")
        elif k < d and k > 50: score -= 5; signals.append("KDJ死叉")

    if macd_data is not None:
        if isinstance(macd_data, dict):
            dif, dea, hist = macd_data["dif"], macd_data["dea"], macd_data["macd"]
        else:
            dif, dea, hist = macd_data
        if dif > dea and hist > 0: score += 10; signals.append("MACD金叉/多头")
        elif dif < dea and hist < 0: score -= 10; signals.append("MACD死叉/空头")

    if obv_data is not None:
        if isinstance(obv_data, dict):
            div = obv_data.get("divergence", "")
            if "底背离" in div: score += 10; signals.append(f"OBV: {div}")
            elif "顶背离" in div: score -= 10; signals.append(f"OBV: {div}")
            else: score += obv_data.get("score_impact", 0); signals.append(f"OBV: {div}")
        else:
            obv_val, obv_trend, divergence = obv_data
            if divergence == "底背离": score += 10; signals.append("OBV底背离（看涨）")
            elif divergence == "顶背离": score -= 10; signals.append("OBV顶背离（看跌）")

    # === v1.5.4 ADX 趋势强度加权 ===
    if adx_val > 50:
        if macd_data and isinstance(macd_data, dict):
            sig = macd_data.get("signal", "")
            if sig in ("金叉↗", "多头"): score += 8; signals.append(f"ADX={adx_val}(强趋势)+MACD多头共振")
            elif sig in ("死叉↘", "空头"): score -= 8; signals.append(f"ADX={adx_val}(强趋势)+MACD空头共振")
    elif adx_val < 20:
        signals.append(f"ADX={adx_val}(震荡市→RSI/KDJ优先)")
        if rsi < 30: score += 5
        elif rsi > 70: score -= 5

    # === v1.5.4 Williams %R 交叉验证 ===
    if wr_signal == "超买" and rsi > 65:
        score -= 6; signals.append(f"W%R={williams_r}+RSI双超买")
    elif wr_signal == "超卖" and rsi < 35:
        score += 6; signals.append(f"W%R={williams_r}+RSI双超卖")

    # === v1.5.4 一目均衡表 ===
    if ichimoku:
        score += ichimoku["score_impact"]
        signals.append(f"一目: {ichimoku['trend']}")

    # === 均线系统评分 ===
    if ma_system:
        ma_score = ma_system.get("score_impact", 0)
        score += ma_score
        signals.append(f"均线: {ma_system.get('trend', '')}")

    # Price changes
    changes = {}
    for d in [1, 3, 5, 10, 20]:
        if len(close) > d:
            chg = (close.iloc[-1] - close.iloc[-1-d]) / close.iloc[-1-d] * 100
            changes[f"{d}日涨跌"] = round(chg, 2)

    return {
        "score": max(0, min(100, score)),
        "signals": signals,
        "rsi": round(rsi, 1) if rsi else None,
        "boll": boll,
        "kdj": stoch,
        "atr": round(atr_val, 2) if atr_val else None,
        "macd": macd_data,
        "obv": obv_data,
        "fib": fib_data,
        "sr": sr_data,
        "latest": round(latest, 2),
        "changes": changes,
        "currency": actual_currency,
        "adx": adx_val,
        "adx_regime": adx_regime,
        "williams_r": williams_r,
        "wr_signal": wr_signal,
        "ichimoku": ichimoku,
        "ma_system": ma_system,
    }


def run_advisor_akshare(days=3):
    """使用 akshare 数据源的完整投资建议（替代主函数）"""
    now = datetime.now()

    print("=" * 50)
    print(f"💰 石油黄金每日投资参考")
    print(f"📅 {now.strftime('%Y-%m-%d %H:%M')} | 短期{days}天")
    print("=" * 50)

    results = {}
    for name in INSTRUMENTS:
        print(f"  分析 {name}...", end=" ", flush=True)
        try:
            r = _analyze_instrument(name, period="90d", horizon=days)
            if r:
                results[name] = r
                trend = "看多" if r["score"] > 60 else "看空" if r["score"] < 40 else "中性"
                print(f"✅ {trend}({r['score']}分) {r['currency']}{r['latest']}")
            else:
                print("❌ 数据不足")
        except Exception as e:
            print(f"❌ {e}")

    if not results:
        print("\n❌ 未获取到有效数据")
        return

    # Generate report for each instrument
    for name, r in results.items():
        cur = r.get("currency", "CNY")
        sym = cur == "CNY" and "¥" or "$"
        print(f"\n{'━' * 50}")
        print(f"📊 {name} 分析报告")
        print(f"{'━' * 50}")
        print(f"  当前价: {sym}{r['latest']}")
        if r.get("rsi"):
            print(f"  RSI(14): {r['rsi']}")
        if r.get("atr"):
            print(f"  ATR(14): {r['atr']}")
        if r.get("kdj"):
            kdj = r["kdj"]
            if isinstance(kdj, dict):
                print(f"  KDJ: K={kdj['K']:.1f} D={kdj['D']:.1f} J={kdj['J']:.1f} ({kdj.get('signal','')})")
            else:
                k, d = kdj
                print(f"  KDJ: K={k:.1f} D={d:.1f}")
        if r.get("macd"):
            m = r["macd"]
            if isinstance(m, dict):
                print(f"  MACD: DIF={m['dif']:.2f} DEA={m['dea']:.2f} HIST={m['macd']:.2f} ({m.get('signal','')})")
            else:
                dif, dea, hist = m
                print(f"  MACD: DIF={dif:.2f} DEA={dea:.2f} HIST={hist:.2f}")
        if r.get("boll"):
            b = r["boll"]
            if isinstance(b, dict):
                print(f"  布林带: {sym}{b['lower']:.2f} / {sym}{b['middle']:.2f} / {sym}{b['upper']:.2f} ({b.get('position','')})")
            else:
                lo, mid, hi = b
                print(f"  布林带: {sym}{lo:.2f} / {sym}{mid:.2f} / {sym}{hi:.2f}")
        if r.get("fib"):
            print(f"  Fibonacci 回撤位:")
            for level, price in r["fib"].items():
                print(f"    {level}: {sym}{price:.2f}")
        if r.get("sr"):
            print(f"  支撑/阻力:")
            for k2, v in r["sr"].items():
                if isinstance(v, (int, float)):
                    print(f"    {k2}: {sym}{v:.2f}")
                elif isinstance(v, list):
                    for vv in v:
                        if isinstance(vv, (int, float)):
                            print(f"    {k2}: {sym}{vv:.2f}")
        if r.get("changes"):
            print(f"  涨跌幅:")
            for k2, v in r["changes"].items():
                arrow = "📈" if v > 0 else "📉" if v < 0 else "➡️"
                print(f"    {arrow} {k2}: {v:+.2f}%")
        if r.get("signals"):
            print(f"  信号: {', '.join(r['signals'])}")

        # v1.5.4 增强指标
        if r.get("adx_regime"):
            print(f"  ADX: {r.get('adx', '?')} ({r['adx_regime']})")
        if r.get("wr_signal"):
            print(f"  Williams %R: {r.get('williams_r', '?')} ({r['wr_signal']})")
        if r.get("ichimoku"):
            ich = r["ichimoku"]
            print(f"  一目均衡: {ich['trend']} | {ich['tk_signal']}")
        if r.get("ma_system") and isinstance(r["ma_system"], dict):
            ms = r["ma_system"]
            print(f"  均线系统: {ms.get('trend', '')}")

        # 技术面评分
        score = r["score"]
        if score >= 70:
            advice = "🟢 偏多（考虑做多）"
        elif score >= 55:
            advice = "🟡 谨慎偏多"
        elif score >= 45:
            advice = "⚪ 中性观望"
        elif score >= 30:
            advice = "🟡 谨慎偏空"
        else:
            advice = "🔴 偏空（考虑做空或回避）"
        print(f"  技术面: {score}/100 {advice}")

    # 收集技术面评分
    tech_scores = {name: r["score"] for name, r in results.items()}

    # ━━━ 国际形势 ━━━
    risk_score = 0
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from geopolitics import generate_geopolitical_section
        geo_lines, risk_score = generate_geopolitical_section()
        for line in geo_lines:
            print(line)
    except Exception as e:
        print(f"  ⚠️ 国际形势不可用: {e}")

    # ━━━ FRED 宏观数据 ━━━
    macro_data = {}
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from fetch_fred import (
            analyze_macro_indicators, analyze_valuation_sentiment,
            market_comprehensive_assessment, format_macro_report,
            format_commodity_signals
        )
        macro_data["indicators"] = analyze_macro_indicators()
        macro_data["sentiment"] = analyze_valuation_sentiment()
        macro_data["assessment"] = market_comprehensive_assessment()
        for line in format_macro_report():
            print(line)
    except Exception as e:
        print(f"  ⚠️ FRED 宏观数据不可用: {e}")

    # ━━━ 最终建议 ━━━
    _print_final_recommendation(results, tech_scores, risk_score, macro_data)


def _print_final_recommendation(results, tech_scores, risk_score, macro_data):
    """最终买卖建议 - 表格风格"""
    
    # 获取宏观信号灯分数
    commodity_signals = {}
    try:
        from fetch_fred import analyze_macro_indicators, analyze_valuation_sentiment
        ind = macro_data.get("indicators") or analyze_macro_indicators()
        sent = macro_data.get("sentiment") or analyze_valuation_sentiment()
        commodity_signals = _calc_commodity_signal_scores(ind, sent)
    except:
        pass
    
    assessment = macro_data.get("assessment", {})
    market_score = assessment.get("score", 50)
    geo_base = risk_score if risk_score else 10
    
    print(f"\n{'━' * 50}")
    print(f"📊 投资决策仪表盘")
    print(f"{'━' * 50}")
    
    details = []  # 止损止盈详情
    
    for name, r in results.items():
        cur = r.get("currency", "CNY")
        sym = "¥" if cur == "CNY" else "$"
        tech = tech_scores.get(name, 50)
        is_gold = "黄金" in name or "gold" in name.lower() or "au" in name.lower() or "沪金" in name
        is_oil = "原油" in name or "oil" in name.lower() or "sc" in name.lower() or "沪油" in name
        icon = "🥇" if is_gold else "🛢️" if is_oil else "📊"
        short_name = "沪金" if is_gold else "沪油" if is_oil else name[:4]
        
        macro_signal = commodity_signals.get("gold" if is_gold else "oil" if is_oil else "neutral", 0)
        macro_combined = (market_score * 0.4 + (50 + macro_signal * 5) * 0.6)
        
        if is_gold:
            geo_adj = 50 + geo_base
        elif is_oil:
            geo_adj = 50 - geo_base * 0.5
        else:
            geo_adj = 50
        
        vix_val = 20
        try:
            vix_val = macro_data.get("sentiment", {}).get("VIXCLS", {}).get("value", 20)
        except:
            pass
        sentiment_score = max(0, 100 - vix_val * 2.5)
        
        final_score = tech * 0.40 + macro_combined * 0.35 + geo_adj * 0.15 + sentiment_score * 0.10
        final_score = max(0, min(100, final_score))
        
        # 等级
        if final_score >= 75:
            grade, action = "🟢🟢建议买入", "可建仓做多"
        elif final_score >= 60:
            grade, action = "🟡可以考虑", "轻仓试探，严格止损"
        elif final_score >= 40:
            grade, action = "⚪观望不动", "等待更明确信号"
        elif final_score >= 25:
            grade, action = "🟠建议回避", "不建议入场"
        else:
            grade, action = "🔴强烈回避", "远离或考虑做空"
        
        # 进度条：分段彩色（每格根据所在区间着色）
        bar_len = 10
        filled = max(1, int(final_score / 100 * bar_len))
        bar = ""
        for i in range(bar_len):
            pos_pct = (i + 0.5) / bar_len * 100  # 该格代表的百分比位置
            if i < filled:
                if pos_pct >= 75:
                    bar += "🟩"
                elif pos_pct >= 60:
                    bar += "🟨"
                elif pos_pct >= 40:
                    bar += "🟦"
                elif pos_pct >= 25:
                    bar += "🟧"
                else:
                    bar += "🟥"
            else:
                bar += "⬜"
        
        print(f"\n  {icon} {short_name} {sym}{r['latest']}  【{grade}】")
        print(f"  {bar} {final_score:.0f}/100")
        print(f"  技术面{tech} 宏观面{macro_combined:.0f} 信号灯{macro_signal:+d} 地缘{geo_base}/50")
        
        # 止损止盈
        if final_score >= 60 and r.get("atr"):
            atr = r["atr"]
            price = r["latest"]
            if isinstance(atr, (int, float)) and atr > 0:
                sl = price - 1.0 * atr
                tp = price + 2.0 * atr
                rr = (tp - price) / (price - sl) if price > sl else 0
                details.append(f"  {icon}{short_name}: 止损{sym}{sl:.0f} 目标{sym}{tp:.0f} 盈亏比1:{rr:.1f}")
        elif final_score < 40:
            details.append(f"  {icon}{short_name}: 已持仓止损{sym}{r['latest']*0.97:.0f}(-3%)")
    
    # 止损止盈详情
    if details:
        print(f"\n  {'─' * 46}")
        for d in details:
            print(d)
    
    # ━━━ 最终购买建议 ━━━
    print(f"\n{'━' * 50}")
    print(f"📌 最终购买建议")
    print(f"{'━' * 50}")
    for name, r in results.items():
        is_gold = "黄金" in name or "gold" in name.lower() or "au" in name.lower() or "沪金" in name
        is_oil = "原油" in name or "oil" in name.lower() or "sc" in name.lower() or "沪油" in name
        icon = "🥇" if is_gold else "🛢️" if is_oil else "📊"
        short_name = "沪金" if is_gold else "沪油" if is_oil else name[:4]
        cur = r.get("currency", "CNY")
        sym = "¥" if cur == "CNY" else "$"
        tech = tech_scores.get(name, 50)
        macro_signal = commodity_signals.get("gold" if is_gold else "oil" if is_oil else "neutral", 0)
        macro_combined = (market_score * 0.4 + (50 + macro_signal * 5) * 0.6)
        if is_gold:
            geo_adj = 50 + geo_base
        elif is_oil:
            geo_adj = 50 - geo_base * 0.5
        else:
            geo_adj = 50
        vix_val = 20
        try:
            vix_val = macro_data.get("sentiment", {}).get("VIXCLS", {}).get("value", 20)
        except:
            pass
        sentiment_score = max(0, 100 - vix_val * 2.5)
        final_score = tech * 0.40 + macro_combined * 0.35 + geo_adj * 0.15 + sentiment_score * 0.10
        final_score = max(0, min(100, final_score))
        
        if final_score >= 75:
            buy_action = "✅ 建议买入做多"
        elif final_score >= 60:
            buy_action = "⚠️ 可轻仓试探买入"
        elif final_score >= 40:
            buy_action = "❌ 不建议买入，观望"
        elif final_score >= 25:
            buy_action = "⛔ 回避，不要买入"
        else:
            buy_action = "🚫 强烈回避"
        
        print(f"\n  {icon} {short_name}（{sym}{r['latest']}）")
        print(f"  {buy_action}")
        
        # 给出具体理由
        reasons = []
        if tech >= 60:
            reasons.append("技术面偏多")
        elif tech < 40:
            reasons.append("技术面偏空")
        if macro_combined >= 60:
            reasons.append("宏观面利好")
        elif macro_combined < 40:
            reasons.append("宏观面利空")
        if macro_signal > 0:
            reasons.append("信号灯利多")
        elif macro_signal < 0:
            reasons.append("信号灯利空")
        if is_gold and geo_base > 30:
            reasons.append("地缘风险利好避险")
        if is_oil and geo_base > 40:
            reasons.append("地缘风险压制需求")
        cs = macro_data.get("indicators", {}).get("UMCSENT")
        if cs and cs["value"] < 65:
            if is_gold:
                reasons.append("消费信心低→避险利多")
            else:
                reasons.append("消费信心低→需求利空")
        
        if reasons:
            print(f"  理由：{'，'.join(reasons)}")
    
    # 风险提示
    alerts = []
    if geo_base > 30:
        alerts.append("地缘风险高")
    cs = macro_data.get("indicators", {}).get("UMCSENT")
    if cs and cs["value"] < 65:
        alerts.append(f"消费者信心{cs['value']:.0f}")
    vix = macro_data.get("sentiment", {}).get("VIXCLS")
    if vix and vix["value"] > 25:
        alerts.append(f"VIX={vix['value']:.0f}")
    rr = macro_data.get("indicators", {}).get("DFII10")
    if rr and rr["value"] > 2:
        alerts.append(f"实际利率{rr['value']:.1f}%")
    if alerts:
        print(f"\n  ⚠️ {' | '.join(alerts)}")
    
    print(f"\n  ⚠️ 仅供参考，不构成投资建议")
    print(f"{'━' * 50}")
    
    # ━━━ 报告总结 ━━━
    _print_summary(results, tech_scores, risk_score, macro_data, commodity_signals, geo_base, market_score)


def _calc_commodity_signal_scores(macro_indicators, sentiment_indicators):
    """计算黄金/原油宏观信号灯分数（复用 fetch_fred 逻辑）"""
    gold_score = 0
    oil_score = 0
    
    # 实际利率 → 黄金 (x2)
    real = macro_indicators.get("DFII10")
    if real:
        r = real["value"]
        gold_score += (-2 if r > 2.5 else -1 if r > 1.5 else 0 if r > 0 else 1 if r > -1 else 2) * 2
    
    # 美元
    dxy = sentiment_indicators.get("DTWEXBGS")
    if dxy:
        d = dxy["value"]
        s = -2 if d > 128 else -1 if d > 120 else 0 if d > 110 else 1
        gold_score += s
        oil_score += s
    
    # VIX → 黄金
    vix = sentiment_indicators.get("VIXCLS")
    if vix:
        v = vix["value"]
        gold_score += 2 if v > 35 else 1 if v > 25 else 0 if v > 15 else -1
    
    # 利差 → 黄金+原油
    spread = sentiment_indicators.get("T10Y2Y")
    if spread:
        sp = spread["value"]
        gold_score += 2 if sp < 0 else 1 if sp < 0.3 else 0
        oil_score += -2 if sp < 0 else -1 if sp < 0.3 else 1
    
    # 信用利差
    credit = sentiment_indicators.get("BAMLH0A0HYM2")
    if credit:
        c = credit["value"]
        sg = 2 if c > 5 else 1 if c > 3.5 else -1
        so = -2 if c > 5 else -1 if c > 3.5 else 1
        gold_score += sg
        oil_score += so
    
    # 消费者信心
    cs = macro_indicators.get("UMCSENT")
    if cs:
        c = cs["value"]
        sg = 2 if c < 60 else 1 if c < 70 else -1 if c > 90 else 0
        so = -2 if c < 60 else -1 if c < 70 else 1 if c > 90 else 0
        gold_score += sg
        oil_score += so
    
    # 工业生产 → 原油
    ip = macro_indicators.get("INDPRO")
    if ip:
        oil_score += 1 if ip["value"] > 103 else -1 if ip["value"] < 100 else 0
    
    return {"gold": gold_score, "oil": oil_score, "neutral": 0}


def _print_summary(results, tech_scores, risk_score, macro_data, commodity_signals, geo_base, market_score):
    """报告总结：5大板块 + 最终结论"""
    print(f"\n{'━' * 50}")
    print(f"📋 报告总结")
    print(f"{'━' * 50}")
    
    print(f"  1. ✅ 技术面分析（RSI/MACD/KDJ/布林带/支撑阻力）")
    print(f"  2. ✅ 国际形势（地缘风险{geo_base}/50）")
    print(f"  3. ✅ 美国宏观数据（3大指数+12项指标+信号灯）")
    print(f"  4. ✅ 投资决策仪表盘（进度条+四维评分）")
    print(f"  5. ✅ 最终购买建议（明确买不买+理由）")
    print(f"  {'─' * 46}")
    
    conclusions = []
    for name, r in results.items():
        is_gold = "黄金" in name or "gold" in name.lower() or "au" in name.lower() or "沪金" in name
        is_oil = "原油" in name or "oil" in name.lower() or "sc" in name.lower() or "沪油" in name
        short = "沪金" if is_gold else "沪油" if is_oil else name[:4]
        icon = "🥇" if is_gold else "🛢️" if is_oil else "📊"
        tech = tech_scores.get(name, 50)
        macro_signal = commodity_signals.get("gold" if is_gold else "oil" if is_oil else "neutral", 0)
        macro_combined = (market_score * 0.4 + (50 + macro_signal * 5) * 0.6)
        if is_gold:
            geo_adj = 50 + geo_base
        elif is_oil:
            geo_adj = 50 - geo_base * 0.5
        else:
            geo_adj = 50
        vix_val = 20
        try:
            vix_val = macro_data.get("sentiment", {}).get("VIXCLS", {}).get("value", 20)
        except:
            pass
        sentiment_score = max(0, 100 - vix_val * 2.5)
        final_score = tech * 0.40 + macro_combined * 0.35 + geo_adj * 0.15 + sentiment_score * 0.10
        final_score = max(0, min(100, final_score))
        
        if final_score >= 75:
            action = "建议买入"
        elif final_score >= 60:
            action = "可轻仓"
        elif final_score >= 40:
            action = "观望"
        elif final_score >= 25:
            action = "回避"
        else:
            action = "强烈回避"
        
        conclusions.append(f"{icon}{short}{final_score:.0f}分{action}")
    
    print(f"  结论：{'，'.join(conclusions)}")
    print(f"{'━' * 50}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=3)
    args = parser.parse_args()
    run_advisor_akshare(days=args.days)
