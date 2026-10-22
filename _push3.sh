#!/bin/bash
set -e
cd /home/ubuntu/.openclaw/workspace

TOKEN=*** -oE 'ghp_[A-Za-z0-9]{36,40}' .env | head -1)

# 修 .git-credentials
printf 'https://zhaog100:%s@github.com\n' "$TOKEN" > .git-credentials
chmod 600 .git-credentials
echo "凭证已修"

# 推主仓 origin
git remote set-url origin "https://zhaog100:${TOKEN}@github.com/zhaog100/xiaomijiao-skills.git"
git push origin main 2>&1 | tail -3
git remote set-url origin "https://github.com/zhaog100/xiaomijiao-skills.git"

# 推技能仓 skills
git remote set-url skills "https://zhaog100:${TOKEN}@github.com/zhaog100/openclaw-skills.git"
git push skills main 2>&1 | tail -3
git remote set-url skills "https://github.com/zhaog100/openclaw-skills.git"

echo "=== 完成 ==="
git log --oneline main -1
git log --oneline skills/main -1 2>/dev/null || echo "skills/main 未更新"
