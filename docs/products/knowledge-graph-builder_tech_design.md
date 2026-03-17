# 技术设计文档 - knowledge-graph-builder

**文档版本**: v1.0  
**创建日期**: 2026-03-17 10:32  
**创建者**: 小米辣 (PM + Dev 双代理) 🌶️  
**关联 PRD**: `docs/products/2026-03-12_knowledge-graph-builder_PRD.md`  
**关联 Issue**: #24

---

## 1. 系统架构

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Web UI (D3.js)                         │
│                    图谱可视化 + 交互                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                      │
│              REST API + WebSocket (实时推送)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Engine (Python)                     │
│  ┌──────────────┬──────────────┬──────────────┬──────────┐ │
│  │  Extractor   │  Relation    │    Graph     │  Search  │ │
│  │  知识提取     │  关系识别     │   图谱操作    │  语义搜索 │ │
│  └──────────────┴──────────────┴──────────────┴──────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                            │
│         ┌─────────────────┐    ┌─────────────────┐         │
│         │   Neo4j Store   │    │  SQLite Store   │         │
│         │   (完整功能)     │    │   (轻量级)      │         │
│         └─────────────────┘    └─────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Integration Layer                        │
│         ┌──────────┐    ┌──────────┐    ┌──────────┐       │
│         │   QMD    │    │ MEMORY   │    │   Git    │       │
│         │ 知识库    │    │  记忆    │    │  版本    │       │
│         └──────────┘    └──────────┘    └──────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 技术选型

| 层级 | 技术 | 选型理由 |
|------|------|---------|
| **核心语言** | Python 3.8+ | 丰富的 NLP 和图处理库 |
| **API 框架** | FastAPI | 高性能，自动文档，异步支持 |
| **图数据库** | Neo4j 社区版 | 成熟的图数据库，Cypher 查询 |
| **轻量存储** | SQLite + NetworkX | 零依赖，适合小规模 |
| **NLP 处理** | spaCy | 高性能实体识别 |
| **AI 增强** | Ollama (Llama 3) | 本地部署，隐私保护 |
| **可视化** | D3.js + ECharts | 强大的力导向图 |
| **Web 框架** | Flask | 轻量，易集成 |

---

## 2. 模块设计

### 2.1 Extractor 模块（知识提取）

```python
# kg_builder/extractor.py

class KnowledgeExtractor:
    """知识提取器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.nlp = spacy.load("zh_core_web_sm")  # 中文 NLP 模型
        self.ai_engine = OllamaEngine()  # AI 增强引擎
    
    def extract_from_document(self, file_path: str) -> List[Entity]:
        """从文档中提取实体"""
        content = self._parse_document(file_path)
        entities = self._extract_entities(content)
        entities = self._ai_enhance(entities)  # AI 增强
        return entities
    
    def _parse_document(self, file_path: str) -> str:
        """解析文档（支持 Markdown/PDF/HTML）"""
        if file_path.endswith('.md'):
            return self._parse_markdown(file_path)
        elif file_path.endswith('.pdf'):
            return self._parse_pdf(file_path)
        elif file_path.endswith('.html'):
            return self._parse_html(file_path)
        else:
            return self._parse_text(file_path)
    
    def _extract_entities(self, content: str) -> List[Entity]:
        """提取实体（规则 + NLP）"""
        # 1. 基于规则的初步提取
        rule_entities = self._rule_based_extract(content)
        
        # 2. 基于 NLP 的实体识别
        nlp_entities = self._nlp_based_extract(content)
        
        # 3. 合并去重
        return self._merge_entities(rule_entities, nlp_entities)
    
    def _ai_enhance(self, entities: List[Entity]) -> List[Entity]:
        """AI 增强（补充属性、分类）"""
        # 使用 Ollama 本地模型增强实体信息
        pass
```

**核心类**：
- `KnowledgeExtractor` - 主提取器
- `Entity` - 实体数据类
- `DocumentParser` - 文档解析器
- `OllamaEngine` - AI 增强引擎

---

### 2.2 Relation 模块（关系识别）

