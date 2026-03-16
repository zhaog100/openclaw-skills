#!/usr/bin/env python3
"""
注释提取器 - 从代码中提取注释和文档字符串

支持风格：
- Google Style Docstrings
- Numpy Style Docstrings
- Sphinx Style Docstrings (reStructuredText)
- JSDoc (JavaScript)
- Bash Comments
"""

import re
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

# 日志配置
logger = logging.getLogger(__name__)


class DocstringStyle(Enum):
    """文档字符串风格"""
    GOOGLE = "google"
    NUMPY = "numpy"
    SPHINX = "sphinx"
    JSDOC = "jsdoc"
    BASH = "bash"


@dataclass
class ParameterDoc:
    """参数文档"""
    name: str
    type: Optional[str] = None
    description: str = ""
    default: Optional[str] = None
    is_optional: bool = False


@dataclass
class ReturnDoc:
    """返回值文档"""
    type: Optional[str] = None
    description: str = ""


@dataclass
class ExceptionDoc:
    """异常文档"""
    type: str
    description: str = ""


@dataclass
class ExampleDoc:
    """示例文档"""
    code: str
    language: str = "python"
    output: Optional[str] = None
    description: str = ""


@dataclass
class ParsedDocstring:
    """解析后的文档字符串"""
    description: str = ""
    parameters: List[ParameterDoc] = field(default_factory=list)
    returns: Optional[ReturnDoc] = None
    raises: List[ExceptionDoc] = field(default_factory=list)
    examples: List[ExampleDoc] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    see_also: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    attributes: List[ParameterDoc] = field(default_factory=list)
    raw_docstring: str = ""
    style: Optional[DocstringStyle] = None


