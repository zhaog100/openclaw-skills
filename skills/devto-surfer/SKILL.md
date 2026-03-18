---
name: devto-surfer
description: Surf Dev.to for AI tutorials and tech articles. Get latest articles, search by tags, and analyze trending topics.
---

# Dev.to Surfer

Dev.to 冲浪技能，获取 AI 教程和技术文章。

## Features

- ✅ **Latest Articles** - Get newest posts
- ✅ **Top Articles** - Get most popular posts
- ✅ **Tag Search** - Search by tags (AI, machinelearning, python)
- ✅ **Article Details** - Get full article content
- ✅ **User Articles** - Get posts by specific user

## API

**Base URL**: `https://dev.to/api/`

**Endpoints**:
- `/articles` - Get articles
- `/articles?tag=ai` - Get articles by tag
- `/articles/{id}` - Get article details
- `/articles?username=username` - Get user articles

## Usage

### Get Latest Articles

```bash
# Get latest 10 articles
curl -s "https://dev.to/api/articles?per_page=10" | jq '.[] | {
  title: .title,
  url: .url,
  user: .user.username,
  reactions: .positive_reactions_count,
  comments: .comments_count
}'
```

### Search AI Articles

```bash
# Get AI-tagged articles
curl -s "https://dev.to/api/articles?tag=ai&per_page=10" | jq '.[] | {
  title: .title,
  url: .url,
  user: .user.username,
  reactions: .positive_reactions_count
}'
```

## Quick Test

```bash
# Test API connection
curl -s "https://dev.to/api/articles?per_page=1" | jq '.[0].title'
```

## Examples

See `USAGE.md` for detailed examples:
- Get top AI tutorials
- Search by multiple tags
- Get article details
- Analyze trending topics

## Installation

✅ No installation required - uses public API

## Rate Limit

- 1000 requests/10 minutes (per IP)
- Be respectful

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
