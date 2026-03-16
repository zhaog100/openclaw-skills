#!/usr/bin/env python3
"""
Auto Document Generator - 单元测试

测试覆盖：
1. 代码解析器（Parser）
2. 注释提取器（Extractor）
3. 文档生成器（Generator）
4. 性能测试
"""

import pytest
import time
from pathlib import Path
from auto_doc_generator.parser import CodeParser, Language, detect_language, FunctionInfo, ClassInfo
from auto_doc_generator.extractor import CommentExtractor, DocstringStyle, ParsedDocstring
from auto_doc_generator.generator import DocumentGenerator


class TestCodeParser:
    """代码解析器测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.parser = CodeParser(Language.PYTHON)
        self.test_dir = Path(__file__).parent.parent / "examples"
    
    def test_parse_simple_function(self):
        """测试：解析简单函数"""
        # 创建测试文件
        test_code = '''
def hello(name: str) -> str:
    """Say hello to someone.
    
    Args:
        name (str): The name of the person.
    
    Returns:
        str: A greeting message.
    """
    return f"Hello, {name}!"
'''
        
        # 写入临时文件
        test_file = self.test_dir / "test_simple.py"
        test_file.write_text(test_code)
        
        # 解析
        result = self.parser.parse_file(str(test_file))
        
        # 验证
        assert result is not None
        assert len(result.functions) == 1
        assert result.functions[0].name == "hello"
        assert len(result.functions[0].parameters) == 1
        assert result.functions[0].parameters[0].name == "name"
        assert result.functions[0].return_type == "str"
        assert "Say hello" in result.functions[0].docstring
        
        # 清理
        test_file.unlink()
    
    def test_parse_class_with_methods(self):
        """测试：解析类和方法的文档字符串"""
        test_code = '''
class Calculator:
    """A simple calculator class."""
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers.
        
        Args:
            a (int): First number
            b (int): Second number
        
        Returns:
            int: Sum of a and b
        """
        return a + b
'''
        
        test_file = self.test_dir / "test_class.py"
        test_file.write_text(test_code)
        
        result = self.parser.parse_file(str(test_file))
        
        # 验证类
        assert len(result.classes) == 1
        assert result.classes[0].name == "Calculator"
        assert "simple calculator" in result.classes[0].docstring
        
        # 验证方法
        assert len(result.classes[0].methods) == 1
        assert result.classes[0].methods[0].name == "add"
        assert len(result.classes[0].methods[0].parameters) == 2
        
        test_file.unlink()
    
    def test_parse_function_with_decorators(self):
        """测试：解析带装饰器的函数"""
        test_code = '''
@staticmethod
def static_method():
    """A static method."""
    pass

@property
def prop(self):
    """A property."""
    return None
'''
        
        test_file = self.test_dir / "test_decorators.py"
        test_file.write_text(test_code)
        
        result = self.parser.parse_file(str(test_file))
        
        assert len(result.functions) == 1  # static_method
        assert len(result.classes) == 0  # 没有类定义
        
        test_file.unlink()
    
    def test_parse_directory(self):
        """测试：解析整个目录"""
        # 创建多个测试文件
        test_files = []
        for i in range(3):
            test_code = f'''
def function_{i}():
    """Function {i}."""
    pass
