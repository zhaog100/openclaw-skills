---
name: hacker-news-surfer
description: Surf Hacker News for AI and tech discussions. Get top stories, search for AI topics, and analyze trending tech news.
---

# Hacker News Surfer

Hacker News（HN）冲浪技能，获取热门技术话题和 AI 相关讨论。

## Features

- ✅ **Top Stories** - Get current top stories
- ✅ **New Stories** - Get latest submissions
- ✅ **Best Stories** - Get highest-rated stories
- ✅ **Search AI Topics** - Find AI-related discussions
- ✅ **Story Details** - Get comments and metadata

## API

**Base URL**: `https://hacker-news.firebaseio.com/v0/`

**Endpoints**:
- `/topstories.json` - Top story IDs
- `/newstories.json` - New story IDs
- `/beststories.json` - Best story IDs
- `/item/{id}.json` - Story details
- `/user/{id}.json` - User profile

## Usage

### Get Top Stories

```bash
# Get top 10 story IDs
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | jq -r '.[:10]'

# Get story details
curl -s "https://hacker-news.firebaseio.com/v0/item/47306655.json" | jq '{
  title: .title,
  url: .url,
  score: .score,
  by: .by,
  time: .time
}'
```

### Search AI Topics

```bash
# Get top stories and filter for AI
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | \
  jq -r '.[:50]' | \
  while read id; do
    curl -s "https://hacker-news.firebaseio.com/v0/item/$id.json" | \
      jq -r 'select(.title | test("AI|artificial intelligence|machine learning|ML|GPT|Claude"; "i"))'
  done
```

## Quick Test

```bash
# Test API connection
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | jq -r '.[0]'
```

## Examples

See `USAGE.md` for detailed examples:
- Get top AI stories
- Search specific topics
- Analyze story trends
- Get user profiles

## Installation

✅ No installation required - uses public API

## Rate Limit

- No official rate limit
- Be respectful (1 request/second recommended)

## Cost

- ✅ **Free** - No API key required

---

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者：小米辣 (miliger)

**商业使用授权**：
- 小微企业（<10 人）：¥999/年
- 中型企业（10-50 人）：¥4,999/年
- 大型企业（>50 人）：¥19,999/年
- 企业定制版：¥99,999 一次性（源码买断）
