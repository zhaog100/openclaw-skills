# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""Comprehensive tests for project-progress-tracker. No network required."""

import json
import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.git_analyzer import analyze_commits
from src.issue_tracker import track_issues
from src.progress_evaluator import evaluate
from src.report_generator import generate_markdown, generate_ascii_chart, generate_trend_chart

# ─── Sample Data ───────────────────────────────────────────────

MOCK_GIT_LOG = (
    "abc1234|Alice|alice@example.com|2026-03-15|feat: add login\n"
    " 3 files changed, 50 insertions(+), 10 deletions(-)\n"
    "\n"
    "def5678|Bob|bob@example.com|2026-03-14|fix: bug in parser\n"
    " 1 file changed, 5 insertions(+), 2 deletions(-)\n"
    "\n"
    "ghi9012|Alice|alice@example.com|2026-03-13|docs: update readme\n"
    " 1 file changed, 20 insertions(+), 0 deletions(-)\n"
    "\n"
    "jkl3456|Bob|bob@example.com|2026-03-12|refactor: clean up utils\n"
    " 2 files changed, 30 insertions(+), 15 deletions(-)\n"
    "\n"
    "mno7890|Alice|alice@example.com|2026-03-10|test: add unit tests\n"
    " 4 files changed, 100 insertions(+), 5 deletions(-)\n"
)

MOCK_GIT_LOG_EMPTY = ""

MOCK_GIT_LOG_NO_SHORTSTAT = (
    "abc1234|Alice|alice@example.com|2026-03-15|feat: add login\n"
)

MOCK_ISSUES = json.dumps([
    {"number": 1, "title": "Bug fix", "state": "CLOSED", "labels": [{"name": "bug"}], "milestone": {"title": "v1.0"}, "assignees": [{"login": "alice"}]},
    {"number": 2, "title": "New feature", "state": "OPEN", "labels": [{"name": "feature"}], "milestone": {"title": "v1.0"}, "assignees": [{"login": "bob"}]},
    {"number": 3, "title": "Documentation", "state": "OPEN", "labels": [{"name": "docs"}], "milestone": None, "assignees": []},
    {"number": 4, "title": "Refactor", "state": "CLOSED", "labels": [{"name": "refactor"}, {"name": "tech-debt"}], "milestone": {"title": "v1.1"}, "assignees": [{"login": "alice"}]},
])

MOCK_ISSUES_EMPTY = "[]"

SAMPLE_GIT_STATS = {
    "commit_count": 5,
    "files_changed": 11,
    "insertions": 205,
    "deletions": 32,
    "commit_frequency": 0.71,
    "daily_commits": {"2026-03-15": 1, "2026-03-14": 1, "2026-03-13": 1, "2026-03-12": 1, "2026-03-10": 1},
    "authors": {"Alice": {"count": 3, "insertions": 170, "deletions": 15}, "Bob": {"count": 2, "insertions": 35, "deletions": 17}},
}

SAMPLE_ISSUE_STATS = {
    "total": 4, "open": 2, "closed": 2,
    "by_label": {"bug": 1, "feature": 1, "docs": 1, "refactor": 1, "tech-debt": 1},
    "by_milestone": {"v1.0": 2, "v1.1": 1, "No Milestone": 1},
    "by_assignee": {"alice": 2, "bob": 1},
}


# ─── git_analyzer tests ────────────────────────────────────────

