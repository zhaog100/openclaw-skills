#!/usr/bin/env python3
import subprocess, re, os, shutil

WS = "/home/ubuntu/.openclaw/workspace"
os.chdir(WS)

# 1) 从 .env 读 40 位有效 token
env = open(".env").read()
m = re.search(r"ghp_[A-Za-z0-9]{36,40}", env)
TOKEN = m.group(0)
print(f"[1] token 长度: {len(TOKEN)}")

# 2) 修 .git-credentials：正确的 user:token@github.com 形式
creds = f"https://zhaog100:{TOKEN}@github.com\n"
open(".git-credentials", "w").write(creds)
os.chmod(".git-credentials", 0o600)
print("[2] .git-credentials 已写（user:token@github.com 格式）")

# 3) 用 python 调 git，把 token 注入到 remote URL（不落 stdout 明文）
def git(*a, check=True):
    r = subprocess.run(["git", *a], capture_output=True, text=True, timeout=120)
    if check and r.returncode != 0:
        print("   GIT ERROR:", r.stderr.strip()[:200])
    return r

# 3a) 修 origin 的 URL（带 token 推，推完恢复脱敏）
git("remote", "set-url", "origin", f"https://zhaog100:{TOKEN}@github.com/zhaog100/xiaomijiao-skills.git")
r = git("push", "origin", "main")
print("[3a] 主仓 origin push:", "OK" if r.returncode == 0 else "FAIL")
git("remote", "set-url", "origin", "https://github.com/zhaog100/xiaomijiao-skills.git")

# 3b) 技能仓：先修 skills remote，把远端 5 个领先 commit 合进本地 main，再推
git("remote", "set-url", "skills", f"https://zhaog100:{TOKEN}@github.com/zhaog100/openclaw-skills.git")

# 3b-1) fetch 远端
git("fetch", "skills", "main")
print("[3b] fetch skills/main")

# 3b-2) 看远端领先本地 main 的 commit，逐个 cherry-pick 进 main（保守 rebase 思路）
# 远端 main tip = FETCH_HEAD，本地 main 不含它 → 把远端领先的 commit 合进来
r = git("log", "--oneline", "main..FETCH_HEAD", check=False)
remote_ahead = [l.split()[0] for l in r.stdout.strip().split("\n") if l.strip()]
print(f"[3b] 远端领先本地 {len(remote_ahead)} 个 commit:")
for c in remote_ahead:
    print("   ", c)

# 3b-3) merge（--no-ff 保留结构）远端线进本地 main
r = git("merge", "FETCH_HEAD", "--no-edit", "-m", "merge: 远端 openclaw-skills main 线对齐进本地 main")
print("[3b] merge FETCH_HEAD → main:", "OK" if r.returncode == 0 else "FAIL " + r.stderr[:150])

# 3b-4) 推技能仓
r = git("push", "skills", "main")
print("[3b] 技能仓 skills push:", "OK" if r.returncode == 0 else "FAIL " + r.stderr[:200])
git("remote", "set-url", "skills", "https://github.com/zhaog100/openclaw-skills.git")

print("=== 完成 ===")
