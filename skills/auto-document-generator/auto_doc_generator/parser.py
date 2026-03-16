#!/usr/bin/env python3
"""
代码解析器 - 使用 tree-sitter 解析多种编程语言

支持语言：
- Python (tree-sitter-python)
- JavaScript (tree-sitter-javascript)
- Bash (tree-sitter-bash)
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

# 日志配置
logger = logging.getLogger(__name__)


class Language(Enum):
    """支持的编程语言"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    BASH = "bash"


@dataclass
class Parameter:
    """函数参数信息"""
    name: str
    type: Optional[str] = None
    default: Optional[str] = None
    description: Optional[str] = None


@dataclass
class FunctionInfo:
    """函数信息"""
    name: str
    parameters: List[Parameter] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    start_line: int = 0
    end_line: int = 0
    source_code: str = ""
    file_path: str = ""
    decorators: List[str] = field(default_factory=list)
    is_async: bool = False
    is_method: bool = False
    class_name: Optional[str] = None


@dataclass
class ClassInfo:
    """类信息"""
    name: str
    docstring: Optional[str] = None
    methods: List[FunctionInfo] = field(default_factory=list)
    attributes: List[Dict[str, Any]] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0
    source_code: str = ""
    file_path: str = ""
    decorators: List[str] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)


@dataclass
class ImportInfo:
    """导入信息"""
    module: str
    names: List[str] = field(default_factory=list)
    alias: Optional[str] = None
    is_from: bool = False


@dataclass
class ParseTree:
    """解析结果"""
    file_path: str
    language: Language
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    module_docstring: Optional[str] = None
    source_code: str = ""
    error: Optional[str] = None


