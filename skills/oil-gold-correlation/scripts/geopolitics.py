#!/usr/bin/env python3
"""
地缘政治分析模块 v3.3
自动采集新闻 → 评估对石油黄金的影响

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) - AI Agent
"""
# 版本: v3.3 | 石油黄金白银相关性分析

import warnings
warnings.filterwarnings('ignore')

import re
import json
import os
from datetime import datetime, timedelta
from pathlib import Path


# ===== 地缘政治风险因子库 =====
# 保留原有因子库，用于关键词匹配

GEOPOLITICAL_FACTORS = {
    "中东冲突": {
        "core_keywords": ["战争", "军事行动", "霍尔木兹", "Hormuz", "空袭", "导弹", "入侵"],
        "keywords": ["伊朗", "Iran", "Israel", "中东", "ceasefire", "停火",
                      "海湾", "以色列", "巴以", "加沙", "黎巴嫩", "叙利亚"],
        "need_pair": [],  # 不需要配对
        "gold_impact": "利多预期",
        "oil_impact": "利多预期",
        "detail": "中东冲突推高避险情绪，黄金受益；霍尔木兹海峡受阻推高油价",
    },
    "美联储政策": {
        "core_keywords": ["降息", "加息", "rate cut", "rate hike", "鲍威尔", "Powell", "Federal Reserve"],
        "keywords": ["Fed", "美联储", "货币政策", "利率决议", "FOMC"],
        "need_pair": [],
        "gold_impact": "降息利多预期/加息利空预期",
        "oil_impact": "降息利多需求预期/加息利空需求预期",
        "detail": "美联储降息 → 美元走弱 → 黄金原油受益",
    },
    "美元走势": {
        "core_keywords": ["美元指数", "DXY", "强美元", "弱美元", "dollar index"],
        "keywords": ["美元走强", "美元走弱", "美元升值", "美元贬值", "dollar strength"],
        "need_pair": ["美元"],  # "美元"需搭配第二关键词
        "pair_with": ["走强", "走弱", "升值", "贬值", "指数", "上涨", "下跌", "反弹", "回落"],
        "gold_impact": "负相关",
        "oil_impact": "负相关",
        "detail": "美元与大宗商品通常呈负相关",
    },
    "OPEC政策": {
        "core_keywords": ["OPEC", "欧佩克", "减产", "增产", "production cut", "quota"],
        "keywords": ["沙特", "产油国", "原油产量", "油组"],
        "need_pair": [],
        "gold_impact": "间接影响",
        "oil_impact": "直接利多/利空预期",
        "detail": "OPEC减产推高油价，增产压低油价",
    },
    "贸易战/关税": {
        "core_keywords": ["tariff", "trade war", "关税", "贸易战", "制裁", "sanctions"],
        "keywords": ["贸易摩擦", "贸易谈判", "报复性关税"],
        "need_pair": [],
        "gold_impact": "利多预期（避险）",
        "oil_impact": "利空需求预期",
        "detail": "贸易紧张 → 避险买黄金 → 但经济放缓压低原油需求",
    },
    "通胀数据": {
        "core_keywords": ["CPI高于", "CPI低于", "超预期通胀", "inflation surge"],
        "keywords": ["CPI", "inflation", "PCE", "通胀", "消费者物价", "物价指数", "PPI"],
        "need_pair": [],
        "gold_impact": "高通胀利多预期",
        "oil_impact": "高通胀利多预期",
        "detail": "高通胀 → 黄金保值需求上升 → 原油作为通胀对冲也受益",
    },
    "地缘风险": {
        "core_keywords": ["军事", "核武", "外交危机", "紧张局势", "冲突升级", "入侵", "military"],
        "keywords": ["避险", "risk-off", "恐慌", "VIX飙升", "地缘"],
        "need_pair": ["冲突"],  # "冲突"需搭配地域词
        "pair_with": ["中东", "俄乌", "台海", "南海", "朝鲜", "印巴", "边境"],
        "gold_impact": "利多预期",
        "oil_impact": "视具体情况",
        "detail": "地缘风险上升 → 避险资产受益",
    },
    "中国经济": {
        "core_keywords": ["PMI", "GDP", "LPR", "降准", "刺激经济", "房地产危机", "经济衰退"],
        "keywords": ["经济刺激", "基建投资", "货币政策", "中国GDP", "中国PMI"],
        "need_pair": ["中国", "China"],  # 需搭配第二关键词
        "pair_with": ["PMI", "GDP", "刺激", "房地产", "衰退", "降准", "降息", "通缩", "复苏", "放缓", "增长"],
        "gold_impact": "间接影响",
        "oil_impact": "利多/利空需求预期",
        "detail": "中国经济数据影响大宗商品需求预期",
    },
}


