#!/bin/bash
# PR Review 监控脚本（每小时）
# 功能：检查所有PR的review/merge状态，有变化时通知
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

WORKSPACE="/root/.openclaw/workspace"
STATE_FILE="$WORKSPACE/data/pr_review_state.json"
LOG_FILE="/tmp/pr_monitor.log"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') [pr-monitor] $1" >> "$LOG_FILE"; }

cd "$WORKSPACE" || exit 1
mkdir -p data

# 需要监控的仓库
REPOS=(
  "Comfy-Org/ComfyUI"
  "Scottcjn/rustchain-bounties"
  "FinMind/finmind-api"
  "Autonomous-Aerial-Platform/APort"
)

# 收集当前PR状态
python3 -c "
import json, subprocess, sys

repos = $(printf '%s\n' "${REPOS[@]}" | jq -R . | jq -s .)

new_state = {}
for repo in repos:
    repo_str = repo.strip('\"')
    try:
        result = subprocess.run(
            ['gh', 'pr', 'list', '--repo', repo_str, '--author', 'zhaog100',
             '--state', 'open', '--json', 'number,title,state,reviewDecision,updatedAt'],
            capture_output=True, text=True, timeout=15
        )
        prs = json.loads(result.stdout)
        new_state[repo_str] = {}
        for pr in prs:
            new_state[repo_str][str(pr['number'])] = {
                'title': pr['title'][:60],
                'state': pr['state'],
                'review': pr.get('reviewDecision', 'PENDING'),
                'updated': pr.get('updatedAt', '')
            }
    except Exception as e:
        new_state[repo_str] = {'error': str(e)}

# 加载旧状态
old_state = {}
try:
    with open('$STATE_FILE') as f:
        old_state = json.load(f)
except:
    pass

# 对比变化
changes = []
for repo, prs in new_state.items():
    old_prs = old_state.get(repo, {})
    for num, info in prs.items():
        if num not in old_prs:
            changes.append(f'🆕 {repo}#{num}: {info[\"title\"]} [{info[\"review\"]}]')
        elif old_prs[num].get('review') != info.get('review'):
            old_r = old_prs[num].get('review', 'N/A')
            new_r = info.get('review', 'N/A')
            changes.append(f'📝 {repo}#{num}: review {old_r}→{new_r} — {info[\"title\"]}')
    # 检查已关闭/合并
    for num in old_prs:
        if num not in prs and num != 'error':
            changes.append(f'🏁 {repo}#{num}: closed/merged — {old_prs[num][\"title\"]}')

# 保存新状态
with open('$STATE_FILE', 'w') as f:
    json.dump(new_state, f, indent=2)

# 输出
open_count = sum(len(v) for v in new_state.values() if isinstance(v, dict))
print(f'Total open PRs: {open_count}')
if changes:
    print('CHANGES:')
    for c in changes:
        print(c)
" 2>&1 | tee -a "$LOG_FILE"
