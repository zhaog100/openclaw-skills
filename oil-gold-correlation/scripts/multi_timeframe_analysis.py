#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License
# Author: 小米粒 (Xiaomili) - AI Agent
# 版本: v3.3 | 石油黄金白银相关性分析
"""
多周期共振分析模块 — 黄金/白银/石油
采集 1周/1月/半年/1年 四个周期数据，进行趋势共振分析

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

# ===== 品种定义 =====
TIMEFRAME_SYMBOLS = {
    "gold": {
        "name": "黄金", "emoji": "🥇", "color": "🟡",
        "ak_key": "gold", "yf_symbol": "GC=F",
    },
    "silver": {
        "name": "白银", "emoji": "🥈", "color": "⚪",
        "ak_key": "silver", "yf_symbol": "SI=F",
    },
    "oil": {
        "name": "原油", "emoji": "🛢️", "color": "🟢",
        "ak_key": "wti", "yf_symbol": "CL=F",
    },
}

# 四个分析周期
TIMEFRAMES = {
    "1w": {"label": "1周", "period": "7d", "days": 7, "weight": 1.0},
    "1m": {"label": "1月", "period": "30d", "days": 30, "weight": 1.5},
    "6m": {"label": "半年", "period": "180d", "days": 180, "weight": 2.0},
    "1y": {"label": "1年", "period": "1y", "days": 365, "weight": 2.5},
}


# ===== 数据获取 =====

def _fetch_akshare_single(ak_key, period="1y"):
    """akshare 获取单个品种"""
    import akshare as ak
    try:
        from config import CACHE_DIR
    except ImportError:
        from pathlib import Path
        CACHE_DIR = Path("/tmp/oil-gold-cache")

    cache_key = f"mta_{ak_key}_{period}"
    cache_file = CACHE_DIR / f"{cache_key}.pkl"
    if cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime
        if age < 3600:
            try:
                import pickle
                with open(cache_file, "rb") as f:
                    return pickle.load(f)
            except:
                pass

    info_map = {
        "gold": {"symbol": "AU0", "futures_key": "gold"},
        "silver": {"symbol": "AG0", "futures_key": "silver"},
        "wti": {"symbol": "SC0", "futures_key": "wti"},
    }
    info = info_map.get(ak_key)
    if not info:
        return None

    try:
        now = datetime.now()
        period_map = {"7d": 7, "30d": 30, "180d": 180, "1y": 365}
        days = period_map.get(period, 365)
        start_date = (now - timedelta(days=days + 5)).strftime("%Y%m%d")
        end_date = now.strftime("%Y%m%d")

        df = ak.futures_main_sina(
            symbol=info["symbol"],
            start_date=start_date,
            end_date=end_date,
        )
        if df is None or len(df) < 3:
            return None

        # 标准化列名
        col_map = {}
        for col in df.columns:
            cl = col.lower()
            if "date" in cl or "日期" in cl:
                col_map[col] = "date"
            elif "open" in cl or "开盘" in cl:
                col_map[col] = "Open"
            elif "high" in cl or "最高" in cl:
                col_map[col] = "High"
            elif "low" in cl or "最低" in cl:
                col_map[col] = "Low"
            elif "close" in cl or "收盘" in cl:
                col_map[col] = "Close"
            elif "volume" in cl or "成交量" in cl:
                col_map[col] = "Volume"
        df = df.rename(columns=col_map)

        # 确保数值列
        for c in ["Open", "High", "Low", "Close", "Volume"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").reset_index(drop=True)

        df = df.dropna(subset=["Close"])
        if len(df) < 3:
            return None

        # 缓存
        try:
            import pickle
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            with open(cache_file, "wb") as f:
                pickle.dump(df, f)
        except:
            pass

        return df
    except Exception as e:
        print(f"  ⚠️ akshare {ak_key}({period}) 失败: {e}")
        return None


def _fetch_yfinance_single(symbol, period="1y"):
    """yfinance 获取单个品种"""
    import yfinance as yf
    try:
        from config import CACHE_DIR
    except ImportError:
        from pathlib import Path
        CACHE_DIR = Path("/tmp/oil-gold-cache")

    cache_key = f"mta_yf_{symbol}_{period}"
    cache_file = CACHE_DIR / f"{cache_key}.pkl"
    if cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime
        if age < 3600:
            try:
                import pickle
                with open(cache_file, "rb") as f:
                    return pickle.load(f)
            except:
                pass

    try:
        t = yf.Ticker(symbol)
        df = t.history(period=period)
        if df is None or len(df) < 3:
            return None

        df = df.dropna(subset=["Close"])
        if len(df) < 3:
            return None

        try:
            import pickle
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            with open(cache_file, "wb") as f:
                pickle.dump(df, f)
        except:
            pass

        return df
    except Exception as e:
        print(f"  ⚠️ yfinance {symbol}({period}) 失败: {e}")
        return None


def fetch_multi_period(commodity_key, source="akshare"):
    """获取一个品种在四个周期的数据"""
    info = TIMEFRAME_SYMBOLS[commodity_key]
    results = {}

    for tf_key, tf_info in TIMEFRAMES.items():
        period = tf_info["period"]
        df = None

        if source == "akshare":
            df = _fetch_akshare_single(info["ak_key"], period)
            if df is None:
                df = _fetch_yfinance_single(info["yf_symbol"], period)
        else:
            df = _fetch_yfinance_single(info["yf_symbol"], period)
            if df is None:
                df = _fetch_akshare_single(info["ak_key"], period)

        if df is not None and len(df) >= 3:
            results[tf_key] = df

        time.sleep(0.5)  # 避免限速

    return results


# ===== 单周期技术分析 =====

def calc_rsi(series, period=14):
    """RSI 指标"""
    if len(series) < period + 1:
        return None
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    val = float(rsi.iloc[-1])
    if np.isnan(val):
        return None
    return round(val, 1)


def calc_ma(series, period):
    """简单移动平均"""
    if len(series) < period:
        return None
    return round(float(series.rolling(period).mean().iloc[-1]), 2)


def calc_macd(series):
    """MACD"""
    if len(series) < 26:
        return None
    ema12 = series.ewm(span=12).mean()
    ema26 = series.ewm(span=26).mean()
    dif = ema12 - ema26
    dea = dif.ewm(span=9).mean()
    hist = (dif - dea) * 2

    dif_v = float(dif.iloc[-1])
    dea_v = float(dea.iloc[-1])
    hist_v = float(hist.iloc[-1])

    if len(dif) >= 2:
        dif_prev = float(dif.iloc[-2])
        dea_prev = float(dea.iloc[-2])
        if dif_v > dea_v and dif_prev <= dea_prev:
            signal = "金叉"
        elif dif_v < dea_v and dif_prev >= dea_prev:
            signal = "死叉"
        elif dif_v > dea_v:
            signal = "多头"
        else:
            signal = "空头"
    else:
        signal = "数据不足"

    return {
        "dif": round(dif_v, 2),
        "dea": round(dea_v, 2),
        "hist": round(hist_v, 2),
        "signal": signal,
    }


def calc_bollinger_position(series, period=20):
    """布林带位置 (0-100)"""
    if len(series) < period:
        return None
    ma = series.rolling(period).mean()
    std = series.rolling(period).std()
    upper = ma + 2 * std
    lower = ma - 2 * std
    price = float(series.iloc[-1])
    u, l = float(upper.iloc[-1]), float(lower.iloc[-1])
    if u == l:
        return 50.0
    pct = (price - l) / (u - l) * 100
    return round(max(0, min(100, pct)), 1)


def calc_volume_trend(volume, period=20):
    """量能趋势：当前量 vs 历史均量"""
    if len(volume) < period:
        return None
    avg = float(volume.rolling(period).mean().iloc[-1])
    cur = float(volume.iloc[-1])
    if avg == 0:
        return 100.0
    ratio = cur / avg
    return round(ratio * 100, 1)


def analyze_single_timeframe(df, tf_key):
    """对单个周期的数据做技术分析"""
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    latest = float(close.iloc[-1])
    n = len(close)

    # 涨跌幅（周期内）
    change_pct = round(float((close.iloc[-1] / close.iloc[0] - 1) * 100), 2)

    # 均线
    ma5 = calc_ma(close, 5)
    ma10 = calc_ma(close, 10)
    ma20 = calc_ma(close, 20)
    ma60 = calc_ma(close, 60) if n >= 60 else None

    # 均线趋势方向
    ma_trend = "—"
    if ma5 and ma10 and ma20:
        if ma5 > ma10 > ma20:
            ma_trend = "多头排列↗"
        elif ma5 < ma10 < ma20:
            ma_trend = "空头排列↘"
        else:
            ma_trend = "交叉整理↔"

    # 价格 vs 均线位置
    ma_signals = []
    if ma5 and latest > ma5:
        ma_signals.append("站上MA5")
    elif ma5 and latest < ma5:
        ma_signals.append("跌破MA5")
    if ma20 and latest > ma20:
        ma_signals.append("站上MA20")
    elif ma20 and latest < ma20:
        ma_signals.append("跌破MA20")
    if ma60 and latest > ma60:
        ma_signals.append("站上MA60")
    elif ma60 and latest < ma60:
        ma_signals.append("跌破MA60")

    # RSI
    rsi = calc_rsi(close)
    rsi_signal = "—"
    if rsi is not None:
        if rsi < 30:
            rsi_signal = "超卖🟢"
        elif rsi > 70:
            rsi_signal = "超买🔴"
        elif rsi < 45:
            rsi_signal = "偏弱🟡"
        elif rsi > 55:
            rsi_signal = "偏强🟡"

    # MACD
    macd = calc_macd(close)

    # 布林带位置
    boll_pos = calc_bollinger_position(close)
    boll_signal = "—"
    if boll_pos is not None:
        if boll_pos > 80:
            boll_signal = "接近上轨🔴"
        elif boll_pos < 20:
            boll_signal = "接近下轨🟢"
        else:
            boll_signal = f"中轨附近({boll_pos:.0f}%位)"

    # 量能趋势
    vol_trend = calc_volume_trend(volume)

    # 支撑/阻力（用布林带上下轨近似）
    support = None
    resistance = None
    if n >= 20:
        ma20_val = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        support = round(float(ma20_val.iloc[-1] - 2 * std20.iloc[-1]), 2)
        resistance = round(float(ma20_val.iloc[-1] + 2 * std20.iloc[-1]), 2)

    # 综合评分 (0-100, 50=中性)
    score = 50

    if rsi is not None:
        if rsi < 30:
            score += 15
        elif rsi < 40:
            score += 8
        elif rsi > 70:
            score -= 15
        elif rsi > 60:
            score -= 8

    if macd:
        if macd["signal"] == "金叉":
            score += 12
        elif macd["signal"] == "死叉":
            score -= 12
        elif macd["signal"] == "多头":
            score += 5
        elif macd["signal"] == "空头":
            score -= 5

    if ma_trend == "多头排列↗":
        score += 10
    elif ma_trend == "空头排列↘":
        score -= 10

    if boll_pos is not None:
        if boll_pos < 20:
            score += 8
        elif boll_pos > 80:
            score -= 8

    # 趋势方向判断
    if change_pct > 5:
        score += 8
    elif change_pct > 2:
        score += 4
    elif change_pct < -5:
        score -= 8
    elif change_pct < -2:
        score -= 4

    score = max(0, min(100, score))

    # 趋势标签
    if score >= 70:
        trend = "强势看多"
        trend_emoji = "🟢🟢"
    elif score >= 58:
        trend = "偏多"
        trend_emoji = "🟢"
    elif score >= 42:
        trend = "中性"
        trend_emoji = "⚪"
    elif score >= 30:
        trend = "偏空"
        trend_emoji = "🔴"
    else:
        trend = "强势看空"
        trend_emoji = "🔴🔴"

    return {
        "tf_key": tf_key,
        "latest": round(latest, 2),
        "change_pct": change_pct,
        "n_bars": n,
        "ma5": ma5, "ma10": ma10, "ma20": ma20, "ma60": ma60,
        "ma_trend": ma_trend,
        "ma_signals": ma_signals,
        "rsi": rsi, "rsi_signal": rsi_signal,
        "macd": macd,
        "boll_pos": boll_pos, "boll_signal": boll_signal,
        "vol_trend": vol_trend,
        "support": support, "resistance": resistance,
        "score": score,
        "trend": trend, "trend_emoji": trend_emoji,
    }


# ===== 多周期共振分析 =====

def multi_timeframe_resonance(commodity_key, source="akshare"):
    """
    对单个品种进行多周期共振分析
    返回: {
        "symbol": "gold",
        "name": "黄金",
        "timeframes": { "1w": {...}, "1m": {...}, "6m": {...}, "1y": {...} },
        "resonance": { "direction": "看多/看空/分歧", "strength": 0-100, "confidence": "高/中/低" },
        "prediction": { "short_term": "...", "mid_term": "..." },
    }
    """
    info = TIMEFRAME_SYMBOLS[commodity_key]

    # 获取四个周期数据
    period_data = fetch_multi_period(commodity_key, source)

    if not period_data:
        return None

    # 逐周期分析
    tf_results = {}
    for tf_key in TIMEFRAMES:
        if tf_key in period_data:
            tf_results[tf_key] = analyze_single_timeframe(period_data[tf_key], tf_key)

    if not tf_results:
        return None

    # ━━━ 共振计算 ━━━
    scores = [r["score"] for r in tf_results.values()]
    weights = [TIMEFRAMES[tf_key]["weight"] for tf_key in tf_results]

    # 加权平均分
    weighted_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)

    # 方向一致性
    bullish_count = sum(1 for s in scores if s >= 58)
    bearish_count = sum(1 for s in scores if s <= 42)
    neutral_count = len(scores) - bullish_count - bearish_count

    total = len(scores)
    if total == 0:
        return None

    # 共振强度 (0-100)
    if bullish_count == total:
        resonance_strength = round(bullish_count / total * 100)
        direction = "看多共振"
    elif bearish_count == total:
        resonance_strength = round(bearish_count / total * 100)
        direction = "看空共振"
    elif bullish_count > bearish_count and bullish_count >= 3:
        resonance_strength = round(bullish_count / total * 80)
        direction = "偏多共振"
    elif bearish_count > bullish_count and bearish_count >= 3:
        resonance_strength = round(bearish_count / total * 80)
        direction = "偏空共振"
    else:
        resonance_strength = round(max(bullish_count, bearish_count) / total * 60)
        direction = "方向分歧"

    # 置信度
    if resonance_strength >= 80 and neutral_count == 0:
        confidence = "高"
    elif resonance_strength >= 60:
        confidence = "中"
    else:
        confidence = "低"

    # 共振方向emoji
    if "看多" in direction:
        res_emoji = "🟢"
    elif "看空" in direction:
        res_emoji = "🔴"
    else:
        res_emoji = "🟡"

    # ━━━ 预测 ━━━
    # 短期预测（基于1周+1月）
    short_tf = [tf_results[k] for k in ["1w", "1m"] if k in tf_results]
    if short_tf:
        short_avg = sum(t["score"] for t in short_tf) / len(short_tf)
        short_changes = [t["change_pct"] for t in short_tf]
        short_vol = sum(abs(c) for c in short_changes) / len(short_changes)

        if short_avg >= 65:
            short_pred = f"短期偏多，可能上涨{short_vol:.1f}%附近"
        elif short_avg <= 35:
            short_pred = f"短期偏空，可能下跌{short_vol:.1f}%附近"
        else:
            short_pred = "短期震荡，方向不明"
    else:
        short_pred = "数据不足"

    # 中期预测（基于半年+1年）
    mid_tf = [tf_results[k] for k in ["6m", "1y"] if k in tf_results]
    if mid_tf:
        mid_avg = sum(t["score"] for t in mid_tf) / len(mid_tf)
        mid_changes = [t["change_pct"] for t in mid_tf]

        if mid_avg >= 65:
            mid_pred = f"中期偏多，趋势向上"
        elif mid_avg <= 35:
            mid_pred = f"中期偏空，趋势向下"
        else:
            mid_pred = "中期横盘整理"
    else:
        mid_pred = "数据不足"

    return {
        "symbol": commodity_key,
        "name": info["name"],
        "emoji": info["emoji"],
        "timeframes": tf_results,
        "resonance": {
            "direction": direction,
            "strength": resonance_strength,
            "confidence": confidence,
            "emoji": res_emoji,
            "weighted_score": round(weighted_score, 1),
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "neutral_count": neutral_count,
            "total_timeframes": total,
        },
        "prediction": {
            "short_term": short_pred,
            "mid_term": mid_pred,
        },
    }


# ===== 报告格式化 =====

def format_mta_report(mta_results, currency="CNY"):
    """
    格式化多周期共振分析报告
    mta_results: list of multi_timeframe_resonance() 返回值
    返回: list of str (报告行)
    """
    sym = "¥" if currency == "CNY" else "$"
    lines = []

    lines.append(f"\n{'━' * 50}")
    lines.append(f"🔔 多周期共振分析（1周/1月/半年/1年）")
    lines.append(f"{'━' * 50}")

    for mta in mta_results:
        if mta is None:
            continue

        info = mta
        res = info["resonance"]
        pred = info["prediction"]

        # ━━━ 品种总览 ━━━
        lines.append(f"\n{info['emoji']} {info['name']} — {res['direction']} "
                      f"({res['strength']}% 强度, {res['confidence']}置信度)")
        lines.append(f"   加权评分: {res['weighted_score']}/100 "
                      f"| 多:{res['bullish_count']} 空:{res['bearish_count']} 中:{res['neutral_count']}")

        # ━━━ 各周期详情 ━━━
        lines.append(f"   {'周期':<6} {'趋势':<10} {'评分':<6} {'RSI':<8} {'MACD':<10} {'涨跌':<8}")
        lines.append(f"   {'—' * 54}")

        for tf_key, tf_info in TIMEFRAMES.items():
            if tf_key not in info["timeframes"]:
                continue
            tf = info["timeframes"][tf_key]
            tf_label = tf_info["label"]

            rsi_str = f"{tf['rsi']}" if tf.get("rsi") else "—"
            macd_str = tf["macd"]["signal"] if tf.get("macd") else "—"
            change_str = f"{tf['change_pct']:+.1f}%"

            lines.append(f"   {tf_label:<6} {tf['trend_emoji']} {tf['trend']:<8} "
                          f"{tf['score']:<6} {rsi_str:<8} {macd_str:<10} {change_str}")

        # ━━━ 关键价位 ━━━
        # 用1年数据的支撑阻力
        if "1y" in info["timeframes"]:
            tf1y = info["timeframes"]["1y"]
            if tf1y.get("support") and tf1y.get("resistance"):
                lines.append(f"   📍 支撑位: {sym}{tf1y['support']}  |  阻力位: {sym}{tf1y['resistance']}")

        # ━━━ 预测 ━━━
        lines.append(f"   📡 短期: {pred['short_term']}")
        lines.append(f"   📡 中期: {pred['mid_term']}")

        # ━━━ 操作建议 ━━━
        strength = res["strength"]
        direction = res["direction"]
        confidence = res["confidence"]

        if strength >= 80 and "看多" in direction:
            advice = "🟢 强烈看多 — 多周期共振向上，可考虑建仓做多"
        elif strength >= 80 and "看空" in direction:
            advice = "🔴 强烈看空 — 多周期共振向下，建议回避或做空"
        elif strength >= 60 and "看多" in direction:
            advice = "🟡 偏多 — 多数周期向上，轻仓试探，严格止损"
        elif strength >= 60 and "看空" in direction:
            advice = "🟡 偏空 — 多数周期向下，谨慎操作"
        elif "分歧" in direction:
            advice = "⚪ 方向分歧 — 各周期信号不一致，建议观望等待明确信号"
        else:
            advice = "⚪ 信号中性 — 观望为主"

        lines.append(f"   💡 建议: {advice}")

    # ━━━ 三品种共振对比 ━━━
    if len(mta_results) >= 2:
        lines.append(f"\n{'━' * 50}")
        lines.append(f"📊 三品种共振强度对比")
        lines.append(f"{'━' * 50}")

        valid = [m for m in mta_results if m is not None]
        # 按共振强度排序
        valid.sort(key=lambda x: x["resonance"]["strength"], reverse=True)

        for m in valid:
            res = m["resonance"]
            bar_len = int(res["strength"] / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(f"   {m['emoji']} {m['name']:<4} {bar} {res['strength']}% "
                          f"{res['direction']} ({res['confidence']})")

    return lines


# ===== 主入口 =====

def run_multi_timeframe_analysis(source="akshare"):
    """
    运行完整的多周期共振分析
    返回: (mta_results, report_lines)
    """
    print("🔍 开始多周期共振分析...")

    mta_results = []
    for key in TIMEFRAME_SYMBOLS:
        print(f"  分析 {TIMEFRAME_SYMBOLS[key]['name']}...", end=" ", flush=True)
        try:
            result = multi_timeframe_resonance(key, source)
            if result:
                mta_results.append(result)
                res = result["resonance"]
                print(f"✅ {res['direction']}({res['strength']}%)")
            else:
                print("❌ 数据不足")
        except Exception as e:
            print(f"❌ {e}")

    # 生成报告
    report_lines = format_mta_report(mta_results)

    return mta_results, report_lines


if __name__ == "__main__":
    results, lines = run_multi_timeframe_analysis()
    for line in lines:
        print(line)

    print(f"\n✅ 分析完成 | {len(results)}个品种 | "
          f"{sum(1 for r in results if r and r['resonance']['strength'] >= 60)}个强共振信号")

# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