```python
# kg_builder/relation.py

class RelationExtractor:
    """关系提取器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.relation_templates = self._load_templates()
        self.ai_engine = OllamaEngine()
    
    def extract_relations(self, entities: List[Entity]) -> List[Relation]:
        """从实体中提取关系"""
        relations = []
        
        # 1. 基于规则的关系抽取
        rule_relations = self._rule_based_extract(entities)
        relations.extend(rule_relations)
        
        # 2. 基于 AI 的关系抽取
        ai_relations = self._ai_based_extract(entities)
        relations.extend(ai_relations)
        
        # 3. 关系去重和置信度评分
        return self._score_and_deduplicate(relations)
    
    def _rule_based_extract(self, entities: List[Entity]) -> List[Relation]:
        """基于规则的关系抽取"""
        relations = []
        for entity1, entity2 in combinations(entities, 2):
            # 检查预定义关系模板
            for template in self.relation_templates:
                if template.match(entity1, entity2):
                    relations.append(template.create_relation(entity1, entity2))
        return relations
    
    def _ai_based_extract(self, entities: List[Entity]) -> List[Relation]:
        """基于 AI 的关系抽取"""
        # 使用 Ollama 识别潜在关系
        pass
    
    def _score_and_deduplicate(self, relations: List[Relation]) -> List[Relation]:
        """置信度评分和去重"""
        # 计算关系置信度
        for rel in relations:
            rel.confidence = self._calculate_confidence(rel)
        
        # 去重（保留高置信度）
        return self._deduplicate_by_confidence(relations)
```

**关系类型**：
- `is-a` - 上下位关系
- `part-of` - 组成关系
- `related-to` - 关联关系
- `causes` - 因果关系
- `before/after` - 时间关系

---

### 2.3 Graph 模块（图谱操作）

```python
# kg_builder/graph.py

class KnowledgeGraph:
    """知识图谱"""
    
    def __init__(self, storage: StorageBackend):
        self.storage = storage
        self.cache = LRUCache(maxsize=1000)
    
    def add_entity(self, entity: Entity) -> str:
        """添加实体"""
        return self.storage.create_node(entity)
    
    def add_relation(self, relation: Relation) -> str:
        """添加关系"""
        return self.storage.create_edge(relation)
    
    def search(self, query: str) -> List[Entity]:
        """搜索实体"""
        # 缓存查询
        if query in self.cache:
            return self.cache[query]
        
        # 执行搜索
        results = self.storage.search(query)
        self.cache[query] = results
        return results
    
    def find_path(self, start: str, end: str) -> List[Relation]:
        """查找两点间路径"""
        return self.storage.find_shortest_path(start, end)
    
    def get_neighbors(self, entity_id: str, depth: int = 1) -> List[Entity]:
        """获取邻居节点"""
        return self.storage.get_neighbors(entity_id, depth)
    
    def export(self, format: str) -> str:
        """导出图谱"""
        if format == 'json':
            return self._export_json()
        elif format == 'graphml':
            return self._export_graphml()
        elif format == 'markdown':
            return self._export_markdown()
```

**存储后端接口**：
```python
class StorageBackend(ABC):
    """存储后端抽象接口"""
    
    @abstractmethod
    def create_node(self, entity: Entity) -> str:
        pass
    
    @abstractmethod
    def create_edge(self, relation: Relation) -> str:
        pass
    
    @abstractmethod
    def search(self, query: str) -> List[Entity]:
        pass
    
    @abstractmethod
    def find_shortest_path(self, start: str, end: str) -> List[Relation]:
        pass
```

---

### 2.4 Search 模块（语义搜索）

```python
# kg_builder/search.py

class SemanticSearcher:
    """语义搜索器"""
    
    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph
        self.nlp = spacy.load("zh_core_web_sm")
        self.ai_engine = OllamaEngine()
    
    def search(self, query: str) -> SearchResult:
        """语义搜索"""
        # 1. 解析查询意图
        intent = self._parse_intent(query)
        
        # 2. 转换为图查询
        graph_query = self._intent_to_query(intent)
        
        # 3. 执行查询
        results = self.graph.execute(graph_query)
        
        # 4. 排序和推荐
        return self._rank_and_recommend(results, intent)
    
    def _parse_intent(self, query: str) -> Intent:
        """解析查询意图"""
        # 使用 AI 解析自然语言意图
        # 例如："查找所有与 Python 相关的技术"
        # -> Intent(type="find_related", entity="Python", relation="related-to")
        pass
    
    def _intent_to_query(self, intent: Intent) -> GraphQuery:
        """将意图转换为图查询"""
        # 根据意图类型生成 Cypher/SQL 查询
        pass
```

