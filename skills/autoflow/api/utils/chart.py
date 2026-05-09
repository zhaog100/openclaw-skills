# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""matplotlib 图表生成"""
import base64
import io
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def generate_chart(
    data: dict,
    chart_type: str = "bar",
    title: str = "",
) -> str:
    """生成图表并返回 base64 编码的 PNG 字符串

    Args:
        data: {"labels": [...], "values": [...]}
        chart_type: line / bar / pie
        title: 图表标题
    Returns:
        base64 字符串（不含 data:image 前缀）
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    labels = data.get("labels", [])
    values = data.get("values", [])

    if chart_type == "line":
        ax.plot(labels, values, marker="o")
    elif chart_type == "pie":
        ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    else:  # bar (default)
        ax.bar(labels, values)

    if title:
        ax.set_title(title)
    ax.tick_params(axis="x", rotation=30)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
