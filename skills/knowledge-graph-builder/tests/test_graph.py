"""
图谱操作测试
"""

import unittest
from kg_builder.graph import KnowledgeGraph
from storage.sqlite_store import SQLiteStorage
import os


class TestKnowledgeGraph(unittest.TestCase):
    """图谱操作测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.db_path = "test_knowledge_graph.db"
        self.storage = SQLiteStorage(self.db_path)
        self.graph = KnowledgeGraph(self.storage)
    
    def tearDown(self):
        """测试后清理"""
        self.storage.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_add_entity(self):
        """测试添加实体"""
        from kg_builder.extractor import Entity
        entity = Entity(id="test_1", name="Python", type="Technology")
        entity_id = self.graph.add_entity(entity)
        self.assertEqual(entity_id, "test_1")
    
    def test_add_relation(self):
        """测试添加关系"""
        from kg_builder.relation import Relation
        relation = Relation(
            id="rel_1",
            source_id="1",
            target_id="2",
            type="is-a"
        )
        relation_id = self.graph.add_relation(relation)
        self.assertEqual(relation_id, "rel_1")
    
    def test_get_stats(self):
        """测试获取统计信息"""
        stats = self.graph.get_stats()
        self.assertIn("nodes", stats)
        self.assertIn("edges", stats)
        self.assertEqual(stats["nodes"], 0)
        self.assertEqual(stats["edges"], 0)
    
    def test_search(self):
        """测试搜索"""
        results = self.graph.search("Python")
        self.assertIsInstance(results, list)
    
    def test_export_json(self):
        """测试导出 JSON"""
        json_output = self.graph.export(format="json")
        self.assertIsInstance(json_output, str)


if __name__ == "__main__":
    unittest.main()
