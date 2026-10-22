---
name: "skill-deployment-fixes"
<<<<<<< HEAD
description: "Common deployment pitfalls for OpenClaw skills: OpenCV headless, shebang ordering, token config, path fixes, QMD install."
=======
description: "部署OpenClaw技能时的经验：使用opencv-python-headless替代opencv-python避免OpenGL依赖问题，修复smart-model-switch重复shebang"
>>>>>>> skills/main
---

# Skill Deployment Fixes

<<<<<<< HEAD
## Problem 1: OpenCV OpenGL dependency

**Symptom:** `ImportError: libGL.so.1: cannot open shared object file`

**Fix:** Use headless variant (no GUI deps).
```bash
pip uninstall opencv-python -y && pip install opencv-python-headless
```
Applies to: image-content-extractor, terminal-ocr.

## Problem 2: Script shebang errors

**Symptom:** `SyntaxError: Invalid or unexpected token` or `bad interpreter`

**Cause:** Duplicate shebang lines or comment before shebang.

**Fix:**
```bash
# Check first two lines
head -2 script.sh
# Remove duplicate or move comment after shebang
sed -i '2d' script.sh
```

## Problem 3: github-bounty-hunter missing token

**Symptom:** `ERROR: GITHUB_TOKEN not set and .env not found`

**Fix:**
```bash
echo "GITHUB_TOKEN=$(gh auth token)" > .env
```
Ensure script reads `.env` via relative path, not `$HOME/.openclaw/workspace/.env`.

## Problem 4: morning-report wrong workspace path

**Symptom:** Script references `/home/zhaog/...` instead of actual path.

**Fix:** Set `WORKSPACE="/home/ubuntu/.openclaw/workspace"` in the script.

## Problem 5: QMD package name

**Symptom:** `npm install -g @tobi/qmd` returns 404; `npm install -g qmd` installs empty shell.

**Fix:**
```bash
npm install -g @tobilu/qmd
```
Verify: `which qmd` → `~/.npm-global/bin/qmd`.

## Problem 6: jq null field causes integer comparison error

**Symptom:** `bash: [: Illegal number:`

**Fix:** Always provide defaults in jq queries:
```bash
value=$(jq -r '.field // 0' "$STATE_FILE")
```

## Problem 7: Cron PATH duplication

**Symptom:** `/usr/bin/bash: /path/skills//usr/bin/bash: No such file`

**Fix:** Use absolute paths in cron; do not prepend `/usr/bin` in scripts.

## Problem 8: Cron log shows historical errors

**Symptom:** Log file has `Bad substitution`, `source: not found`, or other errors at beginning, but task actually executed successfully.

**Cause:** Log file contains old failed runs' errors; new successful runs append below.

**Fix:**
```bash
# Don't grep for errors in full log
# Instead, grep for specific date/time
grep "2026-09-04 23:30" /path/to/log | grep "✅"

# Check execution status by timestamp
grep "2026-09-04 23:30" /path/to/log | tail -20
```

**Debug procedure:**
1. Find execution timestamp in log
2. Grep for that specific timestamp, not entire file
3. Check if success markers (✅) exist after that timestamp
4. Ignore errors before the successful execution

## Problem 9: 日报"失败"可能是时间未到

**Symptom:** 用户反馈"为什么没有定时任务生成报告"，但检查日志发现任务未执行。

**可能原因：**
1. **时间未到**：当前时间早于 cron 调度时间（如 23:30 的任务在 19:00 检查）
2. **journalctl 日志旋转**：journal 轮转后历史日志不可用
3. **cron 环境差异**：cron 的 PATH 与交互 shell 不同

**诊断步骤：**
```bash
# 1. 确认当前时间 vs cron 调度时间
date; crontab -l | grep "<任务关键词>"

# 2. 检查 journalctl 中 cron 执行记录
journalctl --since "2026-09-08 23:25" --until "2026-09-08 23:35" | grep "ubuntu.*CMD.*<任务名>"

# 3. 检查日志文件最新时间
ls -la ~/.openclaw/workspace/logs/*.log
tail -5 ~/.openclaw/workspace/logs/<任务>.log

# 4. 手动执行验证脚本正常
bash /path/to/skill.sh review --mode full
```

**关键发现：**
- cron 日志在 journalctl 中以 `(ubuntu) CMD (command)` 形式记录
- 检查时注意时区：journalctl 使用系统时区（Asia/Shanghai）
- 如果 journalctl 无记录但日志文件有内容，说明任务成功但日志被轮转

**预防：**
- 在任务完成后写入明确的时间戳日志
- 定期检查 cron 服务状态：`systemctl status cron`

## Deployment checklist
1. [ ] Python deps: headless where no GUI needed
2. [ ] Shebang: line 1 only, no comments before it
3. [ ] Cron paths: absolute, no PATH duplication
4. [ ] Test critical function before relying on cron
5. [ ] Record fix in memory/YYYY-MM-DD.md
6. [ ] When debugging: grep by timestamp, not full log

