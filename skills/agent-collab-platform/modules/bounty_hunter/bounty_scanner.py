#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bounty扫描器 - 搜索GitHub/Algora上的赏金任务

版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
GitHub: https://github.com/zhaog100/xiaomila-personal-skills
ClawHub: https://clawhub.com

功能：
- GitHub bounty标签issue搜索
- Algora平台bounty发现（/attempt机制）
- 金额评估和技术栈匹配
- 竞争分析（已有PR数量检查）
"""

import json
import logging
import re
import subprocess
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "bounty_config.json"


@dataclass
class BountyIssue:
    """赏金Issue数据模型"""
    repo: str
    number: int
    title: str
    url: str
    labels: list[str] = field(default_factory=list)
    bounty_amount: Optional[float] = None
    platform: str = "github"
    language: Optional[str] = None
    existing_prs: int = 0
    attempts: int = 0
    score: float = 0.0
    skip_reason: str = ""


class BountyScanner:
    """Bounty扫描器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path or str(DEFAULT_CONFIG_PATH))
        self.preferred = self.config.get("preferred_languages", ["Go", "Python", "TypeScript"])
        self.skip_langs = self.config.get("skip_languages", ["Rust", "Scala", "C++", "Swift", "Objective-C"])

    def _load_config(self, path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning("bounty_config.json not found or invalid, using defaults")
            return {}

    def _run_gh(self, args: list[str]) -> str:
        """Execute gh CLI command"""
        result = subprocess.run(
            ["gh"] + args, capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()

    def detect_language(self, issue: BountyIssue) -> Optional[str]:
        """Detect primary language from repo"""
        try:
            output = self._run_gh([
                "repo", "view", issue.repo, "--json", "primaryLanguage", "-q", ".primaryLanguage.name"
            ])
            return output if output and output != "null" else None
        except Exception:
            return None

    def count_existing_prs(self, issue: BountyIssue) -> int:
        """Count PRs referencing this issue"""
        try:
            output = self._run_gh([
                "search", "prs", f"repo:{issue.repo} {issue.number}",
                "--json", "number", "-q", "length"
            ])
            return int(output) if output.isdigit() else 0
        except Exception:
            return 0

    def count_attempts(self, issue: BountyIssue) -> int:
        """Count /attempt comments on Algora issues"""
        try:
            output = self._run_gh([
                "issue", "view", str(issue.number), "-R", issue.repo,
                "--json", "comments", "-q", ".comments[].body"
            ])
            return output.count("/attempt")
        except Exception:
            return 0

    def calculate_score(self, issue: BountyIssue) -> float:
        """Calculate bounty attractiveness score (0-100)"""
        score = 0.0

        # Amount score (0-40)
        if issue.bounty_amount:
            score += min(40, issue.bounty_amount / 2.5)  # $100 = full marks

        # Language preference (0-25)
        lang = issue.language or ""
        if lang in self.preferred:
            score += 25
        elif lang in self.skip_langs:
            issue.skip_reason = f"Language {lang} in skip list"

        # Competition score (0-25) - fewer PRs = higher score
        score += max(0, 25 - issue.existing_prs * 5 - issue.attempts * 5)

        # Platform bonus (0-10)
        if issue.platform == "algora":
            score += 5

        issue.score = score
        return score

    def should_skip(self, issue: BountyIssue) -> bool:
        """Check if bounty should be skipped"""
        lang = issue.language or ""
        if lang in self.skip_langs:
            return True
        if issue.existing_prs >= 3:
            return True
        if issue.attempts >= 3:
            return True
        return False

    def scan_github_bounties(self, query: Optional[str] = None) -> list[BountyIssue]:
        """Search GitHub for bounty-labeled issues"""
        query = query or "label:bounty state:open"
        issues = []

        try:
            output = self._run_gh([
                "search", "issues", query, "--limit", "50",
                "--json", "repository", "number", "title", "url", "labels"
            ])
            if not output:
                return issues

            data = json.loads(output)
            for item in data:
                repo = item.get("repository", {}).get("nameWithOwner", "")
                if not repo:
                    continue
                issue = BountyIssue(
                    repo=repo,
                    number=item["number"],
                    title=item["title"],
                    url=item["url"],
                    labels=[l["name"] for l in item.get("labels", [])],
                    platform="github"
                )
                issue.language = self.detect_language(issue)
                issue.existing_prs = self.count_existing_prs(issue)
                issue.bounty_amount = self._extract_bounty_amount(item.get("labels", []))
                self.calculate_score(issue)
                if not self.should_skip(issue):
                    issues.append(issue)
        except Exception as e:
            logger.error("Failed to scan GitHub bounties: %s", e)

        return issues

    def scan_algora_bounties(self) -> list[BountyIssue]:
        """Discover Algora bounties via /attempt comments"""
        issues = []
        try:
            output = self._run_gh([
                "search", "issues",
                "label:paid label:hacktoberfest OR label:bounty state:open",
                "--limit", "30",
                "--json", "repository", "number", "title", "url", "labels"
            ])
            if not output:
                return issues

            data = json.loads(output)
            for item in data:
                repo = item.get("repository", {}).get("nameWithOwner", "")
                if not repo:
                    continue
                issue = BountyIssue(
                    repo=repo,
                    number=item["number"],
                    title=item["title"],
                    url=item["url"],
                    labels=[l["name"] for l in item.get("labels", [])],
                    platform="algora"
                )
                issue.language = self.detect_language(issue)
                issue.attempts = self.count_attempts(issue)
                issue.existing_prs = self.count_existing_prs(issue)
                self.calculate_score(issue)
                if not self.should_skip(issue):
                    issues.append(issue)
        except Exception as e:
            logger.error("Failed to scan Algora bounties: %s", e)

        return issues

    def scan_all(self) -> list[BountyIssue]:
        """Run all scan strategies and return sorted results"""
        all_issues = self.scan_github_bounties() + self.scan_algora_bounties()
        # Deduplicate
        seen = set()
        unique = []
        for issue in all_issues:
            key = f"{issue.repo}#{issue.number}"
            if key not in seen:
                seen.add(key)
                unique.append(issue)
        unique.sort(key=lambda x: x.score, reverse=True)
        return unique

    @staticmethod
    def _extract_bounty_amount(labels: list[dict]) -> Optional[float]:
        """Extract bounty amount from labels like '$100'"""
        for label in labels:
            name = label.get("name", "")
            match = re.search(r"\$(\d+)", name)
            if match:
                return float(match.group(1))
        return None
