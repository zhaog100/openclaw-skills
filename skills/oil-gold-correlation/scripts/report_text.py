import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#!/usr/bin/env python3
"""
石油黄金投资参考 - 纯文本报告生成器 v3.4
优化：信号灯颜色更清晰 + 趋势箭头文字化 + 信息密度精简

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
版本: v3.4 | 石油黄金白银相关性分析
"""

import sys
from pathlib import Path
from datetime import datetime
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from advisor import _analyze_instrument, _fetch_akshare_single
from multi_timeframe_analysis import run_multi_timeframe_analysis

BAR_COLORS = {'red': '🟥', 'orange': '🟧', 'blue': '🟦', 'yellow': '🟨', 'green': '🟩', 'empty': '⬜'}

def score_to_bar(score, total=10):
    filled = int(round(total * score / 100))
    bar = []
    for i in range(total):
        if i < filled:
            seg_score = (i + 1) * (100 / total)
            if seg_score <= 25: bar.append(BAR_COLORS['red'])
            elif seg_score <= 40: bar.append(BAR_COLORS['orange'])
            elif seg_score <= 60: bar.append(BAR_COLORS['blue'])
            elif seg_score <= 75: bar.append(BAR_COLORS['yellow'])
            else: bar.append(BAR_COLORS['green'])
        else:
            bar.append(BAR_COLORS['empty'])
    return ''.join(bar)

def score_verdict(score):
    if score >= 75: return '建议买入', '🟢'
    elif score >= 60: return '可考虑', '🟡'
    elif score >= 40: return '观望', '⚪'
    elif score >= 25: return '回避', '🟠'
    else: return '强烈回避', '🔴'

def trend_arrow(score, rsi=50):
    if score >= 60 and rsi < 70: return '看涨📈'
    elif score <= 35 and rsi > 30: return '看跌📉'
    elif score >= 60 and rsi >= 70: return '看涨📈⚠️'
    elif score <= 35 and rsi <= 30: return '看跌📉⚠️'
    else: return '震荡➡️'



def _fetch_intl_gold():
    """国际现货金（美元/盎司）第二口径。GoldAPI 优先，失败降级，不硬造。"""
    import json
    try:
        import requests
        r = requests.get("https://api.gold-api.com/price/XAU",
                         headers={"User-Agent": "Mozilla/5.0 Chrome/120"}, timeout=12)
        if r.status_code == 200:
            d = r.json()
            price = d.get("price")
            chg = d.get("change") or d.get("changePercentage")
            chg_txt = f" 日{chg:+.2f}%" if isinstance(chg, (int, float)) else ""
            return {"ok": True, "price": price, "change": chg_txt,
                    "source": "GoldAPI", "updatedAt": d.get("updatedAt", "")}
        return {"ok": False, "err": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"ok": False, "err": str(e)[:40]}



def _calc_gold_spread(intl_price, gold_result):
    """内外价差：国际价换算人民币克价 vs 沪金，判贴水/升水。需汇率，取不到则降级。"""
    try:
        g_latest = None
        if isinstance(gold_result, dict):
            g_latest = gold_result.get("latest")
        if not g_latest:
            return ""
        # 汇率：走 GoldAPI 同源或取缓存；拉不到用 7.1 估算并标注
        usd_cny = _fetch_usd_cny()
        fx_note = "" if usd_cny.get("ok") else "（汇率估算）"
        rate = usd_cny.get("price", 7.1)
        per_gram_cny = intl_price / 31.1035 * rate   # 国际换算成 人民币/克
        diff = per_gram_cny - g_latest
        if abs(diff) < 1:
            return f"持平（换算≈¥{per_gram_cny:.0f}）{fx_note}"
        direction = "贴水" if diff > 0 else "升水"   # 国际换算>沪金=贴水(国内便宜)
        return f"{direction} ¥{abs(diff):.0f}/克（国际换算≈¥{per_gram_cny:.0f} vs 沪金¥{g_latest:.0f}）{fx_note}"
    except Exception:
        return ""