# ===== 关键词匹配规则 =====
# 用于判断新闻对黄金/原油的影响方向

GOLD_KEYWORDS_BULLISH = ["降息", "避险", "美元走弱", "通胀上升", "CPI高于", "地缘紧张",
                          "冲突升级", "战争", "制裁", "恐慌", "risk-off"]
GOLD_KEYWORDS_BEARISH = ["加息", "美元走强", "降息预期降温", "风险偏好", "risk-on",
                          "通胀回落", "CPI低于", "停火", "和平"]

OIL_KEYWORDS_BULLISH = ["减产", "OPEC减产", "供应中断", "霍尔木兹", "制裁伊朗", "库存下降",
                         "需求增长", "中国刺激"]
OIL_KEYWORDS_BEARISH = ["增产", "OPEC增产", "需求疲软", "库存增加", "经济放缓", "衰退",
                         "停火", "贸易战", "关税"]

# v3.3: 关联词 — 用于二次过滤泛泛新闻
RELEVANCE_WORDS = ["黄金", "原油", "金价", "油价", "商品", "期货", "大宗", "避险",
                    "gold", "oil", "commodity", "crude", "OPEC", "通胀",
                    "能源", "贵金属", "矿产", "铜", "铝", "铁矿"]


# ===== 缓存配置 =====
CACHE_DIR = Path(__file__).parent.parent / "cache"
CACHE_FILE = CACHE_DIR / "geopolitics_cache.json"
CACHE_TTL = 30 * 60  # 30分钟（秒）


def _load_cache():
    """加载缓存"""
    if not CACHE_FILE.exists():
        return None
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        
        # 检查是否过期
        timestamp = cache.get('timestamp', 0)
        if datetime.now().timestamp() - timestamp > CACHE_TTL:
            return None
        
        return cache
    except Exception:
        return None


def _save_cache(lines, risk_score):
    """保存缓存"""
    try:
        CACHE_DIR.mkdir(exist_ok=True)
        cache = {
            'timestamp': int(datetime.now().timestamp()),
            'lines': lines,
            'risk_score': risk_score
        }
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # 缓存失败不影响主流程


def _match_keywords(text, keywords):
    """检查文本是否包含关键词列表中的词"""
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            return True
    return False


def _match_factor(text, factor_info):
    """
    分级匹配：core_keywords(10分) > keywords(5分) > need_pair+pair_with(3分)
    返回 (matched: bool, score: int)
    """
    score = 0
    # 1. 核心关键词（强相关）
    core_kws = factor_info.get("core_keywords", [])
    for kw in core_kws:
        if kw.lower() in text.lower():
            score += 10
            break  # 命中一个核心词即可
    
    # 2. 一般关键词
    if score == 0:
        general_kws = factor_info.get("keywords", [])
        for kw in general_kws:
            if kw.lower() in text.lower():
                score += 5
                break
    
    # 3. 需配对的关键词（弱相关，需搭配第二关键词）
    need_pair = factor_info.get("need_pair", [])
    if score == 0 and need_pair:
        pair_with = factor_info.get("pair_with", [])
        has_pair_word = any(pw.lower() in text.lower() for pw in pair_with)
        if has_pair_word:
            has_need = any(np.lower() in text.lower() for np in need_pair)
            if has_need:
                score += 3
    
    return (score > 0, score)


