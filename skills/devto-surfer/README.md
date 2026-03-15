# Dev.to Surfer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Surf Dev.to for AI tutorials and tech articles. Get latest articles, search by tags, and analyze trending topics.

## 🏄 简介

Dev.to Surfer 是一个 Dev.to 文章获取技能，专门用于获取 AI 教程和技术文章。

### 核心功能

- ✅ **Latest Articles** - 获取最新文章
- ✅ **Top Articles** - 获取最热门文章
- ✅ **Tag Search** - 按标签搜索（AI, machinelearning, python）
- ✅ **Article Details** - 获取文章完整内容
- ✅ **User Articles** - 获取特定用户的文章

## 🚀 快速开始

### API 基础信息

- **Base URL**: `https://dev.to/api/`
- **认证**: 无需 API Key
- **费用**: ✅ **免费**

### 端点

- `/articles` - 获取文章列表
- `/articles?tag=ai` - 按标签获取文章
- `/articles/{id}` - 获取文章详情
- `/articles?username=username` - 获取用户文章

## 📖 使用方法

### 获取最新文章

```bash
# 获取最新 10 篇文章
curl -s "https://dev.to/api/articles?per_page=10" | jq '.[] | {
  title: .title,
  url: .url,
  user: .user.username,
  reactions: .positive_reactions_count,
  comments: .comments_count
}'
```

### 搜索 AI 文章

```bash
# 获取 AI 标签文章
curl -s "https://dev.to/api/articles?tag=ai&per_page=10" | jq '.[] | {
  title: .title,
  url: .url,
  user: .user.username,
  reactions: .positive_reactions_count
}'
```

### 快速测试

```bash
# 测试 API 连接
curl -s "https://dev.to/api/articles?per_page=1" | jq '.[0].title'
```

## 💡 使用场景

- 获取 AI 教程和最新技术文章
- 分析热门话题和趋势
- 按标签搜索特定领域内容
- 获取技术文章详情

## 📦 安装

✅ **无需安装** - 使用公开 API

## 📂 文件结构

```
devto-surfer/
├── SKILL.md              # 技能文档
├── USAGE.md              # 使用指南
├── README.md             # 本文件
├── package.json          # 包信息
└── get-ai-tutorials.sh   # 脚本文件
```

## ⚠️ 速率限制

- **限制**: 1000 请求/10 分钟（每个 IP）
- **建议**: 友好使用，避免频繁请求

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
