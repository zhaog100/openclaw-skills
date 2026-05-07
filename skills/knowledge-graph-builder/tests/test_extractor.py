"""
知识提取器测试
"""

import unittest
from kg_builder.extractor import KnowledgeExtractor, Entity


class TestKnowledgeExtractor(unittest.TestCase):
    """知识提取器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.extractor = KnowledgeExtractor()
    
    def test_entity_creation(self):
        """测试实体创建"""
        entity = Entity(
            id="test_1",
            name="Python",
            type="Technology",
            description="编程语言"
        )
        self.assertEqual(entity.name, "Python")
        self.assertEqual(entity.type, "Technology")
    
    def test_entity_to_dict(self):
        """测试实体转字典"""
        entity = Entity(
            id="test_1",
            name="Python",
            type="Technology"
        )
        entity_dict = entity.to_dict()
        self.assertIn("id", entity_dict)
        self.assertIn("name", entity_dict)
        self.assertEqual(entity_dict["name"], "Python")
    
    def test_extract_from_markdown(self):
        """测试从 Markdown 提取"""
        # TODO: 实现完整测试
        pass
    
    def test_extract_from_directory(self):
        """测试从目录提取"""
        # TODO: 实现完整测试
        pass
    
    def test_clear_entities(self):
        """测试清空实体"""
        self.extractor.entities = [Entity(id="1", name="Test", type="Test")]
        self.extractor.clear()
        self.assertEqual(len(self.extractor.entities), 0)


if __name__ == "__main__":
    unittest.main()