---

## 3. 数据库设计

### 3.1 Neo4j 数据模型

```cypher
// 节点标签
:Entity {
    id: STRING,          // 唯一 ID
    name: STRING,        // 实体名称
    type: STRING,        // 实体类型
    description: STRING, // 描述
    properties: MAP,     // 属性
    created_at: DATETIME,
    updated_at: DATETIME
}

// 关系类型
[:IS_A]          // 上下位
[:PART_OF]       // 组成
[:RELATED_TO]    // 关联
[:CAUSES]        // 因果
[:BEFORE]        // 时间前
[:AFTER]         // 时间后

// 关系属性
{
    confidence: FLOAT,   // 置信度
    source: STRING,      // 来源文档
    extracted_at: DATETIME
}
```

### 3.2 SQLite 数据模型

```sql
-- 实体表
CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    properties JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 关系表
CREATE TABLE relations (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    type TEXT NOT NULL,
    confidence REAL DEFAULT 0.5,
    source TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES entities(id),
    FOREIGN KEY (target_id) REFERENCES entities(id)
);

-- 索引
CREATE INDEX idx_entity_name ON entities(name);
CREATE INDEX idx_entity_type ON entities(type);
CREATE INDEX idx_relation_type ON relations(type);
CREATE INDEX idx_relation_source ON relations(source_id);
CREATE INDEX idx_relation_target ON relations(target_id);
```

---

## 4. API 设计

### 4.1 REST API

```python
# API 端点设计

# 图谱操作
POST   /api/v1/graph/build          # 构建图谱
GET    /api/v1/graph/stats          # 图谱统计
DELETE /api/v1/graph/clear          # 清空图谱

# 实体操作
POST   /api/v1/entities             # 添加实体
GET    /api/v1/entities/{id}        # 获取实体
PUT    /api/v1/entities/{id}        # 更新实体
DELETE /api/v1/entities/{id}        # 删除实体
GET    /api/v1/entities             # 搜索实体

# 关系操作
POST   /api/v1/relations            # 添加关系
GET    /api/v1/relations/{id}       # 获取关系
DELETE /api/v1/relations/{id}       # 删除关系

# 搜索
POST   /api/v1/search               # 语义搜索
GET    /api/v1/search/path          # 路径查找
GET    /api/v1/search/neighbors     # 邻居节点

# 导出
GET    /api/v1/export/json          # 导出 JSON
GET    /api/v1/export/graphml       # 导出 GraphML
GET    /api/v1/export/markdown      # 导出 Markdown
GET    /api/v1/export/png           # 导出 PNG
```

### 4.2 WebSocket（实时推送）

```python
# WebSocket 事件

# 服务端 -> 客户端
{
    "event": "graph.updated",      # 图谱更新
    "data": {"added": 10, "removed": 2}
}

{
    "event": "build.progress",     # 构建进度
    "data": {"current": 50, "total": 100, "status": "extracting"}
}

{
    "event": "search.results",     # 搜索结果
    "data": {"entities": [...], "relations": [...]}
}
```

---

## 5. 文件结构

```
knowledge-graph-builder/
├── skill.sh                    # 主入口脚本
├── kg_builder/                 # 核心模块
│   ├── __init__.py
│   ├── extractor.py            # 知识提取 (500 行)
│   ├── relation.py             # 关系识别 (400 行)
│   ├── graph.py                # 图谱操作 (600 行)
│   ├── search.py               # 语义搜索 (300 行)
│   ├── visualizer.py           # 可视化 (300 行)
│   └── ai_engine.py            # AI 引擎 (200 行)
├── storage/                    # 存储层
│   ├── __init__.py
│   ├── base.py                 # 抽象接口 (100 行)
│   ├── neo4j_store.py          # Neo4j 实现 (400 行)
│   └── sqlite_store.py         # SQLite 实现 (300 行)
├── web/                        # Web UI
│   ├── app.py                  # Flask 应用 (200 行)
│   ├── templates/
│   │   ├── index.html          # 主页面
│   │   └── graph.html          # 图谱可视化
│   └── static/
│       ├── js/
│       │   ├── graph.js        # 图谱逻辑
│       │   └── visualizer.js   # 可视化逻辑
│       └── css/
│           └── style.css       # 样式
├── config/
│   └── config.json             # 配置文件
├── tests/
│   ├── test_extractor.py       # 提取测试
│   ├── test_relation.py        # 关系测试
│   ├── test_graph.py           # 图谱测试
│   └── test_search.py          # 搜索测试
├── docs/
│   ├── API.md                  # API 文档
│   └── USAGE.md                # 使用指南
├── SKILL.md                    # 技能文档
├── README.md                   # 使用说明
└── package.json                # 包配置
```

