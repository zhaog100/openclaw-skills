---
name: "identity-validation-fix"
description: "Fix identity validation format issues in SOUL.md and MEMORY.md for daily-review-assistant compatibility."
---

# Identity Validation Fix

## Problem
daily-review-assistant script fails validation because SOUL.md and MEMORY.md use inconsistent identity formats.

## Root Cause
- Script expects `grep -E "^\- \*\*名字\*\*"` in SOUL.md
- Script expects `grep -oP 'GitHub[^:]*:\s*\K\w+'` in MEMORY.md
- Actual files use different formats (e.g., SOUL.md had `-**名字:**` without space)

## Solution

### Fix SOUL.md
Add line after `## Core Truths`:
```markdown
**-名字:** 小米椒 🌶️🔥
```

### Fix MEMORY.md
Add line after `## 身份`:
```markdown
- **GitHub:** zhaog100
```

## Verification
```bash
grep -E "^\- \*\*名字\*\*" SOUL.md  # Should return: - **名字:** 小米椒 🌶️🔥
grep -oP 'GitHub[^:]*:\s*\K\w+' MEMORY.md  # Should return: zhaog100
```

## When to Apply
- daily-review-assistant steps 1-2 fail with identity validation errors
- Scripts report "SOUL.md 中未找到 '小米椒' 名称" or "GitHub 用户名不匹配"
- New workspace setup requires identity configuration

## Notes
- SOUL.md format: `- **名字:** <name> <emoji>`
- MEMORY.md format: `- **GitHub:** <username>`
- Keep both formats consistent across all identity-related files

## User Instructions (2026-09-03)
- **不生成PROJMGMT日报**：步骤11已禁用，不再生成日报
- **不自动提交远程仓库**：git commit/push已禁用，个人信息和技能不自动推送
- 身份信息仅用于验证，不触发任何推送操作