---

## Ollama 本地模型测试规范

### Problem: Ollama 服务与模型状态

**Symptom:** Gateway 重启后 `ollama list` 返回空列表

**Fix:**
```bash
# 检查并重启 Ollama 服务
pgrep -a ollama || ollama serve &>/dev/null &
sleep 3
ollama list
```

### Problem: 模型拉取失败（注册表无此模型）

**Symptom:** `pulling manifest` 后报错 `file does not exist`

**Fix:** 尝试标准变体名或换用 Qwen 系列（中文优化）
```bash
# phi-3-mini 不存在时，用 qwen 系列替代
ollama pull qwen2.5:0.5b   # 最小中文模型
ollama pull qwen2:0.5b     # 备选
ollama pull tinyllama      # 英文轻量
```

### Problem: OOM Kill（内存不足）

**Symptom:** 并行测试多个模型时系统卡死或进程被杀

**Procedure:**
1. 内存 ≤ 2GB 时，**必须串行**拉取/测试模型
2. 测试前检查可用内存：`free -h | grep -E "Mem|Swap"`
3. 单模型测试使用 timeout：`timeout 30 ollama run <model> "<prompt>"`
4. 避免同时加载多个模型到内存

### Problem: 小模型格式控制不稳定

**Symptom:** 0.5B 模型输出 JSON 格式不符合预期

**Fix:**
- 增加示例数量（2-3个 few-shot 示例）
- 使用思维链引导："请逐步思考，最后以 JSON 格式输出"
- 降级期望：0.5B 模型适合对话，不适合严格格式控制
- 需要稳定格式时升级到 1.5B+ 或使用云端 API

### Model Selection Quick Reference

| 内存可用 | 推荐模型 | 中文能力 | 适用场景 |
|----------|----------|----------|----------|
| ≤ 500MB | qwen2:0.5b | ⭐⭐⭐ | 边缘部署、简单问答 |
| ≤ 600MB | qwen2.5:0.5b | ⭐⭐⭐⭐⭐ | 中文对话、内容生成 |
| ≤ 1.2GB | tinyllama | ⭐ | 英文基础任务 |
| ≤ 1.5GB | qwen2.5:1.5b | ⭐⭐⭐⭐⭐ | 代码、复杂推理 |
| ≥ 8GB | qwen2.5:7b | ⭐⭐⭐⭐⭐ | 生产环境 |

---

## Problem 10: logger.info()参数错误

**Symptom:** `TypeError: Logger._log() got an unexpected keyword argument 'end'`

**Cause:** `logger.info()` 误传了 `print()` 的参数 `end` 和 `flush`。

**Fix:**
```python
# ❌ 错误：logger不支持end/flush参数
logger.info("message", end="", flush=True)

# ✅ 正确：直接调用
logger.info("message")

# 如需格式化输出，用f-string
logger.info(f"分析 {name}...")
```

**教训:** logger和print是不同的API，迁移时需注意参数差异。

---

## Problem 11: gh auth login fails due to GITHUB_TOKEN env var

**Symptom:**
```
The value of the GITHUB_TOKEN environment variable is being used for authentication.
To have GitHub CLI store credentials instead, first clear the value from the environment.
```

**Cause:** `.bashrc` auto-exports `GITHUB_TOKEN` from `.env` file, blocking interactive login.

**Fix:**
```bash
# 1. Clear the env var first
unset GITHUB_TOKEN

# 2. Then run login
gh auth login -h github.com
```

---

## Problem 12: Token invalid after updating .env but not git credentials

**Symptom:** `gh auth status` shows "✓ Logged in" but `git push` returns "Invalid username or token"

**Cause:** Git credentials file (`~/.git-credentials`) still has old token.

**Fix:**
```bash
# Update .git-credentials with new token
echo "https://<username>:<new_token>@github.com" > ~/.git-credentials
git config credential.helper store
```

---

## Problem 13: Git remote URL cached with old token

**Symptom:** Push fails even after updating credentials

**Fix:**
```bash
# Update remote URL to use new token
git remote set-url origin https://<username>:<new_token>@github.com/<owner>/<repo>.git
```

---

## Problem 14: Repository divergence (local vs remote commits)

**Symptom:** `error: failed to push some refs to ... Updates were rejected because the tip of your current branch is behind`

**Cause:** Remote has commits not in local (or vice versa), causing non-fast-forward error.

**Fix:**
```bash
# Fetch and rebase local commits on top of remote
git fetch origin
git rebase origin/main

# Then push
git push origin main
```

---

## Problem 15: Multi-repo workspace sync strategy

**Context:** Workspace has two branches pointing to different GitHub repos:
- `main` → `xiaomijiao-skills` (技能仓库)
- `master` → `openclaw-skills` (个人信息仓库)

**Sync procedure:**
```bash
# Only sync skills repo (main branch)
git push origin main

# Personal repo (master/skills) stays as-is per user instruction
# Do NOT automatically sync master branch
```

