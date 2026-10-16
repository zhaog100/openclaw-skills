#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 统一 git 推送入口（治 token 截断反复坑）
# 用法: bash scripts/git_push.sh [remote]   remote 默认 skills+origin
# 从 .env 读 GITHUB_TOKEN（Python 读，不靠 shell $(...) 截取 → 不再截断末尾字符）
set -u
cd /home/ubuntu/.openclaw/workspace
TARGETS="${1:-skills origin}"

python3 - <<'PYEOF'
import subprocess, os, re

env = open(".env").read()
m = re.search(r"GITHUB_TOKEN=***\n\".*?\]", env, re.DOTALL)
if not m:
    # fallback: 行首 GITHUB_TOKEN= 到行尾
    m = re.search(r"^GITHUB_TOKEN=***\n$]", env, re.MULTILINE)
if not m:
    print("❌ .env 里没有 GITHUB_TOKEN")
    raise SystemExit(1)
TOK = m.group(1).strip()
print(f"token 长度 {len(TOK)} 前缀 {TOK[:8]}...（完整读取，不经 shell）")

repos = {"skills": "zhaog100/openclaw-skills", "origin": "zhaog100/xiaomijiao-skills"}
for name in TARGETS.strip().split():
    if name not in repos:
        print(f"[{name}] 未知 remote，跳过"); continue
    repo = repos[name]
    url = f"https://zhaog100:***}@github.com/{repo}.git"
    subprocess.run(["git", "remote", "set-url", name, url], capture_output=True)
    r = subprocess.run(["git", "push", name, "main"], capture_output=True, text=True, timeout=90)
    print(f"[{name}] push {'✅ OK' if r.returncode==0 else '❌ '+r.stderr.strip()[:150]}")
    subprocess.run(["git", "remote", "set-url", name, f"https://github.com/{repo}.git"], capture_output=True)
PYEOF
