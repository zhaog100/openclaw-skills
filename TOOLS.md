# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## GitHub

- Username: zhaog100
- Token 已存储在 ~/.git-credentials

## 🎯 模型使用策略

### 优先级（重要！）

1. **主力**：智谱 `zai/glm-5` ⭐
   - 日常任务首选
   - 稳定性高，响应快

2. **备用**：
   - 百炼 `bailian/*`
   - OpenRouter `qwen/qwen3.6-plus-preview:free` (100万上下文)
   - AIHubMix `aihubmix/*`
   - MiniMax `MiniMax-M2.7`

### 切换命令

```bash
# 默认使用智谱（无需切换）
/model zai/glm-5

# 超长上下文任务
/model qwen/qwen3.6-plus-preview:free

# 推理密集型
/model MiniMax-M2.7
```

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
