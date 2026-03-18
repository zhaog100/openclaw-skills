#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量开发协调器 - fork/clone/dev/push/PR 全流程自动化

版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
GitHub: https://github.com/zhaog100/xiaomila-personal-skills
ClawHub: https://clawhub.com

功能：
- fork仓库 → clone → 创建分支 → 生成代码 → push → 创建PR
- 子代理并行开发（最大5个并发）
- PR格式：[BOUNTY #N] 描述，body含 /claim #N
- 自动 /attempt 认领
"""

import json
import logging
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .bounty_scanner import BountyIssue

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "bounty_config.json"
WORK_DIR = Path(os.environ.get("BOUNTY_WORK_DIR", "/tmp/bounty-work"))


@dataclass
class PRResult:
    """PR创建结果"""
    issue: BountyIssue
    success: bool
    pr_url: Optional[str] = None
    branch: Optional[str] = None
    error: Optional[str] = None


class BountyBatchDev:
    """批量开发协调器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path or str(DEFAULT_CONFIG_PATH))
        self.max_concurrent = self.config.get("max_concurrent_subagents", 5)
        self.pr_format = self.config.get("pr_format", {})
        self.work_dir = WORK_DIR
        self.work_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _load_config(path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _run(self, cmd: str, cwd: Optional[str] = None, check: bool = False) -> subprocess.CompletedProcess:
        return subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            cwd=cwd, timeout=120
        )

    def _format_title(self, issue: BountyIssue) -> str:
        template = self.pr_format.get("title", "[BOUNTY #{issue_number}] {description}")
        return template.format(issue_number=issue.number, description=issue.title)

    def _format_claim(self, issue: BountyIssue) -> str:
        template = self.pr_format.get("claim_body", "/claim #{issue_number}")
        return template.format(issue_number=issue.number)

    def _format_commit(self, issue: BountyIssue) -> str:
        template = self.pr_format.get("commit", "feat: {description} - Closes #{issue_number}")
        return template.format(issue_number=issue.number, description=issue.title)

    def _attempt_claim(self, issue: BountyIssue) -> bool:
        """Post /attempt comment to claim the bounty"""
        try:
            result = self._run(
                f'gh issue comment {issue.number} -R {issue.repo} '
                f'--body "/attempt"'
            )
            return result.returncode == 0
        except Exception as e:
            logger.error("Failed to post /attempt for %s#%d: %s", issue.repo, issue.number, e)
            return False

    def fork_repo(self, repo: str) -> bool:
        """Fork a GitHub repository"""
        result = self._run(f"gh repo fork {repo} --clone=false 2>&1")
        return result.returncode == 0

    def clone_and_setup(self, issue: BountyIssue) -> Optional[str]:
        """Clone forked repo and create feature branch, returns work dir path"""
        repo_name = issue.repo.split("/")[-1]
        local_path = self.work_dir / f"{repo_name}-{issue.number}"
        branch = f"bounty-{issue.number}"

        # Clone the fork (user's fork)
        result = self._run(f"gh repo fork {issue.repo} --clone=false 2>&1")
        if result.returncode != 0:
            # Might already be forked
            pass

        # Clone user's fork
        result = self._run(f"gh repo clone {issue.repo} {local_path} 2>&1")
        if result.returncode != 0:
            logger.error("Failed to clone %s: %s", issue.repo, result.stderr)
            return None

        # Create and checkout branch
        self._run(f"git checkout -b {branch}", cwd=str(local_path))
        return str(local_path)

    def push_and_create_pr(self, issue: BountyIssue, work_dir: str) -> PRResult:
        """Push changes and create PR"""
        branch = f"bounty-{issue.number}"
        commit_msg = self._format_commit(issue)
        title = self._format_title(issue)
        body = self._format_claim(issue)

        # Stage, commit, push
        self._run("git add -A", cwd=work_dir)
        r = self._run(f'git commit -m "{commit_msg}" --allow-empty', cwd=work_dir)
        if r.returncode != 0:
            return PRResult(issue=issue, success=False, error=r.stderr)

        r = self._run(f"git push origin {branch} --set-upstream 2>&1", cwd=work_dir)
        if r.returncode != 0:
            return PRResult(issue=issue, success=False, error=r.stderr)

        # Create PR
        r = self._run(
            f'gh pr create --title "{title}" --body "{body}" '
            f'-H {branch} -R {issue.repo} 2>&1',
            cwd=work_dir
        )
        if r.returncode != 0:
            return PRResult(issue=issue, success=False, error=r.stderr)

        # Extract PR URL
        pr_url = r.stdout.strip() if r.stdout else None
        return PRResult(issue=issue, success=True, pr_url=pr_url, branch=branch)

    def develop_single(self, issue: BountyIssue) -> PRResult:
        """Full pipeline for a single bounty"""
        # 1. Attempt claim
        self._attempt_claim(issue)

        # 2. Fork & clone
        work_dir = self.clone_and_setup(issue)
        if not work_dir:
            return PRResult(issue=issue, success=False, error="Clone failed")

        # 3. Development placeholder — in real use, a sub-agent generates code here
        logger.info("Development phase for %s#%d — code generation goes here", issue.repo, issue.number)

        # 4. Push & PR
        result = self.push_and_create_pr(issue, work_dir)
        if not result.success:
            return result

        # 5. Post /claim if PR created
        if issue.platform == "algora":
            self._run(
                f'gh issue comment {issue.number} -R {issue.repo} '
                f'--body "/claim {issue.number}"'
            )

        return result

    def batch_develop(self, issues: list[BountyIssue]) -> list[PRResult]:
        """Develop multiple bounties in parallel"""
        results = []
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            futures = {executor.submit(self.develop_single, iss): iss for iss in issues}
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    iss = futures[future]
                    results.append(PRResult(issue=iss, success=False, error=str(e)))
        return results
