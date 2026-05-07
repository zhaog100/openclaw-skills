"""
关系识别器模块

负责从实体中识别关系
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from itertools import combinations


@dataclass
class Relation:
    """关系数据类"""
    
    id: str
    source_id: str
    target_id: str
    type: str
    confidence: float = 0.5
    source: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type,
            "confidence": self.confidence,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
        }


class RelationExtractor:
    """关系提取器"""
    
    # 预定义关系模板
    RELATION_TEMPLATES = {
        "is-a": ["是一种", "属于", "是"],
        "part-of": ["是...的一部分", "包含", "组成"],
        "related-to": ["相关", "关联", "联系"],
        "causes": ["导致", "引起", "造成"],
        "before": ["在...之前", "先于"],
        "after": ["在...之后", "后于"],
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.relations: List[Relation] = []
    
    def extract_relations(self, entities: List[Any]) -> List[Relation]:
        """从实体中提取关系"""
        relations = []
        
        # 1. 基于规则的关系抽取
        rule_relations = self._rule_based_extract(entities)
        relations.extend(rule_relations)
        
        # 2. 基于 AI 的关系抽取
        ai_relations = self._ai_based_extract(entities)
        relations.extend(ai_relations)
        
        # 3. 关系去重和置信度评分
        relations = self._score_and_deduplicate(relations)
        
        self.relations.extend(relations)
        return relations
    
    def _rule_based_extract(self, entities: List[Any]) -> List[Relation]:
        """基于规则的关系抽取"""
        relations = []
        for entity1, entity2 in combinations(entities, 2):
            # 检查预定义关系模板
            for rel_type, patterns in self.RELATION_TEMPLATES.items():
                if self._match_pattern(entity1, entity2, patterns):
                    relation = self._create_relation(entity1, entity2, rel_type)
                    relations.append(relation)
        return relations
    
    def _ai_based_extract(self, entities: List[Any]) -> List[Relation]:
        """基于 AI 的关系抽取"""
        # TODO: 使用 Ollama 识别潜在关系
        return []
    
    def _match_pattern(self, entity1: Any, entity2: Any, patterns: List[str]) -> bool:
        """匹配关系模式"""
        # TODO: 实现模式匹配逻辑
        return False
    
    def _create_relation(self, entity1: Any, entity2: Any, rel_type: str) -> Relation:
        """创建关系"""
        return Relation(
            id=f"rel_{entity1.id}_{entity2.id}_{rel_type}",
            source_id=entity1.id,
            target_id=entity2.id,
            type=rel_type,
            confidence=0.7,
        )
    
    def _score_and_deduplicate(self, relations: List[Relation]) -> List[Relation]:
        """置信度评分和去重"""
        # 计算关系置信度
        for rel in relations:
            rel.confidence = self._calculate_confidence(rel)
        
        # 去重（保留高置信度）
        seen = set()
        unique_relations = []
        for rel in sorted(relations, key=lambda r: r.confidence, reverse=True):
            key = (rel.source_id, rel.target_id, rel.type)
            if key not in seen:
                seen.add(key)
                unique_relations.append(rel)
        
        return unique_relations
    
    def _calculate_confidence(self, relation: Relation) -> float:
        """计算关系置信度"""
        # TODO: 实现置信度计算逻辑
        return relation.confidence
    
    def get_relations(self) -> List[Relation]:
        """获取所有关系"""
        return self.relations
    
    def clear(self):
        """清空关系列表"""
        self.relations = []
