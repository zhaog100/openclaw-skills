# LongCat API 配置指南

## 概述
LongCat（美团龙猫）是美团推出的免费 AI API 平台，OpenAI 兼容协议。

## 接入信息
- **Base URL**: `https://api.longcat.chat/openai`
- **Anthropic 格式**: `https://api.longcat.chat/anthropic`
- **协议**: OpenAI / Anthropic 兼容

## 模型列表（2026-04-09）
| 模型 | 输出上限 | 每日免费额度 |
|------|----------|-------------|
| LongCat-Flash-Lite | 320K | 5000万 token |
| LongCat-Flash-Chat | 256K | 50万→500万 |
| LongCat-Flash-Thinking-2601 | 256K | 50万→500万 |
| LongCat-Flash-Omni-2603 | 8K | 50万→500万 |
| LongCat-Flash-Chat-2602-Exp | 256K | 50万→500万 |

## 额度提升
- 访问用量信息页面申请提额
- Chat/Thinking 可从 50万提到 500万/天
- Lite 不参与提额

## OpenClaw 配置
1. **models.json** — 添加 provider + models
2. **auth-profiles.json** — 添加 `longcat:default` 条目（⚠️ 缺一不可！）
3. **默认模型** — 设为 `longcat/LongCat-Flash-Lite` 省钱

## 常见问题

### "Missing API key" 错误
- 原因: auth-profiles.json 中缺少 longcat:default
- 解决: 添加 `{"type":"api_key","provider":"longcat","key":"ak_xxx"}`

### 429 限流
- 自动切换到备用模型（zai/glm-5.1）
- 建议实现指数退避重试

## 参考链接
- 注册: https://longcat.chat/platform/
- 用量: https://longcat.chat/platform/usage