def _fetch_usd_cny():
    """美元兑人民币。多源，失败降级返回估算。"""
    try:
        import requests
        r = requests.get("https://open.er-api.com/v6/latest/USD",
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            d = r.json()
            cny = d.get("rates", {}).get("CNY")
            if cny:
                return {"ok": True, "price": cny}
        return {"ok": False, "price": 7.1}
    except Exception:
        return {"ok": False, "price": 7.1}
def fetch_data(ak_key, period="90d"):
    from config import CACHE_DIR
    import os, pickle
    cache_file = CACHE_DIR / f"{ak_key}_{period.replace('d', '')}.pkl"
    if cache_file.exists():
        mtime = os.path.getmtime(cache_file)
        if datetime.now().timestamp() - mtime < 300:
            try:
                with open(cache_file, 'rb') as f: return pickle.load(f)
            except: pass
    try:
        df = _fetch_akshare_single(ak_key, period)
        if df is not None and not df.empty:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, 'wb') as f: pickle.dump(df, f)
        return df
    except Exception as e:
        logger.info(f"[fetch_data] {ak_key} 失败: {e}")
        return None

def get_tech_summary(result):
    parts = []
    if result is None:
        return "数据不足"
    ma_sys = result.get('ma_system', {})
    if ma_sys:
        trend = ma_sys.get('trend', '')
        if trend: parts.append(f"均线:{trend}")
    macd = result.get('macd', {})
    if isinstance(macd, dict) and macd.get('signal'):
        parts.append(f"MACD{macd['signal']}")
    rsi = result.get('rsi', 0)
    if rsi > 70: parts.append(f"RSI={rsi:.0f}超买")
    elif rsi < 30: parts.append(f"RSI={rsi:.0f}超卖")
    elif rsi > 0: parts.append(f"RSI={rsi:.0f}")
    kdj = result.get('kdj', {})
    if isinstance(kdj, dict) and kdj.get('signal'):
        parts.append(f"KDJ{kdj['signal']}")
    obv = result.get('obv', {})
    if isinstance(obv, dict) and obv.get('divergence'):
        parts.append(obv['divergence'])
    boll = result.get('boll', {})
    if isinstance(boll, dict) and boll.get('position'):
        parts.append(boll['position'])
    adx = result.get('adx', 0)
    adx_regime = result.get('adx_regime', '')
    if adx > 25 and adx_regime:
        parts.append(f"ADX={adx:.0f}{adx_regime}")
    return " | ".join(parts) if parts else "数据不足"

def get_entry_exit(result, geo_risk=0):
    if result is None:
        return None, None, None
    latest = result.get('latest', 0)
    sr = result.get('sr', {})
    boll = result.get('boll', {})
    score = result.get('score', 50)
    support1 = sr.get('support1')
    support2 = sr.get('support2')
    resistance1 = sr.get('resistance1')
    if not support1 and isinstance(boll, dict): support1 = boll.get('lower')
    if not resistance1 and isinstance(boll, dict): resistance1 = boll.get('upper')
    if score >= 60:
        entry = support1 if support1 else latest * 0.98
        entry_note = f"回踩¥{entry:.0f}附近分批建仓"
    elif score >= 40:
        if support1:
            entry = support1 * 0.99
            entry_note = f"等¥{entry:.0f}附近再考虑"
        else:
            entry = latest * 0.97
            entry_note = f"等¥{entry:.0f}以下再考虑"
    else:
        if support2:
            entry = support2
            entry_note = f"极端情况¥{entry:.0f}附近可试探"
        elif support1:
            entry = support1 * 0.98
            entry_note = f"¥{entry:.0f}以下企稳可试探"
        else:
            entry = None
            entry_note = "信号未明，暂不建议入场"
    if support2:
        stop_loss = support2
    elif support1:
        stop_loss = support1 * 0.98
    elif isinstance(boll, dict) and boll.get('lower'):
        stop_loss = boll['lower']
    else:
        stop_loss = latest * 0.95
    if resistance1:
        target = resistance1
    elif isinstance(boll, dict) and boll.get('upper'):
        target = boll['upper']
    else:
        target = latest * 1.05
    return entry_note, stop_loss, target

