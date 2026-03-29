#!/usr/bin/env python3
"""
命令行接口 - auto-document-generator CLI

Usage:
    auto-doc-generator <command> [options]

Commands:
    generate    生成文档
    watch       监听文件变更
    init        初始化配置
    template    管理模板

Examples:
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
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional, List

from .parser import CodeParser, Language, detect_language
from .extractor import CommentExtractor, DocstringStyle
from .generator import DocumentGenerator
from .enhancer import AIEnhancer, AIConfig

# 版本信息
__version__ = "1.0.0"

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """创建命令行解析器"""
    parser = argparse.ArgumentParser(
        prog='auto-doc-generator',
        description='自动从代码生成技术文档',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate --input src/ --output docs/
  %(prog)s generate --input src/ --ai --model llama3
  %(prog)s watch --input src/ --output docs/
  %(prog)s init --project myproject
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # generate 命令
    gen_parser = subparsers.add_parser('generate', help='生成文档')
    gen_parser.add_argument(
        '--input', '-i',
        required=True,
        help='输入文件或目录路径'
    )
    gen_parser.add_argument(
        '--output', '-o',
        default='docs/',
        help='输出目录（默认：docs/）'
    )
    gen_parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'html', 'json'],
        default='markdown',
        help='输出格式（默认：markdown）'
    )
    gen_parser.add_argument(
        '--ai',
        action='store_true',
        help='启用 AI 增强'
    )
    gen_parser.add_argument(
        '--model',
        default='llama3',
        help='AI 模型名称（默认：llama3）'
    )
    gen_parser.add_argument(
        '--template', '-t',
        default='default',
        help='模板名称（默认：default）'
    )
    gen_parser.add_argument(
        '--language', '-l',
        choices=['python', 'javascript', 'bash', 'auto'],
        default='auto',
        help='编程语言（默认：auto）'
    )
    gen_parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        default=True,
        help='递归处理目录（默认：True）'
    )
    gen_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出'
    )
    
    # watch 命令
    watch_parser = subparsers.add_parser('watch', help='监听文件变更')
    watch_parser.add_argument(
        '--input', '-i',
        required=True,
        help='输入目录路径'
    )
    watch_parser.add_argument(
        '--output', '-o',
        default='docs/',
        help='输出目录（默认：docs/）'
    )
    watch_parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'html'],
        default='markdown',
        help='输出格式（默认：markdown）'
    )
    watch_parser.add_argument(
        '--ai',
        action='store_true',
        help='启用 AI 增强'
    )
    watch_parser.add_argument(
        '--model',
        default='llama3',
        help='AI 模型名称（默认：llama3）'
    )
    watch_parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='检查间隔（秒，默认：5）'
    )
    
    # init 命令
    init_parser = subparsers.add_parser('init', help='初始化配置')
    init_parser.add_argument(
        '--project', '-p',
        required=True,
        help='项目名称'
    )
    init_parser.add_argument(
        '--description', '-d',
        default='',
        help='项目描述'
    )
    init_parser.add_argument(
        '--author', '-a',
        default='',
        help='作者'
    )
    init_parser.add_argument(
        '--license',
        default='MIT',
        help='许可证（默认：MIT）'
    )
    
    # template 命令
    template_parser = subparsers.add_parser('template', help='管理模板')
    template_parser.add_argument(
        'action',
        choices=['list', 'show', 'create'],
        help='模板操作'
    )
    template_parser.add_argument(
        '--name', '-n',
        help='模板名称'
    )
    
    return parser


def cmd_generate(args):
    """执行 generate 命令"""
    logger.info(f"Generating documentation from {args.input}")
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 检测语言
    if args.language == 'auto':
        lang = detect_language(args.input)
        if not lang:
            logger.error(f"Cannot detect language for {args.input}")
            return 1
    else:
        lang_map = {
            'python': Language.PYTHON,
            'javascript': Language.JAVASCRIPT,
            'bash': Language.BASH
        }
        lang = lang_map[args.language]
    
    logger.info(f"Using language: {lang.value}")
    
    # 初始化解析器
    parser = CodeParser(lang)
    
    # 解析代码
    input_path = Path(args.input)
    if input_path.is_file():
        results = [parser.parse_file(str(input_path))]
    elif input_path.is_dir():
        results = parser.parse_directory(str(input_path), recursive=args.recursive)
    else:
        logger.error(f"Input path not found: {args.input}")
        return 1
    
    # 提取注释
    extractor = CommentExtractor()
    for result in results:
        for func in result.functions:
            if func.docstring:
                func.parsed_doc = extractor.parse_docstring(func.docstring)
        for cls in result.classes:
            if cls.docstring:
                cls.parsed_doc = extractor.parse_docstring(cls.docstring)
                for method in cls.methods:
                    if method.docstring:
                        method.parsed_doc = extractor.parse_docstring(method.docstring)
    
    # AI 增强（可选）
    if args.ai:
        logger.info(f"Enhancing documentation with AI model: {args.model}")
        ai_config = AIConfig(model=args.model, local=True)
        enhancer = AIEnhancer(ai_config)
        
        for result in results:
            for func in result.functions:
                if hasattr(func, 'parsed_doc') and func.parsed_doc:
                    # 增强描述
                    if not func.parsed_doc.description:
                        func.parsed_doc.description = enhancer.enhance_description(
                            func.source_code,
                            func.docstring
                        )
                    
                    # 生成示例
                    if not func.parsed_doc.examples:
                        func.parsed_doc.examples = enhancer.generate_examples(
                            func.name,
                            [{'name': p.name, 'type': p.type} for p in func.parameters],
                            func.parsed_doc.description
                        )
    
    # 生成文档
    generator = DocumentGenerator()
    doc_content = generator.generate_api_doc(results)
    
    # 保存文档
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 根据格式保存
    if args.format == 'markdown':
        output_file = output_path / 'API.md'
        generator.save_documentation(doc_content, str(output_file))
    elif args.format == 'html':
        output_file = output_path / 'API.html'
        # TODO: HTML 格式转换
        generator.save_documentation(doc_content, str(output_file))
    elif args.format == 'json':
        output_file = output_path / 'API.json'
        # TODO: JSON 格式转换
        generator.save_documentation(doc_content, str(output_file))
    
    logger.info(f"✅ Documentation generated successfully: {output_file}")
    return 0


def cmd_watch(args):
    """执行 watch 命令"""
    logger.info(f"Watching {args.input} for changes...")
    
    try:
        from .watcher import DocumentWatcher
        
        watcher = DocumentWatcher(
            input_dir=args.input,
            output_dir=args.output,
            format=args.format,
            use_ai=args.ai,
            model=args.model
        )
        
        watcher.start()
        
    except ImportError:
        logger.error("Watcher module not available")
        return 1
    except KeyboardInterrupt:
        logger.info("Watch stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Watch failed: {e}")
        return 1


def cmd_init(args):
    """执行 init 命令"""
    logger.info(f"Initializing project: {args.project}")
    
    # 创建项目结构
    project_dir = Path(args.project)
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建 README
    readme_content = f"""# {args.project}

