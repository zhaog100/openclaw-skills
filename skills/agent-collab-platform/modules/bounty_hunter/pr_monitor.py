#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PR状态监控 - 跟踪赏金PR的review/merge/付款状态

版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
GitHub: https://github.com/zhaog100/xiaomila-personal-skills
ClawHub: https://clawhub.com

功能：
- 定期检查所有PR的review状态
- Gmail付款通知监控
- 合并/关闭状态变更通知
"""

import json
import logging
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

STATE_FILE = Path("/tmp/bounty-pr-state.json")


class PRStatus(Enum):
    OPEN = "OPEN"
    REVIEW_REQUESTED = "REVIEW_REQUESTED"
    APPROVED = "APPROVED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    MERGED = "MERGED"
    CLOSED = "CLOSED"
    PAID = "PAID"


@dataclass
class TrackedPR:
    """Tracked PR with status history"""
    url: str
    repo: str
    number: int
    status: PRStatus = PRStatus.OPEN
    bounty_amount: Optional[float] = None
    last_checked: Optional[str] = None
    history: list[dict] = field(default_factory=list)
    review_count: int = 0


class PRMonitor:
    """PR状态监控器"""

    def __init__(self, state_file: Optional[str] = None):
        self.state_file = Path(state_file) if state_file else STATE_FILE
        self.tracked: dict[str, TrackedPR] = {}
        self._load_state()

    def _load_state(self):
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for url, pr_data in data.items():
                    pr_data["status"] = PRStatus(pr_data["status"])
                    self.tracked[url] = TrackedPR(**pr_data)
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            self.tracked = {}

    def _save_state(self):
        data = {}
        for url, pr in self.tracked.items():
            pr_dict = {
                "url": pr.url,
                "repo": pr.repo,
                "number": pr.number,
                "status": pr.status.value,
                "bounty_amount": pr.bounty_amount,
                "last_checked": pr.last_checked,
                "history": pr.history,
                "review_count": pr.review_count,
            }
            data[url] = pr_dict
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _run_gh(self, args: list[str]) -> str:
        result = subprocess.run(
            ["gh"] + args, capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()

    def add_pr(self, url: str, repo: str, number: int, bounty_amount: Optional[float] = None):
        """Track a new PR"""
        if url not in self.tracked:
            self.tracked[url] = TrackedPR(
                url=url, repo=repo, number=number,
                bounty_amount=bounty_amount,
                status=PRStatus.OPEN,
                last_checked=datetime.utcnow().isoformat()
            )
            self._save_state()

    def check_pr_status(self, url: str) -> Optional[PRStatus]:
        """Check current status of a PR"""
        pr = self.tracked.get(url)
        if not pr:
            return None

        try:
            # Check if merged or closed
            output = self._run_gh([
                "pr", "view", str(pr.number), "-R", pr.repo,
                "--json", "state", "reviewDecision", "reviews"
            ])
            if not output:
                return pr.status

            data = json.loads(output)
            state = data.get("state", "")
            review_decision = data.get("reviewDecision", "")
            reviews = data.get("reviews", [])

            old_status = pr.status

            if state == "MERGED":
                pr.status = PRStatus.MERGED
            elif state == "CLOSED":
                pr.status = PRStatus.CLOSED
            elif review_decision == "APPROVED":
                pr.status = PRStatus.APPROVED
            elif review_decision == "CHANGES_REQUESTED":
                pr.status = PRStatus.CHANGES_REQUESTED
            elif reviews:
                pr.status = PRStatus.REVIEW_REQUESTED
                pr.review_count = len(reviews)

            pr.last_checked = datetime.utcnow().isoformat()

            if old_status != pr.status:
                pr.history.append({
                    "from": old_status.value,
                    "to": pr.status.value,
                    "time": pr.last_checked,
                })

            self._save_state()
            return pr.status

        except Exception as e:
            logger.error("Failed to check PR %s: %s", url, e)
            return pr.status

    def check_all(self) -> list[dict]:
        """Check status of all tracked PRs, return changes"""
        changes = []
        for url in list(self.tracked.keys()):
            old = self.tracked[url].status
            new = self.check_pr_status(url)
            if old != new:
                changes.append({
                    "url": url,
                    "repo": self.tracked[url].repo,
                    "number": self.tracked[url].number,
                    "from": old.value,
                    "to": new.value,
                })
        return changes

    def get_summary(self) -> dict:
        """Get summary of all tracked PRs"""
        summary = {status.value: 0 for status in PRStatus}
        total_bounty = 0.0
        for pr in self.tracked.values():
            summary[pr.status.value] = summary.get(pr.status.value, 0) + 1
            if pr.status == PRStatus.PAID and pr.bounty_amount:
                total_bounty += pr.bounty_amount
        return {
            "total_prs": len(self.tracked),
            "by_status": summary,
            "total_earned": total_bounty,
        }

    def mark_paid(self, url: str):
        """Mark a PR as paid"""
        if url in self.tracked:
            self.tracked[url].status = PRStatus.PAID
            self.tracked[url].history.append({
                "from": self.tracked[url].status.value,
                "to": PRStatus.PAID.value,
                "time": datetime.utcnow().isoformat(),
                "note": "Payment confirmed",
            })
            self._save_state()