class TestGitAnalyzer(unittest.TestCase):

    @patch("src.git_analyzer._run_git")
    def test_analyze_commits_basic(self, mock_run):
        mock_run.return_value = MOCK_GIT_LOG
        result = analyze_commits("/fake/repo", days=7)
        self.assertEqual(result["commit_count"], 5)
        self.assertEqual(result["files_changed"], 11)
        self.assertEqual(result["insertions"], 205)
        self.assertEqual(result["deletions"], 32)
        self.assertEqual(len(result["authors"]), 2)

    @patch("src.git_analyzer._run_git")
    def test_analyze_commits_empty(self, mock_run):
        mock_run.return_value = MOCK_GIT_LOG_EMPTY
        result = analyze_commits("/fake/repo", days=7)
        self.assertEqual(result["commit_count"], 0)
        self.assertEqual(result["files_changed"], 0)

    @patch("src.git_analyzer._run_git")
    def test_analyze_authors(self, mock_run):
        mock_run.return_value = MOCK_GIT_LOG
        result = analyze_commits("/fake/repo", days=7)
        self.assertIn("Alice", result["authors"])
        self.assertIn("Bob", result["authors"])
        self.assertEqual(result["authors"]["Alice"]["count"], 3)
        self.assertEqual(result["authors"]["Bob"]["count"], 2)

    @patch("src.git_analyzer._run_git")
    def test_commit_frequency(self, mock_run):
        mock_run.return_value = MOCK_GIT_LOG
        result = analyze_commits("/fake/repo", days=7)
        self.assertAlmostEqual(result["commit_frequency"], 5 / 7, places=2)

    @patch("src.git_analyzer._run_git")
    def test_daily_commits(self, mock_run):
        mock_run.return_value = MOCK_GIT_LOG
        result = analyze_commits("/fake/repo", days=7)
        self.assertEqual(result["daily_commits"]["2026-03-15"], 1)
        self.assertEqual(result["daily_commits"]["2026-03-10"], 1)

    @patch("src.git_analyzer._run_git")
    def test_no_shortstat(self, mock_run):
        mock_run.return_value = MOCK_GIT_LOG_NO_SHORTSTAT
        result = analyze_commits("/fake/repo", days=7)
        self.assertEqual(result["commit_count"], 1)
        self.assertEqual(result["files_changed"], 0)
        self.assertEqual(result["insertions"], 0)

    @patch("src.git_analyzer._run_git")
    def test_commits_list(self, mock_run):
        mock_run.return_value = MOCK_GIT_LOG
        result = analyze_commits("/fake/repo", days=7)
        self.assertEqual(len(result["commits"]), 5)
        self.assertEqual(result["commits"][0]["hash"], "abc1234")
        self.assertEqual(result["commits"][0]["subject"], "feat: add login")

    @patch("src.git_analyzer._run_git")
    def test_git_command_args(self, mock_run):
        mock_run.return_value = ""
        analyze_commits("/my/repo", days=14)
        call_args = mock_run.call_args[0]
        self.assertEqual(call_args[0], "/my/repo")
        self.assertIn("14 days ago", " ".join(call_args[1]))
        self.assertIn("log", call_args[1])


# ─── issue_tracker tests ───────────────────────────────────────

class TestIssueTracker(unittest.TestCase):

    @patch("src.issue_tracker._run_gh", return_value=json.loads(MOCK_ISSUES))
    def test_track_issues_basic(self, mock_run):
        result = track_issues("owner", "repo")
        self.assertEqual(result["total"], 4)
        self.assertEqual(result["open"], 2)
        self.assertEqual(result["closed"], 2)

    @patch("src.issue_tracker._run_gh", return_value=[])
    def test_track_issues_empty(self, mock_run):
        result = track_issues("owner", "repo")
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["open"], 0)

    @patch("src.issue_tracker._run_gh", return_value=json.loads(MOCK_ISSUES))
    def test_by_label(self, mock_run):
        result = track_issues("owner", "repo")
        self.assertIn("bug", result["by_label"])
        self.assertEqual(result["by_label"]["bug"], 1)
        self.assertEqual(result["by_label"]["refactor"], 1)

    @patch("src.issue_tracker._run_gh", return_value=json.loads(MOCK_ISSUES))
    def test_by_milestone(self, mock_run):
        result = track_issues("owner", "repo")
        self.assertEqual(result["by_milestone"]["v1.0"], 2)
        self.assertEqual(result["by_milestone"]["No Milestone"], 1)

    @patch("src.issue_tracker._run_gh", return_value=json.loads(MOCK_ISSUES))
    def test_by_assignee(self, mock_run):
        result = track_issues("owner", "repo")
        self.assertEqual(result["by_assignee"]["alice"], 2)
        self.assertEqual(result["by_assignee"]["bob"], 1)

    @patch("src.issue_tracker._run_gh")
    def test_gh_args(self, mock_run):
        mock_run.return_value = []
        track_issues("myorg", "myrepo", state="open")
        args = mock_run.call_args[0][0]
        self.assertIn("--repo", args)
        self.assertIn("myorg/myrepo", args)
        self.assertIn("--state", args)
        self.assertIn("open", args)

    @patch("src.issue_tracker._run_gh", return_value=json.loads(MOCK_ISSUES))
    def test_issues_list(self, mock_run):
        result = track_issues("owner", "repo")
        self.assertEqual(len(result["issues"]), 4)
        self.assertEqual(result["issues"][0]["title"], "Bug fix")


