"""
知识提取器模块

负责从文档中提取实体和属性
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Entity:
    """实体数据类"""
    
    id: str
    name: str
    type: str
    description: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class KnowledgeExtractor:
    """知识提取器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.entities: List[Entity] = []
    
    def extract_from_document(self, file_path: str) -> List[Entity]:
        """从文档中提取实体"""
        content = self._parse_document(file_path)
        entities = self._extract_entities(content)
        entities = self._ai_enhance(entities)
        self.entities.extend(entities)
        return entities
    
    def extract_from_directory(self, dir_path: str, pattern: str = "*.md") -> List[Entity]:
        """从目录中提取实体"""
        all_entities = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                if pattern == "*" or file.endswith(pattern.lstrip("*")):
                    file_path = os.path.join(root, file)
                    entities = self.extract_from_document(file_path)
                    all_entities.extend(entities)
        return all_entities
    
    def _parse_document(self, file_path: str) -> str:
        """解析文档（支持 Markdown/PDF/HTML/Text）"""
        if file_path.endswith('.md'):
            return self._parse_markdown(file_path)
        elif file_path.endswith('.pdf'):
            return self._parse_pdf(file_path)
        elif file_path.endswith('.html'):
            return self._parse_html(file_path)
        else:
            return self._parse_text(file_path)
    
    def _parse_markdown(self, file_path: str) -> str:
        """解析 Markdown 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _parse_pdf(self, file_path: str) -> str:
        """解析 PDF 文件"""
        # TODO: 使用 PyPDF2 解析
        return ""
    
    def _parse_html(self, file_path: str) -> str:
        """解析 HTML 文件"""
        # TODO: 使用 BeautifulSoup 解析
        return ""
    
    def _parse_text(self, file_path: str) -> str:
        """解析文本文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_entities(self, content: str) -> List[Entity]:
        """提取实体（规则 + NLP）"""
        # TODO: 实现基于规则的提取
        # TODO: 实现基于 NLP 的提取
        return []
    
    def _ai_enhance(self, entities: List[Entity]) -> List[Entity]:
        """AI 增强（补充属性、分类）"""
        # TODO: 使用 Ollama 增强实体信息
        return entities
    
    def get_entities(self) -> List[Entity]:
        """获取所有实体"""
        return self.entities
    
    def clear(self):
        """清空实体列表"""
        self.entities = []
