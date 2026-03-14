# Tavily Search - AI-Optimized Web Search

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> AI优化的网页搜索，通过Tavily API返回简洁、相关的结果

## 🎯 简介

Tavily Search 是专门为AI代理设计的网页搜索工具，提供：
- ✅ **AI优化结果** - 返回干净、相关的片段
- ✅ **快速响应** - 针对AI应用优化
- ✅ **深度搜索** - 支持复杂研究问题
- ✅ **新闻搜索** - 针对时事和新闻
- ✅ **内容提取** - 从URL提取干净内容

## 🚀 快速开始

### 1. 获取API Key

访问 [https://tavily.com](https://tavily.com) 注册并获取API Key

### 2. 配置环境变量

```bash
export TAVILY_API_KEY="tvly-xxxxxx"
```

### 3. 基础用法

```bash
# 基础搜索
node scripts/search.mjs "量子计算最新进展"

# 指定结果数量
node scripts/search.mjs "AI趋势" -n 10

# 深度搜索（更全面，稍慢）
node scripts/search.mjs "复杂研究问题" --deep

# 新闻搜索
node scripts/search.mjs "今日要闻" --topic news

# 提取网页内容
node scripts/extract.mjs "https://example.com/article"
```

## 📚 功能详解

### 1. 基础搜索

```bash
node scripts/search.mjs "查询内容"
```

**特点**：
- 默认返回5条结果
- 结果已优化，直接可用
- 适合快速查询

**示例**：
```bash
node scripts/search.mjs "OpenAI最新产品"
```

---

### 2. 指定结果数量

```bash
node scripts/search.mjs "查询内容" -n 10
```

**参数**：
- `-n <count>`: 结果数量（默认5，最多20）

**示例**：
```bash
# 获取10条结果
node scripts/search.mjs "机器学习算法" -n 10

# 获取20条结果（最大值）
node scripts/search.mjs "深度学习框架对比" -n 20
```

---

### 3. 深度搜索

```bash
node scripts/search.mjs "查询内容" --deep
```

**特点**：
- 更全面的搜索
- 适合复杂研究问题
- 响应时间稍长

**适用场景**：
- 学术研究
- 技术调研
- 深度分析

**示例**：
```bash
# 深度研究
node scripts/search.mjs "量子计算机的商业应用前景" --deep
```

---

### 4. 新闻搜索

```bash
node scripts/search.mjs "查询内容" --topic news
```

**参数**：
- `--topic <topic>`: 搜索主题
  - `general`: 通用搜索（默认）
  - `news`: 新闻搜索
- `--days <n>`: 限制最近n天的新闻

**示例**：
```bash
# 今日新闻
node scripts/search.mjs "AI领域动态" --topic news

# 最近7天新闻
node scripts/search.mjs "科技新闻" --topic news --days 7

# 最近30天新闻
node scripts/search.mjs "行业趋势" --topic news --days 30
```

---

### 5. 内容提取

```bash
node scripts/extract.mjs "https://example.com/article"
```

**功能**：
- 从URL提取干净内容
- 移除广告和无关内容
- 返回格式化文本

**示例**：
```bash
# 提取文章内容
node scripts/extract.mjs "https://example.com/blog/ai-trends"

# 提取新闻内容
node scripts/extract.mjs "https://news.ycombinator.com/item?id=12345"
```

## 🎯 使用场景

### 1. 快速查询
```bash
# 快速了解某个话题
node scripts/search.mjs "什么是RAG"
```

### 2. 深度研究
```bash
# 复杂研究问题
node scripts/search.mjs "Transformer架构的演进历史" --deep
```

### 3. 新闻追踪
```bash
# 追踪最新动态
node scripts/search.mjs "OpenAI" --topic news --days 7
```

### 4. 内容提取
```bash
# 提取网页内容
node scripts/extract.mjs "https://example.com/long-article"
```

### 5. 多结果对比
```bash
# 对比多个来源
node scripts/search.mjs "Python vs JavaScript" -n 10
```

## ⚙️ 配置

### 环境变量

```bash
# Tavily API Key（必需）
export TAVILY_API_KEY="tvly-xxxxxx"
```

### Node.js 要求

- Node.js >= 14.0.0
- 依赖：无额外依赖

## 🔧 高级用法

### 1. 多关键词搜索

```bash
# 使用引号包裹复杂查询
node scripts/search.mjs "machine learning AND deep learning" -n 15
```

### 2. 时间范围限制

```bash
# 搜索最近7天的新闻
node scripts/search.mjs "AI突破" --topic news --days 7

# 搜索最近30天的新闻
node scripts/search.mjs "科技发展" --topic news --days 30
```

### 3. 结果格式

返回结果为JSON格式：
```json
[
  {
    "title": "文章标题",
    "url": "https://example.com/article",
    "content": "文章内容摘要",
    "score": 0.95
  },
  ...
]
```

## 📊 对比其他搜索工具

| 特性 | Tavily | 传统搜索 |
|------|--------|---------|
| **AI优化** | ✅ 专门优化 | ❌ 需要二次处理 |
| **结果清洁度** | ✅ 高 | ⚠️ 中等 |
| **响应速度** | ✅ 快 | ⚠️ 中等 |
| **深度搜索** | ✅ 支持 | ❌ 不支持 |
| **新闻搜索** | ✅ 支持 | ✅ 支持 |
| **内容提取** | ✅ 内置 | ❌ 需要额外工具 |

## 🎯 最佳实践

### 1. 选择合适的搜索模式

| 需求 | 推荐模式 |
|------|---------|
| 快速查询 | 基础搜索 |
| 深度研究 | `--deep` |
| 追踪动态 | `--topic news` |
| 提取内容 | `extract.mjs` |

### 2. 控制结果数量

- **快速浏览**：3-5条
- **常规查询**：5-10条
- **深度研究**：10-20条

### 3. 优化查询词

```bash
# ❌ 过于宽泛
node scripts/search.mjs "AI"

# ✅ 具体明确
node scripts/search.mjs "GPT-4 Turbo的改进点"
```

### 4. 使用深度搜索的时机

**推荐使用 `--deep`**：
- 学术研究
- 技术调研
- 市场分析
- 竞品对比

**不推荐使用 `--deep`**：
- 快速查询
- 简单问题
- 时间敏感

## 🚨 注意事项

### 1. API Key 安全

```bash
# ✅ 使用环境变量
export TAVILY_API_KEY="tvly-xxxxxx"

# ❌ 不要硬编码
# TAVILY_API_KEY="tvly-xxxxxx"  # 不安全
```

### 2. 使用限制

- 免费计划：每月1,000次查询
- 付费计划：按需购买

### 3. 结果质量

- 优先使用 `--deep` 进行深度研究
- 新闻搜索使用 `--topic news`
- 对比多个结果提高准确性

## 📞 技术支持

- **文档**：`SKILL.md`
- **官方文档**：https://docs.tavily.com
- **API文档**：https://docs.tavily.com/api-reference

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 米粒儿

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 米粒儿

详见 [LICENSE](../../LICENSE) 文件。

---

*最后更新：2026-03-14*
