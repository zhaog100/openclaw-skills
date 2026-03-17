# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""Report generator - Markdown and ASCII charts."""

from collections import OrderedDict


def generate_ascii_chart(data, title="", width=40, max_height=10):
    """Generate an ASCII bar chart from {label: value} dict."""
    if not data:
        return f"=== {title} ===\n  (no data)\n"

    # 过滤非数字值
    numeric = {k: v for k, v in data.items() if isinstance(v, (int, float))}
    if not numeric:
        return f"=== {title} ===\n  (no numeric data)\n"

    max_val = max(numeric.values()) if numeric.values() else 1
    if max_val == 0:
        max_val = 1

    lines = [f"=== {title} ==="]
    for label, value in numeric.items():
        bar_len = int((value / max_val) * width)
        bar = "█" * bar_len + "░" * (width - bar_len)
        lines.append(f"  {label:<15s} │{bar}│ {value}")

    return "\n".join(lines)


def generate_trend_chart(daily, title="Daily Commits"):
    """Generate ASCII trend line chart from {date: count}."""
    if not daily:
        return f"=== {title} ===\n  (no data)\n"

    dates = sorted(daily.keys())
    values = [daily[d] for d in dates]
    max_val = max(values) if values else 1
    if max_val == 0:
        max_val = 1
    height = 5

    lines = [f"=== {title} ==="]
    for row in range(height, -1, -1):
        threshold = (row / height) * max_val
        row_chars = []
        for v in values:
            if v >= threshold:
                row_chars.append("●")
            else:
                row_chars.append(" ")
        lines.append(f"  {threshold:5.1f} │{''.join(row_chars)}")
    lines.append(f"       └{'─' * len(dates)}")
    date_line = "         " + "".join(d[-2:] for d in dates)
    lines.append(date_line)

    return "\n".join(lines)


def generate_markdown(stats, issues, progress):
    """Generate a full Markdown progress report."""
    lines = []
    lines.append("# 📊 Project Progress Report")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append(f"- **Overall Score**: {progress['overall_score']:.1%}")
    lines.append(f"- **Health**: {progress['health']}")
    lines.append(f"- **Trend**: {progress['summary']}")
    lines.append("")

    # Git Stats
    lines.append("## Git Activity")
    lines.append(f"- **Commits**: {stats['commit_count']}")
    lines.append(f"- **Files Changed**: {stats['files_changed']}")
    lines.append(f"- **Insertions**: +{stats['insertions']}")
    lines.append(f"- **Deletions**: -{stats['deletions']}")
    lines.append(f"- **Commits/Day**: {stats['commit_frequency']:.1f}")
    if stats.get("authors"):
        lines.append("")
        lines.append("### Contributors")
        for author, info in stats["authors"].items():
            lines.append(f"- **{author}**: {info['count']} commits, +{info['insertions']}/-{info['deletions']}")
    lines.append("")

    # Issue Stats
    lines.append("## Issues")
    lines.append(f"- **Total**: {issues['total']}")
    lines.append(f"- **Open**: {issues['open']}")
    lines.append(f"- **Closed**: {issues['closed']}")
    lines.append(f"- **Completion Rate**: {progress['completion_rate']:.1%}")
    if issues.get("by_label"):
        lines.append("")
        lines.append("### By Label")
        for label, count in sorted(issues["by_label"].items(), key=lambda x: -x[1]):
            lines.append(f"- {label}: {count}")
    lines.append("")

    # Charts
    if stats.get("daily_commits"):
        lines.append("## Daily Commit Trend")
        lines.append("```")
        lines.append(generate_trend_chart(stats["daily_commits"]))
        lines.append("```")
        lines.append("")

    return "\n".join(lines)
