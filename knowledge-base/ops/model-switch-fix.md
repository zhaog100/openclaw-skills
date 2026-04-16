# 🔧 模型切换不生效的根因与彻底修复

**创建**: 2026-04-16  
**维护**: 小米椒 🌶️‍🔥  
**适用**: OpenClaw v2026.4.x

---

## 问题现象

配置文件 `openclaw.json` 里 `primary` 改成了目标模型，但 Gateway 重启后主会话始终跑旧模型，cron 任务也一样。

---

## 根因（三层叠加）

| 层级 | 位置 | 问题 |
|------|------|------|
| ① Session 文件锁定 | `sessions.json` | `modelOverride` + `providerOverride` 覆盖了配置文件 |
| ② 会话历史推断 | `{sessionId}.jsonl` | Gateway 重启时从 JSONL 最后一轮对话的 `provider/model` 字段恢复模型 |
| ③ Cron 硬编码 | cron 任务的 `payload.model` | 写死旧模型，且 isolated session 里 fallback 链的新模型全部 `model_not_found` |

**根本原因**：`openclaw.json` 的 `auth.profiles` 里缺少目标 provider 的配置，导致 isolated cron session 找不到认证。

---

## 彻底修复（四步）

### 第一步：补 auth profile
```json
// openclaw.json → auth.profiles
{
  "zai:default": { "provider": "zai", "mode": "api_key" },
  "bailian:default": { "provider": "bailian", "mode": "api_key" }
}
```

### 第二步：清理 session 文件
```python
# sessions.json → agent:main:main
# 删除: modelOverride, modelOverrideSource, providerOverride, liveModelSwitchPending
# 显式设置: model="qwen3.5-plus", modelProvider="bailian"
```

### 第三步：替换 JSONL 历史中的模型记录
```python
# {sessionId}.jsonl
# message.provider: "zai" → "bailian"
# message.model: "glm-5" → "qwen3.5-plus"
```

### 第四步：更新全部 cron 任务
```
所有 cron 任务 payload.model: 旧模型 → 新模型
```

---

## 检查清单（以后改模型必做）

- [ ] `openclaw.json` → `agents.defaults.model.primary` 改了没？
- [ ] `openclaw.json` → `auth.profiles` 有对应 provider 没？
- [ ] `agents/main/agent/auth-profiles.json` 有对应 key 没？
- [ ] `sessions.json` 有 `modelOverride` / `providerOverride` 残留没？
- [ ] JSONL 历史最后几条消息的 model 是新的还是旧的？
- [ ] 所有 cron 任务的 `payload.model` 改了没？
- [ ] 改完后重启 Gateway 验证

---

## 关键文件位置

| 文件 | 路径 |
|------|------|
| 主配置 | `~/.openclaw/openclaw.json` |
| Auth 密钥 | `~/.openclaw/agents/main/agent/auth-profiles.json` |
| 模型定义 | `~/.openclaw/agents/main/agent/models.json` |
| 会话元数据 | `~/.openclaw/agents/main/sessions/sessions.json` |
| 会话历史 | `~/.openclaw/agents/main/sessions/{sessionId}.jsonl` |
| Cron 任务 | `openclaw cron list` 或 `~/.openclaw/cron/jobs.json` |

---

## 教训

> 改模型不只是改配置文件。OpenClaw 有三层模型缓存：**session override → JSONL 历史推断 → cron payload**。三层都要清理干净，否则重启后必然回滚。

---

_v1.0 | 2026-04-16 | 小米椒 🌶️‍🔥_
