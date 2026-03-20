---
name: knowledge-graph-builder
description: 知识图谱构建工具。从文档中自动提取知识和关系，支持图谱可视化、语义搜索、多种导出格式。
version: 1.0.1
---

# 知识图谱构建工具 (knowledge-graph-builder)

**版本**: v1.0.0  
**创建时间**: 2026-03-17  
**创建者**: 思捷娅科技 (SJYKJ)  
**用途**: 构建知识图谱，支持知识提取、关系识别、图谱可视化

---

## 🎯 核心功能

### 1. 知识提取
- ✅ 支持 Markdown/PDF/HTML/Text 格式
- ✅ 实体识别（人名/地名/组织/技术术语）
- ✅ AI 增强属性提取

### 2. 关系识别
- ✅ 5 种预定义关系类型
- ✅ 规则 + AI 混合识别
- ✅ 置信度评分

### 3. 图谱存储
- ✅ Neo4j（完整功能）
- ✅ SQLite（轻量级）
- ✅ 抽象接口设计

### 4. 语义搜索
- ✅ 自然语言查询
- ✅ 路径查找
- ✅ 邻居节点展开

### 5. 图谱可视化
- ✅ D3.js 力导向图
- ✅ 节点缩放/拖拽
- ✅ 关系高亮

---

## 🚀 使用方法

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

## 📁 文件结构

```
knowledge-graph-builder/
├── skill.sh              # 主入口
├── kg_builder/           # 核心模块
│   ├── extractor.py      # 知识提取
│   ├── relation.py       # 关系识别
│   ├── graph.py          # 图谱操作
│   ├── search.py         # 语义搜索
│   └── visualizer.py     # 可视化
├── storage/
│   └── sqlite_store.py   # SQLite 存储
├── config/
│   └── config.json       # 配置
├── tests/
│   └── test_extractor.py # 测试
└── package.json          # 包配置
```

---

## 📊 技术栈

- **语言**: Python 3.8+
- **图数据库**: Neo4j / SQLite
- **NLP**: spaCy
- **AI**: Ollama (本地)
- **可视化**: D3.js

---

## 🧪 测试

```bash
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
