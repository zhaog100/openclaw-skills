# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""GitHub issue tracker using gh CLI."""

import subprocess
import json
from collections import defaultdict


def _run_gh(args):
    """Run a gh CLI command and return parsed JSON."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh command failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def track_issues(repo_owner, repo_name, state="all"):
    """Track issues for a GitHub repo."""
    issues = _run_gh([
        "issue", "list",
        "--repo", f"{repo_owner}/{repo_name}",
        "--state", state,
        "--json", "number,title,state,labels,milestone,assignees",
        "--limit", "1000"
    ])

    total = len(issues)
    open_count = sum(1 for i in issues if i["state"] == "OPEN")
    closed_count = sum(1 for i in issues if i["state"] == "CLOSED")

    by_label = defaultdict(int)
    by_milestone = defaultdict(int)
    by_assignee = defaultdict(int)

    for issue in issues:
        for label in (issue.get("labels") or []):
            by_label[label.get("name", "unknown")] += 1
        ms = issue.get("milestone")
        if ms:
            by_milestone[ms.get("title", "untitled")] += 1
        else:
            by_milestone["No Milestone"] += 1
        for assignee in (issue.get("assignees") or []):
            by_assignee[assignee.get("login", "unknown")] += 1

    return {
        "total": total,
        "open": open_count,
        "closed": closed_count,
        "by_label": dict(by_label),
        "by_milestone": dict(by_milestone),
        "by_assignee": dict(by_assignee),
        "issues": issues,
    }
