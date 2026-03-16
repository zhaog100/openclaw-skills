# 技术设计文档 - 自动文档生成器

**文档版本**：v1.0  
**创建日期**：2026-03-16  
**创建者**：小米粒（Dev 代理）  
**状态**：设计中  
**基于 PRD**：v1.1

---

## 1. 系统架构

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    自动文档生成器 v1.0                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  代码解析器   │  │  注释提取器   │  │  AI 增强器   │     │
│  │ (Parser)     │  │ (Extractor)  │  │ (Enhancer)   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│          │                  │                  │              │
│          └──────────────────┼──────────────────┘              │
│                             │                                  │
│                     ┌───────▼───────┐                        │
│                     │  文档生成器   │                        │
│                     │ (Generator)  │                        │
│                     └───────┬───────┘                        │
│                             │                                  │
│          ┌──────────────────┼──────────────────┐              │
│          │                  │                  │              │
│  ┌───────▼───────┐  ┌──────▼──────┐  ┌──────▼──────┐       │
│  │  模板引擎     │  │  格式转换器  │  │  更新检测器  │       │
│  │ (Templates)  │  │ (Converter) │  │ (Watcher)   │       │
│  └───────────────┘  └─────────────┘  └─────────────┘       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 核心模块

1. **代码解析器（Parser）**：解析多种语言的代码文件
2. **注释提取器（Extractor）**：提取注释、docstring、类型信息
3. **AI 增强器（Enhancer）**：使用 AI 增强文档内容（可选）
4. **文档生成器（Generator）**：生成结构化文档
5. **模板引擎（Templates）**：管理文档模板
6. **格式转换器（Converter）**：转换文档格式
7. **更新检测器（Watcher）**：检测代码变更并触发更新

---

## 2. 核心模块设计

### 2.1 代码解析器（Parser）

#### 2.1.1 技术选型
- **tree-sitter**：多语言语法解析器
  - Python: `tree-sitter-python`
  - JavaScript: `tree-sitter-javascript`
  - Bash: `tree-sitter-bash`

#### 2.1.2 接口设计

```python
class CodeParser:
    """代码解析器基类"""
    
    def __init__(self, language: str):
        self.language = language
        self.parser = self._init_parser()
    
    def parse_file(self, file_path: str) -> ParseTree:
        """解析单个文件"""
        pass
    
    def parse_directory(self, dir_path: str) -> List[ParseTree]:
        """解析整个目录"""
        pass
    
    def extract_functions(self, tree: ParseTree) -> List[FunctionInfo]:
        """提取函数信息"""
        pass
    
    def extract_classes(self, tree: ParseTree) -> List[ClassInfo]:
        """提取类信息"""
        pass
```

#### 2.1.3 tree-sitter 使用示例

```python
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

# 初始化 Python 解析器
PY_LANGUAGE = Language(tspython.language())
parser = Parser()
parser.set_language(PY_LANGUAGE)

# 解析 Python 代码
code = """
def hello(name: str) -> str:
    '''Say hello to someone.
    
    Args:
        name: The name of the person.
    
    Returns:
        A greeting message.
    '''
    return f"Hello, {name}!"
"""

tree = parser.parse(bytes(code, "utf8"))

# 提取函数定义
def extract_functions_from_tree(tree):
    """从语法树中提取函数"""
    functions = []
    
    # 查找函数定义节点
    query = tree.root_node.children
    for node in query:
        if node.type == 'function_definition':
            func_name = node.child_by_field_name('name').text.decode()
            func_params = node.child_by_field_name('parameters')
            func_body = node.child_by_field_name('body')
            
            functions.append(FunctionInfo(
                name=func_name,
                parameters=extract_parameters(func_params),
                start_line=node.start_point[0],
                end_line=node.end_point[0],
                source_code=tree.text[node.start_byte:node.end_byte].decode()
            ))
    
    return functions

# 使用示例
functions = extract_functions_from_tree(tree)
print(f"Found {len(functions)} functions")
for func in functions:
    print(f"  - {func.name} (line {func.start_line})")
```

