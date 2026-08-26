---
name: model-switch
description: Switch AI models and providers. Supports LongCat, Agnes AI. Use when user asks to change model, switch provider, or optimize for coding/thinking/cheap tasks.

version: 1.1.0

---

# Model Switch v1.1.0

**创建者**: 思捷娅科技 (SJYKJ)/zhaog100

---

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

免费使用、修改和重新分发时，需注明出处。

---

Switch session model provider and model alias on demand.

## Available Models

| Provider | Models | Best For | Status |
|----------|--------|----------|--------|
| Agnes AI ⭐ | agnes-2.5-flash, agnes-2.0-flash, agnes-1.5-flash, agnes-image-2.0-flash | Primary | ✅ |
| LongCat | LongCat-2.0-Preview, LongCat-Flash-Thinking-2601, LongCat-Flash-Lite, LongCat-Flash-Chat, LongCat-Flash-Omni-2603 | Fallback | ✅ |

**Removed**: 百炼, GLM, MiniMax, OpenRouter, Gemini (disabled 2026-06-09)

## Switching

```
session_status model=agnes-2.5-flash    # switch to agnes-2.5-flash
session_status model=default               # reset to primary
```

See `references/providers.md` for endpoints.

## Model Selection Guide

| Task Type | Recommended Model | Reason |
|-----------|------------------|--------|
| General | agnes-2.5-flash | Primary model, best quality |
| Thinking | agnes-2.5-flash or LongCat-Flash-Thinking-2601 | Deep reasoning |
| Fast/cheap | LongCat-Flash-Lite | Low cost, fast |
| Image | agnesai/agnes-image-2.0-flash | Image understanding |
| Fallback | LongCat-2.0-Preview | Reliable backup |

## 自动降级策略（2026-06-09 更新）

**优先级顺序**：
1. `agnesai/agnes-2.5-flash` — 主力模型（优先使用）
2. `agnesai/agnes-2.0-flash` — 备用 1
3. `agnesai/agnes-1.5-flash` — 备用 2
2. `longcat/LongCat-2.0-Preview` — LongCat 主力（2.0 不可用时切换）
3. `longcat/LongCat-Flash-Thinking-2601` — LongCat 深度思考
4. `longcat/LongCat-Flash-Lite` — LongCat 轻量（快速任务/进一步降级）

**触发条件**：
- API 返回 429 (Rate Limit) → 切换到下一个 LongCat 模型
- API 返回 401/403 (Auth Error) → 切换到下一个 LongCat 模型
- API 返回 500/503 (Server Error) → 切换到下一个 LongCat 模型
- 上下文超限 → 切换到 LongCat-Flash-Lite

## Error Handling

If model switch fails:
1. Check `session_status` for error message
2. Verify auth profile and API key in `.env`
3. Try fallback: `session_status model=longcat/LongCat-2.0-Preview`
4. If persistent, read `references/troubleshooting.md`

## References

- **Provider details**: `references/providers.md` — endpoints, model list
- **Troubleshooting**: `references/troubleshooting.md` — common errors and fixes
