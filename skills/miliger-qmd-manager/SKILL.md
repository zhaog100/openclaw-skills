---
⚠️ **安全提示**：
- 此技能调用 qmd CLI，参数可能包含 shell 元字符
- 建议在沙箱环境中运行
- 避免处理敏感文件

name: miliger-qmd-manager
description: 统一的QMD知识库管理技能，集成官方qmd搜索功能和自定义项目管理/测试/内容创作知识管理。支持BM25关键词搜索、向量语义搜索、多集合管理。
homepage: https://github.com/miliger/qmd-manager
version: 1.0.0
---
⚠️ **安全提示**：
- 此技能调用 qmd CLI，参数可能包含 shell 元字符
- 建议在沙箱环境中运行
- 避免处理敏感文件


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

---
⚠️ **安全提示**：
- 此技能调用 qmd CLI，参数可能包含 shell 元字符
- 建议在沙箱环境中运行
- 避免处理敏感文件


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