**输出**：
```
Found 1 functions
  - hello (line 2)
```

---

#### 2.1.4 数据结构

```python
@dataclass
class FunctionInfo:
    """函数信息"""
    name: str
    parameters: List[Parameter]
    return_type: Optional[str]
    docstring: Optional[str]
    start_line: int
    end_line: int
    source_code: str

@dataclass
class ClassInfo:
    """类信息"""
    name: str
    docstring: Optional[str]
    methods: List[FunctionInfo]
    attributes: List[Attribute]
    start_line: int
    end_line: int
```

---

### 2.2 注释提取器（Extractor）

#### 2.2.1 支持的注释风格

1. **Python**
   - Google 风格
   - Numpy 风格
   - Sphinx 风格（reStructuredText）

2. **JavaScript**
   - JSDoc
   - TypeScript 类型注释

3. **Bash**
   - 标准注释块
   - 函数注释

#### 2.2.2 接口设计

```python
class CommentExtractor:
    """注释提取器"""
    
    def extract_docstring(self, node: ASTNode) -> Optional[str]:
        """提取 docstring"""
        pass
    
    def parse_docstring(self, docstring: str, style: str) -> ParsedDocstring:
        """解析 docstring"""
        pass
    
    def extract_parameters(self, docstring: str) -> List[ParameterDoc]:
        """提取参数说明"""
        pass
    
    def extract_returns(self, docstring: str) -> Optional[ReturnDoc]:
        """提取返回值说明"""
        pass
```

#### 2.2.3 数据结构

```python
@dataclass
class ParsedDocstring:
    """解析后的 docstring"""
    description: str
    parameters: List[ParameterDoc]
    returns: Optional[ReturnDoc]
    raises: List[ExceptionDoc]
    examples: List[str]

@dataclass
class ParameterDoc:
    """参数文档"""
    name: str
    type: Optional[str]
    description: str
    default: Optional[str]
```

---

### 2.3 AI 增强器（Enhancer）

#### 2.3.1 技术选型
- **本地模型**：Ollama（Llama 3 / CodeLlama）
- **云端模型**：Claude / GPT-4（可选）
- **优先级**：本地 > 云端

#### 2.3.2 接口设计

```python
class AIEnhancer:
    """AI 增强器"""
    
    def __init__(self, model: str = "llama3", local: bool = True):
        self.model = model
        self.local = local
        self.client = self._init_client()
    
    def enhance_description(self, code: str, existing_doc: Optional[str]) -> str:
        """增强函数/类描述"""
        pass
    
    def generate_examples(self, function: FunctionInfo) -> List[str]:
        """生成代码示例"""
        pass
    
    def improve_readability(self, doc: str) -> str:
        """改进文档可读性"""
        pass
    
    def fill_missing_params(self, params: List[ParameterDoc]) -> List[ParameterDoc]:
        """补充缺失的参数说明"""
        pass
```

#### 2.3.3 Prompt 模板

```python
ENHANCE_DESCRIPTION_PROMPT = """
You are a technical documentation expert. Enhance the following function description:

Function: {function_name}
Parameters: {parameters}
Return: {return_type}

Existing Description:
{existing_doc}

Code:
```{language}
{code}
```

Generate a clear, concise description that:
1. Explains what the function does
2. Mentions important parameters
3. Describes the return value
4. Includes any important notes or warnings

Output only the enhanced description, no explanations.
"""

GENERATE_EXAMPLES_PROMPT = """
Generate 1-2 code examples for the following function:

Function: {function_name}
Parameters: {parameters}
Description: {description}

Examples should be:
1. Simple and easy to understand
2. Show typical usage
3. Include expected output

Output only the code examples, formatted as Markdown code blocks.
"""
```

---

### 2.4 文档生成器（Generator）

#### 2.4.1 文档类型

