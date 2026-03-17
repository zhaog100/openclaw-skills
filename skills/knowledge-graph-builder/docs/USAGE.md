# 知识图谱构建工具 - 使用指南

**版本**: v1.0.0  
**创建日期**: 2026-03-17  
**作者**: 思捷娅科技 (SJYKJ)

---

## 📋 目录

1. [快速开始](#快速开始)
2. [配置说明](#配置说明)
3. [使用示例](#使用示例)
4. [API 参考](#api 参考)
5. [常见问题](#常见问题)

---

## 快速开始

### 1. 安装依赖

```bash
cd /home/zhaog/.openclaw/workspace/skills/knowledge-graph-builder
pip install -r requirements.txt
```

### 2. 配置文件

编辑 `config/config.json`：

```json
{
  "storage": {
    "type": "sqlite",
    "path": "./data/knowledge_graph.db"
  },
  "extractor": {
    "languages": ["zh", "en"]
  }
}
```

### 3. 构建图谱

```bash
./skill.sh build --input docs/ --output graph.json
```

### 4. 可视化

```bash
./skill.sh visualize --open
```

---

## 配置说明

### 存储配置

```json
{
  "storage": {
    "type": "sqlite",  // 或 neo4j
    "path": "./data/knowledge_graph.db",
    "neo4j": {
      "uri": "bolt://localhost:7687",
      "user": "neo4j",
      "password": "password"
    }
  }
}
```

### 提取器配置

```json
{
  "extractor": {
    "languages": ["zh", "en"],
    "ai_engine": "ollama",
    "ollama": {
      "model": "llama3",
      "base_url": "http://localhost:11434"
    }
  }
}
```

---

## 使用示例

### 示例 1：从 Markdown 文档构建图谱

```bash
./skill.sh build --input docs/products/ --output products_graph.json
```

### 示例 2：查询相关知识

```bash
./skill.sh query "与 Python 相关的所有技术"
```

### 示例 3：导出为 Markdown 报告

```bash
./skill.sh export --format markdown --output knowledge_report.md
```

### 示例 4：使用 Python API

```python
from kg_builder import KnowledgeExtractor, KnowledgeGraph
from storage.sqlite_store import SQLiteStorage

# 创建提取器
extractor = KnowledgeExtractor()

# 提取实体
entities = extractor.extract_from_document("docs/readme.md")

# 创建图谱
storage = SQLiteStorage("my_graph.db")
graph = KnowledgeGraph(storage)

# 添加实体
for entity in entities:
    graph.add_entity(entity)

# 查询
results = graph.search("Python")
print(results)
```

---

## API 参考

### KnowledgeExtractor

```python
class KnowledgeExtractor:
    def extract_from_document(file_path: str) -> List[Entity]
    def extract_from_directory(dir_path: str, pattern: str) -> List[Entity]
    def get_entities() -> List[Entity]
    def clear()
```

### KnowledgeGraph

```python
class KnowledgeGraph:
    def add_entity(entity: Entity) -> str
    def add_relation(relation: Relation) -> str
    def search(query: str) -> List[Any]
    def find_path(start: str, end: str) -> List[Any]
    def get_neighbors(entity_id: str, depth: int) -> List[Any]
    def get_stats() -> Dict[str, Any]
    def export(format: str) -> str
```

---

## 常见问题

### Q1: 支持哪些文档格式？

A: 支持 Markdown、PDF、HTML 和纯文本格式。

### Q2: 如何切换到 Neo4j 存储？

A: 修改 `config/config.json` 中的 `storage.type` 为 `neo4j`，并配置连接信息。

### Q3: 关系识别准确率如何？

A: 基础规则识别准确率约 70%，AI 增强后可达 85%+。

### Q4: 如何自定义关系类型？

A: 在 `config/config.json` 的 `relation.templates` 中添加自定义关系模式。

---

*更多问题请查看 GitHub Issues 或联系作者* 🌾
