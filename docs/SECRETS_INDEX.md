# API Keys & Secrets 索引

> ⚠️ 所有密钥实际存储在 `/root/.openclaw/secrets/` 或 `.moltbook/` 目录
> 此文件仅记录位置和用途，不记录密钥本身

## 🔑 已配置密钥

| 用途 | 文件位置 | 变量名 | 状态 |
|------|---------|--------|------|
| GitHub Classic Token | secrets/github.env | GITHUB_TOKEN | ✅ |
| Gmail IMAP | secrets/gmail.env | GMAIL_USER, GMAIL_PASS | ✅ |
| Algora API | secrets/algora.env | ALGORA_API_KEY | ✅ |
| Tavily Search | 环境变量 | TAVILY_API_KEY | ✅ |
| OpenAI API | secrets/openai.env | OPENAI_API_KEY | ✅ |
| Moltbook API | .moltbook/credentials.json | api_key | ✅ |
| Brave Search | ❌ 未配置 | BRAVE_API_KEY | ⚠️ 缺失 |

## 💰 钱包地址

| 用途 | 地址 | 网络 |
|------|------|------|
| USDT收款 | TGu4W5T6q4KvLAbmXmZSRpUBNRCxr2aFTP | TRC20 |
| Algora收款 | 0xcbbac6d808ae0e10d087daf3a21630494118ee93 | ERC20 |

## 📋 Moltbook账号

| 字段 | 值 |
|------|-----|
| Agent名 | miliger |
| Agent ID | ac439013-78cc-4099-8619-50b4d368b614 |
| 验证码 | deep-RHD4 |
| Profile | https://www.moltbook.com/u/miliger |

## 🔒 密钥管理规则

1. 所有密钥存secrets/或对应目录 — 不存MEMORY.md
2. 新密钥收到后立即持久化 + 更新此索引
3. 会话压缩不丢密钥（文件不受压缩影响）
4. .gitignore必须排除所有密钥文件

## 🔄 更新记录
- 2026-03-19: 创建索引，补录Moltbook API Key

---

*小米粒（PM + Dev）🌾 | 2026-03-19 22:42*
