---
name: "skill-deployment-fixes"
description: "Common deployment pitfalls for OpenClaw skills: OpenCV headless, shebang ordering, token config, path fixes, QMD install."
---

# Skill Deployment Fixes

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