1. **API 文档**
   - 函数列表
   - 参数说明
   - 返回值说明
   - 示例代码

2. **README 文档**
   - 项目简介
   - 安装说明
   - 快速开始
   - API 参考
   - 贡献指南

3. **Changelog 文档**
   - 版本历史
   - 变更记录

#### 2.4.2 接口设计

```python
class DocumentGenerator:
    """文档生成器"""
    
    def __init__(self, template_dir: str):
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))
    
    def generate_api_doc(self, module_info: ModuleInfo) -> str:
        """生成 API 文档"""
        pass
    
    def generate_readme(self, project_info: ProjectInfo) -> str:
        """生成 README"""
        pass
    
    def generate_changelog(self, changes: List[Change]) -> str:
        """生成 Changelog"""
        pass
    
    def render_template(self, template_name: str, context: dict) -> str:
        """渲染模板"""
        pass
```

---

### 2.5 模板引擎（Templates）

#### 2.5.1 模板结构

```
templates/
├── api/
│   ├── markdown.jinja2
│   ├── html.jinja2
│   └── pdf.jinja2
├── readme/
│   ├── python.jinja2
│   ├── javascript.jinja2
│   └── bash.jinja2
├── changelog/
│   └── keep_a_changelog.jinja2
└── base/
    ├── header.jinja2
    ├── footer.jinja2
    └── common.jinja2
```

#### 2.5.2 模板继承

```jinja2
<!-- base/api_base.jinja2 -->
# {{ module_name }}

{{ module_description }}

{% block functions %}
## Functions
{% for func in functions %}
### {{ func.name }}

{{ func.description }}

**Parameters:**
{% for param in func.parameters %}
- `{{ param.name }}` ({{ param.type }}): {{ param.description }}
{% endfor %}

**Returns:** {{ func.return_type }} - {{ func.return_description }}

{% endblock %}

{% block examples %}
{% include "common/examples.jinja2" %}
{% endblock %}
```

---

#### 2.5.3 完整模板示例

**templates/api/python.jinja2**（Python API 文档模板）：

```jinja2
{% extends "base/api_base.jinja2" %}

{% block header %}
# {{ module_name }} - Python API Documentation

> Auto-generated documentation for {{ module_name }}
{% endblock %}

{% block functions %}
## Functions

{% for func in functions %}
### `{{ func.name }}({% for param in func.parameters %}{{ param.name }}{% if not loop.last %}, {% endif %}{% endfor %})`

{{ func.description }}

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
{% for param in func.parameters %}
| `{{ param.name }}` | `{{ param.type }}` | {{ param.description }} |
{% endfor %}

**Returns:** `{{ func.return_type }}`

{{ func.return_description if func.return_description else "None" }}

**Example:**

```python
{% if func.examples %}
{{ func.examples[0] }}
{% else %}
# Example usage (auto-generated)
result = {{ func.name }}()
print(result)
{% endif %}
```

**Raises:**

{% if func.raises %}
{% for exception in func.raises %}
- `{{ exception.type }}`: {{ exception.description }}
{% endfor %}
{% endif %}

{% endfor %}
{% endblock %}

{% block footer %}
---

*Generated by auto-document-generator on {{ generation_date }}*
{% endblock %}
```

**templates/common/examples.jinja2**（通用示例组件）:

```jinja2
## Examples

{% if examples %}
{% for example in examples %}
### Example {{ loop.index + 1 }}

```{{ language }}
{{ example.code }}
```

**Output:**
```
{{ example.output }}
```

{% endfor %}
{% else %}
_No examples available._
{% endif %}
```

---

#### 2.5.4 模板使用示例

