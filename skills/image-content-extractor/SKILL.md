---
name: image-content-extractor
description: 智能图片内容提取技能。专门处理超长截图、复杂图表，自动识别结构，输出Markdown格式。
version: 1.0.0
author: miliger
created: 2026-03-06
---

# 图片内容提取技能

智能图片内容提取技能，专门用于处理超长截图、复杂图表，自动识别内容结构并输出Markdown格式。

## 🎯 核心特性

### ⭐ 智能内容识别
- **自动结构检测**：标题、段落、列表、表格、代码块
- **内容边界识别**：智能去除空白区域
- **格式保留**：保持原文排版和格式

### ⭐ 超长图片处理
- **智能分块**：基于内容边界自动分割
- **重叠处理**：智能合并重复内容
- **并行处理**：提升处理速度

### ⭐ 多格式输出
- **Markdown**：结构化Markdown格式
- **纯文本**：原始文本内容
- **JSON**：结构化数据（可选）

### ⭐ 知识库集成
- **自动分类**：根据内容自动归类
- **QMD索引**：自动更新知识库索引
- **Git提交**：版本控制集成

## 🚀 使用方式

### 基础使用
```bash
# 提取图片内容
python3 scripts/extract-content.py /path/to/image.png

# 指定输出格式
python3 scripts/extract-content.py /path/to/image.png -f markdown

# 指定输出目录
python3 scripts/extract-content.py /path/to/image.png -o /output/dir
```

### 高级使用
```bash
# 知识库集成模式
python3 scripts/extract-content.py /path/to/image.png \
    --knowledge-base \
    --category "testing" \
    --title "测试用例设计"

# 批量处理
python3 scripts/extract-content.py /path/to/images/ \
    --batch \
    --output /knowledge/dir
```

### AI调用方式
```
用户：[发送图片]
AI：[自动调用image-content-extractor] → 提取内容 → 分析结构 → 输出Markdown
```

## 🛠️ 技术实现

### 文件结构
```
image-content-extractor/
├── SKILL.md
├── README.md
├── package.json
├── install.sh
├── config/
│   └── extractor-config.json
├── scripts/
│   ├── extract-content.py      # 主提取脚本
│   ├── analyze-structure.py    # 结构分析
│   ├── merge-blocks.py         # 内容合并
│   └── knowledge-integration.py # 知识库集成
└── data/
    └── templates/              # Markdown模板
```

### 处理流程
```
1. 图片输入
   ↓
2. 智能预处理（去噪、对比度增强）
   ↓
3. 内容分块（基于内容边界）
   ↓
4. OCR识别（Tesseract + AI备用）
   ↓
5. 内容合并（智能去重）
   ↓
6. 结构分析（标题/段落/列表）
   ↓
7. Markdown生成
   ↓
8. 知识库集成（可选）
```

## 💡 使用场景

### 场景1：DeepSeek分享截图
```
用户：[发送DeepSeek分享截图]
AI：[调用extract-content] → 提取完整内容 → 生成Markdown → 保存到知识库

结果：
- 完整识别8大模块
- 自动生成标题和段落
- 保存为测试知识库文档
```

### 场景2：技术文档截图
```
用户：[发送技术文档截图]
AI：[调用extract-content] → 识别代码块 → 格式化输出

结果：
- 代码块语法高亮
- 标题层级清晰
- 表格格式保留
```

### 场景3：知识库建设
```
用户：[批量发送截图]
AI：[批量处理] → 自动分类 → 更新索引 → Git提交

结果：
- 自动识别主题分类
- 生成QMD索引
- 提交到Git仓库
```

## 🔧 配置选项

### extractor-config.json
```json
{
  "ocr": {
    "engine": "tesseract",
    "languages": ["chi_sim", "eng"],
    "fallback_to_ai": true
  },
  "preprocessing": {
    "block_height": 2000,
    "overlap_height": 100,
    "contrast_enhancement": 1.5
  },
  "structure_detection": {
    "detect_headers": true,
    "detect_lists": true,
    "detect_code_blocks": true,
    "detect_tables": true
  },
  "output": {
    "format": "markdown",
    "add_toc": true,
    "add_metadata": true
  },
  "knowledge_base": {
    "auto_index": true,
    "auto_commit": false,
    "default_category": "uncategorized"
  }
}
```

## 📈 性能指标

| 指标 | 目标 | 实际 |
|------|------|------|
| 识别准确率 | > 95% | 待测试 |
| 处理速度 | < 15秒/图 | 待测试 |
| 结构识别 | > 90% | 待测试 |
| 最大尺寸 | 50000px | ✅ |

## 🎓 最佳实践

### 1. 图片质量优化
- 分辨率 ≥ 1500px宽度
- 对比度清晰
- 避免压缩过度

### 2. 内容组织
- 识别后手动校对
- 添加适当的标题
- 补充元数据（作者、来源）

### 3. 知识库集成
- 选择合适的分类
- 添加标签和关键词
- 定期更新索引

## 🚀 未来规划

### 短期（v1.1）
- [ ] 支持PDF文件
- [ ] 批量处理优化
- [ ] 云端OCR集成

### 中期（v1.5）
- [ ] 多语言支持
- [ ] 实时预览
- [ ] 在线编辑

### 长期（v2.0）
- [ ] AI内容摘要
- [ ] 自动翻译
- [ ] 智能推荐

## 📝 更新日志

### v1.0.0 (2026-03-06)
- ✅ 初始版本发布
- ✅ Tesseract OCR集成
- ✅ 智能内容分块
- ✅ Markdown格式输出
- ✅ 知识库集成

---

*图片内容提取技能 - 让知识提取更智能*
*版本：1.0.0*
*创建时间：2026-03-06*