class CommentExtractor:
    """注释提取器"""
    
    def __init__(self, style: Optional[DocstringStyle] = None):
        self.style = style
        self.logger = logging.getLogger(__name__)
    
    def extract_from_function(self, func_info) -> ParsedDocstring:
        """从函数信息中提取文档"""
        if not func_info.docstring:
            return ParsedDocstring()
        
        return self.parse_docstring(func_info.docstring)
    
    def extract_from_class(self, class_info) -> ParsedDocstring:
        """从类信息中提取文档"""
        if not class_info.docstring:
            return ParsedDocstring()
        
        return self.parse_docstring(class_info.docstring)
    
    def parse_docstring(self, docstring: str, style: Optional[DocstringStyle] = None) -> ParsedDocstring:
        """解析文档字符串"""
        if not docstring:
            return ParsedDocstring()
        
        # 自动检测风格
        if not style and not self.style:
            style = self._detect_style(docstring)
        elif not style:
            style = self.style
        
        result = ParsedDocstring(
            raw_docstring=docstring,
            style=style
        )
        
        # 根据风格选择解析器
        if style == DocstringStyle.GOOGLE:
            self._parse_google_style(docstring, result)
        elif style == DocstringStyle.NUMPY:
            self._parse_numpy_style(docstring, result)
        elif style == DocstringStyle.SPHINX:
            self._parse_sphinx_style(docstring, result)
        elif style == DocstringStyle.JSDOC:
            self._parse_jsdoc_style(docstring, result)
        elif style == DocstringStyle.BASH:
            self._parse_bash_style(docstring, result)
        else:
            # 默认按 Google 风格解析
            self._parse_google_style(docstring, result)
        
        self.logger.debug(f"Parsed docstring with style: {style}")
        return result
    
    def _detect_style(self, docstring: str) -> DocstringStyle:
        """检测文档字符串风格"""
        
        # Numpy 风格特征（忽略大小写）
        if re.search(r'^\s*(parameters|returns|attributes)\s*$', docstring, re.MULTILINE | re.IGNORECASE):
            return DocstringStyle.NUMPY
        
        # Sphinx 风格特征
        if re.search(r':param|:type|:return|:rtype|:raises', docstring):
            return DocstringStyle.SPHINX
        
        # JSDoc 风格特征
        if re.search(r'@param|@returns|@throws', docstring):
            return DocstringStyle.JSDOC
        
        # Bash 风格特征
        if re.search(r'^#\s*@param|^#\s*@return', docstring, re.MULTILINE):
            return DocstringStyle.BASH
        
        # 默认 Google 风格
        return DocstringStyle.GOOGLE
    
    def _parse_google_style(self, docstring: str, result: ParsedDocstring):
        """解析 Google 风格文档字符串"""
        lines = docstring.strip().split('\n')
        
        # 提取描述（第一个段落）
        description_lines = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith('Args:') or line.startswith('Arguments:') or \
               line.startswith('Returns:') or line.startswith('Raises:') or \
               line.startswith('Example:') or line.startswith('Examples:') or \
               line.startswith('Note:') or line.startswith('Notes:') or \
               line.startswith('Warning:') or line.startswith('Warnings:'):
                break
            description_lines.append(line)
            i += 1
        
        result.description = ' '.join(description_lines)
        
        # 解析各个部分
        current_section = None
        section_content = []
        
        while i < len(lines):
            raw_line = lines[i]  # 保留原始行（包含缩进）
            line = lines[i].strip()  # 去除缩进的行
            
            # 检测章节标题
            if line in ('Args:', 'Arguments:'):
                # 处理之前的章节
                if current_section and section_content:
                    self._process_section(current_section, section_content, result)
                current_section = 'args'
                section_content = []
            elif line == 'Returns:':
                # 处理之前的章节
                if current_section and section_content:
                    self._process_section(current_section, section_content, result)
                current_section = 'returns'
                section_content = []
            elif line == 'Raises:':
                # 处理之前的章节
                if current_section and section_content:
                    self._process_section(current_section, section_content, result)
                current_section = 'raises'
                section_content = []
            elif line in ('Example:', 'Examples:'):
                # 处理之前的章节
                if current_section and section_content:
                    self._process_section(current_section, section_content, result)
                current_section = 'examples'
                section_content = []
            elif line in ('Note:', 'Notes:'):
                # 处理之前的章节
                if current_section and section_content:
                    self._process_section(current_section, section_content, result)
                current_section = 'notes'
                section_content = []
            elif line in ('Warning:', 'Warnings:'):
                # 处理之前的章节
                if current_section and section_content:
                    self._process_section(current_section, section_content, result)
                current_section = 'warnings'
                section_content = []
            elif raw_line.startswith('    ') or raw_line.startswith('\t') or not line:
                # 缩进内容或空行（使用原始行检查缩进）
                if current_section:
                    section_content.append(line)  # 添加去除缩进的行
            else:
                # 新段落，处理当前章节
                if current_section and section_content:
                    self._process_section(current_section, section_content, result)
                current_section = None
                section_content = []
            
            i += 1
        
        # 处理最后一个章节
        if current_section and section_content:
            self._process_section(current_section, section_content, result)
    
    def _process_section(self, section: str, content: List[str], result: ParsedDocstring):
        """处理章节内容"""
        content_str = '\n'.join(content).strip()
        
        if section == 'args':
            result.parameters = self._parse_google_args(content_str)
        elif section == 'returns':
            result.returns = self._parse_google_returns(content_str)
        elif section == 'raises':
            result.raises = self._parse_google_raises(content_str)
        elif section == 'examples':
            result.examples = self._parse_google_examples(content_str)
        elif section == 'notes':
            result.notes = [content_str]
        elif section == 'warnings':
            result.warnings = [content_str]
    
    def _parse_google_args(self, content: str) -> List[ParameterDoc]:
        """解析 Google 风格参数"""
        parameters = []
        
        # 分行处理
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 匹配参数行：name (type): description 或 name: description
            # 支持格式：
            # a (int): First number
            # a: First number
            # a (int, optional): First number
            pattern = r'^(\w+)\s*(?:\(([^)]+)\))?\s*:\s*(.+)$'
            
            match = re.match(pattern, line)
            if match:
                param = ParameterDoc(
                    name=match.group(1),
                    type=match.group(2),
                    description=match.group(3).strip()
                )
                
                # 检查是否有默认值
                default_match = re.search(r'\(default:\s*(.+?)\)', param.description)
                if default_match:
                    param.default = default_match.group(1)
                    param.description = re.sub(r'\s*\(default:\s*.+?\)', '', param.description)
                
                parameters.append(param)
        
        return parameters
    
    def _parse_google_returns(self, content: str) -> Optional[ReturnDoc]:
        """解析 Google 风格返回值"""
        # 匹配返回值：type: description
        pattern = r'^(?:(\w+)\s*:\s*)?(.+)$'
        match = re.search(pattern, content.strip(), re.MULTILINE)
        
        if match:
            return ReturnDoc(
                type=match.group(1),
                description=match.group(2)
            )
        
        return ReturnDoc(description=content.strip())
    
    def _parse_google_raises(self, content: str) -> List[ExceptionDoc]:
        """解析 Google 风格异常"""
        exceptions = []
        
        # 匹配异常行：ExceptionType: description
        pattern = r'^\s*(\w+)\s*:\s*(.+)$'
        
        for match in re.finditer(pattern, content, re.MULTILINE):
            exc = ExceptionDoc(
                type=match.group(1),
                description=match.group(2)
            )
            exceptions.append(exc)
        
        return exceptions
    
    def _parse_google_examples(self, content: str) -> List[ExampleDoc]:
        """解析 Google 风格示例"""
        examples = []
        
        # 提取代码块
        code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', content, re.DOTALL)
        
        for lang, code in code_blocks:
            example = ExampleDoc(
                code=code.strip(),
                language=lang or 'python'
            )
            examples.append(example)
        
        # 如果没有代码块，将整个内容作为示例
        if not examples and content.strip():
            examples.append(ExampleDoc(
                code=content.strip(),
                language='python'
            ))
        
        return examples
    
    def _parse_numpy_style(self, docstring: str, result: ParsedDocstring):
        """解析 Numpy 风格文档字符串"""
        lines = docstring.strip().split('\n')
        
        # 提取描述
        description_lines = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line in ('Parameters', 'Returns', 'Attributes', 'Raises', 'Examples', 'Notes', 'Warnings'):
                break
            if line:  # 非空行才添加到描述
                description_lines.append(line)
            i += 1
        
        result.description = ' '.join(description_lines)
        
        # 解析参数
        while i < len(lines):
            if lines[i].strip() == 'Parameters':
                break
            i += 1
        
        if i < len(lines) and lines[i].strip() == 'Parameters':
            i += 1  # 跳过 Parameters 标题
            
            # 跳过分隔线（如果有）
            if i < len(lines) and lines[i].strip().startswith('---'):
                i += 1
            
            params_lines = []
            while i < len(lines):
                line = lines[i].strip()
                # 遇到其他章节标题时停止
                if line in ('Returns', 'Attributes', 'Raises', 'Examples', 'Notes', 'Warnings'):
                    break
                # 空行可能是参数之间的分隔，继续
                if not line:
                    i += 1
                    continue
                params_lines.append(lines[i])  # 保留原始行（包含缩进）
                i += 1
            
            result.parameters = self._parse_numpy_params('\n'.join(params_lines))
        
        # 解析返回值
        while i < len(lines):
            if lines[i].strip() == 'Returns':
                break
            i += 1
        
        if i < len(lines) and lines[i].strip() == 'Returns':
            i += 1  # 跳过 Returns 标题
            
            # 跳过分隔线（如果有）
            if i < len(lines) and lines[i].strip().startswith('---'):
                i += 1
            
            returns_lines = []
            while i < len(lines):
                line = lines[i].strip()
                if line in ('Parameters', 'Attributes', 'Raises', 'Examples', 'Notes', 'Warnings'):
                    break
                if not line:
                    i += 1
                    continue
                returns_lines.append(lines[i])
                i += 1
            
            result.returns = self._parse_numpy_returns('\n'.join(returns_lines))
    
    def _parse_numpy_params(self, content: str) -> List[ParameterDoc]:
        """解析 Numpy 风格参数"""
        parameters = []
        
        # Numpy 风格：
        # name : type
        #     description
        # name
        #     description
        
        lines = content.strip().split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 跳过空行
            if not line:
                i += 1
                continue
            
            # 跳过缩进行（描述）
            if line.startswith(' ') or line.startswith('\t'):
                i += 1
                continue
            
            # 检测参数行（行首开始，不缩进）
            # 可能格式：
            # name : type
            # name
            
            # 尝试匹配 name : type
            match = re.match(r'^(\w+)\s*:\s*(\w+)?\s*$', line)
            if match:
                param = ParameterDoc(
                    name=match.group(1),
                    type=match.group(2)
                )
                
                # 读取描述（下一行开始，所有缩进行）
                i += 1
                desc_lines = []
                while i < len(lines):
                    next_line = lines[i]
                    # 检查是否是缩进内容
                    if next_line.startswith(' ') or next_line.startswith('\t'):
                        desc_lines.append(next_line.strip())
                        i += 1
                    elif next_line.strip():  # 非空非缩进行，是下一个参数
                        break
                    else:  # 空行
                        i += 1
                
                param.description = ' '.join(desc_lines) if desc_lines else ''
                parameters.append(param)
                continue
            
            # 没有 ':' 的行，可能是只有 name
            match = re.match(r'^(\w+)\s*$', line)
            if match:
                param = ParameterDoc(name=match.group(1))
                
                # 读取描述
                i += 1
                desc_lines = []
                while i < len(lines):
                    next_line = lines[i]
                    if next_line.startswith(' ') or next_line.startswith('\t'):
                        desc_lines.append(next_line.strip())
                        i += 1
                    elif next_line.strip():
                        break
                    else:
                        i += 1
                
                param.description = ' '.join(desc_lines) if desc_lines else ''
                parameters.append(param)
                continue
            
            i += 1
        
        return parameters
    
    def _parse_numpy_returns(self, content: str) -> Optional[ReturnDoc]:
        """解析 Numpy 风格返回值"""
        lines = content.strip().split('\n')
        if lines:
            first_line = lines[0].strip()
            # type : description
            match = re.match(r'^(\w+)\s*:\s*(.+)$', first_line)
            if match:
                return ReturnDoc(
                    type=match.group(1),
                    description=match.group(2)
                )
        
        return ReturnDoc(description=content.strip())
    
    def _parse_sphinx_style(self, docstring: str, result: ParsedDocstring):
        """解析 Sphinx 风格文档字符串"""
        lines = docstring.strip().split('\n')
        
        # 提取描述（去掉 :param 等指令）
        description_lines = []
        for line in lines:
            if not line.strip().startswith(':'):
                description_lines.append(line.strip())
            else:
                break
        
        result.description = ' '.join(description_lines)
        
        # 解析参数 :param name: description
        param_pattern = r':param\s+(\w+)\s*:\s*(.+?)(?:\n|$)'
        for match in re.finditer(param_pattern, docstring):
            param = ParameterDoc(
                name=match.group(1),
                description=match.group(2).strip()
            )
            result.parameters.append(param)
        
        # 解析类型 :type name: type
        type_pattern = r':type\s+(\w+)\s*:\s*(\w+)'
        for match in re.finditer(type_pattern, docstring):
            param_name = match.group(1)
            param_type = match.group(2)
            # 更新已存在参数的类型
            for param in result.parameters:
                if param.name == param_name:
                    param.type = param_type
                    break
        
        # 解析返回值 :return: description
        return_match = re.search(r':return[s]?\s*:\s*(.+?)(?:\n|:rtype|$)', docstring, re.DOTALL)
        if return_match:
            result.returns = ReturnDoc(description=return_match.group(1).strip())
        
        # 解析返回类型 :rtype: type
        rtype_match = re.search(r':rtype\s*:\s*(\w+)', docstring)
        if rtype_match:
            if result.returns:
                result.returns.type = rtype_match.group(1)
            else:
                result.returns = ReturnDoc(type=rtype_match.group(1))
        
        # 解析异常 :raises Exception: description
        raises_pattern = r':raises?\s+(\w+)\s*:\s*(.+?)(?:\n|$)'
        for match in re.finditer(raises_pattern, docstring):
            exc = ExceptionDoc(
                type=match.group(1),
                description=match.group(2).strip()
            )
            result.raises.append(exc)
    
    def _parse_jsdoc_style(self, docstring: str, result: ParsedDocstring):
        """解析 JSDoc 风格文档字符串"""
        # 提取描述
        description_match = re.search(r'^\s*\*\s*([^@\n]+)', docstring, re.MULTILINE)
        if description_match:
            result.description = description_match.group(1).strip()
        
        # 解析参数 @param {type} name - description
        param_pattern = r'@param\s*\{([^}]+)\}\s+(\w+)\s*-?\s*(.+?)(?:\n|\* @|$)'
        for match in re.finditer(param_pattern, docstring):
            param = ParameterDoc(
                type=match.group(1),
                name=match.group(2),
                description=match.group(3).strip()
            )
            result.parameters.append(param)
        
        # 解析返回值 @returns {type} description
        return_match = re.search(r'@returns?\s*\{([^}]+)\}\s*(.+?)(?:\n|\* @|$)', docstring)
        if return_match:
            result.returns = ReturnDoc(
                type=return_match.group(1),
                description=return_match.group(2).strip()
            )
        
        # 解析异常 @throws {type} description
        throws_pattern = r'@throws?\s*\{([^}]+)\}\s*(.+?)(?:\n|\* @|$)'
        for match in re.finditer(throws_pattern, docstring):
            exc = ExceptionDoc(
                type=match.group(1),
                description=match.group(2).strip()
            )
            result.raises.append(exc)
    
    def _parse_bash_style(self, docstring: str, result: ParsedDocstring):
        """解析 Bash 风格文档字符串"""
        lines = docstring.strip().split('\n')
        
        # 提取描述
        description_lines = []
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                content = line.lstrip('#').strip()
                if content and not content.startswith('@'):
                    description_lines.append(content)
                else:
                    break
        
        result.description = ' '.join(description_lines)
        
        # 解析参数 @param name description
        param_pattern = r'#\s*@param\s+(\w+)\s+(.+?)$'
        for match in re.finditer(param_pattern, docstring, re.MULTILINE):
            param = ParameterDoc(
                name=match.group(1),
                description=match.group(2).strip()
            )
            result.parameters.append(param)
        
        # 解析返回值 @return description
        return_match = re.search(r'#\s*@return\s+(.+?)$', docstring, re.MULTILINE)
        if return_match:
            result.returns = ReturnDoc(description=return_match.group(1).strip())
        
        # 解析示例 @example
        example_match = re.search(r'#\s*@example\s+(.+?)(?=#\s*@|\Z)', docstring, re.DOTALL)
        if example_match:
            example = ExampleDoc(
                code=example_match.group(1).strip(),
                language='bash'
            )
            result.examples.append(example)
    
    def fill_missing_types(self, parsed_doc: ParsedDocstring, func_info) -> None:
        """从函数信息中补充缺失的类型"""
        # 补充参数类型
        for param in parsed_doc.parameters:
            if not param.type:
                # 从函数参数中查找类型
                for func_param in func_info.parameters:
                    if func_param.name == param.name and func_param.type:
                        param.type = func_param.type
                        break
        
        # 补充返回值类型
        if parsed_doc.returns and not parsed_doc.returns.type:
            if func_info.return_type:
                parsed_doc.returns.type = func_info.return_type
