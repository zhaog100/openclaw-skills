# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""Core pipeline orchestrator."""

from .git_analyzer import analyze_commits
from .issue_tracker import track_issues
from .progress_evaluator import evaluate
from .report_generator import generate_markdown


def run_analysis(repo_path, repo_owner, repo_name, days=7):
    """Run full project progress analysis."""
    git_stats = analyze_commits(repo_path, days)
    issue_stats = track_issues(repo_owner, repo_name)
    progress = evaluate(git_stats, issue_stats)
    report = generate_markdown(git_stats, issue_stats, progress)
    return {
        "git_stats": git_stats,
        "issue_stats": issue_stats,
        "progress": progress,
        "report": report,
    }
