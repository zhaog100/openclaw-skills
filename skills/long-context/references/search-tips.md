# Memory Search Tips

## Effective Search Queries

### Good Queries (specific)
```
memory_search query="bounty PR rustchain status"
memory_search query="payment RTC claim issue"
memory_search query="homelab-stack PR review"
```

### Bad Queries (too vague)
```
memory_search query="bounty"          # too broad
memory_search query="what happened"    # not specific
memory_search query="task"             # too generic
```

## Search Tips

1. **Use keywords from the task** — PR numbers, repo names, specific terms
2. **Combine terms** — "rustchain PR merged" better than just "rustchain"
3. **Use corpus filter**:
   - `corpus=memory` — memory files only (faster)
   - `corpus=wiki` — wiki supplements
   - `corpus=sessions` — session transcripts
4. **Limit results** — `maxResults=5` to avoid overload
5. **Set minScore** — `minScore=0.7` for high-confidence matches

## Search → Read Pattern

```
# Step 1: Search
memory_search query="PR #451 status" maxResults=3

# Step 2: Read relevant excerpt
memory_get path="memory/2026-04-30.md" from=50 lines=30

# Step 3: Act on the info
```

## When Search Fails

If `memory_search` returns nothing useful:
1. Try different keywords
2. Fall back to `memory_get` on today's file
3. Check `session_status` for current state
4. Ask user for context if still stuck
