#!/usr/bin/env python3
"""
隐藏机遇扫描器
跨市场背离、跨品种异常、量价背离、多时间框架共振检测

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) - AI Agent
"""
# 版本: v3.3 | 石油黄金白银相关性分析

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from datetime import datetime


# 关联词（用于二次过滤泛泛新闻不相关的机遇）
COMMODITY_WORDS = ["黄金", "原油", "金价", "油价", "商品", "期货", "大宗", "避险",
                    "gold", "oil", "commodity", "crude", "bullion", "OPEC", "联储"]


class Opportunity:
    """单个机遇"""
    def __init__(self, op_type, title, direction, confidence, detail, score_impact=0):
        self.type = op_type           # divergence / cross_commodity / volume_price / mtf_resonance
        self.title = title            # 标题
        self.direction = direction    # bullish / bearish / neutral
        self.confidence = confidence  # 0-100
        self.detail = detail          # 详细描述
        self.score_impact = score_impact  # 对评分的影响


class OpportunityScanner:
    """跨市场隐藏机遇扫描"""

    def __init__(self):
        self.opportunities = []

    def scan_divergence(self, domestic_data, international_data, domestic_name="沪金", international_name="国际金"):
        """
        内外盘背离扫描
        domestic_data/international_data: DataFrame with Close column
        """
        if domestic_data is None or international_data is None:
            return
        if domestic_data.empty or international_data.empty:
            return

        # 取近5日和近20日涨跌幅
        def get_changes(df):
            col = "Close" if "Close" in df.columns else "close"
            close = df[col].dropna()
            if len(close) < 5:
                return None, None
            latest = float(close.iloc[-1])
            c5 = (latest - float(close.iloc[-6])) / float(close.iloc[-6]) * 100 if len(close) > 5 else 0
            c20 = (latest - float(close.iloc[-21])) / float(close.iloc[-21]) * 100 if len(close) > 20 else 0
            return c5, c20

        d5, d20 = get_changes(domestic_data)
        i5, i20 = get_changes(international_data)
        if d5 is None or i5 is None:
            return

        # 5日背离检测
        gap_5 = abs(i5 - d5)
        gap_20 = abs(i20 - d20) if i20 is not None and d20 is not None else 0

        # 背离阈值：内外盘涨跌幅差距 > 1.5%
        if gap_5 > 1.5:
            if i5 > d5 and i5 > 0:
                # 国际涨得多 → 国内补涨机会
                conf = min(50 + gap_5 * 10, 85)
                self.opportunities.append(Opportunity(
                    "divergence",
                    f"内外盘背离：{domestic_name}补涨机会",
                    "bullish",
                    conf,
                    f"国际{international_name}5日{i5:+.1f}% vs {domestic_name}{d5:+.1f}% → 差距{gap_5:.1f}%\n"
                    f"   建议关注{domestic_name}做多机会",
                    score_impact=int(gap_5 * 3),
                ))
            elif d5 > i5 and d5 > 0:
                # 国内涨得多 → 国际可能补涨，或国内有特殊因素
                conf = min(40 + gap_5 * 8, 70)
                self.opportunities.append(Opportunity(
                    "divergence",
                    f"内外盘背离：{domestic_name}强于国际",
                    "neutral",
                    conf,
                    f"{domestic_name}5日{d5:+.1f}% vs {international_name}{i5:+.1f}% → 国内需求强劲？\n"
                    f"   关注国内供需基本面变化",
                    score_impact=0,
                ))

        # 国际跌但国内不跌
        if i5 < -1 and d5 > -0.5:
            self.opportunities.append(Opportunity(
                "divergence",
                f"{domestic_name}抗跌：国内需求支撑",
                "bullish",
                60,
                f"国际{international_name}跌{i5:.1f}%但{domestic_name}仅{d5:+.1f}%\n"
                f"   国内需求可能强劲，支撑价格",
                score_impact=5,
            ))

    def scan_cross_commodity(self, gold_data, oil_data):
        """
        跨品种背离：黄金-原油比率异常
        gold_data/oil_data: DataFrame with Close
        """
        if gold_data is None or oil_data is None:
            return

        col = "Close"
        gold_close = gold_data[col].dropna() if col in gold_data.columns else gold_data.iloc[:, 0].dropna()
        oil_close = oil_data[col].dropna() if col in oil_data.columns else oil_data.iloc[:, 0].dropna()

        if len(gold_close) < 20 or len(oil_close) < 20:
            return

        # 对齐日期（取交集）
        common_idx = gold_close.index.intersection(oil_close.index)
        if len(common_idx) < 20:
            return

        gold_aligned = gold_close.loc[common_idx]
        oil_aligned = oil_close.loc[common_idx]

        ratio = gold_aligned / oil_aligned
        current_ratio = float(ratio.iloc[-1])
        mean_ratio = float(ratio.mean())
        std_ratio = float(ratio.std())

        if std_ratio == 0:
            return

        z_score = (current_ratio - mean_ratio) / std_ratio

        # 涨跌幅方向
        gold_ret = (float(gold_close.iloc[-1]) - float(gold_close.iloc[-6])) / float(gold_close.iloc[-6]) * 100 if len(gold_close) > 5 else 0
        oil_ret = (float(oil_close.iloc[-1]) - float(oil_close.iloc[-6])) / float(oil_close.iloc[-6]) * 100 if len(oil_close) > 5 else 0

        # 黄金涨+原油跌 = 避险飙升
        if gold_ret > 1 and oil_ret < -1:
            self.opportunities.append(Opportunity(
                "cross_commodity",
                "避险情绪飙升：黄金涨+原油跌",
                "bearish_oil",
                min(50 + abs(gold_ret - oil_ret) * 5, 80),
                f"黄金5日{gold_ret:+.1f}% vs 原油{oil_ret:+.1f}%\n"
                f"   典型避险模式：经济衰退信号？关注风险资产",
                score_impact=-10,
            ))

        # 比率偏离均值 > 1σ
        if abs(z_score) > 1.0:
            if z_score > 1.5:
                self.opportunities.append(Opportunity(
                    "cross_commodity",
                    f"黄金-原油比率异常偏高 ({z_score:+.1f}σ)",
                    "bearish_gold",
                    min(40 + abs(z_score) * 15, 75),
                    f"当前比率: {current_ratio:.1f} (历史均值{mean_ratio:.1f}, {z_score:+.1f}σ)\n"
                    f"   黄金相对偏贵/原油相对便宜，关注原油做多机会",
                    score_impact=-5,
                ))
            elif z_score < -1.5:
                self.opportunities.append(Opportunity(
                    "cross_commodity",
                    f"黄金-原油比率异常偏低 ({z_score:+.1f}σ)",
                    "bearish_oil",
                    min(40 + abs(z_score) * 15, 75),
                    f"当前比率: {current_ratio:.1f} (历史均值{mean_ratio:.1f}, {z_score:+.1f}σ)\n"
                    f"   原油相对偏贵，关注原油回调风险",
                    score_impact=5,
                ))

    def scan_volume_price(self, data, name=""):
        """
        量价背离检测
        data: DataFrame with Close and Volume columns
        """
        if data is None or data.empty:
            return

        col_close = "Close" if "Close" in data.columns else "close"
        col_vol = "Volume" if "Volume" in data.columns else "volume"
        if col_close not in data.columns or col_vol not in data.columns:
            return

        close = data[col_close].dropna()
        volume = data[col_vol].dropna()

        if len(close) < 10 or len(volume) < 10:
            return

        # 对齐
        common = close.index.intersection(volume.index)
        if len(common) < 10:
            return

        close = close.loc[common]
        volume = volume.loc[common]

        # 近5日 vs 前5日
        recent_price = float(close.iloc[-1])
        prev_price = float(close.iloc[-6]) if len(close) > 5 else recent_price
        price_up = recent_price > prev_price

        recent_vol = volume.iloc[-5:].mean()
        prev_vol = volume.iloc[-10:-5].mean()
        vol_up = recent_vol > prev_vol

        # 近5日成交量趋势（递增/递减）
        vol_recent = volume.iloc[-5:].values
        vol_decreasing = all(vol_recent[i] >= vol_recent[i+1] for i in range(len(vol_recent)-1))
        vol_increasing = all(vol_recent[i] <= vol_recent[i+1] for i in range(len(vol_recent)-1))

        label = f" {name}" if name else ""

        # 价格创新高但量缩
        if price_up and vol_decreasing:
            self.opportunities.append(Opportunity(
                "volume_price",
                f"量价顶背离{label}",
                "bearish",
                55,
                f"近5日价格上行但成交量递减 → 上涨动力不足\n"
                f"   可能是顶部信号，注意回调风险",
                score_impact=-8,
            ))

        # 价格下跌但量缩
        if not price_up and vol_decreasing:
            self.opportunities.append(Opportunity(
                "volume_price",
                f"量价底背离{label}",
                "bullish",
                55,
                f"近5日价格下行但成交量递减 → 卖压减弱\n"
                f"   可能是底部信号，关注反弹机会",
                score_impact=8,
            ))

    def scan_multi_timeframe(self, data_short, data_long, name=""):
        """
        多时间框架共振
        data_short: 短期数据（如30天）
        data_long: 长期数据（如1年）
        """
        if data_short is None or data_long is None:
            return

        col = "Close" if "Close" in data_short.columns else "close"

        # 短期趋势（MA5 vs MA10）
        short_close = data_short[col].dropna()
        if len(short_close) < 10:
            return

        short_ma5 = float(short_close.tail(5).mean())
        short_ma10 = float(short_close.tail(10).mean())
        short_bull = short_ma5 > short_ma10

        # 长期趋势（周线级别）
        long_close = data_long[col].dropna()
        if len(long_close) < 50:
            return

        long_ma20 = float(long_close.tail(20).mean())
        long_ma50 = float(long_close.tail(50).mean()) if len(long_close) >= 50 else long_ma20
        long_bull = long_ma20 > long_ma50

        label = f" {name}" if name else ""

        if short_bull and long_bull:
            self.opportunities.append(Opportunity(
                "mtf_resonance",
                f"多周期共振看多{label}",
                "bullish",
                75,
                f"短线上行+长线上行 → 高确信看多信号\n"
                f"   可考虑逢低买入",
                score_impact=15,
            ))
        elif not short_bull and not long_bull:
            self.opportunities.append(Opportunity(
                "mtf_resonance",
                f"多周期共振看空{label}",
                "bearish",
                75,
                f"短线下行+长线下行 → 高确信看空信号\n"
                f"   建议观望或减仓",
                score_impact=-15,
            ))
        elif long_bull and not short_bull:
            self.opportunities.append(Opportunity(
                "mtf_resonance",
                f"长多短空{label}（等待确认）",
                "neutral",
                45,
                f"长线上行但短线回调 → 等待短线止跌\n"
                f"   可能是回调买入机会",
                score_impact=3,
            ))

    def generate_opportunity_report(self):
        """生成机遇报告，按置信度排序"""
        if not self.opportunities:
            return ["  ✅ 未检测到明显异常机遇"]

        # 排序：置信度降序
        sorted_opps = sorted(self.opportunities, key=lambda o: o.confidence, reverse=True)

        lines = []
        medals = ["🥇", "🥈", "🥉"] + ["  "] * 10

        for i, opp in enumerate(sorted_opps[:5]):  # 最多显示5个
            medal = medals[i] if i < len(medals) else "  "

            # 确信度标签
            if opp.confidence >= 70:
                conf_label = "高确信"
                conf_emoji = "🟢"
            elif opp.confidence >= 50:
                conf_label = "中确信"
                conf_emoji = "🟡"
            else:
                conf_label = "待确认"
                conf_emoji = "🔴"

            lines.append(f"  {medal} [{conf_label}] {opp.title}")
            for line in opp.detail.split("\n"):
                lines.append(f"     {line.strip()}")
            lines.append(f"     置信度：{conf_emoji} {opp.confidence:.0f}%")
            lines.append("")

        return lines

    def get_total_score_impact(self):
        """获取所有机遇对评分的累计影响"""
        return sum(o.score_impact for o in self.opportunities)


if __name__ == "__main__":
    print("OpportunityScanner 模块 — 请通过 advisor.py 调用")

# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
