# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License

---
name: context-manager
description: Auto context management with seamless session switching. Monitors usage, triggers at 70% threshold (proactive check every 10 tool calls), automatically creates new session with loaded memory. Zero user intervention required. Trigger on "context", "memory", "session management", "context limit", "memory transfer".
version: 2.9.0
---

# Context Manager v2.9.0 - 无感会话切换

自动监控上下文使用率，达到阈值时自动保存记忆并创建新会话，用户完全无感知。

## 🎯 核心特性

- **启动优化**：分层读取（核心<5KB + 摘要<10KB），启动占用<10%
- **无感自动切换**：70%阈值自动触发 cron agentTurn 创建新会话
- **主动保存**：cron 每30分钟自动检查上下文，不等阈值
- **真实API监控**：totalTokens/contextTokens准确计算
- **记忆传递**：自动更新MEMORY.md + daily log
- **冷却机制**：1小时冷却期，避免重复通知
- **通知适配**：qqbot 渠道（原飞书已替换）
- **自动压缩**：每4小时检查 MEMORY.md 大小，超限自动压缩
- **MEMORY.md 大小警告**：>20KB 会导致 QQ Bot 截断警告，建议保持在 15KB 以内

## 📋 工作流程

```
启动 → 读SOUL/USER → 读MEMORY-LITE → session_status检测（>30%预警）
对话中 → 每10次工具调用主动检查 + 每5分钟定时监控 → ≥70%自动保存记忆 → agentTurn新会话 → 分层加载 → 自然继续
```

## 🚀 使用方式

Cron 任务已自动配置：
- `context-monitor` — 每30分钟执行一次
- `context-switch-check` — 每小时执行一次

手动运行：
```bash
bash ~/.openclaw/workspace/skills/context-manager-v2/scripts/context-monitor.sh
bash ~/.openclaw/workspace/skills/context-manager-v2/scripts/seamless-switch.sh
```

查看日志：
```bash
tail -50 ~/.openclaw/workspace/logs/context-monitor.log
tail -50 ~/.openclaw/workspace/logs/seamless-switch.log
tail -50 ~/.openclaw/workspace/logs/auto-compaction.log
```

### 多通道兼容性
- ✅ **QQ 通道**：完全支持
- ✅ **微信通道**：完全支持（openclaw-weixin 插件）
- ✅ **飞书通道**：完全支持
- 本技能为通道无关设计，所有通道共用同一套会话管理逻辑

## 🔧 阈值配置

```bash
DIALOG_THRESHOLD=70   # 对话中触发切换（原85%，降低到70%提前保护）
STARTUP_THRESHOLD=30  # 启动后警告
```

## 📊 版本里程碑

- v2.0：无感自动切换（agentTurn）
- v2.1：启动优化（分层读取，节省75%空间）
- v2.2：真实API监控（70%阈值，5分钟间隔）
- v2.9.1：新增 MEMORY.md 20KB 警告阈值提示（2026-08-03）
- v2.9.0：启动优化 + 自动压缩
- v2.2.2：阈值85→70%，增加每10次工具调用主动检查
- v2.2.1：Cron环境修复（生产就绪）

## 🛡️ "Something went wrong" 防护（v2.3 新增）

### 错误根因
`⚠️ Something went wrong` 通常由以下原因触发：
1. **上下文溢出（>90%）** → 模型请求失败
2. **API 限流（429）** → 配额用完
3. **LLM 请求超时** → 模型响应慢或网络不稳定（⭐ 最常见）
4. **API Key 缺失/无效** → No API key found for provider
5. **模型未注册** → Unknown model（本地 models.json 未配置）
6. **Compaction 失败** → 上下文无法压缩
7. **模型服务异常（500/503）**

### 防护流程
```
上下文 > 75% → /compact 压缩（预防性）
上下文 > 85% → 切换大窗口模型（LongCat-Lite 320K）+ /compact
上下文 > 90% → 保存记忆到 memory/ → 创建新会话
API 429 → 自动切换备用模型（Agnes AI ↔ LongCat 轮转）
LLM 超时 → 自动 fallback 到快速模型（longcat/LongCat-Flash-Lite）
API Key 缺失 → 检查 auth-profiles.json + models.json 是否存在
Unknown model → 检查 models.json 是否包含该 provider 定义
连续 2 次请求失败 → 强制 compaction + 切换模型
连续 3 次失败 → 保存记忆 + /new 新会话
```

### 超时防护配置（⭐ 重点）

**问题**：模型在上下文较大时容易超时（>150s），触发 `Something went wrong`。

**解决方案**：配置 fallback，超时自动切换到快速模型。

```json
// 降级策略：primary → fallback → LongCat
// agnes-2.5-flash 超时/不可用 → 切到 agnes-2.0-flash → agnes-1.5-flash
```

**容器实例额外检查**：
1. 确保 `/root/.openclaw/agents/main/agent/auth-profiles.json` 存在且包含 provider 的 API Key
2. 确保 `/root/.openclaw/agents/main/agent/models.json` 存在且包含 fallback 模型的定义
3. 两个文件缺一不可，否则 `Unknown model` 或 `No API key found`

### 模型轮转顺序
```
1. agnesai/agnes-2.5-flash（主力）
2. agnesai/agnes-2.0-flash（fallback 1）
3. agnesai/agnes-1.5-flash（fallback 2）
4. longcat/LongCat-Flash-Lite（快速降级）
5. longcat/LongCat-Flash-Chat（备用）
6. longcat/LongCat-Flash-Thinking-2601（深度思考）
```

### 心跳集成
每次心跳自动执行：
1. `session_status` 检查上下文使用率
2. > 75%: 预防性 `/compact`
3. > 85%: 切换大窗口模型 + `/compact`
4. > 90%: 保存记忆 → `agentTurn` 新会话
5. 检查 LongCat 额度（运行 `scripts/longcat-monitor.sh`）
6. 额度不足时自动切换到备用模型

## ⚠️ 注意

- 新会话自然接续，不提示"已切换"
- MEMORY-LITE.md 暂不需要
- 与 smart-memory-sync 双保险协作
- **"Something went wrong" 错误大幅减少** — 多层防护自动处理

## 🔄 主动保存机制（Proactive Save）

Cron 任务已替代手动每10次工具调用检查：
- `context-monitor` 每30分钟自动检查
- `context-switch-check` 每小时自动检查并触发切换
- `context-auto-compact` 每4小时自动压缩 MEMORY.md
- 无需手动计数工具调用

> 详细技术实现、版本历史见 `REVIEW-AUDIT.md`

---

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/example-user/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者：思捷娅科技 (SJYKJ)/zhaog100

**商业使用授权**：
- 个人/开源：免费
- 小微企业（<10 人）：¥999/年
- 中型企业（10-50 人）：¥4,999/年
- 大型企业（>50 人）：¥19,999/年
- 源码买断：¥99,999 一次性

详情请查看：[LICENSE](../../LICENSE)
