# Context Compaction Patterns

## Pattern 1: Quick Compact (50+ messages)

```
1. Read MEMORY.md (curated long-term)
2. Read memory/YYYY-MM-DD.md (today)
3. Read memory/(yesterday).md (if needed)
4. Skip SOUL.md/USER.md/AGENTS.md (already in project context)
5. Use sessions_history limit=10 for recent conversation
```

## Pattern 2: Deep Compact (100+ messages)

```
1. memory_search for current topic
2. memory_get only relevant excerpts
3. session_status for current config
4. Skip all reference files unless specifically needed
5. Summarize what's known, proceed from summary
```

## Pattern 3: Emergency Compact (approaching limit)

```
1. Only read: SOUL.md + USER.md + MEMORY.md
2. memory_search for immediate task
3. Proceed with minimal context
4. Do not load any reference files
```

## When to Compact

- Response time > 5 seconds
- Token count > 80% of limit
- User reports "slow" or "stuck"
- Multiple files loaded without clear purpose

## What to Keep

Always keep loaded:
- SOUL.md (identity)
- USER.md (user info)
- MEMORY.md (long-term memory)
- Current task context

Can skip:
- TOOLS.md (unless using specific tool)
- HEARTBEAT.md (unless doing heartbeat)
- Reference files (load on-demand)
