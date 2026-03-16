#!/usr/bin/env python3
"""
Auto Document Generator Setup

自动文档生成器安装脚本
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="auto-document-generator",
    version="1.0.0",
    author="思捷娅科技 (SJYKJ)",
    author_email="contact@sjykj.com",
    description="自动从代码生成技术文档，支持多种语言和AI增强",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zhaog100/openclaw-skills",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
    ],
    python_requires=">=3.8",
    install_requires=[
        "tree-sitter>=0.20.0",
        "tree-sitter-python>=0.20.0",
        "tree-sitter-javascript>=0.20.0",
        "tree-sitter-bash>=0.20.0",
        "jinja2>=3.0.0",
        "markdown>=3.4.0",
        "pygments>=2.15.0",
        "watchdog>=3.0.0",
    ],
    extras_require={
        "ai": ["ollama>=0.1.0"],
        "pdf": ["weasyprint>=60.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-benchmark>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "auto-doc-generator=auto_doc_generator.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