```python
from jinja2 import Environment, FileSystemLoader

# 初始化模板环境
env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True
)

# 加载模板
template = env.get_template('api/python.jinja2')

# 渲染文档
doc_content = template.render(
    module_name='my_module',
    module_description='A sample Python module',
    functions=[
        {
            'name': 'add_numbers',
            'description': 'Add two numbers together',
            'parameters': [
                {'name': 'a', 'type': 'int', 'description': 'First number'},
                {'name': 'b', 'type': 'int', 'description': 'Second number'}
            ],
            'return_type': 'int',
            'return_description': 'Sum of a and b',
            'examples': ['result = add_numbers(1, 2)\nprint(result)  # Output: 3'],
            'raises': []
        }
    ],
    generation_date='2026-03-16'
)

print(doc_content)
```

---

### 2.6 格式转换器（Converter）

#### 2.6.1 支持的格式

- **输入**：Markdown
- **输出**：Markdown, HTML, PDF

#### 2.6.2 技术选型

- **Markdown → HTML**：markdown-it-py
- **HTML → PDF**：WeasyPrint（可选）

#### 2.6.3 接口设计

```python
class DocumentConverter:
    """文档格式转换器"""
    
    def markdown_to_html(self, markdown: str) -> str:
        """Markdown 转 HTML"""
        pass
    
    def html_to_pdf(self, html: str) -> bytes:
        """HTML 转 PDF"""
        pass
    
    def add_syntax_highlighting(self, html: str) -> str:
        """添加语法高亮"""
        pass
```

---

### 2.7 更新检测器（Watcher）

#### 2.7.1 更新策略

1. **Git Hooks**
   - pre-commit：提交前检测文档更新
   - post-commit：提交后自动生成文档

2. **文件监听**
   - watchdog：实时监听文件变更
   - 增量更新：只更新变更的文档

3. **CI/CD 集成**
   - GitHub Actions：自动生成文档
   - 触发条件：push to master

#### 2.7.2 接口设计

```python
class DocumentWatcher:
    """文档更新检测器"""
    
    def detect_changes(self, file_path: str) -> List[Change]:
        """检测文件变更"""
        pass
    
    def should_update_doc(self, changes: List[Change]) -> bool:
        """判断是否需要更新文档"""
        pass
    
    def setup_git_hooks(self, repo_path: str):
        """设置 Git Hooks"""
        pass
    
    def start_watching(self, directory: str):
        """开始监听目录"""
        pass
```

---

## 3. 数据流设计

### 3.1 主流程

```
输入：代码文件/目录
  ↓
1. 代码解析（Parser）
  ↓
2. 注释提取（Extractor）
  ↓
3. AI 增强（Enhancer，可选）
  ↓
4. 文档生成（Generator）
  ↓
5. 格式转换（Converter，可选）
  ↓
输出：文档文件
```

### 3.2 详细流程

```python
def generate_documentation(
    code_path: str,
    output_format: str = "markdown",
    use_ai: bool = False,
    template: str = "default"
) -> str:
    """生成文档的主流程"""
    
    # 1. 代码解析
    parser = CodeParser(language=detect_language(code_path))
    parse_tree = parser.parse_file(code_path)
    
    # 2. 提取函数/类信息
    functions = parser.extract_functions(parse_tree)
    classes = parser.extract_classes(parse_tree)
    
    # 3. 注释提取
    extractor = CommentExtractor()
    for func in functions:
        func.docstring = extractor.extract_docstring(func)
        func.parsed_doc = extractor.parse_docstring(func.docstring)
    
    # 4. AI 增强（可选）
    if use_ai:
        enhancer = AIEnhancer(model="llama3", local=True)
        for func in functions:
            if not func.parsed_doc.description:
                func.parsed_doc.description = enhancer.enhance_description(
                    func.source_code, func.docstring
                )
    
    # 5. 文档生成
    generator = DocumentGenerator(template_dir="templates")
    doc_content = generator.generate_api_doc(ModuleInfo(
        functions=functions,
        classes=classes
    ))
    
    # 6. 格式转换（可选）
    if output_format == "html":
        converter = DocumentConverter()
        doc_content = converter.markdown_to_html(doc_content)
    
    return doc_content

---

### 3.2 模块间通信机制

#### 3.2.1 数据传递方式

**序列化格式**：JSON（模块间通信的标准格式）

```python
import json
from dataclasses import asdict

