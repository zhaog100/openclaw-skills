#!/usr/bin/env python3
"""
模板管理器 - 管理文档模板

提供模板加载、继承、缓存功能
"""

import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound

# 日志配置
logger = logging.getLogger(__name__)


class TemplateManager:
    """模板管理器"""
    
    def __init__(self, template_dir: Optional[str] = None):
        self.template_dir = Path(template_dir) if template_dir else Path(__file__).parent.parent / "templates"
        
        self.logger = logging.getLogger(__name__)
        
        # 初始化 Jinja2 环境
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
            extensions=['jinja2.ext.do', 'jinja2.ext.loopcontrols']
        )
        
        # 模板缓存
        self.cache: Dict[str, Template] = {}
    
    def get_template(self, template_name: str, use_cache: bool = True) -> Template:
        """获取模板"""
        # 检查缓存
        if use_cache and template_name in self.cache:
            return self.cache[template_name]
        
        try:
            template = self.env.get_template(template_name)
            
            # 缓存模板
            if use_cache:
                self.cache[template_name] = template
            
            return template
            
        except TemplateNotFound:
            self.logger.error(f"Template not found: {template_name}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to load template {template_name}: {e}")
            raise
    
    def render(self, template_name: str, context: Dict[str, Any], use_cache: bool = True) -> str:
        """渲染模板"""
        try:
            template = self.get_template(template_name, use_cache)
            return template.render(**context)
        except Exception as e:
            self.logger.error(f"Failed to render template {template_name}: {e}")
            raise
    
    def list_templates(self) -> List[str]:
        """列出所有可用模板"""
        try:
            return self.env.list_templates()
        except Exception as e:
            self.logger.error(f"Failed to list templates: {e}")
            return []
    
    def clear_cache(self):
        """清除模板缓存"""
        self.cache.clear()
        self.logger.info("Template cache cleared")