class CodeParser:
    """代码解析器基类"""
    
    def __init__(self, language: Language):
        self.language = language
        self.parser = self._init_parser()
        self.logger = logging.getLogger(f"{__name__}.{language.value}")
    
    def _init_parser(self) -> Optional[Any]:
        """初始化 tree-sitter 解析器"""
        try:
            import tree_sitter_python as tspython
            import tree_sitter_javascript as tsjavascript
            import tree_sitter_bash as tsbash
            from tree_sitter import Language, Parser
            
            # 语言映射
            language_map = {
                Language.PYTHON: tspython,
                Language.JAVASCRIPT: tsjavascript,
                Language.BASH: tsbash
            }
            
            if self.language in language_map:
                lang_module = language_map[self.language]
                parser = Parser()
                parser.set_language(Language(lang_module.language()))
                return parser
            
            self.logger.error(f"Unsupported language: {self.language}")
            return None
            
        except ImportError as e:
            self.logger.error(f"Failed to import tree-sitter: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to initialize parser: {e}")
            return None
    
    def parse_file(self, file_path: str) -> ParseTree:
        """解析单个文件"""
        result = ParseTree(
            file_path=file_path,
            language=self.language
        )
        
        if not self.parser:
            result.error = "Parser not initialized"
            return result
        
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                result.source_code = code
            
            # 解析代码
            tree = self.parser.parse(bytes(code, "utf8"))
            root_node = tree.root_node
            
            # 根据语言类型提取信息
            if self.language == Language.PYTHON:
                self._parse_python(root_node, result)
            elif self.language == Language.JAVASCRIPT:
                self._parse_javascript(root_node, result)
            elif self.language == Language.BASH:
                self._parse_bash(root_node, result)
            
            self.logger.info(f"Parsed {file_path}: {len(result.functions)} functions, {len(result.classes)} classes")
            
        except FileNotFoundError:
            result.error = f"File not found: {file_path}"
            self.logger.error(result.error)
        except Exception as e:
            result.error = f"Parse error: {str(e)}"
            self.logger.error(result.error)
        
        return result
    
    def parse_directory(self, dir_path: str, recursive: bool = True) -> List[ParseTree]:
        """解析整个目录"""
        results = []
        path = Path(dir_path)
        
        if not path.exists():
            self.logger.error(f"Directory not found: {dir_path}")
            return results
        
        # 文件扩展名映射
        ext_map = {
            Language.PYTHON: '.py',
            Language.JAVASCRIPT: '.js',
            Language.BASH: '.sh'
        }
        
        extension = ext_map.get(self.language)
        if not extension:
            self.logger.error(f"Unknown extension for language: {self.language}")
            return results
        
        # 查找文件
        if recursive:
            files = list(path.rglob(f"*{extension}"))
        else:
            files = list(path.glob(f"*{extension}"))
        
        # 排除常见目录
        exclude_dirs = {'__pycache__', 'node_modules', '.git', 'venv', 'env'}
        files = [f for f in files if not any(excluded in f.parts for excluded in exclude_dirs)]
        
        self.logger.info(f"Found {len(files)} {self.language.value} files in {dir_path}")
        
        # 解析文件
        for file in files:
            result = self.parse_file(str(file))
            results.append(result)
        
        return results
    
    def _parse_python(self, root_node, result: ParseTree):
        """解析 Python 代码"""
        code = result.source_code
        
        # 查找函数定义
        for node in root_node.children:
            if node.type == 'function_definition':
                func_info = self._extract_python_function(node, code, result.file_path)
                result.functions.append(func_info)
            elif node.type == 'class_definition':
                class_info = self._extract_python_class(node, code, result.file_path)
                result.classes.append(class_info)
            elif node.type == 'import_statement':
                import_info = self._extract_python_import(node, code)
                result.imports.append(import_info)
            elif node.type == 'import_from_statement':
                import_info = self._extract_python_import(node, code, is_from=True)
                result.imports.append(import_info)
            elif node.type == 'expression_statement':
                # 检查模块级 docstring
                if node.children and node.children[0].type == 'string':
                    if not result.module_docstring:
                        result.module_docstring = self._extract_string(node.children[0], code)
    
    def _extract_python_function(self, node, code: str, file_path: str) -> FunctionInfo:
        """提取 Python 函数信息"""
        func_info = FunctionInfo(file_path=file_path)
        
        # 函数名
        name_node = node.child_by_field_name('name')
        if name_node:
            func_info.name = code[name_node.start_byte:name_node.end_byte].decode()
        
        # 参数
        params_node = node.child_by_field_name('parameters')
        if params_node:
            func_info.parameters = self._extract_python_parameters(params_node, code)
        
        # 返回类型
        return_type_node = node.child_by_field_name('return_type')
        if return_type_node:
            func_info.return_type = code[return_type_node.start_byte:return_type_node.end_byte].decode()
        
        # 函数体（查找 docstring）
        body_node = node.child_by_field_name('body')
        if body_node and body_node.children:
            # 第一个表达式可能是 docstring
            first_child = body_node.children[0]
            if first_child.type == 'expression_statement' and first_child.children:
                if first_child.children[0].type == 'string':
                    func_info.docstring = self._extract_string(first_child.children[0], code)
        
        # 位置信息
        func_info.start_line = node.start_point[0] + 1
        func_info.end_line = node.end_point[0] + 1
        func_info.source_code = code[node.start_byte:node.end_byte].decode()
        
        return func_info
    
    def _extract_python_parameters(self, params_node, code: str) -> List[Parameter]:
        """提取 Python 函数参数"""
        parameters = []
        
        for child in params_node.children:
            if child.type in ('identifier', 'typed_parameter', 'default_parameter', 'list_splat_pattern', 'dictionary_splat_pattern'):
                param = Parameter()
                
                if child.type == 'identifier':
                    param.name = code[child.start_byte:child.end_byte].decode()
                elif child.type == 'typed_parameter':
                    name_node = child.child_by_field_name('name')
                    type_node = child.child_by_field_name('type')
                    if name_node:
                        param.name = code[name_node.start_byte:name_node.end_byte].decode()
                    if type_node:
                        param.type = code[type_node.start_byte:type_node.end_byte].decode()
                elif child.type == 'default_parameter':
                    name_node = child.child_by_field_name('name')
                    value_node = child.child_by_field_name('value')
                    if name_node:
                        param.name = code[name_node.start_byte:name_node.end_byte].decode()
                    if value_node:
                        param.default = code[value_node.start_byte:value_node.end_byte].decode()
                elif child.type == 'list_splat_pattern':
                    # *args
                    param.name = f"*{code[child.start_byte:child.end_byte].decode()}"
                elif child.type == 'dictionary_splat_pattern':
                    # **kwargs
                    param.name = f"**{code[child.start_byte:child.end_byte].decode()}"
                
                if param.name:
                    parameters.append(param)
        
        return parameters
    
    def _extract_python_class(self, node, code: str, file_path: str) -> ClassInfo:
        """提取 Python 类信息"""
        class_info = ClassInfo(file_path=file_path)
        
        # 类名
        name_node = node.child_by_field_name('name')
        if name_node:
            class_info.name = code[name_node.start_byte:name_node.end_byte].decode()
        
        # 基类
        bases_node = node.child_by_field_name('superclasses')
        if bases_node:
            for child in bases_node.children:
                if child.type in ('identifier', 'attribute'):
                    class_info.base_classes.append(code[child.start_byte:child.end_byte].decode())
        
        # 类体
        body_node = node.child_by_field_name('body')
        if body_node:
            # 查找 docstring
            if body_node.children:
                first_child = body_node.children[0]
                if first_child.type == 'expression_statement' and first_child.children:
                    if first_child.children[0].type == 'string':
                        class_info.docstring = self._extract_string(first_child.children[0], code)
            
            # 查找方法
            for child in body_node.children:
                if child.type == 'function_definition':
                    method_info = self._extract_python_function(child, code, file_path)
                    method_info.is_method = True
                    method_info.class_name = class_info.name
                    class_info.methods.append(method_info)
        
        # 位置信息
        class_info.start_line = node.start_point[0] + 1
        class_info.end_line = node.end_point[0] + 1
        class_info.source_code = code[node.start_byte:node.end_byte].decode()
        
        return class_info
    
    def _extract_python_import(self, node, code: str, is_from: bool = False) -> ImportInfo:
        """提取 Python 导入信息"""
        import_info = ImportInfo(is_from=is_from)
        
        if is_from:
            # from X import Y
            module_node = node.child_by_field_name('module_name')
            if module_node:
                import_info.module = code[module_node.start_byte:module_node.end_byte].decode()
            
            # 导入的名称
            for child in node.children:
                if child.type == 'dotted_name' or child.type == 'identifier':
                    if child.type == 'identifier':
                        import_info.names.append(code[child.start_byte:child.end_byte].decode())
        else:
            # import X
            for child in node.children:
                if child.type == 'dotted_name':
                    import_info.module = code[child.start_byte:child.end_byte].decode()
                elif child.type == 'aliased_import':
                    name_node = child.child_by_field_name('name')
                    alias_node = child.child_by_field_name('alias')
                    if name_node:
                        import_info.module = code[name_node.start_byte:name_node.end_byte].decode()
                    if alias_node:
                        import_info.alias = code[alias_node.start_byte:alias_node.end_byte].decode()
        
        return import_info
    
    def _extract_string(self, node, code: str) -> str:
        """提取字符串内容（去掉引号）"""
        string_content = code[node.start_byte:node.end_byte].decode()
        
        # 去掉引号
        if string_content.startswith('"""') or string_content.startswith("'''"):
            return string_content[3:-3].strip()
        elif string_content.startswith('"') or string_content.startswith("'"):
            return string_content[1:-1].strip()
        
        return string_content
    
    def _parse_javascript(self, root_node, result: ParseTree):
        """解析 JavaScript 代码"""
        # TODO: 实现 JavaScript 解析
        pass
    
    def _parse_bash(self, root_node, result: ParseTree):
        """解析 Bash 代码"""
        # TODO: 实现 Bash 解析
        pass


def detect_language(file_path: str) -> Optional[Language]:
    """检测文件语言"""
    ext = Path(file_path).suffix.lower()
    
    language_map = {
        '.py': Language.PYTHON,
        '.js': Language.JAVASCRIPT,
        '.sh': Language.BASH,
    }
    
    return language_map.get(ext)
