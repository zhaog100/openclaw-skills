# 图片内容提取技能

智能图片内容提取技能，专门用于处理超长截图、复杂图表，自动识别内容结构并输出Markdown格式。

## 快速开始

### 安装依赖
```bash
bash install.sh
```

### 基础使用
```bash
# 提取图片内容
python3 scripts/extract-content.py /path/to/image.png

# 保存到知识库
python3 scripts/extract-content.py /path/to/image.png -k -c testing -t "测试用例设计"
```

## 核心特性

✅ **智能内容识别** - 自动检测标题、段落、列表、代码块
✅ **超长图片处理** - 智能分块，自动合并
✅ **多格式输出** - Markdown、纯文本、JSON
✅ **知识库集成** - 自动更新索引

## 使用场景

- DeepSeek分享截图提取
- 技术文档数字化
- 知识库建设
- 批量图片处理

## 文档

详细文档请查看 [SKILL.md](./SKILL.md)

---
版本: 1.0.0
创建: 2026-03-06
