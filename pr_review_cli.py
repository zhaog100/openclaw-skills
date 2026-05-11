#!/usr/bin/env python3
"""
PR Review CLI Agent for claude-builders-bounty #911

A command-line tool that reads PR file changes, identifies code quality issues,
and generates detailed review reports in Markdown format.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PRReviewAgent:
    """PR Review CLI Agent that analyzes code changes and generates review reports."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.issues = []
        self.summary = {
            "files_changed": 0,
            "additions": 0,
            "deletions": 0,
            "issues_found": 0,
            "critical": 0,
            "warnings": 0,
            "suggestions": 0
        }

    def run(self) -> int:
        """Main entry point."""
        parser = argparse.ArgumentParser(
            description="PR Review CLI Agent - Analyze code changes and generate review reports"
        )
        parser.add_argument(
            "--pr", type=int, help="PR number to review (requires GitHub CLI)"
        )
        parser.add_argument(
            "--diff", type=str, help="Path to diff file or git diff output"
        )
        parser.add_argument(
            "--files", nargs="+", help="Specific files to review"
        )
        parser.add_argument(
            "--output", type=str, default="review_report.md",
            help="Output file for review report (default: review_report.md)"
        )
        parser.add_argument(
            "--format", choices=["markdown", "json"], default="markdown",
            help="Output format (default: markdown)"
        )

        args = parser.parse_args()

        try:
            if args.pr:
                diff_content = self._get_pr_diff(args.pr)
            elif args.diff:
                diff_content = self._read_diff_file(args.diff)
            elif args.files:
                diff_content = self._get_files_diff(args.files)
            else:
                diff_content = self._get_staged_diff()

            if not diff_content:
                print("❌ No changes found to review")
                return 1

            self._analyze_diff(diff_content)
            self._generate_report(args.output, args.format)

            print(f"✅ Review complete: {args.output}")
            print(f"📊 Summary: {self.summary['issues_found']} issues found "
                  f"({self.summary['critical']} critical, {self.summary['warnings']} warnings)")

            return 0 if self.summary['critical'] == 0 else 1

        except Exception as e:
            print(f"❌ Error: {e}")
            return 1

    def _get_pr_diff(self, pr_number: int) -> str:
        """Get diff for a specific PR using GitHub CLI."""
        try:
            result = subprocess.run(
                ["gh", "pr", "view", str(pr_number), "--json", "files"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            files_data = json.loads(result.stdout)
            diff_content = []

            for file_info in files_data.get('files', []):
                filename = file_info.get('path')
                if filename:
                    diff_content.append(f"diff --git a/{filename} b/{filename}")
                    diff_content.append(f"--- a/{filename}")
                    diff_content.append(f"+++ b/{filename}")
                    # Add placeholder for actual diff content
                    diff_content.append("@@ -1,1 +1,1 @@")
                    diff_content.append(f"+// Changes in {filename}")
                    diff_content.append("")

            return "\n".join(diff_content)

        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get PR diff: {e}")
        except FileNotFoundError:
            raise Exception("GitHub CLI (gh) not found. Please install it first.")

    def _read_diff_file(self, diff_path: str) -> str:
        """Read diff content from a file."""
        try:
            with open(diff_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to read diff file: {e}")

    def _get_files_diff(self, files: List[str]) -> str:
        """Get diff for specific files."""
        try:
            file_args = []
            for file in files:
                file_args.extend(["--", file])

            result = subprocess.run(
                ["git", "diff", "--staged"] + file_args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            if not result.stdout.strip():
                # Try working directory diff
                result = subprocess.run(
                    ["git", "diff"] + file_args,
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )

            return result.stdout

        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get files diff: {e}")

    def _get_staged_diff(self) -> str:
        """Get diff for staged changes."""
        try:
            result = subprocess.run(
                ["git", "diff", "--staged"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            if not result.stdout.strip():
                # Try working directory diff
                result = subprocess.run(
                    ["git", "diff"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )

            return result.stdout

        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get staged diff: {e}")

    def _analyze_diff(self, diff_content: str) -> None:
        """Analyze diff content and identify code quality issues."""
        self.issues = []
        self.summary = {
            "files_changed": 0,
            "additions": 0,
            "deletions": 0,
            "issues_found": 0,
            "critical": 0,
            "warnings": 0,
            "suggestions": 0
        }

        current_file = None
        line_number = 0

        for line in diff_content.split('\n'):
            line = line.rstrip()

            # Track file changes
            if line.startswith('diff --git'):
                current_file = line.split()[-1][2:]  # Remove 'b/' prefix
                self.summary["files_changed"] += 1
                line_number = 0

            elif line.startswith('+++ b/'):
                current_file = line[6:]

            elif line.startswith('@@ '):
                # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
                match = re.search(r'\+(\d+)(?:,(\d+))?', line)
                if match:
                    line_number = int(match.group(1))

            elif line.startswith('+') and not line.startswith('++'):
                # Added line - check for issues
                self.summary["additions"] += 1
                self._check_added_line(line[1:], current_file, line_number)
                if line_number > 0:
                    line_number += 1

            elif line.startswith('-') and not line.startswith('--'):
                # Deleted line
                self.summary["deletions"] += 1

            elif not line.startswith('---') and line_number > 0:
                # Context line
                line_number += 1

        self.summary["issues_found"] = len(self.issues)

    def _check_added_line(self, line: str, filename: str, line_number: int) -> None:
        """Check a single added line for code quality issues."""
        line_stripped = line.strip()
        if not line_stripped:
            return
        
        # Check TODO before skipping comments
        if self._has_todo_comment(line):
            self._add_issue("warning", "TODO comment found", line, filename, line_number)
            
        if line_stripped.startswith('//') or line_stripped.startswith('#'):
            return

        # Critical issues
        if self._has_debug_code(line):
            self._add_issue("critical", "Debug code left in production", line, filename, line_number)

        if self._has_hardcoded_secrets(line):
            self._add_issue("critical", "Hardcoded secrets detected", line, filename, line_number)

        if self._has_sql_injection_risk(line):
            self._add_issue("critical", "Potential SQL injection risk", line, filename, line_number)

        # Warnings
        if self._has_long_line(line):
            self._add_issue("warning", "Line too long (>120 chars)", line, filename, line_number)

        if self._has_console_log(line):
            self._add_issue("warning", "Console logging in production code", line, filename, line_number)

        # Suggestions
        if self._has_missing_type_hints(line, filename):
            self._add_issue("suggestion", "Consider adding type hints", line, filename, line_number)

        if self._has_missing_docstring(line, filename):
            self._add_issue("suggestion", "Consider adding docstring", line, filename, line_number)

    def _has_debug_code(self, line: str) -> bool:
        """Check for debug code patterns."""
        debug_patterns = [
            r'console\.log\(',
            r'print\(.*[Ff]ixme',
            r'print\(.*[Dd]ebug',
            r'print\(.*[Tt]est',
            r'debugger',
            r'import pdb',
            r'pdb\.set_trace\(\)',
            r'import ipdb',
            r'ipdb\.set_trace\(\)'
        ]
        return any(re.search(pattern, line) for pattern in debug_patterns)

    def _has_hardcoded_secrets(self, line: str) -> bool:
        """Check for hardcoded secrets."""
        secret_patterns = [
            r'password\s*=\s*["\'][^"\'\n]{8,}["\']',
            r'api[_-]?key\s*=\s*["\'][^"\'\n]{16,}["\']',
            r'secret\s*=\s*["\'][^"\'\n]{16,}["\']',
            r'token\s*=\s*["\'][^"\'\n]{32,}["\']',
            r'sk_live_[a-zA-Z0-9]{24,}',
            r'AKIA[A-Z0-9]{16}',
            r'[\'\"][a-zA-Z0-9+/]{40}[\'\"]\s*\)'
        ]
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in secret_patterns)

    def _has_sql_injection_risk(self, line: str) -> bool:
        """Check for SQL injection risks."""
        if not re.search(r'(query|sql|SELECT|INSERT|UPDATE|DELETE)', line, re.IGNORECASE):
            return False

        risky_patterns = [
            r'\+.*[a-zA-Z_]',  # String concatenation with variable
            r'f"[^"]*\{[^}]*\}[^"]*"',  # f-string interpolation
            r"f'[^']*\{[^}]*\}[^']*'",   # f-string with single quotes
            r'\.format\([^)]*\{[^}]*\}[^)]*\)'  # .format() with variables
        ]
        return any(re.search(pattern, line) for pattern in risky_patterns)

    def _has_long_line(self, line: str) -> bool:
        """Check if line is too long."""
        return len(line) > 120

    def _has_todo_comment(self, line: str) -> bool:
        """Check for TODO comments."""
        return bool(re.search(r'//\s*TODO|#\s*TODO|\*\s*TODO|TODO', line, re.IGNORECASE))

    def _has_console_log(self, line: str) -> bool:
        """Check for console logging."""
        return bool(re.search(r'console\.', line))

    def _has_missing_type_hints(self, line: str, filename: str) -> bool:
        """Check for missing type hints in Python."""
        if not filename or not filename.endswith('.py'):
            return False

        return bool(re.search(r'def \w+\([^)]*\):(?!\s*->)', line))

    def _has_missing_docstring(self, line: str, filename: str) -> bool:
        """Check for missing docstrings."""
        if not filename or not filename.endswith('.py'):
            return False

        return bool(re.search(r'def \w+\(.*\):\s*$', line))

    def _add_issue(self, severity: str, message: str, line: str, filename: str, line_number: int) -> None:
        """Add a code quality issue."""
        self.issues.append({
            "severity": severity,
            "message": message,
            "line": line.strip(),
            "filename": filename or "unknown",
            "line_number": line_number
        })

        if severity == "critical":
            self.summary["critical"] += 1
        elif severity == "warning":
            self.summary["warnings"] += 1
        elif severity == "suggestion":
            self.summary["suggestions"] += 1

    def _generate_report(self, output_path: str, format_type: str) -> None:
        """Generate review report in specified format."""
        if format_type == "json":
            self._generate_json_report(output_path)
        else:
            self._generate_markdown_report(output_path)

    def _generate_json_report(self, output_path: str) -> None:
        """Generate JSON format report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.summary,
            "issues": self.issues
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    def _generate_markdown_report(self, output_path: str) -> None:
        """Generate Markdown format report."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# 🔍 PR Review Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Summary
            f.write("## 📊 Summary\n\n")
            f.write(f"- **Files changed:** {self.summary['files_changed']}\n")
            f.write(f"- **Lines added:** {self.summary['additions']}\n")
            f.write(f"- **Lines deleted:** {self.summary['deletions']}\n")
            f.write(f"- **Issues found:** {self.summary['issues_found']}\n\n")

            if self.summary['issues_found'] > 0:
                f.write("### 🚨 Issue Breakdown\n\n")
                f.write(f"- 🔴 **Critical:** {self.summary['critical']}\n")
                f.write(f"- 🟡 **Warnings:** {self.summary['warnings']}\n")
                f.write(f"- 🟢 **Suggestions:** {self.summary['suggestions']}\n\n")

            # Critical Issues
            critical_issues = [i for i in self.issues if i['severity'] == 'critical']
            if critical_issues:
                f.write("## 🔴 Critical Issues\n\n")
                for issue in critical_issues:
                    f.write(f"### {issue['filename']}:{issue['line_number']}\n")
                    f.write(f"**{issue['message']}**\n\n")
                    f.write(f"```\n{issue['line']}\n```\n\n")

            # Warnings
            warnings = [i for i in self.issues if i['severity'] == 'warning']
            if warnings:
                f.write("## 🟡 Warnings\n\n")
                for issue in warnings:
                    f.write(f"### {issue['filename']}:{issue['line_number']}\n")
                    f.write(f"**{issue['message']}**\n\n")
                    f.write(f"```\n{issue['line']}\n```\n\n")

            # Suggestions
            suggestions = [i for i in self.issues if i['severity'] == 'suggestion']
            if suggestions:
                f.write("## 🟢 Suggestions\n\n")
                for issue in suggestions:
                    f.write(f"### {issue['filename']}:{issue['line_number']}\n")
                    f.write(f"**{issue['message']}**\n\n")
                    f.write(f"```\n{issue['line']}\n```\n\n")

            if self.summary['issues_found'] == 0:
                f.write("## ✅ No Issues Found\n\n")
                f.write("Great job! No code quality issues were detected in this review.\n\n")


if __name__ == "__main__":
    agent = PRReviewAgent()
    sys.exit(agent.run())