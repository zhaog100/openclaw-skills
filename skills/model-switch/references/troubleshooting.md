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
- **Fix**: Wait and retry, or switch to different provider

### "Connection timeout"
- **Cause**: Network issue or endpoint down
- **Fix**: Try fallback model (bailian/qwen3.5-plus)

## LongCat Endpoint Gotcha
- **Wrong**: `https://api.longcat.chat/openai/v1`
- **Right**: `https://api.longcat.chat/openai`
- **Rule**: No trailing `/v1` for LongCat

## Fallback Chain
1. Primary: bailian/qwen3.6-plus
2. Backup: bailian/qwen3.5-plus
3. Emergency: LongCat-Flash-Lite
