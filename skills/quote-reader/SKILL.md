---
name: quote-reader
description: 引用前文内容读取技能。当用户引用之前的消息时，自动检索并理解引用内容，支持飞书/QQ/企业微信交互式卡片内容获取。Trigger on "引用", "回复", "quote", "reply", "前文"。
version: 1.3.1
---

# 引用前文内容读取技能 v1.1.0

智能识别用户引用的历史消息，通过平台API获取真实消息内容。

## 🎯 核心特性

- **多平台支持**：飞书（已完成）、QQ（待实现）、微信（待实现）
- **引用标记检测**：`[quote]`、`[reply]`、`[reply_to]`等
- **交互式卡片解析**：获取卡片完整JSON结构
- **意图识别**：澄清、补充、反驳、深入、关联
- **Token自动管理**：缓存Token，自动刷新

## 📊 引用识别规则

| 平台 | 引用标记 | 示例 |
|------|----------|------|
| 飞书 | `[quote]` | `[quote:om_x100b55b]` |
| QQ | `[reply]` | `[reply:12345678]` |
| 微信 | 引用消息结构 | `引用消息: {...}` |
| Telegram | `reply_to` | `reply_to_message_id: 123` |

## 🚀 使用方式

```bash
# 引用检测
scripts/detect-quote.sh "$USER_MESSAGE"

# 引用提取
scripts/extract-quote.sh '{"message_id":"..."}'

# AI集成（推荐）
scripts/integrate-quote.sh "$USER_MESSAGE"
```

## 📁 文件结构

```
quote-reader/
├── scripts/
│   ├── detect-quote.sh     # 引用检测
│   ├── extract-quote.sh    # 引用提取
│   └── integrate-quote.sh  # AI集成
├── config/
│   ├── quote-patterns.json # 引用模式
│   └── intent-rules.json   # 意图规则
└── data/quote-cache.json   # 缓存
```

## 🔧 配置

**quote-patterns.json**：定义各平台的引用正则模式
**intent-rules.json**：定义意图关键词和优先级（clarify/supplement/refute/deepen）

## ⚠️ 注意

- 限制检索范围最近50条消息
- 启用缓存避免重复检索
- 异步处理不阻塞AI回复

> 详细的技术实现、使用示例、性能指标、故障排除见 `references/skill-details.md`