'''
            test_file = self.test_dir / f"test_file_{i}.py"
            test_file.write_text(test_code)
            test_files.append(test_file)
        
        # 解析目录
        results = self.parser.parse_directory(str(self.test_dir), recursive=False)
        
        # 验证
        assert len(results) >= 3
        total_functions = sum(len(r.functions) for r in results)
        assert total_functions >= 3
        
        # 清理
        for f in test_files:
            f.unlink()
    
    def test_detect_language(self):
        """测试：自动检测文件语言"""
        assert detect_language("test.py") == Language.PYTHON
        assert detect_language("test.js") == Language.JAVASCRIPT
        assert detect_language("test.sh") == Language.BASH
        assert detect_language("test.txt") is None


class TestCommentExtractor:
    """注释提取器测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.extractor = CommentExtractor()
    
    def test_parse_google_style(self):
        """测试：解析 Google 风格 docstring"""
        docstring = """Add two numbers together.

Args:
    a (int): First number
    b (int): Second number

Returns:
    int: Sum of a and b

Raises:
    ValueError: If a or b is negative

Examples:
    ```python
    result = add(1, 2)
    print(result)  # Output: 3
    ```
"""
        
        result = self.extractor.parse_docstring(docstring, DocstringStyle.GOOGLE)
        
        # 验证描述
        assert "Add two numbers" in result.description
        
        # 验证参数
        assert len(result.parameters) == 2
        assert result.parameters[0].name == "a"
        assert result.parameters[0].type == "int"
        assert "First number" in result.parameters[0].description
        
        # 验证返回值
        assert result.returns is not None
        assert result.returns.type == "int"
        assert "Sum" in result.returns.description
        
        # 验证异常
        assert len(result.raises) == 1
        assert result.raises[0].type == "ValueError"
    
    def test_parse_numpy_style(self):
        """测试：解析 Numpy 风格 docstring"""
        docstring = """Calculate the sum of two numbers.

Parameters
----------
a : int
    First number
b : int
    Second number

Returns
-------
int
    Sum of a and b
"""
        
        result = self.extractor.parse_docstring(docstring, DocstringStyle.NUMPY)
        
        assert "Calculate the sum" in result.description
        assert len(result.parameters) >= 1
    
    def test_parse_sphinx_style(self):
        """测试：解析 Sphinx 风格 docstring"""
        docstring = """Add two numbers.

:param a: First number
:type a: int
:param b: Second number
:type b: int
:return: Sum of a and b
:rtype: int
:raises ValueError: If a or b is negative
"""
        
        result = self.extractor.parse_docstring(docstring, DocstringStyle.SPHINX)
        
        assert "Add two numbers" in result.description
        assert len(result.parameters) == 2
        assert result.returns is not None
        assert result.returns.type == "int"
    
    def test_auto_detect_style(self):
        """测试：自动检测 docstring 风格"""
        # Google 风格
        google_doc = """Add two numbers.

Args:
    a (int): First number
    b (int): Second number

Returns:
    int: Sum
"""
        result = self.extractor.parse_docstring(google_doc)
        # 应该能正确解析
        
        # Sphinx 风格
        sphinx_doc = """Add two numbers.

:param a: First number
:return: Sum
"""
        result = self.extractor.parse_docstring(sphinx_doc)
        assert ":param" in result.raw_docstring
    
    def test_empty_docstring(self):
        """测试：空 docstring 处理"""
        result = self.extractor.parse_docstring("")
        assert result.description == ""
        assert len(result.parameters) == 0


class TestDocumentGenerator:
    """文档生成器测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.generator = DocumentGenerator()
        self.test_dir = Path(__file__).parent.parent / "docs" / "test_output"
        self.test_dir.mkdir(parents=True, exist_ok=True)
    
    def test_generate_api_doc(self):
        """测试：生成 API 文档"""
        # 创建模拟解析结果
        from auto_doc_generator.parser import ParseTree, FunctionInfo, Parameter
        
        result = ParseTree(
            file_path="test.py",
            language=Language.PYTHON
        )
        
        func = FunctionInfo(
            name="add",
            docstring="Add two numbers.",
            file_path="test.py"
        )
        func.parameters = [
            Parameter(name="a", type="int"),
            Parameter(name="b", type="int")
        ]
        func.return_type = "int"
        
        result.functions = [func]
        
        # 生成文档
        doc_content = self.generator.generate_api_doc([result])
        
        # 验证
        assert doc_content is not None
        assert len(doc_content) > 0
        assert "add" in doc_content
        assert "Add two numbers" in doc_content
    
    def test_save_documentation(self):
        """测试：保存文档到文件"""
        content = "# Test Documentation\n\nThis is a test."
        output_path = self.test_dir / "test_api.md"
        
        success = self.generator.save_documentation(content, str(output_path))
        
        assert success is True
        assert output_path.exists()
        assert output_path.read_text() == content
        
        # 清理
        output_path.unlink()


class TestPerformance:
    """性能测试"""
    
    def test_parse_performance(self):
        """测试：解析性能（< 1 秒）"""
        parser = CodeParser(Language.PYTHON)
        
        # 创建大型测试文件（> 1000 行）
        test_code = "\n".join([
            f'''
