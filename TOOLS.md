# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## GitHub

- Username: zhaog100
- Token 已存储在 ~/.git-credentials

## 🎯 模型使用策略（2026-04-09 更新）

### 默认模型（省钱优先）
**LongCat-Flash-Lite** — 每天5500万免费token，日常任务首选 ⭐⭐⭐

### 分级策略
| 层级 | 模型 | 用途 | 成本 |
|------|------|------|------|
| 🟢 轻量 | longcat/LongCat-Flash-Lite | 心跳、搜索、简单问答 | 免费 |
| 🟡 标准 | longcat/LongCat-Flash-Chat | 写作、分析、内容创作 | 免费 |
| 🟠 推理 | longcat/LongCat-Flash-Thinking-2601 | 复杂推理 | 免费 |
| 🔴 高级 | zai/glm-5 | 代码、bounty开发 | 免费 |
| 🔵 超长 | openrouter/qwen3.6-plus-preview:free | 超长上下文(100万) | 免费 |

### 切换命令
```bash
/model longcat/LongCat-Flash-Lite    # 默认（省钱）
/model longcat/LongCat-Flash-Chat    # 中等任务
/model longcat/LongCat-Flash-Thinking-2601  # 深度推理
/model zai/glm-5                      # 代码/复杂任务
```

### 额度监控
- 脚本: `scripts/longcat-monitor.sh`
- 日志: `data/longcat-usage.log`
- Base URL: `https://api.longcat.chat/openai`

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
