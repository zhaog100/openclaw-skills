#!/usr/bin/env python3
"""
Auto Document Generator - 自动文档生成器
从代码自动生成技术文档

版本: v1.0.0
作者: 思捷娅科技 (SJYKJ)
许可证: MIT
"""

__version__ = "1.0.0"
__author__ = "思捷娅科技 (SJYKJ)"
__license__ = "MIT"

from .parser import CodeParser, ParseTree
from .extractor import CommentExtractor, ParsedDocstring
from .generator import DocumentGenerator
from .enhancer import AIEnhancer
from .converter import DocumentConverter
from .watcher import DocumentWatcher

__all__ = [
    "CodeParser",
    "ParseTree", 
    "CommentExtractor",
    "ParsedDocstring",
    "DocumentGenerator",
    "AIEnhancer",
    "DocumentConverter",
    "DocumentWatcher",
]
