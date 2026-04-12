#!/usr/bin/env python3
"""
石油黄金投资建议模块
短期（1天~1周）为主 + 中长期（1月~6月）补充

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) — AI Agent
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
INSTRUMENTS = {
    "黄金期货": {"symbol": "GC=F", "type": "期货", "exchange": "COMEX"},
    "黄金ETF": {"symbol": "GLD", "type": "ETF", "exchange": "NYSE"},
    "WTI原油期货": {"symbol": "CL=F", "type": "期货", "exchange": "NYMEX"},
    "布伦特原油期货": {"symbol": "BZ=F", "type": "期货", "exchange": "ICE"},
    "原油ETF": {"symbol": "USO", "type": "ETF", "exchange": "NYSE"},
    "美元指数": {"symbol": "DX-Y.NYB", "type": "指数", "exchange": "ICE"},
    "白银期货": {"symbol": "SI=F", "type": "期货", "exchange": "COMEX"},
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

    stop_loss = round(price - 1.5 * atr, 2)
    take_profit = round(price + 2.0 * atr, 2)

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
    """生成每日推送报告：批量下载 → 短期为主 + 中长期补充"""
    horizon = f"{days}天"
    now = datetime.now()

    print("=" * 50)
    print(f"💰 石油黄金每日投资参考")
    print(f"📅 {now.strftime('%Y-%m-%d %H:%M')} | 短期{horizon} + 中长期")
    print("=" * 50)

    # 去重品种列表
    unique_symbols = list(set(info["symbol"] for info in INSTRUMENTS.values()))

    # 批量下载（短期3mo + 长期1y）
    print("  批量下载数据...", flush=True)
    batch_3mo = batch_download(unique_symbols, period="3mo", interval="1d")
    time.sleep(2)
    batch_1y = batch_download(unique_symbols, period="1y", interval="1d")

    short_results = {}
    long_results = {}

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

    # ===== 一、快速摘要 =====
    lines.append(f"\n{'━' * 50}")
    lines.append(f"⚡ 一、今日操作摘要（短期{horizon}）")
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

    # ===== 二、短期详细 =====
    lines.append(f"\n{'━' * 50}")
    lines.append(f"📊 二、短期分析（{horizon}，主报告）")
    lines.append(f"{'━' * 50}")

    for name, r in short_results.items():
        lines.append(f"\n  【{name}】({r['symbol']} · {r['type']})")
        lines.append(f"    💵 ${r['price']:,.2f} | 日{r['change_1d']:+.2f}% | 5日{r['change_5d']:+.2f}%")
        lines.append(f"    📈 RSI {r['rsi']} | KDJ K={r['stoch']['K']} D={r['stoch']['D']} ({r['stoch']['signal']})")
        lines.append(f"    📉 MACD {r['macd']['signal']} | 布林 {r['bollinger']['position']}")
        lines.append(f"    📏 {horizon}预测: ${r['pred_low']} ~ ${r['pred_high']} (波动{r['volatility']:.1f}%)")
        lines.append(f"    🎯 {r['advice']} — {r['strategy']}")

    # ===== 三、中长期 =====
    lines.append(f"\n{'━' * 50}")
    lines.append("📐 三、中长期趋势（参考）")
    lines.append(f"{'━' * 50}")

    for name, r in long_results.items():
        lines.append(f"\n  【{name}】")
        lines.append(f"    📊 月{r['change_1m']:+.2f}% | 季{r['change_3m']:+.2f}% | 半年{r['change_6m']:+.2f}%")
        lines.append(f"    📏 均线: {r['ma']['trend']} | 趋势强度: {r['trend_strength']:.0f}%")
        lines.append(f"    📐 支撑: ${r['support']} | 阻力: ${r['resistance']}")
        lines.append(f"    🎯 {r['advice']}")

    # ===== 四、综合建议 =====
    lines.append(f"\n{'━' * 50}")
    lines.append("🎯 四、综合建议")
    lines.append(f"{'━' * 50}")

    gold_dict = {k: v for k, v in short_results.items() if "黄金" in k}
    oil_dict = {k: v for k, v in short_results.items() if "原油" in k or "USO" in k}
    silver_dict = {k: v for k, v in short_results.items() if "白银" in k}
    dxy_dict = {k: v for k, v in short_results.items() if "美元" in k}

    if gold_dict:
        gold_short_score = np.mean([v["score"] for v in gold_dict.values()])
        lines.append(f"\n  🥇 黄金: 短期评分{gold_short_score:+.0f}")
        if any("黄金" in k for k in long_results):
            gold_long_score = np.mean([long_results[k]["score"] for k in long_results if "黄金" in k])
            lines.append(f"         中长期评分{gold_long_score:+.0f}")
            if gold_short_score >= 20 and gold_long_score >= 15:
                lines.append("    → ⭐ 短中长共振看多！可重仓做多")
            elif gold_short_score >= 20:
                lines.append("    → 短期强势，中期待确认，逢低买入")
            elif gold_short_score <= -20:
                lines.append("    → 短期偏空，观望为主")

    if oil_dict:
        oil_short_score = np.mean([v["score"] for v in oil_dict.values()])
        lines.append(f"\n  🛢️ 原油: 短期评分{oil_short_score:+.0f}")
        if oil_short_score >= 20: lines.append("    → 短期看多，可轻仓做多")
        elif oil_short_score <= -20: lines.append("    → 短期偏空，观望")
        else: lines.append("    → 震荡，暂不操作")

    if silver_dict:
        silver_score = np.mean([v["score"] for v in silver_dict.values()])
        lines.append(f"\n  🪙 白银: 短期评分{silver_score:+.0f}")

    if dxy_dict:
        dxy_r = list(dxy_dict.values())[0]
        dxy_dir = "偏强⚠️利空商品" if dxy_r["score"] > 10 else "偏弱✅利好商品" if dxy_r["score"] < -10 else "中性"
        lines.append(f"\n  💵 美元: {dxy_dir}")

    # ===== 五、国际形势 =====
    try:
        from geopolitics import generate_geopolitical_section
        geo_lines, geo_score = generate_geopolitical_section()
        lines.extend(geo_lines)
    except Exception:
        lines.append(f"\n{'━' * 50}")
        lines.append("🌍 五、国际形势（获取失败）")
        geo_score = 0

    # ===== 六、最终建议 =====
    lines.append(f"\n{'━' * 50}")
    lines.append("🎯 六、最终建议（技术面 + 地缘面）")
    lines.append(f"{'━' * 50}")

    if gold_dict:
        gs = np.mean([v["score"] for v in gold_dict.values()])
        final_gold = gs + geo_score * 0.3
        lines.append(f"\n  🥇 黄金最终评分: {final_gold:+.0f} (技术{gs:+.0f} + 地缘{geo_score*0.3:+.0f})")
        if final_gold >= 30:
            lines.append("    → ⭐ 技术面+地缘面共振！强烈做多黄金")
        elif final_gold >= 15:
            lines.append("    → ✅ 做多黄金，地缘风险提供额外支撑")
        elif final_gold >= 0:
            lines.append("    → 📊 黄金中性偏多，地缘风险提供底部支撑")
        else:
            lines.append("    → ⚠️ 黄金偏空，但地缘风险可能限制跌幅")

    if oil_dict:
        os_score = np.mean([v["score"] for v in oil_dict.values()])
        final_oil = os_score + geo_score * 0.2
        lines.append(f"\n  🛢️ 原油最终评分: {final_oil:+.0f} (技术{os_score:+.0f} + 地缘{geo_score*0.2:+.0f})")
        if final_oil >= 25:
            lines.append("    → 做多原油，但注意高位波动")
        elif final_oil >= 0:
            lines.append("    → 原油震荡，地缘溢价存在")
        else:
            lines.append("    → 技术面偏空，但地缘溢价托底")

    # ===== 风险提示 =====
    lines.append(f"\n{'━' * 50}")
    lines.append("⚠️ 风险提示")
    lines.append(f"{'━' * 50}")
    lines.append("  • 技术分析 + 地缘分析仅供参考，不构成投资建议")
    lines.append("  • 地缘局势变化极快，建议关注实时新闻")
    lines.append("  • 期货有杠杆风险，新手从ETF开始")
    lines.append("  • 单品种仓位 ≤ 10%，总仓位 ≤ 30%")
    lines.append("  • 重大事件前观望，严守止损线")

    report = "\n".join(lines)
    print(report)
    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="石油黄金每日投资参考")
    parser.add_argument("--days", type=int, default=3, help="短期预测天数")
    args = parser.parse_args()
    generate_daily_report(args.days)