def _compute_macro_label():
    """从 FRED 宏观数据动态计算宏观面评分"""
    try:
        from fetch_fred import (
            analyze_macro_indicators, analyze_valuation_sentiment,
            market_comprehensive_assessment
        )
        macro = analyze_macro_indicators()
        sentiment = analyze_valuation_sentiment()
        assessment = market_comprehensive_assessment()
        score = assessment.get('score', 50)
        if score >= 65:
            return '偏多'
        elif score >= 45:
            return '中性'
        else:
            return '偏空'
    except Exception:
        return '⏳无数据'


def generate_report():
    import signal
    class ReportTimeout(Exception):
        pass
    def timeout_handler(signum, frame):
        raise ReportTimeout("报告生成超时（300秒）")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(300)  # 5分钟超时
    
    try:
        _generate_report_inner()
    except ReportTimeout:
        logger.info("\n⚠️ 报告生成超时，输出缓存数据...")
        _generate_report_cached()
    finally:
        signal.alarm(0)

def _generate_report_inner():
    """报告生成主逻辑（带超时保护）"""
    now = datetime.now()
    lines = []

    # ========== 顶部摘要卡（优化：信号灯颜色+分数独立行） ==========
    lines.append(f'📊 石油黄金投资参考 {now.strftime("%Y-%m-%d %H:%M")}')
    lines.append('')

    gold_result = _analyze_instrument('沪金期货', period="90d", horizon=3)
    silver_result = _analyze_instrument('沪银期货', period="90d", horizon=3)
    oil_result = _analyze_instrument('沪油期货', period="90d", horizon=3)

    gold_score = gold_result.get('score', 50) if gold_result else 50
    silver_score = silver_result.get('score', 50) if silver_result else 50
    oil_score = oil_result.get('score', 50) if oil_result else 50

    risk_score = 50
    try:
        from geopolitics import generate_geopolitical_section
        _, risk_score = generate_geopolitical_section()
    except: pass

    g_verdict, g_emoji = score_verdict(gold_score)
    s_verdict, s_emoji = score_verdict(silver_score)
    o_verdict, o_emoji = score_verdict(oil_score)

    # 信号灯：每个品种独立一行，颜色+文字+分数
    lines.append(f'┌─ 📡 信号灯 ──────────────────────────────┐')
    lines.append(f'│  🥇 黄金  {g_emoji} {g_verdict:<6}  综合评分 {gold_score:>3}/100  │')
    lines.append(f'│  🥈 白银  {s_emoji} {s_verdict:<6}  综合评分 {silver_score:>3}/100  │')
    lines.append(f'│  🛢️ 原油  {o_emoji} {o_verdict:<6}  综合评分 {oil_score:>3}/100  │')
    risk_label = '🔴极高' if risk_score >= 40 else '🟡中等' if risk_score >= 20 else '🟢低'
    # 宏观面评分：从 FRED 宏观数据动态计算
    macro_label = _compute_macro_label()
    lines.append(f'│  🌍地缘风险 {risk_label}  宏观面:{macro_label:<7} │')
    lines.append(f'└────────────────────────────────────────────┘')
    lines.append('')

    # ========== 行情数据（精简：去掉30日区间） ==========
    lines.append('>> 📊 行情数据')
    lines.append('')

    instruments_data = [
        ('🥇 黄金', 'gold', gold_result),
        ('🥈 白银', 'silver', silver_result),
        ('🛢️ 原油', 'wti', oil_result),
    ]

    for label, key, result in instruments_data:
        try:
            df = fetch_data(key, period="365d")
            if df is not None and not df.empty:
                latest = df['Close'].iloc[-1]
                change_1d = df['Close'].pct_change().iloc[-1] * 100
                change_30d = (df['Close'].iloc[-1] / df['Close'].iloc[-30] - 1) * 100
                change_ytd = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
                lines.append(f'  {label} ¥{latest:,.0f}/克'
                             f'  日{change_1d:+.2f}%'
                             f'  30日{change_30d:+.1f}%'
                             f'  年初至今{change_ytd:+.1f}%')
            else:
                lines.append(f'  {label} ¥{result.get("latest", 0):,.0f}/克  (缓存)')
        except Exception as e:
            lines.append(f'  {label} 错误: {e}')
    # 国际美元金价（第二口径，与人民币沪金对比；失败降级不硬造）
    intl = _fetch_intl_gold()
    if intl.get("ok"):
        lines.append(f'  🌍 国际现货金 ${intl["price"]:.2f}/盎司  {intl.get("change", "n/a")}')
        # 内外价差（贴水/升水）：换算值 vs 沪金；需汇率，取最近报告值或降级
        spread_txt = _calc_gold_spread(intl["price"], gold_result)
        if spread_txt:
            lines.append(f'  ⚖️ 内外价差: {spread_txt}  （价差为相对参考，非无风险套利信号）')
    else:
        lines.append(f'  🌍 国际现货金: 数据源不可用（{intl.get("err","?")}），仅人民币口径')
    lines.append('')

    # ========== 仪表盘（趋势箭头文字化） ==========
    lines.append('>> 🎯 仪表盘')
    lines.append('')

    for label, key, result in instruments_data:
        if result:
            score = result.get('score', 50)
            rsi = result.get('rsi', 50) or 50
            verdict, v_emoji = score_verdict(score)
            price = f'¥{result.get("latest", 0):,.0f}'
            sig = result.get('macd', {}).get('signal', '+0') if isinstance(result.get('macd'), dict) else '+0'
            bar = score_to_bar(score)
            arrow = trend_arrow(score, rsi)
            lines.append(f'  {label} {price}  {v_emoji}{verdict}  {arrow}')
            lines.append(f'    {bar} {score}/100  RSI={rsi:.0f}  信号{sig}')
        else:
            lines.append(f'  {label} 数据不足')
    lines.append('')

    # ========== 波动率对比 ==========
    lines.append('>> 📉 波动率 & 风险对比')
    lines.append('')

    vol_data = []
    for label, key, result in instruments_data:
        df = fetch_data(key, period="90d")
        if df is not None and len(df) >= 20:
            returns = df['Close'].pct_change().dropna()
            vol_30 = returns.tail(20).std() * np.sqrt(252) * 100 if len(returns) >= 20 else 0
            peak = df['Close'].expanding().max()
            dd = ((df['Close'] - peak) / peak).min() * 100
            vol_data.append((label, vol_30, dd))

    if vol_data:
        vol_data.sort(key=lambda x: x[1], reverse=True)
        for label, vol, dd in vol_data:
            vol_level = '🔴高' if vol > 50 else '🟡中' if vol > 25 else '🟢低'
            dd_level = '🔴' if dd < -20 else '🟡' if dd < -10 else '🟢'
            lines.append(f'  {label} 波动率{vol:.0f}%{vol_level}  最大回撤{dd_level}{dd:.1f}%')
        high_vol = [d for d in vol_data if d[1] > 50]
        if high_vol:
            names = ''.join([d[0].split()[-1] for d in high_vol])
            lines.append(f'  ⚠️ {names}波动率超50%，注意仓位控制')
    lines.append('')

    # ========== 联动性 ==========
    lines.append('>> 🔗 联动性')
    lines.append('')

    gold_df = fetch_data('gold', period="90d")
    oil_df = fetch_data('wti', period="90d")
    silver_df = fetch_data('silver', period="90d")

    try:
        if gold_df is not None and oil_df is not None:
            g_ret = gold_df['Close'].pct_change().dropna()
            o_ret = oil_df['Close'].pct_change().dropna()
            min_len = min(len(g_ret), len(o_ret))
            if min_len > 10:
                corr_val = g_ret.iloc[-min_len:].corr(o_ret.iloc[-min_len:])
                if corr_val < -0.5:
                    corr_label = '强负相关'
                elif corr_val < -0.2:
                    corr_label = '弱负相关'
                elif corr_val < 0.5:
                    corr_label = '弱正相关'
                else:
                    corr_label = '强正相关'
                lines.append(f'  黄金-原油 90日收益率相关系数: {corr_val:.3f} ({corr_label})')
                if corr_val < -0.3:
                    lines.append(f'  📉 避险主导：黄金涨→原油跌')
                elif corr_val > 0.3:
                    lines.append(f'  📈 同涨同跌：风险情绪主导')
                else:
                    lines.append(f'  ➡️ 走势相对独立')
    except Exception as e:
        lines.append(f'  计算失败: {e}')

    try:
        if gold_df is not None and silver_df is not None:
            g_price = gold_df['Close'].iloc[-1]
            s_price = silver_df['Close'].iloc[-1]
            if g_price > 0 and s_price > 0:
                s_per_gram = s_price / 1000
                ratio = g_price / s_per_gram
                ratio_label = '偏低(白银贵)' if ratio < 50 else '正常' if ratio < 80 else '偏高(黄金贵)'
                lines.append(f'  金银比: {ratio:.1f} ({ratio_label})')
    except:
        pass
    lines.append('')

    # ========== 技术详解（精简：只保留关键指标一行） ==========
    lines.append('>> 📈 技术详解')
    lines.append('')

    for label, key, result in instruments_data:
        if result:
            score = result.get('score', 50)
            verdict, emoji = score_verdict(score)
            tech_detail = get_tech_summary(result)
            lines.append(f'  {label} {emoji} {verdict}  {tech_detail}')
    lines.append('')

    # ========== 操作建议（精简：去掉仓位，合并到组合建议） ==========
    lines.append('>> 📝 操作建议')
    lines.append('')

    for label, key, result in instruments_data:
        if result:
            score = result.get('score', 50)
            verdict, v_emoji = score_verdict(score)
            entry_note, stop_loss, target = get_entry_exit(result, geo_risk=risk_score)
            lines.append(f'  {label} {v_emoji} {verdict}')
            if entry_note:
                lines.append(f'    策略: {entry_note}')
            if stop_loss and target:
                lines.append(f'    止损: ¥{stop_loss:,.0f} → 目标: ¥{target:,.0f}')
            lines.append('')

    # 组合建议（含仓位）
    gold_adj = gold_score + (20 if risk_score >= 40 else 10 if risk_score >= 20 else 0)
    if gold_adj >= 60 and oil_score < 40:
        ratio = '5:2:3（黄金防守为主）'
    elif gold_adj >= 60 and oil_score >= 40:
        ratio = '4:3:3（均衡偏防守）'
    elif gold_adj < 40 and oil_score >= 50:
        ratio = '3:2:5（原油偏强）'
    elif gold_adj < 40 and oil_score < 40:
        ratio = '5:3:2（黄金防守为主）'
    else:
        ratio = '4:3:3（均衡配置）'

    lines.append(f'  组合建议：黄金:白银:原油 = {ratio}')
    lines.append('')

    # ========== 历史阶段定位（精简：一句话） ==========
    lines.append('>> 📊 历史阶段定位')
    lines.append('')

    try:
        if gold_df is not None and len(gold_df) >= 60:
            g_close = gold_df['Close']
            g_ma60 = g_close.rolling(60).mean().iloc[-1]
            g_ma20 = g_close.rolling(20).mean().iloc[-1]
            g_latest = g_close.iloc[-1]
            if g_latest < g_ma60 and g_ma20 < g_ma60:
                gold_phase = '中期调整区间'
            elif g_latest > g_ma60 and g_ma20 > g_ma60:
                gold_phase = '中期上行趋势'
            else:
                gold_phase = '趋势转换期'
            high_30 = g_close.tail(30).max()
            dd_30 = (g_latest / high_30 - 1) * 100
            lines.append(f'  黄金: {gold_phase} | 距30日高点回撤{dd_30:.1f}%')
    except:
        pass

    try:
        if oil_df is not None and len(oil_df) >= 60:
            o_close = oil_df['Close']
            o_ma60 = o_close.rolling(60).mean().iloc[-1]
            o_ma20 = o_close.rolling(20).mean().iloc[-1]
            o_latest = o_close.iloc[-1]
            if o_latest < o_ma60 and o_ma20 < o_ma60:
                oil_phase = '中期调整区间'
            elif o_latest > o_ma60 and o_ma20 > o_ma60:
                oil_phase = '中期上行趋势'
            else:
                oil_phase = '趋势转换期'
            high_30 = o_close.tail(30).max()
            dd_30 = (o_latest / high_30 - 1) * 100
            lines.append(f'  原油: {oil_phase} | 距30日高点回撤{dd_30:.1f}%')
    except:
        pass
    lines.append('')

    # ========== 多周期共振分析 ==========
    try:
        mta_results, mta_lines = run_multi_timeframe_analysis(source="akshare")
        if mta_lines:
            lines.append("")
            for mta_line in mta_lines:
                lines.append(mta_line)
            lines.append("")
    except Exception as e:
        lines.append(f"  ⚠️ 多周期共振分析不可用: {e}")
        lines.append("")

    # ========== 结论（必须与三品种建议一致） ==========
    lines.append('━' * 30)

    buy_count = sum(1 for s in [gold_score, silver_score, oil_score] if s >= 60)
    hold_count = sum(1 for s in [gold_score, silver_score, oil_score] if 40 <= s < 60)
    avoid_count = sum(1 for s in [gold_score, silver_score, oil_score] if s < 40)

    # 优先检查回避品种数量，避免"可考虑"掩盖"回避"信号
    if avoid_count >= 2:
        conclusion = '多品种偏弱，强烈建议观望，等信号灯转正。'
    elif avoid_count == 1 and buy_count >= 2:
        # 有回避品种但其他两个可考虑 → 不能笼统说"偏强"
        conclusion = '个别品种有支撑，但存在回避品种，轻仓试探，严控仓位。'
    elif avoid_count == 1 and buy_count == 1:
        conclusion = '信号混杂，建议观望，等待方向明朗。'
    elif avoid_count == 1:
        conclusion = '存在回避品种，建议观望为主，仅对可考虑品种轻仓试探。'
    elif buy_count >= 2 and avoid_count == 0:
        conclusion = '多品种信号偏强，可逢低分批布局。'
    elif buy_count == 1 and hold_count >= 1:
        conclusion = '个别品种有支撑，轻仓试探，其余观望。'
    elif hold_count >= 2:
        conclusion = '方向分歧，建议观望为主，等待信号明朗。'
    else:
        conclusion = '信号混杂，建议观望，等待方向明朗。'

    # 地缘风险始终检查，只要偏高就追加警告
    if risk_score >= 40:
        conclusion += f' 地缘风险({risk_score})偏高，注意避险。'

    lines.append(f'>> 💡 结论：{conclusion}')
    lines.append(f'>> ⚠️ 仅供参考，不构成投资建议')

    full = '\n'.join(lines)
    logger.info(full)

    # 精简模式（OIL_GOLD_BRIEF=1）：按"段"白名单裁剪，只保留 头部+信号灯+行情+操作建议+结论+免责
    import os
    if os.environ.get('OIL_GOLD_BRIEF') == '1':
        # 段白名单（只保留这些"段标题"开头的段）
        keep_sections = ['📊 石油黄金', '>> 📊 行情数据', '>> 📝 操作建议', '>> 💡 结论', '>> ⚠️ 仅供参考']
        out, in_keep = [], False
        for line in lines:
            s = line.strip()
            # 段边界：'>>' 段标题；⚠️ 框线(┌)会连带引入信号灯框，必须显式排除
            if s.startswith('>>') or s.startswith('📊 石油黄金'):
                in_keep = any((m in s) or (m in line) for m in keep_sections)
            elif s.startswith('┌') or s.startswith('└') or s.startswith('📡'):
                in_keep = False
            if in_keep:
                out.append(line)
        # 去掉多余空行
        full = re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip() + '\n'

    from config import REPORT_TEXT, ensure_dirs
    ensure_dirs()
    with open(REPORT_TEXT, 'w') as f:
        f.write(full)
    logger.info(f'\n已保存: {REPORT_TEXT}（{"精简" if os.environ.get("OIL_GOLD_BRIEF")=="1" else "完整"}）')

if __name__ == '__main__':
    generate_report()

# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