# ─── progress_evaluator tests ──────────────────────────────────

class TestProgressEvaluator(unittest.TestCase):

    def test_completion_rate(self):
        result = evaluate(SAMPLE_GIT_STATS, SAMPLE_ISSUE_STATS)
        self.assertAlmostEqual(result["completion_rate"], 0.5)

    def test_activity_score(self):
        result = evaluate(SAMPLE_GIT_STATS, SAMPLE_ISSUE_STATS)
        self.assertAlmostEqual(result["activity_score"], 0.71 / 5.0, places=2)

    def test_overall_score(self):
        result = evaluate(SAMPLE_GIT_STATS, SAMPLE_ISSUE_STATS)
        self.assertGreater(result["overall_score"], 0)
        self.assertLessEqual(result["overall_score"], 1)

    def test_health_good(self):
        stats = {**SAMPLE_GIT_STATS, "commit_frequency": 4.0}
        issues = {"total": 10, "closed": 8, "open": 2}
        result = evaluate(stats, issues)
        self.assertIn(result["health"], ["excellent", "good", "moderate", "needs_attention"])

    def test_health_needs_attention(self):
        stats = {"commit_frequency": 0.1, "daily_commits": {}}
        issues = {"total": 10, "closed": 1, "open": 9}
        result = evaluate(stats, issues)
        self.assertEqual(result["health"], "needs_attention")

    def test_health_excellent(self):
        stats = {"commit_frequency": 10, "daily_commits": {}}
        issues = {"total": 10, "closed": 10, "open": 0}
        result = evaluate(stats, issues)
        self.assertEqual(result["health"], "excellent")

    def test_trend_positive(self):
        stats = {"commit_frequency": 3, "daily_commits": {
            "2026-03-09": 1, "2026-03-10": 1, "2026-03-11": 1, "2026-03-12": 1,
            "2026-03-13": 3, "2026-03-14": 3, "2026-03-15": 3,
        }}
        issues = {"total": 4, "closed": 2, "open": 2}
        result = evaluate(stats, issues)
        self.assertGreater(result["trend"], 0)

    def test_trend_negative(self):
        stats = {"commit_frequency": 1, "daily_commits": {
            "2026-03-09": 5, "2026-03-10": 5, "2026-03-11": 5, "2026-03-12": 5,
            "2026-03-13": 1, "2026-03-14": 1, "2026-03-15": 1,
        }}
        issues = {"total": 4, "closed": 2, "open": 2}
        result = evaluate(stats, issues)
        self.assertLess(result["trend"], 0)

    def test_zero_issues(self):
        stats = {"commit_frequency": 1, "daily_commits": {}}
        issues = {"total": 0, "closed": 0, "open": 0}
        result = evaluate(stats, issues)
        self.assertEqual(result["completion_rate"], 0.0)

    def test_summary_format(self):
        result = evaluate(SAMPLE_GIT_STATS, SAMPLE_ISSUE_STATS)
        self.assertIn("Score:", result["summary"])
        self.assertIn("Health:", result["summary"])

    def test_all_scores_rounded(self):
        result = evaluate(SAMPLE_GIT_STATS, SAMPLE_ISSUE_STATS)
        # Check they have reasonable decimal precision
        for key in ["completion_rate", "activity_score", "overall_score", "trend"]:
            self.assertEqual(result[key], round(result[key], 4))