def _judge_sentiment(title, content=""):
    """v3.3 判断单条新闻的情感倾向 — 核心因子5分/边缘因子1分 + 关联词二次过滤"""
    text = f"{title} {content}"

    # 匹配风险因子（使用分级匹配）
    matched_factors = []
    factor_scores = {}
    for factor_name, factor_info in GEOPOLITICAL_FACTORS.items():
        matched, match_score = _match_factor(text, factor_info)
        if matched:
            # v3.3: 关联词二次过滤
            relevance_required = factor_info.get("relevance_required", False)
            if relevance_required:
                if not _match_keywords(text, RELEVANCE_WORDS):
                    continue  # 泛泛新闻，不包含商品关联词，跳过
            matched_factors.append(factor_name)
            factor_scores[factor_name] = match_score

    # 判断黄金影响
    gold_bull = _match_keywords(text, GOLD_KEYWORDS_BULLISH)
    gold_bear = _match_keywords(text, GOLD_KEYWORDS_BEARISH)
    if gold_bull and not gold_bear:
        gold_impact = "利多预期"
    elif gold_bear and not gold_bull:
        gold_impact = "利空预期"
    elif gold_bull and gold_bear:
        gold_impact = "多空交织"
    else:
        gold_impact = "中性"

    # 判断原油影响
    oil_bull = _match_keywords(text, OIL_KEYWORDS_BULLISH)
    oil_bear = _match_keywords(text, OIL_KEYWORDS_BEARISH)
    if oil_bull and not oil_bear:
        oil_impact = "利多预期"
    elif oil_bear and not oil_bull:
        oil_impact = "利空预期"
    elif oil_bull and oil_bear:
        oil_impact = "多空交织"
    else:
        oil_impact = "中性"

    # v3.3 评分：核心因子5分 + 边缘因子1分
    score = sum(factor_scores.values())
    if gold_bull:
        score += 3
    if gold_bear:
        score -= 3
    score = min(score, 25)  # 单条新闻最多25分

    return {
        "factors": matched_factors,
        "gold_impact": gold_impact,
        "oil_impact": oil_impact,
        "score": score,
    }


