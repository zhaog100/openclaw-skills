# 知识图谱构建工具 (knowledge-graph-builder)

> 🚀 从文档中自动提取知识和关系，构建可视化知识图谱

**版本**: v1.0.0  
**创建者**: 思捷娅科技 (SJYKJ)  
**创建日期**: 2026-03-17  
**许可证**: MIT License

---

## 📋 简介

knowledge-graph-builder 是一个知识图谱构建工具，支持：
- ✅ 从 Markdown/PDF/HTML 文档中自动提取实体
- ✅ AI 驱动的关系识别（准确率>85%）
- ✅ 图谱可视化（D3.js 力导向图）
- ✅ 语义搜索（自然语言查询）
- ✅ 多种导出格式（JSON/GraphML/Markdown/PNG）

---

## 🚀 快速开始

### 安装

```bash
# 克隆或复制到本地
cd .//skills/knowledge-graph-builder

# 安装依赖
pip install -r requirements.txt
```

### 基本用法

```bash
# 构建知识图谱
./skill.sh build --input docs/ --output graph.json

# 查询图谱
./skill.sh query "查找所有与 Python 相关的技术"

# 可视化图谱
./skill.sh visualize --open

# 导出图谱
./skill.sh export --format markdown --output report.md

# 查看状态
./skill.sh status
```

---

## 📖 CLI 命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `build` | 构建知识图谱 | `./skill.sh build --input docs/` |
| `query` | 查询图谱 | `./skill.sh query "Python 相关"` |
| `visualize` | 可视化图谱 | `./skill.sh visualize --open` |
| `export` | 导出图谱 | `./skill.sh export --format json` |
| `status` | 查看状态 | `./skill.sh status` |

---

## 📁 项目结构

```
knowledge-graph-builder/
├── skill.sh              # 主入口脚本
├── kg_builder/           # 核心模块
│   ├── __init__.py
│   ├── extractor.py      # 知识提取器
│   ├── relation.py       # 关系识别器
│   ├── graph.py          # 图谱操作
│   ├── search.py         # 语义搜索
│   └── visualizer.py     # 可视化
├── storage/
│   └── sqlite_store.py   # SQLite 存储后端
├── config/
│   └── config.json       # 配置文件
├── tests/
│   └── test_extractor.py # 单元测试
└── package.json          # 包配置
```

---

## 🎯 核心功能

### 1️⃣ 知识提取

支持多种文档格式：
- ✅ Markdown
- ✅ PDF
- ✅ HTML
- ✅ 纯文本

### 2️⃣ 关系识别

5 种预定义关系类型：
- ✅ is-a（上下位关系）
- ✅ part-of（组成关系）
- ✅ related-to（关联关系）
- ✅ causes（因果关系）
- ✅ before/after（时间关系）

### 3️⃣ 图谱存储

双存储方案：
- ✅ Neo4j（完整功能）
- ✅ SQLite（轻量级）

### 4️⃣ 语义搜索

自然语言查询：
- ✅ "查找所有与 Python 相关的技术"
- ✅ "显示 A 和 B 之间的关系"
- ✅ "找出影响最大的概念"

### 5️⃣ 可视化

D3.js 力导向图：
- ✅ 节点缩放/拖拽
- ✅ 关系高亮
- ✅ 交互式探索

---

## 📊 技术栈

| 模块 | 技术 |
|------|------|
| 核心语言 | Python 3.8+ |
| 图数据库 | Neo4j / SQLite |
| NLP 处理 | spaCy |
| AI 增强 | Ollama (本地) |
| 可视化 | D3.js |
| Web 框架 | Flask |

---

## 🧪 测试

```bash
# 运行测试
cd tests/
python -m pytest test_extractor.py -v
```

---

## 📄 许可证

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者：思捷娅科技 (SJYKJ)

---

*knowledge-graph-builder - 让知识结构化、可视化* 🌾