def function_{i}(param_{i}: int) -> int:
    """Function {i}.
    
    Args:
        param_{i} (int): Parameter {i}
    
    Returns:
        int: Result {i}
    """
    return param_{i} * 2
''' for i in range(100)
        ])
        
        test_dir = Path(__file__).parent.parent / "examples"
        test_file = test_dir / "test_performance.py"
        test_file.write_text(test_code)
        
        # 计时
        start_time = time.time()
        result = parser.parse_file(str(test_file))
        end_time = time.time()
        
        # 验证
        assert len(result.functions) == 100
        assert (end_time - start_time) < 1.0, f"解析耗时 {end_time - start_time:.2f} 秒，超过 1 秒"
        
        # 清理
        test_file.unlink()
    
    def test_extraction_accuracy(self):
        """测试：提取准确率（> 90%）"""
        extractor = CommentExtractor()
        
        # 测试用例
        test_cases = [
            {
                "docstring": "Add two numbers.\n\nArgs:\n    a (int): First\n    b (int): Second\n\nReturns:\n    int: Sum",
                "expected_params": ["a", "b"],
                "expected_return": "int"
            },
            {
                "docstring": "Calculate sum.\n\nParameters\n----------\na : int\n    First\nb : int\n    Second",
                "expected_params": ["a", "b"],
                "expected_return": None
            },
            {
                "docstring": "Add numbers.\n\n:param a: First\n:param b: Second\n:return: Sum",
                "expected_params": ["a", "b"],
                "expected_return": None
            }
        ]
        
        correct = 0
        total = len(test_cases)
        
        for case in test_cases:
            result = extractor.parse_docstring(case["docstring"])
            
            # 检查参数
            param_names = [p.name for p in result.parameters]
            if param_names == case["expected_params"]:
                correct += 1
        
        accuracy = (correct / total) * 100
        assert accuracy >= 90, f"提取准确率 {accuracy:.1f}%，低于 90%"


class TestIntegration:
    """集成测试"""
    
    def test_end_to_end(self):
        """测试：端到端流程（解析 → 提取 → 生成）"""
        # 1. 准备测试代码
        test_code = '''
def calculate_sum(numbers: list) -> int:
    """Calculate the sum of a list of numbers.
    
    Args:
        numbers (list): List of numbers to sum
    
    Returns:
        int: Sum of all numbers
    
    Examples:
        ```python
        result = calculate_sum([1, 2, 3])
        print(result)  # Output: 6
        ```
    """
    return sum(numbers)
'''
        
        test_dir = Path(__file__).parent.parent / "examples"
        test_file = test_dir / "test_integration.py"
        test_file.write_text(test_code)
        
        # 2. 解析代码
        parser = CodeParser(Language.PYTHON)
        parse_result = parser.parse_file(str(test_file))
        
        assert len(parse_result.functions) == 1
        func = parse_result.functions[0]
        
        # 3. 提取注释
        extractor = CommentExtractor()
        func.parsed_doc = extractor.parse_docstring(func.docstring)
        
        assert "Calculate the sum" in func.parsed_doc.description
        assert len(func.parsed_doc.parameters) == 1
        
        # 4. 生成文档
        generator = DocumentGenerator()
        doc_content = generator.generate_api_doc([parse_result])
        
        assert "calculate_sum" in doc_content
        assert "Calculate the sum" in doc_content
        
        # 清理
        test_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