**总计**：约 4000 行代码

---

## 6. 开发计划

### Phase 1 (MVP) - 3 天

| Day | 任务 | 产出 |
|-----|------|------|
| **Day 1** | 核心架构 + 知识提取 | extractor.py, 文档解析 |
| **Day 2** | 关系识别 + 图谱存储 | relation.py, sqlite_store.py |
| **Day 3** | 基础 CLI + 单元测试 | skill.sh, tests/ |

### Phase 2 (增强) - 3 天

| Day | 任务 | 产出 |
|-----|------|------|
| **Day 4** | Web UI 可视化 | web/, D3.js 集成 |
| **Day 5** | 语义搜索 | search.py, AI 意图解析 |
| **Day 6** | 导出功能 + 集成测试 | export/, 集成测试 |

### Phase 3 (集成) - 2 天

| Day | 任务 | 产出 |
|-----|------|------|
| **Day 7** | OpenClaw 集成 | QMD/MEMORY/Git集成 |
| **Day 8** | 性能优化 + 文档 | 缓存，索引，文档 |

---

## 7. 测试策略

### 7.1 单元测试

```python
# tests/test_extractor.py

def test_extract_from_markdown():
    extractor = KnowledgeExtractor(config)
    entities = extractor.extract_from_document("test.md")
    assert len(entities) > 0
    assert all(isinstance(e, Entity) for e in entities)

def test_ai_enhancement():
    extractor = KnowledgeExtractor(config)
    entities = extractor._ai_enhance([Entity(name="Python")])
    assert entities[0].type == "Technology"
```

### 7.2 集成测试

```python
# tests/test_integration.py

def test_build_graph():
    kg = KnowledgeGraph(SQLiteStorage())
    extractor = KnowledgeExtractor(config)
    
    # 构建图谱
    entities = extractor.extract_from_document("docs/")
    for e in entities:
        kg.add_entity(e)
    
    # 验证
    assert kg.count_nodes() > 0
    assert kg.count_edges() > 0
```

### 7.3 性能测试

```python
# tests/test_performance.py

def test_large_graph():
    kg = KnowledgeGraph(Neo4jStorage())
    
    # 添加 1000 个节点
    start = time.time()
    for i in range(1000):
        kg.add_entity(Entity(name=f"Entity_{i}"))
    elapsed = time.time() - start
    
    assert elapsed < 600  # <10 分钟
```

---

## 8. 风险与缓解

| 风险 | 影响 | 缓解措施 | 状态 |
|------|------|---------|------|
| **Neo4j 部署复杂** | 高 | 提供 SQLite 轻量替代 | ✅ 已缓解 |
| **关系识别准确率低** | 中 | AI 增强 + 人工校验 | ✅ 已缓解 |
| **大规模性能问题** | 中 | 分页 + 缓存 + 索引 | ✅ 已缓解 |
| **与 QMD 集成困难** | 低 | 使用标准 API | ✅ 已缓解 |

---

## 9. 验收标准

### 9.1 功能验收

- [ ] 支持 Markdown/PDF/HTML 解析
- [ ] 实体识别准确率 >90%
- [ ] 关系识别准确率 >85%
- [ ] 支持 5+ 种关系类型
- [ ] Web UI 可视化可用
- [ ] 语义搜索可用
- [ ] 导出功能完整

### 9.2 性能验收

- [ ] 构建 1000 节点 <10 分钟
- [ ] 查询响应 <2s (P95)
- [ ] 并发 10 用户无卡顿
- [ ] 内存占用 <500MB

### 9.3 文档验收

- [ ] SKILL.md 完整
- [ ] README.md 包含示例
- [ ] API 文档完整
- [ ] 测试覆盖率 >80%

---

**技术设计完成时间**: 2026-03-17 10:32  
**设计者**: 小米辣 (PM + Dev 双代理) 🌶️  
**状态**: ✅ 技术设计完成，待开发

---

*下一步：开始 Phase 1 开发（3 天）*