def serialize_parse_result(tree: ParseTree) -> str:
    """序列化解析结果（Parser → Extractor）"""
    return json.dumps({
        'file_path': tree.file_path,
        'language': tree.language,
        'functions': [asdict(f) for f in tree.functions],
        'classes': [asdict(c) for c in tree.classes]
    })

def deserialize_parse_result(json_str: str) -> ParseTree:
    """反序列化解析结果"""
    data = json.loads(json_str)
    return ParseTree(**data)

def serialize_comment_data(comment_data: ParsedDocstring) -> str:
    """序列化注释数据（Extractor → AI Enhancer/Generator）"""
    return json.dumps(asdict(comment_data))

def serialize_module_info(module_info: ModuleInfo) -> str:
    """序列化模块信息（Generator → Converter）"""
    return json.dumps({
        'module_name': module_info.module_name,
        'functions': [serialize_comment_data(f.parsed_doc) for f in module_info.functions],
        'classes': [serialize_comment_data(c.parsed_doc) for c in module_info.classes]
    })
```

#### 3.2.2 数据流示例

```python
# Parser → Extractor
parse_tree = parser.parse_file("example.py")
parse_json = serialize_parse_result(parse_tree)
# 传递给 Extractor
comment_data = extractor.extract_from_json(parse_json)

# Extractor → AI Enhancer
comment_json = serialize_comment_data(comment_data)
enhanced_data = enhancer.enhance_from_json(comment_json)

# Generator → Converter
module_info = generator.generate_module_info(enhanced_data)
module_json = serialize_module_info(module_info)
html_content = converter.convert_from_json(module_json, "html")
```

#### 3.2.3 性能优化
- **批量传输**：一次传递多个函数/类的信息
- **增量更新**：只传递变更的部分
- **压缩传输**：使用 gzip 压缩 JSON 数据
```

---

## 4. 命令行接口设计

### 4.1 命令结构

```bash
auto-doc-generator <command> [options]

Commands:
  generate    生成文档
  watch       监听文件变更
  init        初始化配置
  template    管理模板

Options:
  --format    输出格式（markdown/html/pdf）
  --ai        启用 AI 增强
  --template  指定模板
  --output    输出目录
```

### 4.2 使用示例

```bash
# 生成 API 文档
auto-doc-generator generate --input src/ --output docs/

# 启用 AI 增强
auto-doc-generator generate --input src/ --ai --model llama3

# 生成 HTML 格式
auto-doc-generator generate --input src/ --format html

# 监听文件变更
auto-doc-generator watch --input src/ --output docs/

# 初始化配置
auto-doc-generator init --project myproject

# 列出可用模板
auto-doc-generator template list
```

---

## 5. 技术栈详解

### 5.1 核心依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| tree-sitter | 0.20.x | 代码解析 |
| tree-sitter-python | 0.20.x | Python 语法 |
| tree-sitter-javascript | 0.20.x | JavaScript 语法 |
| tree-sitter-bash | 0.20.x | Bash 语法 |
| Jinja2 | 3.x | 模板引擎 |
| markdown-it-py | 3.x | Markdown 渲染 |
| watchdog | 3.x | 文件监听 |
| ollama | 0.1.x | 本地 AI（可选） |

### 5.2 可选依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| WeasyPrint | 60.x | PDF 生成 |
| Pygments | 2.x | 语法高亮 |
| openai | 1.x | 云端 AI（可选） |

---

## 6. 性能优化

### 6.1 解析优化
- **增量解析**：只解析变更的文件
- **并行解析**：多线程解析多个文件
- **缓存机制**：缓存解析结果

### 6.2 AI 优化
- **批量处理**：一次处理多个函数
- **本地优先**：使用 Ollama 本地模型
- **结果缓存**：缓存 AI 生成结果

