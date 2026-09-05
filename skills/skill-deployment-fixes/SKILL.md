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

## Deployment checklist
1. [ ] Python deps: headless where no GUI needed
2. [ ] Shebang: line 1 only, no comments before it
3. [ ] Cron paths: absolute, no PATH duplication
4. [ ] Test critical function before relying on cron
5. [ ] Record fix in memory/YYYY-MM-DD.md
6. [ ] When debugging: grep by timestamp, not full log
