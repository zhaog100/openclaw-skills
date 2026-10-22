#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 统一 git 推送入口（治 token 截断反复 401 的坑）
# 用法: bash scripts/git_push.sh [skills|origin|双推]
# 从 .env 读 GITHUB_TOKEN（Python 逐行字符串读，不经 shell 截取 → 不再截断末尾字符）
set -u
cd "$HOME/.openclaw/workspace"
TARGETS="${1:-skills origin}"

python3 - "$TARGETS" <<'PYEOF'
import subprocess, sys

targets = sys.argv[1].split()

# 逐行读 .env，取 GITHUB_TOKEN= 后面的 40 位 ghp token（纯字符串，不用易错正则）
TOK = ""
for line in open(".env"):
    s = line.strip()
    if s.startswith("GITHUB_TOKEN="):
        cand = s.split("=", 1)[1].strip().strip('"').strip("'")
        # 取候选里第一个 40 位的 ghp_ token
        i = cand.find("ghp_")
        if i >= 0:
            tail = cand[i:i+40]
            if len(tail) == 40 and all(c.isalnum() for c in tail[4:]):
                TOK = tail
                break
if not TOK:
    print("❌ .env 里没找到 40 位 GITHUB_TOKEN")
    sys.exit(1)
print(f"token 长度 {len(TOK)} 前缀 {TOK[:8]}...（完整读取，不经 shell）")

repos = {"skills": "zhaog100/openclaw-skills", "origin": "zhaog100/xiaomijiao-skills"}
for name in targets:
    if name not in repos:
        print(f"[{name}] 未知 remote，跳过"); continue
    repo = repos[name]
    url = "https://zhaog100:" + TOK + "@github.com/" + repo + ".git"
    subprocess.run(["git", "remote", "set-url", name, url], capture_output=True)
    r = subprocess.run(["git", "push", name, "main"], capture_output=True, text=True, timeout=90)
    print(f"[{name}] push " + ("✅ OK" if r.returncode == 0 else "❌ " + r.stderr.strip()[:150]))
    subprocess.run(["git", "remote", "set-url", name, "https://github.com/" + repo + ".git"], capture_output=True)
PYEOF