### 6.3 生成优化
- **模板缓存**：缓存编译后的模板
- **增量更新**：只更新变更的部分
- **并行生成**：并行生成多个文档

---

## 7. 错误处理

### 7.1 错误类型

1. **解析错误**：代码语法错误
2. **提取错误**：注释格式不支持
3. **生成错误**：模板渲染错误
4. **AI 错误**：模型调用失败

### 7.2 错误处理策略

```python
class DocumentGenerationError(Exception):
    """文档生成错误"""
    pass

def generate_documentation_safe(code_path: str) -> Optional[str]:
    """安全的文档生成"""
    try:
        return generate_documentation(code_path)
    except ParseError as e:
        logger.error(f"Parse error: {e}")
        return None
    except ExtractionError as e:
        logger.warning(f"Extraction error: {e}")
        # 继续生成，但跳过该部分
        return generate_documentation(code_path, skip_errors=True)
    except AIError as e:
        logger.warning(f"AI error: {e}")
        # 降级到基础文档
        return generate_documentation(code_path, use_ai=False)
```

---

## 8. 测试策略

### 8.1 单元测试
- **解析器测试**：测试各种代码结构
- **提取器测试**：测试各种注释风格
- **生成器测试**：测试模板渲染

### 8.2 集成测试
- **端到端测试**：从代码到文档
- **AI 增强测试**：测试 AI 功能
- **格式转换测试**：测试各种输出格式

### 8.3 性能测试
- **大型项目测试**：测试大型代码库
- **并行测试**：测试并行性能
- **内存测试**：测试内存占用

---

## 9. 部署方案

### 9.1 本地部署
```bash
# 安装依赖
pip install -r requirements.txt

# 安装 tree-sitter 语言包
python -c "import tree_sitter_python; print('OK')"

# 安装 Ollama（可选）
curl https://ollama.ai/install.sh | sh
ollama pull llama3
```

### 9.2 ClawHub 发布
```bash
# 打包技能
clawhub pack auto-document-generator/

# 发布到 ClawHub
clawhub publish auto-document-generator/
```

---

## 10. 文件结构

```
auto-document-generator/
├── SKILL.md                    # 技能说明
├── package.json                # 包配置
├── requirements.txt            # Python 依赖
├── setup.py                    # 安装脚本
├── auto_doc_generator/         # 核心代码
│   ├── __init__.py
│   ├── parser.py               # 代码解析器
│   ├── extractor.py            # 注释提取器
│   ├── enhancer.py             # AI 增强器
│   ├── generator.py            # 文档生成器
│   ├── templates.py            # 模板管理
│   ├── converter.py            # 格式转换器
│   ├── watcher.py              # 更新检测器
│   └── cli.py                  # 命令行接口
├── templates/                  # 模板文件
│   ├── api/
│   ├── readme/
│   └── changelog/
├── tests/                      # 测试文件
│   ├── test_parser.py
│   ├── test_extractor.py
│   ├── test_generator.py
│   └── test_enhancer.py
├── examples/                   # 示例代码
│   ├── python_example.py
│   ├── javascript_example.js
│   └── bash_example.sh
└── docs/                       # 文档
    ├── README.md
    ├── API.md
    └── EXAMPLES.md
```

---

## 11. 下一步计划

### 11.1 立即开始
1. ✅ 创建技术设计文档（已完成）
2. ⏳ 搭建项目结构
3. ⏳ 实现 Parser 模块
4. ⏳ 实现 Extractor 模块

### 11.2 本周完成
- Phase 1 (MVP)：代码注释提取 + API 文档生成
- 测试覆盖率 > 85%
- Git 提交并推送

---

*创建时间：2026-03-16 15:41*  
*版本：v1.0*  
*状态：技术设计完成*  
*下一步：开始开发实现*

---

## 12. 性能测试详细方案（补充）

