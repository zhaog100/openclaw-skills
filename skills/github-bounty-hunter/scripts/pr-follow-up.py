#!/usr/bin/env python3
"""
GitHub Bounty Hunter - PR 跟进脚本
基于 bounty-pr-tracker.json 跟踪所有 PR 状态变化

使用：
  python3 pr-follow-up.py          # 检查所有 Open/Blocked PR
  python3 pr-follow-up.py --notify  # 检查并生成变化摘要（供通知用）
"""

import json
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # skills/github-bounty-hunter
WORKSPACE_DIR = BASE_DIR.parent.parent  # workspace
TRACKER_FILE = WORKSPACE_DIR / "data" / "bounty-pr-tracker.json"
STATE_FILE = TRACKER_FILE.parent / "pr-follow-up-state.json"


def gh_api(endpoint: str) -> dict:
    """调用 gh api，返回 JSON"""
    result = subprocess.run(
        ["gh", "api", endpoint],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        return {"error": result.stderr.strip()}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response"}


def load_tracker() -> dict:
    with open(TRACKER_FILE) as f:
        return json.load(f)


def save_tracker(tracker: dict):
    with open(TRACKER_FILE, "w") as f:
        json.dump(tracker, f, indent=2, ensure_ascii=False)
    tracker["updated"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_check": None, "changes": []}


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def check_pr(pr: dict) -> dict:
    """检查单个 PR 的当前状态"""
    changes = []
    
    if not pr.get("pr"):
        # 没有 PR（被屏蔽等），只记录
        return {"changes": changes, "current_status": pr["status"]}
    
    repo = pr["repo"]
    pr_num = pr["pr"]
    
    # 获取 PR 信息
    data = gh_api(f"repos/{repo}/pulls/{pr_num}"])
    if "error" in data:
        changes.append(f"⚠️ API错误: {data['error']}")
        return {"changes": changes, "current_status": pr["status"]}
    
    # 检查状态变化
    gh_state = "closed" if data.get("merged_at") else ("closed" if data.get("closed_at") else "open")
    if gh_state == "open" and data.get("merged_at"):
        gh_state = "merged"
    elif gh_state == "open" and data.get("closed_at"):
        gh_state = "closed"
    
    if pr["status"] != gh_state:
        changes.append(f"📌 状态变更: {pr['status']} → {gh_state}")
        pr["status"] = gh_state
    
    # 检查是否已合并
    if data.get("merged_at") and pr["status"] != "merged":
        pr["status"] = "merged"
        pr["merged_at"] = data["merged_at"]
        changes.append(f"🎉 已合并！{data['merged_at'][:10]}")
    
    # 检查 review 状态
    reviews = gh_api(f"repos/{repo}/pulls/{pr_num}/reviews"])
    if isinstance(reviews, list):
        latest_reviews = {}
        for r in reviews:
            author = r.get("user", {}).get("login", "")
            if author not in latest_reviews or r.get("submitted_at", "") > latest_reviews[author].get("submitted_at", ""):
                latest_reviews[author] = r
        
        new_reviews = []
        for author, r in latest_reviews.items():
            if author == "zhaog100":
                continue
            state = r.get("state", "")
            if state in ("APPROVED", "CHANGES_REQUESTED"):
                new_reviews.append(f"{author}: {state}")
        
        prev_reviews = pr.get("last_reviews", [])
        if new_reviews != prev_reviews:
            changes.append(f"📋 Review更新: {', '.join(new_reviews)}")
            pr["last_reviews"] = new_reviews
    
    # 检查评论数变化
    comments = data.get("comments", 0)
    prev_comments = pr.get("last_comment_count", 0)
    if comments != prev_comments:
        if comments > prev_comments:
            changes.append(f"💬 新增 {comments - prev_comments} 条评论 (共{comments}条)")
        pr["last_comment_count"] = comments
    
    # 检查 CI 状态
    checks = gh_api(f"repos/{repo}/commits/{data.get('head',{}).get('sha','')}/status"])
    if "state" in checks:
        ci_state = checks["state"]
        if ci_state != pr.get("last_ci_state"):
            if ci_state == "failure":
                changes.append(f"❌ CI 失败！")
            elif ci_state == "success":
                changes.append(f"✅ CI 通过")
            pr["last_ci_state"] = ci_state
    
    return {"changes": changes, "current_status": pr["status"]}


def main():
    notify_mode = "--notify" in sys.argv
    
    tracker = load_tracker()
    state = load_state()
    
    all_changes = []
    checked = 0
    
    for pr in tracker["prs"]:
        if pr["status"] in ("open", "blocked"):
            result = check_pr(pr)
            if result["changes"]:
                repo_short = pr["repo"]
                issue = pr["issue"]
                for change in result["changes"]:
                    line = f"[{repo_short} #{issue}] {change}"
                    all_changes.append(line)
                    print(line)
            checked += 1
    
    # 保存更新后的 tracker
    save_tracker(tracker)
    
    # 保存状态
    state["last_check"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    state["changes"] = all_changes
    save_state(state)
    
    # 输出摘要
    open_count = sum(1 for p in tracker["prs"] if p["status"] == "open")
    merged_count = sum(1 for p in tracker["prs"] if p["status"] == "merged")
    closed_count = sum(1 for p in tracker["prs"] if p["status"] == "closed")
    blocked_count = sum(1 for p in tracker["prs"] if p["status"] == "blocked")
    
    print(f"\n{'='*60}")
    print(f"📊 PR 跟进摘要 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  检查: {checked} | Open: {open_count} | Merged: {merged_count} | Closed: {closed_count} | Blocked: {blocked_count}")
    print(f"  变化: {len(all_changes)}")
    
    if all_changes:
        print(f"\n📋 需要关注的变更:")
        for c in all_changes:
            print(f"  • {c}")
    else:
        print(f"\n✅ 无新变化")
    
    return 0 if not all_changes or not notify_mode else 1


if __name__ == "__main__":
    main()
