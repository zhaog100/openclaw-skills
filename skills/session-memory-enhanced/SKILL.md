---
name: session-memory-enhanced
description: "Session-Memory Enhanced v4.0 - 统一增强版。融合 session-memory + memu-engine 核心功能。特性：结构化提取 + 向量检索 + 不可变分片 + 三位一体自动化 + 多代理隔离 + AI 摘要 + 零配置启动。"
version: 4.2.0
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

## 📖 分层读取策略（⚠️ 重要 - Token节省核心）

### 🚫 禁止全量读取 MEMORY.md（16KB+）
**绝对禁止**在任何场景下直接 `read MEMORY.md` 全量读取。这是最大的Token浪费源。

### 分层规则

| 场景 | 方法 | 预估Token |
|------|------|-----------|
| **会话启动** | 读 `MEMORY-LITE.md`（<3KB，唯一允许全量读取的记忆文件） | ~800 |
| **常规问题** | `memory_search("关键词")` 精准检索 | ~150 |
| **深度查询** | `memory_get(path="MEMORY.md", from=N, lines=50)` 按需读取 | ~200 |
| **历史日志** | `qmd search "关键词" -n 3` 语义检索 | ~200 |

### 操作指南

```bash
# ✅ 正确：精准检索
memory_search("用户偏好")
memory_search("项目决策")

# ✅ 正确：按需读取特定段落
memory_get(path="MEMORY.md", from=100, lines=50)

# ✅ 正确：启动时只读精简版
read MEMORY-LITE.md

# ❌ 禁止：全量读取
read MEMORY.md  # 绝对禁止！
```

### MEMORY-LITE.md 维护
- `MEMORY-LITE.md` 是唯一允许全量读取的记忆文件
- 必须控制在 **3KB 以内**（当前 ~2.5KB）
- 由定时脚本自动从 MEMORY.md 精华摘要生成
- 内容：核心偏好、关键决策、重要约束

## ⚙️ 环境变量

- `OPENAI_API_KEY`：向量嵌入和AI摘要（不提供时降级为纯文本模式）

> 详细功能对比、安装步骤、Python集成指南见 `references/skill-details.md`

---

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者：小米辣 (PM + Dev)

**商业使用授权**：
- 个人/开源：免费
- 小微企业（<10 人）：¥999/年
- 中型企业（10-50 人）：¥4,999/年
- 大型企业（>50 人）：¥19,999/年
- 源码买断：¥99,999 一次性

详情请查看：[LICENSE](../../LICENSE)