def fetch_news_akshare():
    """多渠道新闻采集：国内(央视+东方财富+上期所) + 国际(CNBC)"""
    try:
        import akshare as ak
        news_list = []

        # ── 国内渠道 ──

        # 来源1：央视新闻联播（国家权威，地缘/政策覆盖好）
        try:
            from datetime import timedelta
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
            today = datetime.now().strftime('%Y%m%d')
            for date_str in [today, yesterday]:
                try:
                    df = ak.news_cctv(date=date_str)
                    if df is not None and not df.empty:
                        for _, row in df.iterrows():
                            news_list.append({
                                "source": "央视新闻",
                                "title": str(row.get("title", "")),
                                "content": str(row.get("content", ""))[:500],
                                "time": str(row.get("date", "")),
                            })
                except Exception:
                    pass
        except Exception:
            pass

        # 来源2：东方财富全球财经（实时200条，覆盖面广）
        try:
            df = ak.stock_info_global_em()
            if df is not None and not df.empty:
                for _, row in df.head(40).iterrows():
                    news_list.append({
                        "source": "东方财富",
                        "title": str(row.get("标题", "")),
                        "content": str(row.get("摘要", ""))[:500],
                        "time": str(row.get("发布时间", "")),
                    })
        except Exception:
            pass

        # 来源3：上海商品交易所（期货市场专业新闻）
        try:
            df2 = ak.futures_news_shmet(symbol="全部")
            if df2 is not None and not df2.empty:
                for _, row in df2.head(15).iterrows():
                    news_list.append({
                        "source": "上期所",
                        "title": str(row.get("内容", ""))[:100],
                        "content": str(row.get("内容", "")),
                        "time": str(row.get("发布时间", "")),
                    })
        except Exception:
            pass

        # ── 国际渠道（RSS，无法获取自动跳过） ──
        try:
            import subprocess
            import re as _re

            from config import RSS_SOURCES
            INTERNATIONAL_RSS = RSS_SOURCES + [
                ("https://www.forexlive.com/feed/", "ForexLive"),
                ("https://hnrss.org/frontpage", "HackerNews"),
            ]

            for feed_url, feed_name in INTERNATIONAL_RSS:
                try:
                    result = subprocess.run(["curl", "-sL", "--max-time", "6", feed_url],
                                       capture_output=True, text=True, timeout=8)
                    if not r.stdout or len(r.stdout) < 200:
                        continue
                    titles = _re.findall(r'<title>(.*?)</title>', r.stdout[:30000])
                    descs = _re.findall(r'<description><!\[CDATA\[(.*?)\]\]></description>', r.stdout[:30000])
                    if not descs:
                        descs = _re.findall(r'<description>(.*?)</description>', r.stdout[:30000])
                    items = [t for t in titles[1:] if len(t) > 15][:15]
                    for i, title in enumerate(items):
                        desc = descs[i+1][:300] if i+1 < len(descs) else ""
                        news_list.append({
                            "source": feed_name,
                            "title": _re.sub(r'&[a-z]+;', ' ', title),
                            "content": _re.sub(r'<[^>]+>', '', desc),
                            "time": "",
                        })
                except Exception:
                    pass
        except Exception:
            pass

        # 去重（按标题前30字）
        seen = set()
        unique = []
        for n in news_list:
            key = n["title"][:30]
            if key not in seen:
                seen.add(key)
                unique.append(n)

        cn = sum(1 for n in unique if n.get("source","") in ("央视新闻","东方财富","上期所"))
        intl = len(unique) - cn
        print(f"  📡 多渠道采集: {len(unique)}条（国内{cn} + 国际{intl}）")

        return unique
    except ImportError:
        print("⚠️ akshare 未安装，无法自动采集新闻")
        return []
    except Exception as e:
        print(f"⚠️ 新闻采集异常: {e}")
        return []


def filter_relevant_news(news_list):
    """过滤与黄金/原油相关的新闻（分级匹配+去重）"""
    relevant = []
    seen_titles = set()

    for news in news_list:
        title = news.get("title", "")
        content = news.get("content", "")
        text = f"{title} {content}"

        # 分级匹配每个因子
        best_factor = None
        best_score = 0
        for factor_name, factor_info in GEOPOLITICAL_FACTORS.items():
            matched, score = _match_factor(text, factor_info)
            if matched and score > best_score:
                best_score = score
                best_factor = factor_name
        
        if best_factor and best_score >= 3 and title not in seen_titles:
            seen_titles.add(title)
            judgment = _judge_sentiment(title, content)
            judgment["primary_factor"] = best_factor
            judgment["factor_score"] = best_score
            news["judgment"] = judgment
            relevant.append(news)

    # 按因子得分排序
    relevant.sort(key=lambda x: x.get("judgment", {}).get("factor_score", 0), reverse=True)
    return relevant[:15]


