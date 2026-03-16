#!/usr/bin/env python3
"""
文档生成器 - 从解析结果生成文档

支持格式：
- Markdown（默认）
- HTML（可选）
- PDF（可选）
"""

import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import asdict
from datetime import datetime

# Jinja2 模板引擎
try:
    from jinja2 import Environment, FileSystemLoader, Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    logging.warning("Jinja2 not available, using basic templates")

# 日志配置
logger = logging.getLogger(__name__)


class DocumentGenerator:
    """文档生成器"""
    
    def __init__(self, template_dir: Optional[str] = None):
        self.template_dir = template_dir or str(Path(__file__).parent.parent / "templates")
        self.logger = logging.getLogger(__name__)
        
        # 初始化 Jinja2 环境
        if JINJA2_AVAILABLE:
            self.env = Environment(
                loader=FileSystemLoader(self.template_dir),
                autoescape=True,
                trim_blocks=True,
                lstrip_blocks=True
            )
        else:
            self.env = None
    
    def generate_api_doc(self, parse_results: List, output_format: str = "markdown") -> str:
        """生成 API 文档"""
        self.logger.info(f"Generating API documentation for {len(parse_results)} files")
        
        # 收集所有信息
        all_functions = []
        all_classes = []
        module_info = {
            'name': '',
            'description': '',
            'functions': [],
            'classes': [],
            'imports': [],
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
        for result in parse_results:
            # 模块文档字符串
            if result.module_docstring and not module_info['description']:
                module_info['description'] = result.module_docstring
            
            # 函数
            for func in result.functions:
                func_data = self._function_to_dict(func)
                module_info['functions'].append(func_data)
            
            # 类
            for cls in result.classes:
                cls_data = self._class_to_dict(cls)
                module_info['classes'].append(cls_data)
        
        # 使用模板生成
        if self.env:
            try:
                template = self.env.get_template('api/markdown.jinja2')
                return template.render(**module_info)
            except Exception as e:
                self.logger.error(f"Template rendering failed: {e}")
                return self._generate_basic_api_doc(module_info)
        else:
            return self._generate_basic_api_doc(module_info)
    
    def generate_readme(self, project_info: Dict[str, Any]) -> str:
        """生成 README 文档"""
        self.logger.info(f"Generating README for {project_info.get('name', 'unknown')}")
        
        # 补充生成日期
        project_info['generation_date'] = datetime.now().strftime('%Y-%m-%d')
        
        if self.env:
            try:
                template = self.env.get_template('readme/python.jinja2')
                return template.render(**project_info)
            except Exception as e:
                self.logger.error(f"Template rendering failed: {e}")
                return self._generate_basic_readme(project_info)
        else:
            return self._generate_basic_readme(project_info)
    
    def generate_changelog(self, changes: List[Dict[str, Any]]) -> str:
        """生成 Changelog 文档"""
        self.logger.info(f"Generating Changelog with {len(changes)} changes")
        
        changelog_info = {
            'changes': changes,
            'generation_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        if self.env:
            try:
                template = self.env.get_template('changelog/keep_a_changelog.jinja2')
                return template.render(**changelog_info)
            except Exception as e:
                self.logger.error(f"Template rendering failed: {e}")
                return self._generate_basic_changelog(changelog_info)
        else:
            return self._generate_basic_changelog(changelog_info)
    
    def _function_to_dict(self, func) -> Dict[str, Any]:
        """将函数信息转换为字典"""
        data = {
            'name': func.name,
            'parameters': [
                {
                    'name': p.name,
                    'type': p.type,
                    'default': p.default,
                    'description': p.description
                }
                for p in func.parameters
            ],
            'return_type': func.return_type,
            'docstring': func.docstring,
            'source_code': func.source_code,
            'start_line': func.start_line,
            'end_line': func.end_line,
            'file_path': func.file_path,
            'is_async': func.is_async,
            'is_method': func.is_method,
            'class_name': func.class_name
        }
        
        # 如果有解析后的文档，添加详细信息
        if hasattr(func, 'parsed_doc') and func.parsed_doc:
            data['description'] = func.parsed_doc.description
            data['returns'] = func.parsed_doc.returns
            data['raises'] = func.parsed_doc.raises
            data['examples'] = func.parsed_doc.examples
        
        return data
    
    def _class_to_dict(self, cls) -> Dict[str, Any]:
        """将类信息转换为字典"""
        data = {
            'name': cls.name,
            'docstring': cls.docstring,
            'methods': [self._function_to_dict(m) for m in cls.methods],
            'attributes': cls.attributes,
            'base_classes': cls.base_classes,
            'start_line': cls.start_line,
            'end_line': cls.end_line,
            'file_path': cls.file_path
        }
        
        # 如果有解析后的文档，添加详细信息
        if hasattr(cls, 'parsed_doc') and cls.parsed_doc:
            data['description'] = cls.parsed_doc.description
            data['class_attributes'] = cls.parsed_doc.attributes
        
        return data
    
    def _generate_basic_api_doc(self, module_info: Dict[str, Any]) -> str:
        """生成基础 API 文档（无模板时使用）"""
        lines = []
        
        # 标题
        lines.append(f"# {module_info.get('name', 'API Documentation')}")
        lines.append("")
        
        # 描述
        if module_info.get('description'):
            lines.append(module_info['description'])
            lines.append("")
        
        # 函数列表
        if module_info['functions']:
            lines.append("## Functions")
            lines.append("")
            
            for func in module_info['functions']:
                lines.append(f"### `{func['name']}()`")
                lines.append("")
                
                if func.get('description'):
                    lines.append(func['description'])
                    lines.append("")
                
                # 参数
                if func.get('parameters'):
                    lines.append("**Parameters:**")
                    lines.append("")
                    for param in func['parameters']:
                        type_str = f" ({param['type']})" if param.get('type') else ""
                        lines.append(f"- `{param['name']}`{type_str}: {param.get('description', '')}")
                    lines.append("")
                
                # 返回值
                if func.get('return_type'):
                    lines.append(f"**Returns:** `{func['return_type']}`")
                    lines.append("")
                
                lines.append("---")
                lines.append("")
        
        # 类列表
        if module_info['classes']:
            lines.append("## Classes")
            lines.append("")
            
            for cls in module_info['classes']:
                lines.append(f"### `{cls['name']}`")
                lines.append("")
                
                if cls.get('description'):
                    lines.append(cls['description'])
                    lines.append("")
                
                # 方法
                if cls.get('methods'):
                    lines.append("**Methods:**")
                    lines.append("")
                    for method in cls['methods']:
                        lines.append(f"- `{method['name']}()`")
                    lines.append("")
                
                lines.append("---")
                lines.append("")
        
        # 页脚
        lines.append(f"*Generated on {module_info['generation_date']}*")
        
        return '\n'.join(lines)
    
    def _generate_basic_readme(self, project_info: Dict[str, Any]) -> str:
        """生成基础 README（无模板时使用）"""
        lines = []
        
        # 标题
        name = project_info.get('name', 'Project')
        lines.append(f"# {name}")
        lines.append("")
        
        # 描述
        if project_info.get('description'):
            lines.append(project_info['description'])
            lines.append("")
        
        # 安装
        lines.append("## Installation")
        lines.append("")
        lines.append("```bash")
        lines.append("pip install -r requirements.txt")
        lines.append("```")
        lines.append("")
        
        # 使用
        lines.append("## Usage")
        lines.append("")
        lines.append("```python")
        lines.append(f"import {name.lower().replace('-', '_')}")
        lines.append("")
        lines.append("# TODO: Add usage examples")
        lines.append("```")
        lines.append("")
        
        # API 参考
        if project_info.get('functions'):
            lines.append("## API Reference")
            lines.append("")
            for func in project_info['functions']:
                lines.append(f"### `{func['name']}()`")
                if func.get('description'):
                    lines.append(func['description'])
                lines.append("")
        
        # 许可证
        license_text = project_info.get('license', 'MIT')
        lines.append("## License")
        lines.append("")
        lines.append(license_text)
        lines.append("")
        
        # 页脚
        lines.append(f"*Generated on {project_info['generation_date']}*")
        
        return '\n'.join(lines)
    
    def _generate_basic_changelog(self, changelog_info: Dict[str, Any]) -> str:
        """生成基础 Changelog（无模板时使用）"""
        lines = []
        
        lines.append("# Changelog")
        lines.append("")
        lines.append("All notable changes to this project will be documented in this file.")
        lines.append("")
        
        for change in changelog_info['changes']:
            version = change.get('version', 'Unreleased')
            date = change.get('date', '')
            changes = change.get('changes', [])
            
            lines.append(f"## [{version}] - {date}")
            lines.append("")
            
            for change_item in changes:
                change_type = change_item.get('type', 'changed')
                description = change_item.get('description', '')
                lines.append(f"- **{change_type.title()}**: {description}")
            
            lines.append("")
        
        lines.append(f"*Generated on {changelog_info['generation_date']}*")
        
        return '\n'.join(lines)
    
    def save_documentation(self, content: str, output_path: str) -> bool:
        """保存文档到文件"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Documentation saved to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save documentation: {e}")
            return False
    
    def generate_from_directory(self, dir_path: str, output_dir: str = "docs/") -> Dict[str, str]:
        """从目录生成文档"""
        from .parser import CodeParser, detect_language, Language
        
        results = {}
        path = Path(dir_path)
        
        if not path.exists():
            self.logger.error(f"Directory not found: {dir_path}")
            return results
        
        # 查找所有 Python 文件
        python_files = list(path.rglob("*.py"))
        python_files = [f for f in python_files if '__pycache__' not in str(f)]
        
        if not python_files:
            self.logger.warning(f"No Python files found in {dir_path}")
            return results
        
        # 解析所有文件
        parser = CodeParser(Language.PYTHON)
        parse_results = []
        
        for file in python_files:
            result = parser.parse_file(str(file))
            parse_results.append(result)
        
        # 生成 API 文档
        api_doc = self.generate_api_doc(parse_results)
        api_path = Path(output_dir) / "api.md"
        
        if self.save_documentation(api_doc, str(api_path)):
            results['api'] = str(api_path)
        
        # 生成 README
        readme_info = {
            'name': path.name,
            'description': f"Auto-generated documentation for {path.name}",
            'functions': [func for result in parse_results for func in result.functions],
            'license': 'MIT'
        }
        
        readme_doc = self.generate_readme(readme_info)
        readme_path = Path(output_dir) / "README.md"
        
        if self.save_documentation(readme_doc, str(readme_path)):
            results['readme'] = str(readme_path)
        
        self.logger.info(f"Generated documentation for {len(python_files)} files")
        return results
