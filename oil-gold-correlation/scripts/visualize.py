#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License
# Author: 小米粒 (Xiaomili) - AI Agent
# 版本: v3.3 | 石油黄金白银相关性分析
"""
石油黄金可视化模块
生成 Plotly 交互式图表

Author: 小米粒 (Xiaomili) - AI Agent
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).parent))
from fetch_data import fetch_data
from analysis import load_data, rolling_corr


def plot_analysis(period: str = "1y", window: int = 30, output: str = None):
    """生成完整分析图表"""
    df = load_data(period)
    if df.empty:
        return

    rc = rolling_corr(df, window)

    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            f"价格走势（{period}）",
            f"日收益率散点图",
            f"{window}日滚动相关系数",
        ),
        vertical_spacing=0.08,
        row_heights=[0.4, 0.3, 0.3],
    )

    # 1. 价格走势（双 Y 轴）
    fig.add_trace(
        go.Scatter(x=df.index, y=df["gold"], name="黄金", line=dict(color="gold", width=2)),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["wti"], name="WTI原油", line=dict(color="#333", width=2)),
        row=1, col=1,
    )

    # 2. 散点图
    fig.add_trace(
        go.Scatter(
            x=df["wti_ret"], y=df["gold_ret"],
            mode="markers", name="日收益率",
            marker=dict(size=3, opacity=0.5, color="steelblue"),
        ),
        row=2, col=1,
    )

    # 添加回归线
    from numpy.polynomial.polynomial import polyfit
    mask = ~(df["wti_ret"].isna() | df["gold_ret"].isna())
    x = df["wti_ret"][mask].values
    y = df["gold_ret"][mask].values
    b, m = polyfit(x, y, 1)
    fig.add_trace(
        go.Scatter(
            x=sorted(x), y=[b + m * xi for xi in sorted(x)],
            mode="lines", name="回归线",
            line=dict(color="red", width=2, dash="dash"),
        ),
        row=2, col=1,
    )

    # 3. 滚动相关系数
    fig.add_trace(
        go.Scatter(
            x=rc.index, y=rc, name=f"{window}日相关系数",
            line=dict(color="purple", width=2),
        ),
        row=3, col=1,
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=3, col=1)
    fig.add_hrect(y0=0.5, y1=1.0, fillcolor="green", opacity=0.05, row=3, col=1)
    fig.add_hrect(y0=-1.0, y1=-0.5, fillcolor="red", opacity=0.05, row=3, col=1)

    # 更新布局
    fig.update_layout(
        title="石油-黄金相关性分析",
        height=900,
        showlegend=True,
        template="plotly_white",
    )
    fig.update_xaxes(title_text="日期", row=1, col=1)
    fig.update_yaxes(title_text="价格 (USD)", row=1, col=1)
    fig.update_xaxes(title_text="WTI 收益率", row=2, col=1)
    fig.update_yaxes(title_text="黄金收益率", row=2, col=1)
    fig.update_yaxes(title_text="相关系数", row=3, col=1)

    # 保存
    if output is None:
        output_dir = Path(__file__).parent.parent.parent.parent / "media"
        output_dir.mkdir(exist_ok=True)
        output = str(output_dir / "oil-gold-correlation.html")

    fig.write_html(output)
    print(f"✅ 图表已保存: {output}")

    # 也输出文本摘要
    try:
        fig.show()
    except Exception:
        pass  # 无GUI环境跳过
    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成石油黄金可视化图表")
    parser.add_argument("--period", default="1y")
    parser.add_argument("--window", type=int, default=30)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    plot_analysis(args.period, args.window, args.output)

# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
