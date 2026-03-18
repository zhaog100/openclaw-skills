#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bounty Scanner 单元测试

版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
GitHub: https://github.com/zhaog100/xiaomila-personal-skills
ClawHub: https://clawhub.com
"""

import json
import sys
import tempfile
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.bounty_hunter.bounty_scanner import BountyScanner, BountyIssue


class TestBountyScanner:
    """BountyScanner unit tests"""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        config_path = Path(self.tmpdir) / "bounty_config.json"
        with open(config_path, "w") as f:
            json.dump({
                "preferred_languages": ["Go", "Python", "TypeScript"],
                "skip_languages": ["Rust", "Scala"],
            }, f)
        self.scanner = BountyScanner(str(config_path))

    def test_init_loads_config(self):
        assert self.scanner.preferred == ["Go", "Python", "TypeScript"]
        assert self.scanner.skip_langs == ["Rust", "Scala"]

    def test_init_default_config(self):
        scanner = BountyScanner("/nonexistent/path.json")
        assert scanner.config == {}

    def test_should_skip_rust(self):
        issue = BountyIssue(repo="test/test", number=1, title="test", url="http://x",
                            language="Rust")
        assert self.scanner.should_skip(issue) is True

    def test_should_skip_scala(self):
        issue = BountyIssue(repo="test/test", number=1, title="test", url="http://x",
                            language="Scala")
        assert self.scanner.should_skip(issue) is True

    def test_should_not_skip_go(self):
        issue = BountyIssue(repo="test/test", number=1, title="test", url="http://x",
                            language="Go", existing_prs=0, attempts=0)
        assert self.scanner.should_skip(issue) is False

    def test_should_not_skip_python(self):
        issue = BountyIssue(repo="test/test", number=1, title="test", url="http://x",
                            language="Python", existing_prs=0, attempts=0)
        assert self.scanner.should_skip(issue) is False

    def test_should_skip_too_many_prs(self):
        issue = BountyIssue(repo="test/test", number=1, title="test", url="http://x",
                            language="Python", existing_prs=5, attempts=0)
        assert self.scanner.should_skip(issue) is True

    def test_should_skip_too_many_attempts(self):
        issue = BountyIssue(repo="test/test", number=1, title="test", url="http://x",
                            language="Python", existing_prs=0, attempts=5)
        assert self.scanner.should_skip(issue) is True

    def test_calculate_score_preferred_lang(self):
        issue = BountyIssue(repo="test/test", number=1, title="test", url="http://x",
                            language="Python", existing_prs=0, attempts=0,
                            bounty_amount=50.0)
        score = self.scanner.calculate_score(issue)
        assert score >= 65  # amount(40) + language(25) + competition(25)

    def test_calculate_score_skip_lang(self):
        issue = BountyIssue(repo="test/test", number=1, title="test", url="http://x",
                            language="Rust", existing_prs=0, attempts=0)
        score = self.scanner.calculate_score(issue)
        assert issue.skip_reason != ""
        assert score <= 25  # only competition(25) + platform(5)=30, language bonus skipped

    def test_extract_bounty_amount(self):
        labels = [{"name": "bounty"}, {"name": "$200"}]
        amount = BountyScanner._extract_bounty_amount(labels)
        assert amount == 200.0

    def test_extract_bounty_amount_none(self):
        labels = [{"name": "bug"}, {"name": "help wanted"}]
        amount = BountyScanner._extract_bounty_amount(labels)
        assert amount is None

    def test_scan_all_returns_list(self):
        # Without gh CLI, should return empty list without crashing
        results = self.scanner.scan_all()
        assert isinstance(results, list)

    def test_calculate_score_competition_penalty(self):
        issue1 = BountyIssue(repo="t/t", number=1, title="t", url="http://x",
                             language="Go", existing_prs=0, attempts=0)
        issue2 = BountyIssue(repo="t/t", number=2, title="t", url="http://x",
                             language="Go", existing_prs=2, attempts=2)
        s1 = self.scanner.calculate_score(issue1)
        s2 = self.scanner.calculate_score(issue2)
        assert s1 > s2  # Less competition = higher score


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