{args.description if args.description else 'Project description'}

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
import {args.project.lower().replace('-', '_')}

# TODO: Add usage examples
```

## API Reference

See [API.md](docs/API.md) for detailed API documentation.

## Author

{args.author if args.author else 'Unknown'}

## License

{args.license}
"""
    
    readme_path = project_dir / 'README.md'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # 创建 docs 目录
    docs_dir = project_dir / 'docs'
    docs_dir.mkdir(exist_ok=True)
    
    # 创建配置文件
    config_content = f"""# auto-document-generator 配置
project_name: {args.project}
description: {args.description}
author: {args.author}
license: {args.license}

# 生成配置
input: src/
output: docs/
format: markdown

# AI 配置
ai_enabled: false
model: llama3
"""
    
    config_path = project_dir / 'doc-gen.yaml'
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    logger.info(f"✅ Project initialized: {project_dir}")
    logger.info(f"  - Created README.md")
    logger.info(f"  - Created docs/ directory")
    logger.info(f"  - Created doc-gen.yaml")
    
    return 0


def cmd_template(args):
    """执行 template 命令"""
    if args.action == 'list':
        logger.info("Available templates:")
        logger.info("  - default (Markdown)")
        logger.info("  - python (Python specific)")
        logger.info("  - javascript (JavaScript specific)")
        logger.info("  - html (HTML output)")
        logger.info("  - minimal (Minimal documentation)")
        return 0
    
    elif args.action == 'show':
        if not args.name:
            logger.error("Template name required for 'show' action")
            return 1
        
        logger.info(f"Template: {args.name}")
        # TODO: 显示模板内容
        return 0
    
    elif args.action == 'create':
        if not args.name:
            logger.error("Template name required for 'create' action")
            return 1
        
        logger.info(f"Creating template: {args.name}")
        # TODO: 创建自定义模板
        return 0
    
    return 0


def main():
    """主入口"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 没有命令时显示帮助
    if not args.command:
        parser.print_help()
        return 0
    
    # 执行命令
    if args.command == 'generate':
        return cmd_generate(args)
    elif args.command == 'watch':
        return cmd_watch(args)
    elif args.command == 'init':
        return cmd_init(args)
    elif args.command == 'template':
        return cmd_template(args)
    else:
        logger.error(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
