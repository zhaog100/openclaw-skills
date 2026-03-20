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

---

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者：小米辣 (PM + Dev)

**商业使用授权**：
- 个人/开源：免费
- 小微企业（<10 人）：¥999/年
- 中型企业（10-50 人）：¥4,999/年
- 大型企业（>50 人）：¥19,999/年
- 源码买断：¥99,999 一次性

详情请查看：[LICENSE](../../LICENSE)
