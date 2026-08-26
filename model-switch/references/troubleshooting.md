<!--
Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
-->
# Model Switch Troubleshooting

## Common Errors

### "Unknown model"
- **Cause**: Missing auth profile in config
- **Fix**: Check `~/.openclaw/workspace/.env` for API key
- **Verify**: `session_status` to see current config

### "401 Unauthorized"
- **Cause**: Invalid/expired API key
- **Fix**: Update key in `.env`, restart gateway if needed

### "429 Rate Limited"
- **Cause**: Too many requests
- **Fix**: Wait and retry, or switch to fallback model

### "Connection timeout"
- **Cause**: Network issue or endpoint down
- **Fix**: Try fallback model (LongCat-Flash-Lite)

## LongCat Endpoint Gotcha
- **Wrong**: `https://api.longcat.chat/openai/v1`
- **Right**: `https://api.longcat.chat/openai`
- **Rule**: No trailing `/v1` for LongCat

## Fallback Chain (2026-06-09)
1. Primary: agnesai/agnes-2.5-flash
2. Fallback 1: agnesai/agnes-2.0-flash
3. Fallback 2: agnesai/agnes-1.5-flash
2. Backup: longcat/LongCat-2.0-Preview
3. Thinking: longcat/LongCat-Flash-Thinking-2601
4. Emergency: longcat/LongCat-Flash-Lite

**Removed**: 百炼, GLM, MiniMax, OpenRouter, SenseNova (disabled 2026-06-09)