def assess_geopolitical_risk():
    """
    评估当前地缘政治风险（自动采集版）
    返回 (events, risk_score)
    风险评分规则：核心关键词10分/条，一般关键词5分/条，配对3分/条
    同一新闻只计入得分最高的因子（去重）
    """
    events = []
    risk_score = 0

    news_list = fetch_news_akshare()
    relevant = filter_relevant_news(news_list)

    if not relevant:
        events.append({
            "name": "📡 新闻采集",
            "status": "暂无重大事件（采集源未返回数据）",
            "gold": "中性",
            "oil": "中性",
            "score": 0,
            "detail": ["• 自动采集未获取到相关新闻", "• 建议关注实时新闻获取最新动态"],
        })
        return events, 0

    # 按风险因子聚合新闻（同一新闻只计入主因子）
    factor_events = {}
    for news in relevant:
        judgment = news.get("judgment", {})
        factor_name = judgment.get("primary_factor", "其他")
        factor_score = judgment.get("factor_score", 3)
        
        if factor_name not in factor_events:
            factor_events[factor_name] = {
                "news": [],
                "gold_impacts": [],
                "oil_impacts": [],
                "total_score": 0,
            }
        factor_events[factor_name]["news"].append(news)
        factor_events[factor_name]["gold_impacts"].append(judgment["gold_impact"])
        factor_events[factor_name]["oil_impacts"].append(judgment["oil_impact"])
        factor_events[factor_name]["total_score"] += factor_score

    # 生成事件列表
    for factor_name, data in sorted(factor_events.items(),
                                     key=lambda x: abs(x[1]["total_score"]),
                                     reverse=True)[:6]:
        gold_mode = max(set(data["gold_impacts"]), key=data["gold_impacts"].count)
        oil_mode = max(set(data["oil_impacts"]), key=data["oil_impacts"].count)

        score = data["total_score"]
        risk_score += score

        details = []
        for news in data["news"][:3]:
            title = news.get("title", "")
            if title:
                details.append(f"• {title[:60]}")

        factor_info = GEOPOLITICAL_FACTORS.get(factor_name, {})
        icon = {"中东冲突": "🔥", "美联储政策": "🏦", "美元走势": "💵",
                "OPEC政策": "🛢️", "贸易战/关税": "⚔️", "通胀数据": "📊",
                "地缘风险": "⚠️", "中国经济": "🇨🇳"}.get(factor_name, "📰")

        events.append({
            "name": f"{icon} {factor_name}",
            "status": f"近期{len(data['news'])}条相关新闻",
            "gold": gold_mode,
            "oil": oil_mode,
            "score": score,
            "detail": details if details else [f"• {factor_info.get('detail', '综合分析')}"],
        })

    # 风险评分上限50（避免虚高）
    risk_score = min(risk_score, 50)

    return events, risk_score


def generate_geopolitical_section():
    """生成地缘政治分析部分（嵌入到每日报告中）"""
    # 检查缓存
    cache = _load_cache()
    if cache:
        return cache['lines'], cache['risk_score']
    
    # 缓存未命中，重新采集
    events, risk_score = assess_geopolitical_risk()

    lines = []
    lines.append(f"\n{'━' * 50}")
    lines.append("🌍 五、国际形势与政策分析（自动采集）")
    lines.append(f"{'━' * 50}")

    # 风险等级
    if risk_score >= 30:
        risk_level = "🔴🔴 极高风险（强烈利多黄金预期）"
    elif risk_score >= 15:
        risk_level = "🔴 高风险（利多黄金预期）"
    elif risk_score >= 5:
        risk_level = "🟡 中等风险（偏利多黄金预期）"
    elif risk_score <= -15:
        risk_level = "🟢 低风险（利多风险资产预期）"
    else:
        risk_level = "🟢 正常"

    lines.append(f"\n  📊 地缘风险指数: {risk_score:+d}/100 | {risk_level}")

    # 各事件
    for event in events:
        lines.append(f"\n  {event['name']}")
        lines.append(f"    状态: {event['status']}")
        lines.append(f"    🥇 黄金: {event['gold']}")
        lines.append(f"    🛢️ 原油: {event['oil']}")
        for d in event["detail"]:
            lines.append(f"    {d}")

    # 综合判断
    lines.append(f"\n  🎯 地缘形势综合研判:")
    if risk_score >= 20:
        lines.append("    ⚠️ 地缘风险较高 → 黄金利多预期较强")
        lines.append("    ⚠️ 原油供应面不确定性上升 → 波动加剧")
        lines.append("    📌 建议: 关注避险资产，注意仓位管理")
    elif risk_score >= 5:
        lines.append("    📊 地缘风险偏高 → 黄金存在支撑")
        lines.append("    📊 原油受消息面影响，波动可能加大")
    elif risk_score <= -10:
        lines.append("    📊 地缘风险较低 → 避险需求回落")
        lines.append("    📊 关注技术面信号为主")
    else:
        lines.append("    ✅ 地缘风险可控 → 回归技术面分析")

    # 保存缓存
    _save_cache(lines, risk_score)
    
    return lines, risk_score

# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
