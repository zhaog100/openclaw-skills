---
name: auto-document-generator
description: 自动从代码生成技术文档，支持 Python/JavaScript/Bash，AI 增强文档质量
version: "1.0.0"
author: 思捷娅科技 (SJYKJ)
license: MIT
---

# Auto Document Generator - 自动文档生成器

自动从代码生成技术文档，保持文档与代码同步。

## 🎯 核心功能

- **多语言支持**：Python, JavaScript, Bash
- **多种注释风格**：Google, Numpy, Sphinx, JSDoc
- **多格式输出**：Markdown, HTML, PDF
- **AI增强**：改进描述、生成示例、补充参数说明
- **自动更新**：文件监听、Git Hooks、CI/CD集成

## 🚀 使用方式

```bash
# 生成 API 文档
auto-doc-generator generate --input src/ --output docs/

# 启用 AI 增强
auto-doc-generator generate --input src/ --ai --model llama3

# 监听文件变更
auto-doc-generator watch --input src/ --output docs/

# 初始化配置
auto-doc-generator init --project myproject
```

## 📋 命令参考

| 命令 | 说明 | 关键参数 |
|------|------|----------|
| `generate` | 生成文档 | `--input`, `--output`, `--format`, `--ai`, `--template`, `--language` |
| `watch` | 监听变更 | `--input`, `--output`, `--interval` |
| `init` | 初始化配置 | `--project`, `--description`, `--author` |
| `template` | 管理模板 | `list`, `show`, `create` |

## 🎨 内置模板

`default` | `python` | `javascript` | `html` | `minimal`（支持自定义Jinja2模板）

## 📦 依赖

**核心**：tree-sitter, jinja2, markdown, pygments, watchdog
**可选**：ollama（本地AI）, weasyprint（PDF）, openai（云端AI）

## ⚠️ 故障排除

- tree-sitter失败 → `pip install tree-sitter-python`
- AI增强失败 → 确保Ollama运行 `ollama pull llama3`
- 文档为空 → 检查代码注释完整性

> 详细代码示例、配置模板、性能指标见 `references/skill-details.md`
