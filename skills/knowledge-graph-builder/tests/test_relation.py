"""
关系识别器测试
"""

import unittest
from kg_builder.relation import RelationExtractor, Relation
from kg_builder.extractor import Entity


class TestRelationExtractor(unittest.TestCase):
    """关系识别器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.extractor = RelationExtractor()
    
    def test_relation_creation(self):
        """测试关系创建"""
        relation = Relation(
            id="rel_1",
            source_id="entity_1",
            target_id="entity_2",
            type="is-a",
            confidence=0.8
        )
        self.assertEqual(relation.type, "is-a")
        self.assertEqual(relation.confidence, 0.8)
    
    def test_relation_to_dict(self):
        """测试关系转字典"""
        relation = Relation(
            id="rel_1",
            source_id="entity_1",
            target_id="entity_2",
            type="related-to"
        )
        relation_dict = relation.to_dict()
        self.assertIn("id", relation_dict)
        self.assertIn("source_id", relation_dict)
        self.assertEqual(relation_dict["type"], "related-to")
    
    def test_extract_relations(self):
        """测试关系提取"""
        entities = [
            Entity(id="1", name="Python", type="Technology"),
            Entity(id="2", name="编程语言", type="Concept"),
        ]
        relations = self.extractor.extract_relations(entities)
        # TODO: 完善测试
        self.assertIsInstance(relations, list)
    
    def test_confidence_scoring(self):
        """测试置信度评分"""
        relation = Relation(
            id="rel_1",
            source_id="1",
            target_id="2",
            type="is-a",
            confidence=0.7
        )
        scored_confidence = self.extractor._calculate_confidence(relation)
        # TODO: 完善评分逻辑测试
        self.assertIsInstance(scored_confidence, float)
    
    def test_deduplication(self):
        """测试关系去重"""
        relations = [
            Relation(id="r1", source_id="1", target_id="2", type="is-a", confidence=0.9),
            Relation(id="r2", source_id="1", target_id="2", type="is-a", confidence=0.7),
        ]
        unique_relations = self.extractor._score_and_deduplicate(relations)
        # 应该保留高置信度的关系
        self.assertEqual(len(unique_relations), 1)
        self.assertEqual(unique_relations[0].confidence, 0.9)
    
    def test_clear_relations(self):
        """测试清空关系"""
        self.extractor.relations = [Relation(id="1", source_id="1", target_id="2", type="is-a")]
        self.extractor.clear()
        self.assertEqual(len(self.extractor.relations), 0)


if __name__ == "__main__":
    unittest.main()