### 12.1 测试环境
- **硬件**：标准开发机（8核CPU + 16GB内存）
- **测试项目**：
  - 小型项目：< 10 文件，< 1000 行代码
  - 中型项目：10-50 文件，1000-5000 行代码
  - 大型项目：> 50 文件，> 5000 行代码

### 12.2 性能指标测试

| 指标 | 测试方法 | 目标值 | 测试工具 |
|------|----------|--------|----------|
| **文档生成时间** | 解析 + 生成全流程 | < 30 秒/项目 | Python `time` + `pytest-benchmark` |
| **提取准确率** | 对比手工文档与自动生成 | > 90% | 人工审核 + 自动对比脚本 |
| **模板加载时间** | 加载 + 渲染模板 | < 1 秒 | Python `time.time()` |
| **AI 增强时间** | Ollama 调用 | < 10 秒/文档 | Python `time.time()` |

### 12.3 性能测试脚本

**tests/test_performance.py**:

```python
import pytest
import time
from auto_doc_generator import CodeParser, DocumentGenerator

class TestPerformance:
    """性能测试"""
    
    @pytest.mark.benchmark
    def test_parse_large_file(self, benchmark):
        """测试解析大型文件（> 1000 行）"""
        parser = CodeParser(language='python')
        
        # 基准测试：解析大型文件
        result = benchmark(parser.parse_file, 'examples/large_file.py')
        
        # 验证：解析时间 < 1 秒
        assert benchmark.stats['mean'] < 1.0
    
    @pytest.mark.benchmark
    def test_generate_large_project(self, benchmark):
        """测试生成大型项目文档（> 50 文件）"""
        generator = DocumentGenerator(template_dir='templates')
        
        # 基准测试：生成文档
        result = benchmark(generator.generate_from_directory, 'examples/large_project/')
        
        # 验证：生成时间 < 30 秒
        assert benchmark.stats['mean'] < 30.0
    
    @pytest.mark.benchmark
    def test_template_loading(self, benchmark):
        """测试模板加载时间"""
        from jinja2 import Environment, FileSystemLoader
        
        # 基准测试：加载模板
        result = benchmark(
            lambda: Environment(loader=FileSystemLoader('templates')).get_template('api/python.jinja2')
        )
        
        # 验证：加载时间 < 1 秒
        assert benchmark.stats['mean'] < 1.0
    
    def test_extraction_accuracy(self):
        """测试提取准确率"""
        from auto_doc_generator import CommentExtractor
        
        extractor = CommentExtractor()
        
        # 测试用例：标准 Google 风格 docstring
        test_code = '''
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together.
    
    Args:
        a (int): First number
        b (int): Second number
    
    Returns:
        int: Sum of a and b
    """
    return a + b
'''
        
        # 提取注释
        parsed_doc = extractor.extract_from_code(test_code)
        
        # 验证：提取准确率 > 90%
        assert parsed_doc.description == "Add two numbers together."
        assert len(parsed_doc.parameters) == 2
        assert parsed_doc.returns == "int: Sum of a and b"
```

### 12.4 运行性能测试

```bash
# 安装 pytest-benchmark
pip install pytest-benchmark

# 运行所有性能测试
pytest tests/test_performance.py -v --benchmark-only

# 运行特定测试
pytest tests/test_performance.py::TestPerformance::test_generate_large_project -v

# 生成性能报告
pytest tests/test_performance.py --benchmark-only --benchmark-json=performance_report.json
```

### 12.5 性能测试通过标准

| 指标 | 通过标准 | 失败处理 |
|------|----------|----------|
| 文档生成时间 | < 30 秒（大型项目） | 优化并行解析 + 增量更新 |
| 提取准确率 | > 90% | 改进正则表达式 + 多风格支持 |
| 模板加载时间 | < 1 秒 | 启用模板缓存 |
| AI 增强时间 | < 10 秒/文档 | 优化 Prompt + 批量处理 |

---

*补充时间：2026-03-16 15:55*  
*版本：v1.0 + 性能测试方案补充*  
