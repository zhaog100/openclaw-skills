# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""Progress evaluator combining git stats and issue stats."""

def evaluate(git_stats, issue_stats, prd_path=None):
    """Evaluate overall project progress and return a score."""
    # Issue completion rate
    total = issue_stats.get("total", 0)
    closed = issue_stats.get("closed", 0)
    completion_rate = closed / total if total > 0 else 0.0

    # Code activity (normalized 0-1, 5+ commits/day = very active)
    commits_per_day = git_stats.get("commit_frequency", 0)
    activity_score = min(commits_per_day / 5.0, 1.0)

    # Overall score (weighted)
    overall = completion_rate * 0.6 + activity_score * 0.4

    # Trend: compare recent vs older daily commits
    daily = git_stats.get("daily_commits", {})
    dates = sorted(daily.keys())
    if len(dates) >= 7:
        recent = sum(daily[d] for d in dates[-3:]) / 3
        older = sum(daily[d] for d in dates[:4]) / 4 if len(dates) >= 4 else recent
        if older > 0:
            trend = (recent - older) / older
        else:
            trend = 1.0 if recent > 0 else 0.0
    else:
        trend = 0.0

    # Health assessment
    if overall >= 0.8:
        health = "excellent"
    elif overall >= 0.6:
        health = "good"
    elif overall >= 0.4:
        health = "moderate"
    else:
        health = "needs_attention"

    return {
        "completion_rate": round(completion_rate, 4),
        "activity_score": round(activity_score, 4),
        "overall_score": round(overall, 4),
        "trend": round(trend, 4),
        "health": health,
        "summary": f"Score: {overall:.1%} | Health: {health} | Trend: {'↑' if trend > 0 else '↓' if trend < 0 else '→'} {abs(trend):.1%}",
    }
