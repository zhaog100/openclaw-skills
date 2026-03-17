# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""Git commit statistics analyzer."""

import subprocess
import re
from collections import defaultdict


def _run_git(repo_path, args):
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git", "-C", repo_path] + args,
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"git command failed: {result.stderr.strip()}")
    return result.stdout


def analyze_commits(repo_path, days=7):
    """Analyze git commits for the given repo and time range."""
    raw = _run_git(repo_path, [
        "log", f"--since={days} days ago",
        "--pretty=format:%h|%an|%ae|%ad|%s",
        "--shortstat", "--date=short"
    ])

    commits = []
    total_files = 0
    total_insertions = 0
    total_deletions = 0
    authors = defaultdict(lambda: {"count": 0, "insertions": 0, "deletions": 0})
    daily = defaultdict(int)

    # Parse commit blocks
    blocks = re.split(r'\n\n', raw.strip()) if raw.strip() else []

    for block in blocks:
        lines = block.strip().split('\n')
        header = lines[0]
        parts = header.split('|', 4)
        if len(parts) < 5:
            continue

        short_hash, author, email, date, subject = parts
        commits.append({
            "hash": short_hash,
            "author": author,
            "email": email,
            "date": date,
            "subject": subject,
        })
        authors[author]["count"] += 1
        daily[date] += 1

        # Parse shortstat lines
        for line in lines[1:]:
            m = re.match(r'\s*(\d+) file(?:s)? changed(?:,\s*(\d+) insertion(?:s)?\(\+\))?(?:,\s*(\d+) deletion(?:s)?\(-\))?', line)
            if m:
                files = int(m.group(1))
                ins = int(m.group(2) or 0)
                dels = int(m.group(3) or 0)
                total_files += files
                total_insertions += ins
                total_deletions += dels
                authors[author]["insertions"] += ins
                authors[author]["deletions"] += dels

    avg_per_day = len(commits) / max(days, 1)

    return {
        "commit_count": len(commits),
        "files_changed": total_files,
        "insertions": total_insertions,
        "deletions": total_deletions,
        "authors": dict(authors),
        "commit_frequency": avg_per_day,
        "daily_commits": dict(daily),
        "commits": commits,
    }
