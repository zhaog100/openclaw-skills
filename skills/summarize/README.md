# Summarize

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 快速摘要工具 - 支持URL、PDF、图片、音频、YouTube视频的智能摘要

## 🎯 简介

Summarize 是一个快速的CLI工具，使用AI技术对多种格式的内容进行摘要。

### 支持的格式

- ✅ **网页** - 任何URL
- ✅ **PDF文档** - 本地或在线PDF
- ✅ **图片** - 支持多种图片格式
- ✅ **音频** - 音频转录
- ✅ **YouTube视频** - 视频内容摘要

## 🚀 快速开始

### 安装

✅ **已预装**：`summarize` CLI已安装

### 基础用法

```bash
# 摘要网页
summarize "https://example.com"

# 摘要PDF
summarize "/path/to/file.pdf"

# 摘要YouTube视频
summarize "https://youtu.be/dQw4w9WgXcQ" --youtube auto
```

## 🔧 配置

### API密钥设置

```bash
# OpenAI
export OPENAI_API_KEY="sk-xxx"

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-xxx"

# xAI
export XAI_API_KEY="xai-xxx"

# Google Gemini
export GEMINI_API_KEY="AIza-xxx"
# 别名：GOOGLE_GENERATIVE_AI_API_KEY, GOOGLE_API_KEY
```

### 可选服务

```bash
# 用于访问被屏蔽的网站
export FIRECRAWL_API_KEY="fc-xxx"

# 用于YouTube视频（fallback）
export APIFY_API_TOKEN="apify_api_xxx"
```

### 配置文件

创建配置文件：`~/.summarize/config.json`

```json
{
  "model": "openai/gpt-5.2",
  "length": "medium"
}
```

## 📚 详细功能

### 1. 网页摘要

```bash
# 默认长度
summarize "https://example.com"

# 指定长度
summarize "https://example.com" --length short
summarize "https://example.com" --length xxl

# 仅提取内容（不生成摘要）
summarize "https://example.com" --extract-only
```

### 2. PDF文档

```bash
# 本地PDF
summarize "/path/to/document.pdf"

# 在线PDF
summarize "https://example.com/document.pdf"

# 指定输出长度
summarize "report.pdf" --length xl
```

### 3. YouTube视频

```bash
# 自动使用Apify（如果配置）
summarize "https://youtu.be/dQw4w9WgXcQ" --youtube auto
```

### 4. 音频

```bash
# 音频文件
summarize "/path/to/podcast.mp3"

# 指定模型
summarize "interview.wav" --model google/gemini-3-flash-preview
```

## ⚙️ 高级选项

### 模型选择

```bash
# 指定模型
summarize "url" --model openai/gpt-5.2
summarize "url" --model anthropic/claude-5
summarize "url" --model google/gemini-3-flash-preview
summarize "url" --model xai/grok-2-latest
```

**默认模型**：`google/gemini-3-flash-preview`

### 输出控制

```bash
# 指定摘要长度
--length short     # 简短
--length medium    # 中等
--length long      # 详细
--length xl        # 超长
--length xxl       # 极长
--length 500       # 指定字符数

# 控制输出token数
--max-output-tokens 1000

# JSON输出（机器可读）
--json
```

### 高级提取

```bash
# 使用Firecrawl（处理复杂/被屏蔽网站）
--firecrawl always
--firecrawl auto

# 仅提取内容（不生成摘要）
--extract-only
```

## 🎯 使用场景

### 1. 研究与学习

```bash
# 快速了解论文
summarize "https://arxiv.org/abs/1234.56789" --length long

# 摘要技术文档
summarize "https://docs.example.com/guide" --length xl
```

### 2. 内容创作

```bash
# 摘要参考文章
summarize "https://blog.example.com/post" --length medium

# 快速了解视频内容
summarize "https://youtu.be/xyz" --youtube auto
```

### 3. 信息整理

```bash
# 批量摘要
for url in $(cat urls.txt); do
  echo "=== $url ===" >> summary.txt
  summarize "$url" >> summary.txt
  echo "" >> summary.txt
done
```

## 📊 支持的提供商

| 提供商 | 环境变量 | 推荐用途 |
|--------|---------|---------|
| **OpenAI** | `OPENAI_API_KEY` | 通用摘要 |
| **Anthropic** | `ANTHROPIC_API_KEY` | 高质量摘要 |
| **Google** | `GEMINI_API_KEY` | 快速且免费 |
| **xAI** | `XAI_API_KEY` | 创意内容 |

## 🔍 故障排查

### 问题1：无法访问网站

**解决方案**：使用Firecrawl

```bash
summarize "url" --firecrawl always
```

### 问题2：YouTube视频无法处理

**解决方案**：配置Apify

```bash
export APIFY_API_TOKEN="apify_api_xxx"
summarize "youtube_url" --youtube auto
```

### 问题3：API密钥未识别

**检查**：
```bash
echo $GEMINI_API_KEY
echo $OPENAI_API_KEY
```

## 📝 最佳实践

### 1. 选择合适的长度

| 内容类型 | 推荐长度 | 说明 |
|---------|---------|------|
| 新闻文章 | `short` | 快速了解要点 |
| 技术文档 | `medium` | 平衡细节与速度 |
| 研究论文 | `long/xl` | 需要详细理解 |
| 长视频 | `xl/xxl` | 复杂内容 |

### 2. 模型选择建议

- **速度优先**：`google/gemini-3-flash-preview`（默认）
- **质量优先**：`anthropic/claude-5`
- **成本敏感**：`google/gemini-3-flash-preview`

### 3. 批量处理

```bash
# 批量摘要脚本
#!/bin/bash
while IFS= read -r url; do
  echo "Processing: $url"
  summarize "$url" --json >> results.jsonl
done < urls.txt
```

## 📖 详细文档

- **SKILL.md** - 详细使用说明
- **官方文档**：https://summarize.sh/docs
- **GitHub**：https://github.com/steipete/summarize

## 📞 技术支持

- **官网**：https://summarize.sh
- **文档**：`SKILL.md`
- **GitHub**：https://github.com/steipete/suminci

## 📄 许可证

MIT License

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 思捷娅科技 (SJYKJ)

详见 [LICENSE](../../LICENSE) 文件。

---

*最后更新：2026-03-14*
