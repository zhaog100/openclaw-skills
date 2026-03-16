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

#### 2.1.3 数据结构

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
