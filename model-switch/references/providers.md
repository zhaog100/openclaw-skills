<!--
Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
-->
# Provider Reference

## LongCat
- **Endpoint**: `https://api.longcat.chat/openai` (note: no trailing `/v1`)
- **Models**: LongCat-2.0-Preview, LongCat-Flash-Thinking-2601, LongCat-Flash-Lite, LongCat-Flash-Chat, LongCat-Flash-Omni-2603
- **Context**: 128K
- **Status**: ✅ Configured (5 models)
- **Notes**: Good for fast/cheap tasks

## Agnes AI ⭐
- **Endpoint**: `https://apihub.agnes-ai.com/v1`
- **Models**: agnes-2.5-flash, agnes-2.0-flash, agnes-1.5-flash, agnes-image-2.0-flash, agnes-image-2.1-flash, agnes-video-v2.0
- **Context**: 128K
- **Status**: ✅ Primary provider
- **Notes**: Main model for all tasks

## Model Aliases
| Alias | Full Model |
|-------|-----------|
| primary | agnesai/agnes-2.5-flash |
| fallback1 | agnesai/agnes-2.0-flash |
| fallback2 | agnesai/agnes-1.5-flash |
| thinking | longcat/LongCat-Flash-Thinking-2601 |
| lite | longcat/LongCat-Flash-Lite |
| image | agnesai/agnes-image-2.0-flash |
