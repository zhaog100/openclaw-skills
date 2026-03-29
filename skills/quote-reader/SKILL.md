---
⚠️ **安全提示**：
- 检索真实消息需要 Feishu 凭据和适当权限
- get-feishu-token.sh 需要自行实现
- 请勿将凭据告诉 AI agent

name: quote-reader
description: 引用前文内容读取技能。当用户引用之前的消息时，自动检索并理解引用内容，支持飞书/QQ/企业微信交互式卡片内容获取。Trigger on "引用", "回复", "quote", "reply", "前文"。
version: 1.3.1
---
⚠️ **安全提示**：
- 检索真实消息需要 Feishu 凭据和适当权限
- get-feishu-token.sh 需要自行实现
- 请勿将凭据告诉 AI agent


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

---
⚠️ **安全提示**：
- 检索真实消息需要 Feishu 凭据和适当权限
- get-feishu-token.sh 需要自行实现
- 请勿将凭据告诉 AI agent


## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者：小米粒 (PM + Dev)

**商业使用授权**：
- 个人/开源：免费
- 小微企业（<10 人）：¥999/年
- 中型企业（10-50 人）：¥4,999/年
- 大型企业（>50 人）：¥19,999/年
- 源码买断：¥99,999 一次性

详情请查看：[LICENSE](../../LICENSE)
