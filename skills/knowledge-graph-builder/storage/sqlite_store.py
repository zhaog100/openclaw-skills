"""
SQLite 存储后端

轻量级图谱存储方案
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from .graph import StorageBackend


class SQLiteStorage(StorageBackend):
    """SQLite 存储后端"""
    
    def __init__(self, db_path: str = "knowledge_graph.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_schema()
    
    def _init_schema(self):
        """初始化数据库模式"""
        cursor = self.conn.cursor()
        
        # 创建实体表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                properties JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建关系表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relations (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                type TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                source TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES entities(id),
                FOREIGN KEY (target_id) REFERENCES entities(id)
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_name ON entities(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relation_type ON relations(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relation_source ON relations(source_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relation_target ON relations(target_id)")
        
        self.conn.commit()
    
    def create_node(self, entity: Any) -> str:
        """创建节点"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO entities (id, name, type, description, properties, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            entity.id,
            entity.name,
            entity.type,
            entity.description,
            json.dumps(entity.properties),
            entity.created_at,
            entity.updated_at,
        ))
        self.conn.commit()
        return entity.id
    
    def create_edge(self, relation: Any) -> str:
        """创建边"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO relations (id, source_id, target_id, type, confidence, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            relation.id,
            relation.source_id,
            relation.target_id,
            relation.type,
            relation.confidence,
            relation.source,
            relation.created_at,
        ))
        self.conn.commit()
        return relation.id
    
    def search(self, query: str) -> List[Any]:
        """搜索实体"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, type, description, properties
            FROM entities
            WHERE name LIKE ? OR description LIKE ?
        """, (f"%{query}%", f"%{query}%"))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "description": row[3],
                "properties": json.loads(row[4]),
            })
        return results
    
    def find_shortest_path(self, start: str, end: str) -> List[Any]:
        """查找最短路径（BFS）"""
        # TODO: 实现 BFS 路径查找
        return []
    
    def get_neighbors(self, entity_id: str, depth: int = 1) -> List[Any]:
        """获取邻居节点"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT e.id, e.name, e.type, e.description, r.type as relation_type
            FROM entities e
            JOIN relations r ON e.id = r.target_id
            WHERE r.source_id = ?
            LIMIT ?
        """, (entity_id, depth * 10))
        
        neighbors = []
        for row in cursor.fetchall():
            neighbors.append({
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "description": row[3],
                "relation_type": row[4],
            })
        return neighbors
    
    def count_nodes(self) -> int:
        """统计节点数"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM entities")
        return cursor.fetchone()[0]
    
    def count_edges(self) -> int:
        """统计边数"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM relations")
        return cursor.fetchone()[0]
    
    def close(self):
        """关闭连接"""
        self.conn.close()
