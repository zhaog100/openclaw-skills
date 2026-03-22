# Shubham文件系统记忆方法论

来源：微信公众号（2026-03-22 官家分享）
作者：Shubham（Google AI Senior PM）

## 核心观点
> 护城河不是模型，是积累的上下文。同一个模型，文件变了，输出判若两人。

## 三层架构
1. **身份层** — SOUL.md / IDENTITY.md / USER.md
2. **操作层** — AGENTS.md / HEARTBEAT.md
3. **知识层** — MEMORY.md / daily logs / shared-context/

## 关键实践
- SOUL.md ≤ 60行，每次启动必读
- 反馈写进文件才有效（聊天里纠正下次就忘）
- shared-context/ 跨代理共享纠正，写一次所有人同步
- 每日日志只加载今+昨，定期归档（避免16万tokens拖慢）
- 单写者规则：每个共享文件只有一个写入者

## 与我们的对比
我们已覆盖所有建议，额外拥有：QMD向量检索、版权管理、全自动Bounty流水线

---
*© 2026 思捷娅科技 (SJYKJ) | MIT License*
