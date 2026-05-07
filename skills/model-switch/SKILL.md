---
name: model-switch
description: Switch AI models and providers for the current session. Supports 百炼(bailian), LongCat, OpenRouter, Gemini, GLM, MiniMix and more. Use when user asks to change model, switch provider, compare models, or optimize for coding/thinking/cheap tasks. Also use when model errors occur and fallback is needed.

version: 1.0.0

---

# Model Switch

Switch session model provider and model alias on demand.

## Available Models

Read `references/providers.md` for the full provider list, endpoints, and model aliases.

**Quick reference** (current workspace config):

| Provider | Models | Best For | Status |
|----------|--------|----------|--------|
| 百炼/bailian | qwen3.6-plus, qwen3.5-plus, qwen3-max, glm-5, glm-4.7, kimi-k2.5, MiniMix-M2.5 | Coding, general | ✅ Primary |
| LongCat | LongCat-Flash-Thinking-2601, LongCat-Flash-Lite | Fast tasks | ✅ |
| OpenRouter | qwen/qwen3.6-plus-preview:free | Large context (1M) | ⚠️ Low balance |
| Gemini | gemini-2.5-pro, gemini-2.5-flash | Multi-modal | ✅ |

## Switching Models

### Method 1: Per-session override (recommended)

Use `session_status` with `model` parameter:

```
session_status model=qwen/qwen3.5-plus    # switch to qwen3.5-plus
session_status model=default               # reset to primary
```

### Method 2: Gateway config (persistent)

For permanent changes, use `gateway` tool:
```
gateway config.schema.lookup    # find config field
gateway config.get              # read current
gateway config.patch            # update
```

**Never** edit config files directly — use `gateway` tool for hot-reload.

## Model Selection Guide

| Task Type | Recommended Model | Reason |
|-----------|------------------|--------|
| Coding/PR | bailian/qwen3.6-plus | Best code quality, fast |
| Complex reasoning | bailian/glm-5 or bailian/qwen3-max | Strong reasoning |
| Fast/cheap tasks | LongCat-Flash-Lite | Low cost, fast |
| Large context | OpenRouter (free tier) | 1M context window |
| Multi-modal | Gemini | Image understanding |
| Fallback | bailian/qwen3.5-plus | Reliable backup |

## Common Commands

- "切换到百炼" → `session_status model=bailian/qwen3.6-plus`
- "用 GLM" → `session_status model=bailian/glm-5`
- "切回默认" → `session_status model=default`
- "当前什么模型" → `session_status` (check current)
- "对比模型" → Read `references/providers.md` for comparison

## Error Handling

If model switch fails:
1. Check `session_status` for error message
2. Verify auth profile exists (check `~/.openclaw/workspace/.env`)
3. Try fallback: `session_status model=bailian/qwen3.5-plus`
4. If persistent, read `references/troubleshooting.md`

## References

- **Provider details**: `references/providers.md` — endpoints, API keys, model list
- **Troubleshooting**: `references/troubleshooting.md` — common errors and fixes
