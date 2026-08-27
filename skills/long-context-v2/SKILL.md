---
name: long-context
description: Minimize startup context by loading MEMORY-LITE.md instead of full MEMORY.md. Use for session bootstrap optimization.
version: 2.0.0
---

# Long Context v2.0.0

**创建者**: 思捷娅科技 (SJYKJ)/zhaog100

---

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

免费使用、修改和重新分发时，需注明出处。

---

## Strategy: Startup Optimization

### File Hierarchy

| File | Size | Purpose | Loaded When |
|------|------|---------|-------------|
| MEMORY-LITE.md | ~2KB | Core identity, workflows, tracked PRs | **Every session startup** |
| MEMORY.md | ~10KB | Full history, detailed logs | Only when needed via memory_search |
| memory/YYYY-MM-DD.md | Variable | Daily raw notes | Only when searching specific dates |

### How It Works

1. **Startup**: Agent loads MEMORY-LITE.md (not full MEMORY.md)
2. **Deep recall**: Use `memory_search` to find specific information
3. **Detailed read**: Use `memory_get` to fetch specific lines from MEMORY.md

### Token Savings

- Before: MEMORY.md ~28KB → ~7000 tokens
- After: MEMORY-LITE.md ~2KB → ~500 tokens
- **Savings: ~6500 tokens per session startup**

## When to Use

- Session starts with large context files
- Need to recall historical events without loading full memory
- Want to reduce initial token consumption

## References

- Compaction patterns: `references/compaction.md`
- Memory search tips: `references/search-tips.md`