**User directive:** "值更新技能仓库，不要更新个人信息仓库" - Only update skills repo, leave personal repo unchanged.

**Key point:** When token expires:
1. Generate new token at https://github.com/settings/tokens
2. Update `~/.openclaw/workspace/.env`
3. Update `~/.git-credentials`
4. Update git remote URLs if needed
5. `unset GITHUB_TOKEN` before running `gh auth login`
6. Push only `main` branch (skills repo)

---

## Problem 16: OpenClaw cron tasks missing despite script existence

**Symptom:** Script exists and is correct, but reports never get generated/pushed on schedule. User reports "报告没收到".

**Root cause:** OpenClaw automations (cron) are separate from system crontab and from MEMORY.md records. Having a script ≠ having a scheduled task.

**Diagnostic procedure:**
```bash
# 1. Check OpenClaw automations (NOT system crontab)
openclaw cron list --json

# 2. Check system crontab separately
crontab -l

# 3. Verify task execution status
openclaw cron list --json | python3 -c "
import json, sys, datetime
data = json.load(sys.stdin)
for c in data.get('jobs', []):
    name = c.get('name','')
    expr = c.get('schedule',{}).get('expr','N/A')
    state = c.get('state',{})
    last = state.get('lastRunAtMs','')
    st = state.get('lastRunStatus','')
    dt = datetime.datetime.fromtimestamp(int(last)/1000).strftime('%m-%d %H:%M') if last else 'never'
    print(f'{name}: schedule={expr} last={dt} status={st}')
"
```

**Fix: Create OpenClaw cron task**
```bash
# For command-based tasks (like oil-gold analysis)
openclaw cron add --cron "0 10 * * *" \
  --name "oil-gold-morning" \
  --command "sh -lc '/path/to/script.sh'" \
  --announce

# For agent-turn tasks (like daily review)
openclaw cron add --cron "5 23 * * *" \
  --name "daily-review-evening" \
  --message "执行每日回顾：运行 skill.sh review --mode full，生成今日工作总结并推送QQ"
```

**Verification:**
```bash
# Check next run time
openclaw cron list --json | python3 -c "
import json, sys, datetime
data = json.load(sys.stdin)
for c in data.get('jobs', []):
    name = c.get('name','')
    state = c.get('state',{})
    next_run = state.get('nextRunAtMs','')
    if next_run:
        dt = datetime.datetime.fromtimestamp(int(next_run)/1000).strftime('%Y-%m-%d %H:%M')
        print(f'{name}: next={dt}')
"
```

**Key insight:** OpenClaw 2026.8+ uses its own automation system (`openclaw cron`). System crontab is separate. Scripts can be perfect but if no OpenClaw cron task is configured, nothing runs automatically. Always verify with `openclaw cron list` after deployment.

=======
部署技能时的常见问题和解决方案。

## 问题1：OpenCV缺少OpenGL库

### 症状
```
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

### 原因
服务器无图形界面，opencv-python依赖OpenGL库。

### 解决方案
```bash
# 错误做法
pip install opencv-python

# 正确做法：使用headless版本
pip uninstall opencv-python -y
pip install opencv-python-headless
```

### 适用技能
- image-content-extractor
- terminal-ocr

## 问题2：smart-model-switch重复shebang

### 症状
```
SyntaxError: Invalid or unexpected token
```

### 原因
文件第一行和第二行都是`#!/usr/bin/env node`

### 解决方案
```bash
# 删除第二行shebang
sed -i '2d' scripts/analyze-complexity.js
```

## 部署检查清单

1. [ ] 检查Python依赖（headless vs 标准版）
2. [ ] 检查脚本shebang是否唯一
3. [ ] 配置cron任务
4. [ ] 测试关键功能
5. [ ] 记录到memory/YYYY-MM-DD.md

## 问题3：github-bounty-hunter需要Token

### 症状
```
ERROR: GITHUB_TOKEN not set and .env not found
```

### 解决方案
创建.env文件：
```bash
# 在项目根目录
echo "GITHUB_TOKEN=$(gh auth token)" > .env
```

### 脚本修改
bounty_scan.sh已更新为使用相对路径：
```bash
# 错误: $HOME/.openclaw/workspace/.env
# 正确: .env (相对路径)
```

## Cron配置示例

```bash
# context-manager-v2
*/10 * * * * ~/.openclaw/skills/context-manager/scripts/seamless-switch.sh >> logs/seamless-switch-cron.log 2>&1

# daily-review-assistant
0 9 * * * skills/daily-review-assistant/skill.sh review --mode morning >> logs/daily-review-morning.log 2>&1
30 23 * * * skills/daily-review-assistant/skill.sh review --mode full >> logs/daily-review-evening.log 2>&1

# smart-memory-sync
*/5 * * * * cd workspace && python3 skills/smart-memory-sync/scripts/smart-sync.py --check >> logs/smart-memory-sync.log 2>&1
```
>>>>>>> skills/main
