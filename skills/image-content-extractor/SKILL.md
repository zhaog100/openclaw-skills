---
name: image-content-extractor
description: 统一图片内容提取技能。智能识别终端/文档/通用模式，自动提取内容生成Markdown。
version: 2.0.0
author: miliger
created: 2026-03-06
updated: 2026-03-06
---

# 图片内容提取技能 v2.0

智能识别终端/文档/通用模式，自动提取内容生成Markdown。

## 🎯 三大模式

- **终端模式（Terminal）**：终端/命令行截图，命令高亮
- **文档模式（Document）**：文档截图，标题/列表/代码块检测
- **通用模式（General）**：各种图片，自动类型检测

## 🚀 使用方式

```bash
# 自动检测模式（推荐）
python3 scripts/extract.py /path/to/image.png

# 指定模式
python3 scripts/extract.py image.png --mode terminal|document|general

# 保存到文件
python3 scripts/extract.py image.png -o output.md

# 保存到知识库
python3 scripts/extract.py image.png -k -c testing -t "标题"

# 批量处理
python3 scripts/extract.py ./images/ --batch -k -c knowledge
```

## 🛠️ 处理流程

```
图片输入 → 模式检测 → 预处理 → 智能分块 → OCR识别 → 智能合并 → 结构分析 → Markdown输出
```

## 📁 文件结构

```
image-content-extractor/
├── scripts/extract.py          # 主入口
├── core/                       # 核心（ocr, preprocess, merge, structure）
├── modes/                      # 模式（terminal, document, general）
└── config/extractor-config.json
```

## 🔧 关键配置（extractor-config.json）

- `ocr.engine`：tesseract，支持AI降级
- `preprocessing.block_height`：2000px分块
- `structure_detection`：标题/列表/代码块/表格
- `knowledge_base.auto_index`：自动更新QMD

## ⚠️ 注意

- 图片分辨率≥1500px宽度效果最佳
- OCR引擎：Tesseract + AI备用
- 最大图片尺寸：50000px

> 详细配置选项、使用场景、更新日志见 `references/skill-details.md`
