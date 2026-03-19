# API Keys & Secrets 索引

> ⚠️ 所有密钥实际存储在 `/root/.openclaw/secrets/` 目录，此文件仅记录位置和用途

## 🔑 已配置密钥

| 用途 | 文件位置 | 变量名 | 状态 |
|------|---------|--------|------|
| GitHub Classic Token | secrets/github.env | GITHUB_TOKEN (ghp_开头) | ✅ |
| Gmail IMAP | secrets/gmail.env | GMAIL_USER, GMAIL_PASS | ✅ |
| Algora API | secrets/algora.env | ALGORA_API_KEY | ✅ |
| Tavily Search | 环境变量 | TAVILY_API_KEY | ✅ |
| Brave Search | ❌ 未配置 | BRAVE_API_KEY | ⚠️ 缺失 |

## ❓ 待确认/可能丢失

| 用途 | 说明 | 状态 |
|------|------|------|
| Moltbook API Key | 官家说之前给过，会话压缩丢失 | ❓ 需重新提供 |
| OpenAI API Key | openai.env | ✅ |

## 💰 钱包地址

| 用途 | 地址 | 网络 |
|------|------|------|
| USDT收款 | TGu4W5T6q4KvLAbmXmZSRpUBNRCxr2aFTP | TRC20 |
| Algora收款 | 0xcbbac6d808ae0e10d087daf3a21630494118ee93 | ERC20 |

## 📋 密钥管理规则

1. **所有密钥存secrets/目录** — 不存MEMORY.md或其他md文件
2. **索引文件记录位置** — 本文件只记录"存在什么"，不记录密钥本身
3. **新密钥必须立即记录** — 收到后立即写入secrets/ + 更新此索引
4. **会话压缩不丢密钥** — secrets/文件不受会话压缩影响

## 🔄 更新记录
- 2026-03-19: 创建索引，发现Moltbook API Key丢失

---

*小米粒（PM + Dev）🌾 | 2026-03-19*
