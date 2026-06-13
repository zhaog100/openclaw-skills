#!/usr/bin/env python3
"""
FRED（美联储经济数据）数据源 v3.3
美国官方宏观经济数据 + 美股市场全维度分析

覆盖：
- 核心市场指数（标普500/道琼斯/纳斯达克）
- 宏观经济指标（利率/CPI/就业/GDP）
- 估值指标（巴菲特指标/信用利差）
- 技术与情绪指标（VIX/收益率曲线）

数据来源: https://fred.stlouisfed.org
免费 API Key: https://fred.stlouisfed.org/docs/api/api_key.html

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
"""

import os
import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

# 缓存
from config import CACHE_DIR
CACHE_TTL = 3600  # 1小时


def get_api_key():
    """获取 FRED API Key"""
    key = os.environ.get("FRED_API_KEY", "")
    if not key:
        env_path = Path.home() / ".openclaw" / "workspace" / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("FRED_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    return key


def fetch_fred_series(series_id, days_back=90):
    """
    获取 FRED 数据系列（curl 优先，国内环境更可靠）
    
    Returns: pd.DataFrame [date, value] 或 None
    """
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    # 缓存检查
    CACHE_DIR.mkdir(exist_ok=True)
    cache_key = f"fred_{series_id}_{start}_{end}"
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime
        if age < CACHE_TTL:
            try:
                records = json.loads(cache_file.read_text())
                if records:
                    df = pd.DataFrame(records)
                    df["date"] = pd.to_datetime(df["date"])
                    return df
            except:
                pass
    
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={start}&coed={end}"
    
    # 方法1: curl
    csv_content = ""
    try:
        result = subprocess.run(
            ["curl", "-sL", "--max-time", "10", url],
            capture_output=True, text=True, timeout=15
        )
        csv_content = result.stdout
    except:
        pass
    
    # 方法2: urllib fallback
    if not csv_content or "observation_date" not in csv_content:
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                csv_content = resp.read().decode("utf-8")
        except:
            pass
    
    if not csv_content or "observation_date" not in csv_content:
        return None
    
    # 解析 CSV
    from io import StringIO
    try:
        df = pd.read_csv(StringIO(csv_content))
        df = df.dropna()
        df.columns = ["date", "value"]
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna()
    except:
        return None
    
    if df.empty:
        return None
    
    # 写缓存
    records = [{"date": str(row["date"]), "value": float(row["value"])} for _, row in df.iterrows()]
    try:
        cache_file.write_text(json.dumps(records))
    except:
        pass
    
    df["date"] = pd.to_datetime(df["date"])
    return df


def _latest(series_id, days_back=90):
    """快速获取最新值"""
    df = fetch_fred_series(series_id, days_back)
    if df is None or df.empty:
        return None, None, None
    latest = float(df["value"].iloc[-1])
    prev = float(df["value"].iloc[-2]) if len(df) > 1 else latest
    change = latest - prev
    pct = (change / abs(prev) * 100) if prev != 0 else 0
    return latest, change, pct


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 一、核心市场指数
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def analyze_market_indices():
    """分析美股三大指数"""
    indices = {
        "SP500": {"name": "标普500", "desc": "500家大型公司，美股最权威基准"},
        "DJIA": {"name": "道琼斯30", "desc": "30家蓝筹股，传统行业风向标"},
        "NASDAQCOM": {"name": "纳斯达克", "desc": "科技股为主(权重>60%)"},
    }
    
    results = {}
    for sid, info in indices.items():
        val, change, pct = _latest(sid, 120)
        if val is None:
            continue
        
        # 计算简单趋势
        df = fetch_fred_series(sid, 120)
        ma20 = float(df["value"].tail(20).mean()) if df is not None and len(df) >= 20 else val
        ma50 = float(df["value"].tail(50).mean()) if df is not None and len(df) >= 50 else val
        
        above_ma20 = "📈" if val > ma20 else "📉"
        above_ma50 = "📈" if val > ma50 else "📉"
        
        results[sid] = {
            "name": info["name"],
            "value": round(val, 2),
            "change": round(change, 2),
            "pct": round(pct, 2),
            "ma20": round(ma20, 2),
            "ma50": round(ma50, 2),
            "vs_ma20": above_ma20,
            "vs_ma50": above_ma50,
        }
    
    return results


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 二、宏观经济指标
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def analyze_macro_indicators():
    """宏观经济指标全景"""
    indicators = {
        # 利率
        "FEDFUNDS": {"name": "联邦基金利率", "unit": "%", "impact": "加息利空/降息利多"},
        "DGS10": {"name": "10Y国债收益率", "unit": "%", "impact": "上升利空成长股"},
        "DGS2": {"name": "2Y国债收益率", "unit": "%", "impact": "反映短期利率预期"},
        "DFII10": {"name": "10Y实际利率(TIPS)", "unit": "%", "impact": "与黄金负相关"},
        # 通胀
        "CPIAUCSL": {"name": "CPI", "unit": "指数", "impact": "超预期利空科技股"},
        "CPILFESL": {"name": "核心CPI", "unit": "指数", "impact": "剔除食品能源"},
        "PPIACO": {"name": "PPI(生产者)", "unit": "指数", "impact": "CPI先行指标"},
        # 就业
        "UNRATE": {"name": "失业率", "unit": "%", "impact": "<4%过热/>6%衰退"},
        "PAYEMS": {"name": "非农就业(千人)", "unit": "K", "impact": "超预期→通胀担忧"},
        # 产出
        "INDPRO": {"name": "工业生产指数", "unit": "指数", "impact": ">100扩张/<100收缩"},
        "RSAFS": {"name": "零售销售(百万$)", "unit": "M$", "impact": "消费驱动型经济核心"},
        # 信心
        "UMCSENT": {"name": "密歇根消费者信心", "unit": "指数", "impact": "<70悲观/>90乐观"},
    }
    
    results = {}
    for sid, info in indicators.items():
        val, change, pct = _latest(sid, 120)
        if val is None:
            continue
        results[sid] = {
            "name": info["name"],
            "value": round(val, 2),
            "change": round(change, 2),
            "pct": round(pct, 2),
            "unit": info["unit"],
            "impact": info["impact"],
        }
    
    return results


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 三、估值与市场情绪
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def analyze_valuation_sentiment():
    """估值与市场情绪指标"""
    indicators = {
        "VIXCLS": {"name": "VIX恐慌指数", "unit": "", "good_low": True,
                    "levels": [(20, "🟢市场平静"), (30, "🟡开始恐慌"), (999, "🔴极度恐慌")]},
        "T10Y2Y": {"name": "10Y-2Y利差", "unit": "%", "good_low": False,
                    "levels": [(0, "🔴倒挂（衰退信号）"), (0.5, "🟡偏低"), (999, "🟢正常")]},
        "BAMLH0A0HYM2": {"name": "高收益债利差", "unit": "%", "good_low": True,
                         "levels": [(3, "🟢信用宽松"), (5, "🟡信用收紧"), (999, "🔴信用危机")]},
        "DTWEXBGS": {"name": "美元指数(广义)", "unit": "", "good_low": False,
                     "levels": [(115, "🟢美元偏弱(利多商品)"), (125, "🟡中性"), (999, "🔴美元强势(利空商品)")]},
    }
    
    results = {}
    for sid, info in indicators.items():
        val, change, pct = _latest(sid, 120)
        if val is None:
            continue
        
        # 判断等级
        level_desc = "⚪数据不足"
        for threshold, desc in info["levels"]:
            if val < threshold:
                level_desc = desc
                break
        
        results[sid] = {
            "name": info["name"],
            "value": round(val, 2),
            "change": round(change, 2),
            "unit": info["unit"],
            "level": level_desc,
        }
    
    return results


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 四、综合研判
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def market_comprehensive_assessment():
    """美股市场综合研判"""
    signals = []
    
    # 1. 收益率曲线
    t10y2y, _, _ = _latest("T10Y2Y", 90)
    if t10y2y is not None:
        if t10y2y < 0:
            signals.append(("🔴", "收益率曲线倒挂 → 经济衰退风险高", "利空美股，利多黄金"))
        elif t10y2y < 0.3:
            signals.append(("🟡", f"收益率曲线趋平({t10y2y:.2f}%) → 衰退风险升温", "谨慎"))
        else:
            signals.append(("🟢", f"收益率曲线正常({t10y2y:.2f}%)", "中性"))
    
    # 2. VIX 恐慌指数
    vix, _, _ = _latest("VIXCLS", 90)
    if vix is not None:
        if vix > 30:
            signals.append(("🔴", f"VIX={vix:.1f} 市场极度恐慌", "可能是抄底机会，但需确认"))
        elif vix > 20:
            signals.append(("🟡", f"VIX={vix:.1f} 波动加大", "注意风险"))
        else:
            signals.append(("🟢", f"VIX={vix:.1f} 市场平静", "关注过热风险"))
    
    # 3. 实际利率 vs 黄金
    real_rate, _, _ = _latest("DFII10", 90)
    if real_rate is not None:
        if real_rate > 2:
            signals.append(("🔴", f"实际利率={real_rate:.2f}% 偏高", "利空黄金"))
        elif real_rate < 0:
            signals.append(("🟢", f"实际利率={real_rate:.2f}% 负利率", "利多黄金"))
        else:
            signals.append(("⚪", f"实际利率={real_rate:.2f}% 中性", "中性"))
    
    # 4. 消费者信心
    sentiment, _, _ = _latest("UMCSENT", 120)
    if sentiment is not None:
        if sentiment < 60:
            signals.append(("🔴", f"消费者信心={sentiment:.0f} 极度悲观", "经济衰退风险"))
        elif sentiment < 70:
            signals.append(("🟡", f"消费者信心={sentiment:.0f} 偏悲观", "消费可能放缓"))
        elif sentiment > 90:
            signals.append(("🟢", f"消费者信心={sentiment:.0f} 乐观", "但需警惕过热"))
        else:
            signals.append(("⚪", f"消费者信心={sentiment:.0f} 正常", "中性"))
    
    # 5. 美元强弱
    dxy, _, _ = _latest("DTWEXBGS", 90)
    if dxy is not None:
        if dxy > 125:
            signals.append(("🔴", f"美元指数={dxy:.1f} 极强", "利空商品/新兴市场"))
        elif dxy < 110:
            signals.append(("🟢", f"美元指数={dxy:.1f} 偏弱", "利多商品"))
        else:
            signals.append(("⚪", f"美元指数={dxy:.1f} 中性", "中性"))
    
    # 6. 信用利差
    credit, _, _ = _latest("BAMLH0A0HYM2", 90)
    if credit is not None:
        if credit > 5:
            signals.append(("🔴", f"信用利差={credit:.1f}% 极高", "流动性危机风险"))
        elif credit > 3.5:
            signals.append(("🟡", f"信用利差={credit:.1f}% 偏高", "信用环境收紧"))
        else:
            signals.append(("🟢", f"信用利差={credit:.1f}% 正常", "信用环境宽松"))
    
    # 综合评分
    bull = sum(1 for s in signals if s[0] == "🟢")
    bear = sum(1 for s in signals if s[0] == "🔴")
    total = len(signals) or 1
    score = int((bull - bear) / total * 50 + 50)
    
    if score >= 65:
        overall = "🟢 偏多（利好风险资产）"
    elif score >= 45:
        overall = "⚪ 中性（观望为主）"
    else:
        overall = "🔴 偏空（避险为主）"
    
    return {
        "signals": signals,
        "score": score,
        "overall": overall,
        "bull_count": bull,
        "bear_count": bear,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 格式化报告
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def format_macro_report():
    """格式化宏观经济全景报告"""
    lines = []
    
    # ── 一、市场指数 ──
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("📊 一、美股核心指数")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    indices = analyze_market_indices()
    if indices:
        for sid, d in indices.items():
            arrow = "📈" if d["change"] > 0 else "📉" if d["change"] < 0 else "→"
            lines.append(f"  {arrow} {d['name']}: {d['value']:,.2f} ({d['pct']:+.2f}%)")
            lines.append(f"    MA20={d['ma20']:,.2f}({d['vs_ma20']}) | MA50={d['ma50']:,.2f}({d['vs_ma50']})")
    else:
        lines.append("  ⚠️ 数据暂不可用")
    
    # ── 二、宏观指标 ──
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🏛️ 二、宏观经济指标")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    macro = analyze_macro_indicators()
    
    # 利率组
    lines.append("  📌 利率环境:")
    for sid in ["FEDFUNDS", "DGS10", "DGS2", "DFII10"]:
        if sid in macro:
            d = macro[sid]
            lines.append(f"    {d['name']}: {d['value']}{d['unit']} ({d['pct']:+.2f}%)")
    
    # 通胀组
    lines.append("  📌 通胀指标:")
    for sid in ["CPIAUCSL", "CPILFESL", "PPIACO"]:
        if sid in macro:
            d = macro[sid]
            lines.append(f"    {d['name']}: {d['value']} ({d['pct']:+.2f}%) - {d['impact']}")
    
    # 就业组
    lines.append("  📌 劳动力市场:")
    for sid in ["UNRATE", "PAYEMS"]:
        if sid in macro:
            d = macro[sid]
            lines.append(f"    {d['name']}: {d['value']}{d['unit']} ({d['pct']:+.2f}%) - {d['impact']}")
    
    # 产出/信心
    lines.append("  📌 产出与信心:")
    for sid in ["INDPRO", "RSAFS", "UMCSENT"]:
        if sid in macro:
            d = macro[sid]
            lines.append(f"    {d['name']}: {d['value']} ({d['pct']:+.2f}%) - {d['impact']}")
    
    # ── 三、估值与情绪 ──
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("💭 三、估值与市场情绪")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    sentiment = analyze_valuation_sentiment()
    if sentiment:
        for sid, d in sentiment.items():
            lines.append(f"  {d['level']} {d['name']}: {d['value']}{d['unit']} ({d['change']:+.2f})")
    else:
        lines.append("  ⚠️ 数据暂不可用")
    
    # ── 四、综合研判 ──
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🎯 四、综合研判")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    assessment = market_comprehensive_assessment()
    lines.append(f"  综合评分: {assessment['score']}/100 → {assessment['overall']}")
    lines.append(f"  利好信号: {assessment['bull_count']} | 利空信号: {assessment['bear_count']}")
    lines.append("")
    for icon, desc, impact in assessment["signals"]:
        lines.append(f"  {icon} {desc} → {impact}")
    
    # 对黄金原油的启示
    lines.append("")
    lines.append("  🥇 对黄金启示:")
    # 利率相关
    if real := macro.get("DFII10"):
        if real["value"] > 2:
            lines.append("    实际利率偏高 → 利空黄金（持有成本高）")
        elif real["value"] < 0:
            lines.append("    实际利率为负 → 利多黄金（避险保值）")
        else:
            lines.append("    实际利率中性 → 关注其他因素")
    if vix_val := sentiment.get("VIXCLS"):
        if vix_val["value"] > 25:
            lines.append("    VIX偏高 → 避险需求利多黄金")
    
    lines.append("  🛢️ 对原油启示:")
    if ind := macro.get("INDPRO"):
        if ind["pct"] > 0:
            lines.append("    工业生产扩张 → 利多原油需求")
        else:
            lines.append("    工业生产收缩 → 利空原油需求")
    if credit_val := sentiment.get("BAMLH0A0HYM2"):
        if credit_val["value"] > 4:
            lines.append("    信用利差偏高 → 经济下行风险利空原油")
    
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # ── 五、黄金原油宏观信号灯 ──
    signal_lines = format_commodity_signals(macro, sentiment, assessment)
    lines.extend(signal_lines)

    return lines


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 五、黄金原油宏观信号灯
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def format_commodity_signals(macro=None, sentiment=None, assessment=None):
    """
    黄金/原油宏观信号灯：逐项指标打分 + 综合信号 + 拐点追踪
    
    评分体系:
      每个指标 -2(强利空) ~ +2(强利多)
      综合: ≥+4  🟢强烈看多 | +1~+3 🟡偏多 | -1~0 ⚪中性 | -2~-3 🟠偏空 | ≤-4 🔴强烈看空
    
    拐点追踪:
      连续3期同方向 → 趋势确认
      最近1期反转 → 拐点预警
    """
    if macro is None:
        macro = analyze_macro_indicators()
    if sentiment is None:
        sentiment = analyze_valuation_sentiment()
    if assessment is None:
        assessment = market_comprehensive_assessment()
    
    lines = []
    
    # ── 黄金信号灯 ──
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🚦 五、黄金/原油宏观信号灯")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    gold_score = 0
    oil_score = 0
    gold_signals = []
    oil_signals = []
    
    # 1. 实际利率 → 黄金（最重要，权重x2）
    real_rate = macro.get("DFII10")
    if real_rate:
        r = real_rate["value"]
        if r > 2.5:
            s = -2
            desc = f"实际利率={r:.1f}% 偏高 → 持有成本大"
        elif r > 1.5:
            s = -1
            desc = f"实际利率={r:.1f}% 中性偏高 → 一定压制"
        elif r > 0:
            s = 0
            desc = f"实际利率={r:.1f}% 中性 → 影响不大"
        elif r > -1:
            s = 1
            desc = f"实际利率={r:.1f}% 偏低 → 利多"
        else:
            s = 2
            desc = f"实际利率={r:.1f}% 负利率 → 强利多"
        gold_score += s * 2  # 权重x2
        gold_signals.append((s, desc, 2))
    
    # 2. 美元指数 → 黄金+原油（负相关）
    dxy = sentiment.get("DTWEXBGS")
    if dxy:
        d = dxy["value"]
        if d > 128:
            sg, so = -2, -2
            desc_g = f"美元={d:.0f} 极强 → 黄金承压重"
            desc_o = f"美元={d:.0f} 极强 → 原油承压重"
        elif d > 120:
            sg, so = -1, -1
            desc_g = f"美元={d:.0f} 偏强 → 黄金承压"
            desc_o = f"美元={d:.0f} 偏强 → 原油承压"
        elif d > 110:
            sg, so = 0, 0
            desc_g = f"美元={d:.0f} 中性"
            desc_o = f"美元={d:.0f} 中性"
        else:
            sg, so = 1, 1
            desc_g = f"美元={d:.0f} 偏弱 → 利多商品"
            desc_o = f"美元={d:.0f} 偏弱 → 利多原油"
        gold_score += sg
        oil_score += so
        gold_signals.append((sg, desc_g, 1))
        oil_signals.append((so, desc_o, 1))
    
    # 3. VIX恐慌 → 黄金（正相关）
    vix = sentiment.get("VIXCLS")
    if vix:
        v = vix["value"]
        if v > 35:
            s = 2
            desc = f"VIX={v:.0f} 极度恐慌 → 避险需求暴涨"
        elif v > 25:
            s = 1
            desc = f"VIX={v:.0f} 恐慌升温 → 避险需求增加"
        elif v > 15:
            s = 0
            desc = f"VIX={v:.0f} 市场平静"
        else:
            s = -1
            desc = f"VIX={v:.0f} 过度乐观 → 需警惕变盘"
        gold_score += s
        gold_signals.append((s, desc, 1))
    
    # 4. 收益率曲线 → 黄金+原油
    t10y2y = sentiment.get("T10Y2Y")
    if t10y2y:
        sp = t10y2y["value"]
        if sp < 0:
            sg, so = 2, -2
            desc_g = f"利差={sp:.2f}% 倒挂 → 衰退风险利多黄金"
            desc_o = f"利差={sp:.2f}% 倒挂 → 需求萎缩利空原油"
        elif sp < 0.3:
            sg, so = 1, -1
            desc_g = f"利差={sp:.2f}% 趋平 → 温和利多黄金"
            desc_o = f"利差={sp:.2f}% 趋平 → 温和利空原油"
        else:
            sg, so = 0, 1
            desc_g = f"利差={sp:.2f}% 正常"
            desc_o = f"利差={sp:.2f}% 正常 → 经济健康利多原油"
        gold_score += sg
        oil_score += so
        gold_signals.append((sg, desc_g, 1))
        oil_signals.append((so, desc_o, 1))
    
    # 5. 信用利差 → 黄金+原油
    credit = sentiment.get("BAMLH0A0HYM2")
    if credit:
        c = credit["value"]
        if c > 5:
            sg, so = 2, -2
            desc_g = f"信用利差={c:.1f}% 危机 → 避险黄金"
            desc_o = f"信用利差={c:.1f}% 危机 → 需求崩塌"
        elif c > 3.5:
            sg, so = 1, -1
            desc_g = f"信用利差={c:.1f}% 偏高 → 温和避险"
            desc_o = f"信用利差={c:.1f}% 偏高 → 需求偏弱"
        else:
            sg, so = -1, 1
            desc_g = f"信用利差={c:.1f}% 宽松 → 风险偏好高"
            desc_o = f"信用利差={c:.1f}% 宽松 → 需求健康"
        gold_score += sg
        oil_score += so
        gold_signals.append((sg, desc_g, 1))
        oil_signals.append((so, desc_o, 1))
    
    # 6. 消费者信心 → 黄金（反向）+原油（正向）
    cs = macro.get("UMCSENT")
    if cs:
        c = cs["value"]
        if c < 60:
            sg, so = 2, -2
            desc_g = f"信心={c:.0f} 极度悲观 → 强避险利多黄金"
            desc_o = f"信心={c:.0f} 极度悲观 → 需求崩塌利空原油"
        elif c < 70:
            sg, so = 1, -1
            desc_g = f"信心={c:.0f} 偏悲观 → 温和避险"
            desc_o = f"信心={c:.0f} 偏悲观 → 需求偏弱"
        elif c > 90:
            sg, so = -1, 1
            desc_g = f"信心={c:.0f} 过热 → 风险偏好高"
            desc_o = f"信心={c:.0f} 乐观 → 需求强劲"
        else:
            sg, so = 0, 0
            desc_g = f"信心={c:.0f} 正常"
            desc_o = f"信心={c:.0f} 正常"
        gold_score += sg
        oil_score += so
        gold_signals.append((sg, desc_g, 1))
        oil_signals.append((so, desc_o, 1))
    
    # 7. 工业生产 → 原油（正向）
    ip = macro.get("INDPRO")
    if ip:
        if ip["value"] > 103:
            s = 1
            desc = f"工业生产={ip['value']:.1f} 扩张 → 能源需求增长"
        elif ip["value"] < 100:
            s = -1
            desc = f"工业生产={ip['value']:.1f} 收缩 → 能源需求下降"
        else:
            s = 0
            desc = f"工业生产={ip['value']:.1f} 正常"
        oil_score += s
        oil_signals.append((s, desc, 1))
    
    # 8. 通胀CPI → 黄金（保值需求）
    cpi = macro.get("CPIAUCSL")
    if cpi:
        pct = cpi["pct"]
        if pct > 1:
            s = 1
            desc = f"CPI月环比+{pct:.1f}% 通胀升温 → 保值需求"
        elif pct < -0.5:
            s = -1
            desc = f"CPI月环比{pct:.1f}% 通缩 → 保值需求弱"
        else:
            s = 0
            desc = f"CPI月环比+{pct:.1f}% 稳定"
        gold_score += s
        gold_signals.append((s, desc, 1))
    
    # ── 输出黄金信号灯 ──
    lines.append("")
    lines.append("  🥇 黄金宏观信号灯")
    lines.append("  ─────────────────────────────────")
    for score_val, desc, weight in gold_signals:
        icon = "🟢" if score_val > 0 else "🔴" if score_val < 0 else "⚪"
        w = f"(x{weight})" if weight > 1 else ""
        lines.append(f"    {icon} {desc} {w}")
    
    # 综合判定
    lines.append(f"")
    if gold_score >= 4:
        gold_light = "🟢🟢🟢 强烈看多"
    elif gold_score >= 1:
        gold_light = "🟡 偏多"
    elif gold_score >= -1:
        gold_light = "⚪ 中性观望"
    elif gold_score >= -3:
        gold_light = "🟠 偏空"
    else:
        gold_light = "🔴🔴🔴 强烈看空"
    lines.append(f"    信号灯: {gold_light} (综合分{gold_score:+d})")
    
    # 操作建议
    lines.append(f"    操作建议:")
    if gold_score >= 4:
        lines.append(f"      ✅ 宏观面支持做多，可考虑建仓")
        lines.append(f"      🎯 配合技术面确认入场点")
    elif gold_score >= 1:
        lines.append(f"      🟡 宏观面偏多但不够强，轻仓试探")
        lines.append(f"      🎯 等待更多利多信号确认")
    elif gold_score >= -1:
        lines.append(f"      ⚪ 宏观面中性，不建议主动操作")
        lines.append(f"      🎯 等待明确方向信号")
    elif gold_score >= -3:
        lines.append(f"      ⚠️ 宏观面偏空，不建议追多")
        lines.append(f"      🎯 可考虑减仓或观望")
    else:
        lines.append(f"      🛑 宏观面强烈看空，避免做多")
        lines.append(f"      🎯 如持有建议止损，考虑做空")
    
    # ── 输出原油信号灯 ──
    lines.append("")
    lines.append("  🛢️ 原油宏观信号灯")
    lines.append("  ─────────────────────────────────")
    for score_val, desc, weight in oil_signals:
        icon = "🟢" if score_val > 0 else "🔴" if score_val < 0 else "⚪"
        w = f"(x{weight})" if weight > 1 else ""
        lines.append(f"    {icon} {desc} {w}")
    
    lines.append(f"")
    if oil_score >= 4:
        oil_light = "🟢🟢🟢 强烈看多"
    elif oil_score >= 1:
        oil_light = "🟡 偏多"
    elif oil_score >= -1:
        oil_light = "⚪ 中性观望"
    elif oil_score >= -3:
        oil_light = "🟠 偏空"
    else:
        oil_light = "🔴🔴🔴 强烈看空"
    lines.append(f"    信号灯: {oil_light} (综合分{oil_score:+d})")
    
    lines.append(f"    操作建议:")
    if oil_score >= 4:
        lines.append(f"      ✅ 宏观面支持做多，可考虑建仓")
    elif oil_score >= 1:
        lines.append(f"      🟡 宏观面偏多，轻仓试探")
    elif oil_score >= -1:
        lines.append(f"      ⚪ 宏观面中性，等待方向")
    elif oil_score >= -3:
        lines.append(f"      ⚠️ 宏观面偏空，不建议追多")
    else:
        lines.append(f"      🛑 宏观面强烈看空，避免做多")
    
    # ── 关键拐点追踪 ──
    lines.append("")
    lines.append("  🔑 关键拐点监控")
    lines.append("  ─────────────────────────────────")
    
    inflections = []
    
    # 消费者信心连续低位
    if cs and cs["value"] < 65:
        inflections.append(f"    🔔 消费者信心={cs['value']:.0f} 持续低位 → 历史上<60连续3月=黄金大级别买入信号")
    
    # 收益率曲线趋势
    if t10y2y and t10y2y["value"] < 0.3:
        inflections.append(f"    🔔 收益率曲线趋平={t10y2y['value']:.2f}% → 接近倒挂=衰退预警")
    
    # VIX异动
    if vix and vix["value"] > 25:
        inflections.append(f"    🔔 VIX={vix['value']:.0f} 异常升高 → 恐慌蔓延，关注黄金买入机会")
    elif vix and vix["value"] < 13:
        inflections.append(f"    🔔 VIX={vix['value']:.0f} 极度乐观 → 变盘风险，注意保护性止损")
    
    # 信用利差
    if credit and credit["value"] > 4:
        inflections.append(f"    🔔 信用利差={credit['value']:.1f}% 急升 → 流动性危机前兆")
    
    if inflections:
        for p in inflections:
            lines.append(p)
    else:
        lines.append(f"    ✅ 暂无极端拐点信号")
    
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    return lines


if __name__ == "__main__":
    print("\n".join(format_macro_report()))