# ─── report_generator tests ────────────────────────────────────

class TestReportGenerator(unittest.TestCase):

    def test_markdown_has_headers(self):
        report = generate_markdown(SAMPLE_GIT_STATS, SAMPLE_ISSUE_STATS,
                                   {"overall_score": 0.6, "health": "good", "trend": 0.1,
                                    "completion_rate": 0.5, "activity_score": 0.7,
                                    "summary": "test"})
        self.assertIn("# 📊 Project Progress Report", report)
        self.assertIn("## Summary", report)
        self.assertIn("## Git Activity", report)
        self.assertIn("## Issues", report)

    def test_markdown_has_values(self):
        report = generate_markdown(SAMPLE_GIT_STATS, SAMPLE_ISSUE_STATS,
                                   {"overall_score": 0.6, "health": "good", "trend": 0.1,
                                    "completion_rate": 0.5, "activity_score": 0.7,
                                    "summary": "test"})
        self.assertIn("5", report)
        self.assertIn("205", report)

    def test_ascii_chart_basic(self):
        chart = generate_ascii_chart({"A": 10, "B": 20, "C": 5}, "Test Chart")
        self.assertIn("Test Chart", chart)
        self.assertIn("A", chart)
        self.assertIn("B", chart)
        self.assertIn("█", chart)

    def test_ascii_chart_empty(self):
        chart = generate_ascii_chart({}, "Empty")
        self.assertIn("no data", chart)

    def test_ascii_chart_all_zero(self):
        chart = generate_ascii_chart({"A": 0, "B": 0}, "Zero")
        self.assertIn("Zero", chart)

    def test_trend_chart(self):
        chart = generate_trend_chart({"2026-03-14": 3, "2026-03-15": 5, "2026-03-16": 2})
        self.assertIn("Daily Commits", chart)
        self.assertIn("●", chart)

    def test_trend_chart_empty(self):
        chart = generate_trend_chart({})
        self.assertIn("no data", chart)

    def test_trend_chart_all_zero(self):
        chart = generate_trend_chart({"2026-03-14": 0, "2026-03-15": 0})
        self.assertIn("Daily Commits", chart)

    def test_markdown_has_contributors(self):
        report = generate_markdown(SAMPLE_GIT_STATS, SAMPLE_ISSUE_STATS,
                                   {"overall_score": 0.6, "health": "good", "trend": 0.1,
                                    "completion_rate": 0.5, "activity_score": 0.7,
                                    "summary": "test"})
        self.assertIn("Alice", report)
        self.assertIn("Bob", report)

    def test_markdown_has_labels(self):
        report = generate_markdown(SAMPLE_GIT_STATS, SAMPLE_ISSUE_STATS,
                                   {"overall_score": 0.6, "health": "good", "trend": 0.1,
                                    "completion_rate": 0.5, "activity_score": 0.7,
                                    "summary": "test"})
        self.assertIn("bug", report)

    def test_ascii_chart_width_param(self):
        chart = generate_ascii_chart({"X": 100}, "W", width=20)
        lines = chart.strip().split('\n')
        bar_line = lines[1]
        # Should have blocks + padding = width
        self.assertIn("█", bar_line)

    def test_markdown_no_authors(self):
        stats = {**SAMPLE_GIT_STATS, "authors": {}}
        report = generate_markdown(stats, SAMPLE_ISSUE_STATS,
                                   {"overall_score": 0.6, "health": "good", "trend": 0.1,
                                    "completion_rate": 0.5, "activity_score": 0.7,
                                    "summary": "test"})
        self.assertIn("## Git Activity", report)

    def test_markdown_has_trend_section(self):
        report = generate_markdown(SAMPLE_GIT_STATS, SAMPLE_ISSUE_STATS,
                                   {"overall_score": 0.6, "health": "good", "trend": 0.1,
                                    "completion_rate": 0.5, "activity_score": 0.7,
                                    "summary": "test"})
        self.assertIn("## Daily Commit Trend", report)


if __name__ == "__main__":
    unittest.main()
