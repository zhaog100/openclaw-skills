---
name: context-manager
description: Auto context management with seamless session switching. Monitors usage, triggers at 70% threshold (proactive check every 10 tool calls), automatically creates new session with loaded memory. Zero user intervention required. Trigger on "context", "memory", "session management", "context limit", "memory transfer".
version: 2.7.0
---

# Context Manager v2.7.0 - 无感会话切换

自动监控上下文使用率，达到阈值时自动保存记忆并创建新会话，用户完全无感知。

## 🎯 核心特性

- **启动优化**：分层读取（核心<5KB + 摘要<10KB + QMD检索），启动占用<10%
- **无感自动切换**：70%阈值自动触发agentTurn创建新会话
- **主动保存**：每10次工具调用后自动检查上下文，不等阈值
- **真实API监控**：totalTokens/contextTokens准确计算，每5分钟检查
- **记忆传递**：自动更新MEMORY.md + MEMORY-LITE.md + daily log
- **冷却机制**：1小时冷却期，避免重复通知

## 📋 工作流程

```
启动 → 读SOUL/USER → 读MEMORY-LITE → session_status检测（>30%预警）
对话中 → 每10次工具调用主动检查 + 每5分钟定时监控 → ≥70%自动保存记忆 → agentTurn新会话 → 分层加载 → 自然继续
```

## 🚀 使用方式

```bash
# 安装
clawhub install miliger-context-manager

# 配置定时任务
*/5 * * * * ~/.openclaw/skills/context-manager/scripts/seamless-switch.sh

# 查看日志
tail -50 ~/.openclaw/workspace/logs/seamless-switch.log
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
上下文 > 85% → 切换大窗口模型（LongCat-2.0-Preview 128K）+ /compact
上下文 > 90% → 保存记忆到 memory/ → 创建新会话
API 429 → 自动切换备用模型（minimax/MiniMax-M2.7 ↔ longcat 轮转）
LLM 超时 → 自动 fallback 到快速模型（longcat/LongCat-2.0-Preview）
API Key 缺失 → 检查 auth-profiles.json + models.json 是否存在
Unknown model → 检查 models.json 是否包含该 provider 定义
连续 2 次请求失败 → 强制 compaction + 切换模型
连续 3 次失败 → 保存记忆 + /new 新会话
```

### 超时防护配置（⭐ 重点）

**问题**：模型在上下文较大时容易超时（>150s），触发 `Something went wrong`。

**解决方案**：配置 `modelFallbacks`，超时自动切换到备用模型。

```json
// ~/.openclaw/openclaw.json → agents.defaults
{
  "model": "longcat/LongCat-2.0-Preview",
  "modelFallbacks": [
    "minimax/MiniMax-M2.7"
  ]
}
```

**容器实例额外检查**：
1. 确保 `/root/.openclaw/agents/main/agent/auth-profiles.json` 存在且包含 provider 的 API Key
2. 确保 `/root/.openclaw/agents/main/agent/models.json` 存在且包含 fallback 模型的定义
3. 两个文件缺一不可，否则 `Unknown model` 或 `No API key found`

### 模型轮转顺序
```
1. longcat/LongCat-2.0-Preview（128K窗口，主力）
2. minimax/MiniMax-M2.7（200K窗口，备用）
3. longcat/LongCat-Flash-Omni-2603（多模态，图片/视频理解）
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

- 新会话不说"新会话"/"已切换"，自然接续
- MEMORY-LITE.md需手动创建（<10KB精简版）
- 与smart-memory-sync双保险协作
- **"Something went wrong" 错误不再发生** — 多层防护自动处理

## 🔄 主动保存机制（Proactive Save）

在对话过程中，除了定时监控外，还应在**每10次工具调用后**主动检查上下文：

```bash
# 在对话流中，每处理10次工具调用后执行：
TOOL_CALL_COUNT=$((TOOL_CALL_COUNT + 1))
if [ $((TOOL_CALL_COUNT % 10)) -eq 0 ]; then
    session_status  # 检查当前上下文占用
    # 如果占用>50%，即使未达阈值也主动保存关键记忆
    # 确保compaction前已有备份
fi
```

**目的**：不等阈值触发，提前保护对话上下文，防止compaction丢失信息。

> 详细技术实现、性能指标、版本历史见 `references/skill-details.md`

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
