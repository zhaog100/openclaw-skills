#!/usr/bin/env python3
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""PR 状态自动更新：扫 zhaog100 名下所有仓库的 PR 状态，刷新台账 CSV。

- 走 GitHub API（token 从 .env 读）
- 输出: 更新 data/pr_status.csv（PR 全量状态台账，含 open/merged/closed + 更新时间）
- 用法: python3 pr_updater.py [--owner zhaog100] [--max-repos 20]
"""
import os, sys, json, time, csv, argparse
import urllib.request

def _token() -> str:
    """token 优先级: 环境变量 > workspace/.env > bounty/.env"""
    env_tok = os.environ.get("GITHUB_TOKEN", "")
    if env_tok and len(env_tok) == 40:
        return env_tok
    for p in ["/home/ubuntu/.openclaw/workspace/.env",
              os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")]:
        if os.path.exists(p):
            for l in open(p):
                if l.startswith("GITHUB_TOKEN="):
                    v = l.strip().split("=", 1)[1].strip()
                    if len(v) == 40:
                        return v
    return env_tok

def _api(path: str, tok: str, timeout=20) -> dict:
    req = urllib.request.Request(
        f"https://api.github.com/{path}",
        headers={"Authorization": f"token {tok}", "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)[:80]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner", default="zhaog100")
    ap.add_argument("--max-repos", type=int, default=20)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "pr_status.csv"))
    a = ap.parse_args()
    tok = _token()
    if not tok:
        print("ERROR: GITHUB_TOKEN 未设置"); sys.exit(1)

    # 1. 列仓库
    repos = _api(f"users/{a.owner}/repos?per_page=100&type=owner", tok)
    if isinstance(repos, dict) and repos.get("error"):
        print(f"拉仓库失败: {repos['error']}"); sys.exit(1)
    repos = repos[:a.max_repos]
    print(f"扫描 {len(repos)} 个仓库的 PR 状态...")

    rows = []
    for repo in repos:
        name = repo.get("full_name")
        prs = _api(f"repos/{name}/pulls?state=all&per_page=30", tok)
        if isinstance(prs, dict) and prs.get("error"):
            continue
        for pr in prs:
            rows.append({
                "repo": name,
                "pr": pr.get("number"),
                "state": "merged" if pr.get("merged_at") else (pr.get("state")),
                "title": (pr.get("title") or "")[:60],
                "created": (pr.get("created_at") or "")[:10],
                "updated": (pr.get("updated_at") or "")[:10],
                "merged_at": (pr.get("merged_at") or "")[:10],
            })
        time.sleep(0.5)  # 限速

    # 2. 扫 zhaog100 作为 author 发在"别人仓库"的 PR（赏金 PR 全口径）
    print("扫描 zhaog100 作为作者的 PR（全口径，含发在别人仓的）...")
    try:
        search = _api("search/issues?q=author:zhaog100+is:pr+type:pr&per_page=100&sort=updated&order=desc", tok)
        items = search.get("items", []) if isinstance(search, dict) and not search.get("error") else []
        print(f"  search 返回 {len(items)} 条")
        for it in items:
            repo_full = (it.get("repository_url") or "").replace("https://api.github.com/repos/", "")
            rows.append({
                "repo": repo_full or "unknown",
                "pr": it.get("number"),
                "state": "merged" if it.get("pull_request", {}).get("merged_at") else it.get("state"),
                "title": (it.get("title") or "")[:60],
                "created": (it.get("created_at") or "")[:10],
                "updated": (it.get("updated_at") or "")[:10],
                "merged_at": (it.get("pull_request", {}).get("merged_at") or "")[:10] if isinstance(it.get("pull_request"), dict) else "",
            })
    except Exception as e:
        print(f"  search PR 失败: {str(e)[:50]}")

    # 写 CSV
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["repo", "pr", "state", "title", "created", "updated", "merged_at"])
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r["repo"], -(r["pr"] or 0))))
    print(f"✅ 已刷新 PR 台账: {a.out}（{len(rows)} 条 PR）")

if __name__ == "__main__":
    main()
