# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License

# 通用模型锁定守护方案

_日期：2026-04-16 | 更新：2026-06-09_

> MIT License · Copyright (c) 2026 思捷娅科技 (SJYKJ) · 创建者：小米辣 🌶️‍🔥

## 一、问题本质

任何模型厂商都可能触发 Rate Limit（429错误），OpenClaw 的 Fallback 机制是**单向的**：

```
模型A → 模型B → 模型C（只能前进，不能回头）
```

一旦切换，Gateway 把当前模型写入 sessions.json，即使原模型恢复了也不会自动切回。

**适用于所有模型厂商**：Agnes AI 等都可能出现。

## 二、锁定流程

```
1. 模型A Rate Limit → 429
2. Fallback 到模型B → 成功
3. Gateway 写 sessions.json（模型B）
4. 下次对话读 sessions.json → 继续用模型B
5. 模型A 恢复了 → 还是模型B → 锁死
```

**关键**：Rate Limit 是临时的（几分钟就恢复），但 Gateway 当永久故障处理。

## 三、通用解决方案：model-guard.sh

### 核心逻辑（循环守护）

```bash
#!/bin/bash
# model-guard.sh — 通用模型锁定守护
# 每5分钟执行，清理所有模型锁定状态

# 1. 清理 sessions.json 所有 session 的 override 字段（11种）
#    - modelOverride / providerOverride / authProfileOverride
#    - authProfileOverrideSource / authProfileOverrideCompactionCount
#    - modelOverrideSource / fallbackNoticeActiveModel
#    - fallbackNoticeReason / fallbackNoticeSelectedModel
#    - model / modelProvider

# 2. 清理 auth-state.json 所有厂商的错误记录
#    - errorCount / failureCounts / lastFailureAt
#    - cooldownUntil / cooldownReason

# 效果：任何模型被锁定，最多5分钟自动解锁，切回默认模型
```

### 关键特性
- **厂商无关**：适用于所有模型厂商
- **循环执行**：crontab `*/5 * * * *`，每5分钟清理一次
- **全量清理**：清理所有 session 的所有 override 字段，不针对特定模型
- **自动恢复**：锁定 → 最多5分钟 → 自动切回默认模型

## 四、Fallback 链示例（2026-06-09）

```
默认: agnesai/agnes-2.0-flash

Fallback链：
 1. agnesai/agnes-2.0-flash       ← 主力
 2. agnes/agnes-2.0-flash   ← 备用
```

## 五、部署

```bash
# crontab 配置
*/5 * * * * /path/to/model-guard.sh >> /path/to/logs/model-guard.log 2>&1

# 日志轮转（建议）
# 每月检查 logs/model-guard.log 大小，超过10MB轮转
```

## 六、注意事项

1. 不影响正常使用（只清理锁定状态，不改默认配置）
2. 如果模型 Key 本身失效（非 Rate Limit），需手动更新 Key
3. 清理 override 后，Gateway 会重新使用 openclaw.json 中的默认模型
4. 守护脚本适用于所有 OpenClaw 实例

> **⚠️ 2026-06-10 清理**: 移除 agnes-1.5-flash 等不可用模型
