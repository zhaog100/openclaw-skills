---
name: session-memory-enhanced
description: "Session-Memory Enhanced v4.0 - 统一增强版。融合 session-memory + memu-engine 核心功能。特性：结构化提取 + 向量检索 + 不可变分片 + 三位一体自动化 + 多代理隔离 + AI 摘要 + 零配置启动。"
---

# Session-Memory Enhanced v4.0

融合 session-memory + memu-engine 的统一增强版记忆管理。

## 🎯 核心特性

**memu-engine 优势**：结构化提取、向量检索、多代理隔离、去重机制
**session-memory 优势**：不可变分片（Token节省90%+）、三位一体（记忆+QMD+Git）、AI摘要、零配置

## 🚀 使用方式

```bash
# 安装
cd skills/session-memory-enhanced
cp config/unified.json.example config/unified.json

# 自动模式（crontab）
0 * * * * $(pwd)/skills/session-memory-enhanced/scripts/session-memory-enhanced-v4.sh

# 手动执行
bash scripts/session-memory-enhanced-v4.sh

# 语义检索
python3 python/searcher.py --query "关键词" --db memory/agents/main/vectors.db
```

## 🔧 配置（unified.json）

```json
{
  "version": "4.0.0",
  "flushIdleSeconds": 1800,
  "maxMessagesPerPart": 60,
  "features": {
    "structuredExtraction": false,
    "vectorSearch": false,
    "aiSummary": true,
    "gitBackup": true,
    "qmdUpdate": true
  }
}
```

## 📁 文件结构

```
session-memory-enhanced/
├── scripts/session-memory-enhanced-v4.sh  # 主脚本
├── python/extractor.py, embedder.py, searcher.py
├── config/unified.json
└── docs/
```

## ⚙️ 环境变量

- `OPENAI_API_KEY`：向量嵌入和AI摘要（不提供时降级为纯文本模式）

> 详细功能对比、安装步骤、Python集成指南见 `references/skill-details.md`
