# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License

---
name: smart-model-switch
description: 智能模型自动切换 + 错误 Fallback。根据消息复杂度和文件类型自动选择最优模型（Flash/Main/Coding/Vision/Complex），API 失败时自动切换备用模型。Trigger on "模型切换", "智能模型", "自动选择模型", "model switch", "fallback", "模型降级".
version: 2.0.0
---

# 智能模型切换 v2.0.0

根据消息复杂度、文件类型自动选择最优模型，**API 失败时自动 Fallback 到备用模型**。

## v2.1.0 更新（2026-08-19）

- 新增 SenseNova 模型集成（sensenova-6.8-flash-lite / deepseek-v4-flash / glm-5.2）
- Flash 默认切换到 sensenova-6.8-flash-lite（免费+多模态）
- Coding 切换至 deepseek-v4-flash（1M上下文+thinking模式）
- Complex/Long-context 使用 glm-5.2（1M上下文，旗舰模型）
- Fallback 链：agnes-2.5-flash → sensenova-6.8-flash-lite → agnes-2.0-flash

## v2.0.0 更新（2026-07-20）

- 主力模型升级为 `agnes/agnes-2.0-flash`
- Fallback 链：`agnes/agnes-1.5-flash` → `agnes/agnes-2.5-flash`
- 清理过时脚本引用，聚焦核心 fallback 逻辑

### 1. 增强关键词规则库
- `forceComplex`: 架构设计、微服务、分布式等 → complex 模型
- `forceFlash`: 简单问候语、问句 → flash 模型
- `forceCoding`: 代码关键词、帮我写 → coding 模型
- `forceVision`: 图片视频格式 → vision 模型
- `forceAgnes`: agnes-2.0-flash 作为主力模型

## 🎯 模型选择规则

| 类型 | 模型 | 触发条件 |
|------|------|------|
| **Primary** ⭐ | agnes/agnes-2.0-flash | **默认优先使用** |
| Flash | agnes/agnes-2.0-flash | 简单问答、"你好"/"谢谢" |
| Main | agnes/agnes-2.0-flash | 常规对话 |
| Coding | agnes/agnes-2.0-flash | 代码/推理 |
| Vision | agnes/agnes-2.0-flash | 图片/视频相关 |
| Complex | agnes/agnes-2.0-flash | 架构设计、深度分析 |

**优先级**：forceRule > complexityScore > defaultModel

**降级策略（Fallback Chain）**：
1. 默认使用 `agnes/agnes-2.0-flash`
2. 报错/超时 → 切换到 `agnes/agnes-1.5-flash`
3. 1.5 也不可用 → 切换到 `agnes/agnes-2.5-flash`
4. 全部不可用 → 通知用户，停止自动切换

**上下文窗口参考**：
- 1.5-flash: 131k
- 2.0-flash: 131k
- 2.5-flash: 131k

## 📝 会话级 fallback 配置示例

如需在当前会话启用自动 fallback，可通过 session 配置设置：

```json
{
  "model": "agnes/agnes-2.0-flash",
  "fallbacks": ["agnes/agnes-1.5-flash", "agnes/agnes-2.5-flash"]
}
```

或通过 `/model` 命令切换。

## ⚠️ 注意事项

- 此技能提供的是**选择逻辑参考**，实际 fallback 由 OpenClaw 会话级配置驱动
- 每个会话可独立配置自己的 fallback 链
- 没有全局 fallback 配置，需逐个会话设置
- 旧版脚本（feedback-log.sh、manual-override.sh 等）已废弃，以配置为准

---

# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
