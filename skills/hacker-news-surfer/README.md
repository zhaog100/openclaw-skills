# Hacker News Surfer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Surf Hacker News for AI and tech discussions. Get top stories, search for AI topics, and analyze trending tech news.

## 🏄 简介

Hacker News Surfer 是一个 Hacker News 文章获取技能，专门用于获取热门技术话题和 AI 相关讨论。

### 核心功能

- ✅ **Top Stories** - 获取当前热门文章
- ✅ **New Stories** - 获取最新提交
- ✅ **Best Stories** - 获取最高评分文章
- ✅ **Search AI Topics** - 搜索 AI 相关讨论
- ✅ **Story Details** - 获取评论和元数据

## 🚀 快速开始

### 无需安装

✅ **零配置** - 使用公开 API，无需 API Key

### 测试连接

```bash
# 测试 API 连接
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | jq -r '.[0]'
```

## 📖 使用方法

### 获取热门文章

```bash
# 获取前 10 个热门文章 ID
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | jq -r '.[:10]'

# 获取文章详情
curl -s "https://hacker-news.firebaseio.com/v0/item/47306655.json" | jq '{
  title: .title,
  url: .url,
  score: .score,
  by: .by,
  time: .time
}'
```

### 搜索 AI 话题

```bash
# 获取热门文章并筛选 AI 相关
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | \
  jq -r '.[:50]' | \
  while read id; do
    curl -s "https://hacker-news.firebaseio.com/v0/item/$id.json" | \
      jq -r 'select(.title | test("AI|artificial intelligence|machine learning|ML|GPT|Claude"; "i"))'
  done
```

## 📚 API 端点

**Base URL**: `https://hacker-news.firebaseio.com/v0/`

| 端点 | 说明 |
|------|------|
| `/topstories.json` | 热门文章 ID |
| `/newstories.json` | 最新文章 ID |
| `/beststories.json` | 最佳文章 ID |
| `/item/{id}.json` | 文章详情 |
| `/user/{id}.json` | 用户资料 |

## 💡 使用场景

- 获取 AI 技术趋势
- 监控热门技术讨论
- 发现优质技术文章
- 追踪技术社区动态
- 分析技术趋势

## 📂 文件结构

```
hacker-news-surfer/
├── SKILL.md             # 技能文档
├── USAGE.md             # 使用指南
├── README.md            # 本文件
├── package.json         # 包信息
└── get-ai-stories.sh    # 脚本文件
```

## ⚠️ 速率限制

- **限制**: 无官方限制
- **建议**: 友好使用（推荐 1 请求/秒）

## 📄 许可证

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 思捷娅科技 (SJYKJ)

详见 [LICENSE](../../LICENSE) 文件。

---

*最后更新：2026-03-14*
