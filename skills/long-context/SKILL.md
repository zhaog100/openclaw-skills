---
name: long-context
description: Handle long conversations and large context windows efficiently. Use when conversation is getting long, context window is filling up, user asks to summarize/compact/continue, or when token usage is high. Supports memory search, context pruning, session compaction, and progressive loading strategies.

version: 1.0.0

---

# Long Context

Manage context window usage for long-running sessions. Keep responses fast and relevant even with large conversation history.

## When to Use

- Conversation history is growing large (>50 messages)
- Token usage approaching limits
- User asks to "summarize", "compact", "continue", "remember"
- Session feels slow or unresponsive
- Need to recall distant information

## Strategies

### 1. Memory Search First

Before loading full context, search memory:

```
memory_search query="specific topic" corpus=memory
memory_get path="memory/YYYY-MM-DD.md"
```

**Why**: Memory files are curated and smaller than full transcript.

### 2. Context Summarization

When context is too large, summarize instead of loading everything:

```
# Read today's memory
memory_get path="memory/YYYY-MM-DD.md"

# Search for specific info
memory_search query="bounty PR status" maxResults=5

# Get session status
session_status
```

### 3. Progressive Loading

Load only what's needed:

| Need | Tool | What it loads |
|------|------|---------------|
| Recent context | `memory_get` (today/yesterday) | 2 files |
| Specific topic | `memory_search` | Relevant snippets |
| Session info | `session_status` | Current config |
| Full history | `sessions_history` (last N) | Limited messages |

### 4. Context Pruning

For very long sessions:

1. **Skip redundant files** — Don't load SOUL.md/USER.md/AGENTS.md if already in project context
2. **Use targeted reads** — `memory_get path=X from=Y lines=Z` instead of full file
3. **Search before read** — `memory_search` first, only `memory_get` what's relevant
4. **Trim history** — Use `sessions_history limit=20` for recent context only

## Commands

- "总结一下" → Summarize recent memory files + current session state
- "继续" → Check memory for last task, resume where left off
- "忘了" → Clear context, reload only essential files (SOUL/USER/AGENTS)
- "搜索记忆" → `memory_search query="..."`
- "今天做了什么" → Read `memory/YYYY-MM-DD.md`

## Memory Organization

```
memory/
├── YYYY-MM-DD.md      # Daily logs (raw)
├── INDEX.md           # Memory index
└── heartbeat-state.json  # Heartbeat tracking

MEMORY.md              # Long-term curated memory
```

**Rule**: Daily files = raw notes. MEMORY.md = distilled wisdom. Search daily files for recent events, MEMORY.md for persistent knowledge.

## Token Budget Guide

| Component | Approx Tokens | Action if Over Budget |
|-----------|--------------|----------------------|
| System prompt | ~3000 | Skip non-essential sections |
| Project context files | ~5000 | Load only SOUL + USER |
| Memory files | ~2000 | Use search, not full read |
| Conversation history | Variable | Use `sessions_history limit=N` |
| **Total budget** | **~15-20K** | Prune to essentials |

## References

- **Compaction patterns**: `references/compaction.md` — how to compact long conversations
- **Memory search tips**: `references/search-tips.md` — effective search strategies
