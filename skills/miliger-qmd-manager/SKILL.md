---
name: miliger-qmd-manager
description: 统一的QMD知识库管理技能，集成官方qmd搜索功能和自定义项目管理/测试/内容创作知识管理。支持BM25关键词搜索、向量语义搜索、多集合管理。
homepage: https://github.com/miliger/qmd-manager
version: 1.0.0
---

# miliger-qmd-manager - 统一知识库管理

集成官方qmd搜索 + 自定义项目管理/测试/内容创作知识管理。

## 🎯 核心功能

- **BM25关键词搜索**（秒级）→ **向量语义搜索**（1-2分钟）→ **混合搜索**（2-5分钟，最准）
- **多集合管理**：项目管理(pm)、软件测试(testing)、内容创作(content)

## 🚀 使用方式

```bash
# 安装qmd
bun install -g @tobi/qmd  # 或 npm install -g @tobi/qmd

# 配置知识库
qmd collection add ./knowledge/project-management --name pm
qmd collection add ./knowledge/software-testing --name testing
qmd collection add ./knowledge/content-creation --name content
qmd embed  # 生成向量索引

# 搜索
qmd search "敏捷开发" -n 5              # 关键词搜索
qmd vsearch "如何提高效率" -c testing    # 语义搜索
qmd query "风险管理策略"                 # 混合搜索

# 获取文档
qmd get "knowledge/pm/pmp-guide.md"
qmd multi-get "doc1.md, doc2.md"
```

## 📊 搜索模式

| 模式 | 速度 | 准确度 | 适用 |
|------|------|--------|------|
| `search` | ⚡秒级 | ⭐⭐⭐ | 关键词明确 |
| `vsearch` | 🐢1-2分钟 | ⭐⭐⭐⭐ | 需要理解意图 |
| `query` | 🐌2-5分钟 | ⭐⭐⭐⭐⭐ | 最高质量 |

## 🛠️ 维护

```bash
qmd status    # 索引状态
qmd update    # 增量更新
qmd embed     # 重新生成向量
qmd clean     # 清理缓存
```

## ⚠️ 提示

- 优先用search，BM25通常够快够准
- vsearch首次慢（加载模型），后续快
- CPU模式：`export QMD_FORCE_CPU=1`

> 详细知识库结构、环境变量、使用场景见 `references/skill-details.md`
