# 图片转文档工具

将超长图片转换为Word或PDF格式，便于内容读取和OCR处理。

## 📋 功能特点

### ✅ 已实现
- **智能分块**：自动分割超长图片（支持10000px+高度）
- **多格式输出**：Word (.docx) 和 PDF 格式
- **保持质量**：保留原始图片质量和宽高比
- **独立环境**：Python虚拟环境，不依赖系统包

### ⏳ 待实现
- **批量处理**：支持多张图片同时转换
- **OCR集成**：直接在文档中提取文本
- **Web界面**：图形化操作界面

## 🚀 使用方法

### 1. 安装依赖
```bash
cd /home/zhaog/.openclaw/workspace/image-to-doc
python3 -m venv doc-env
source doc-env/bin/activate
pip install python-docx reportlab pillow opencv-python
```

### 2. 基本使用
```bash
# 转换为Word文档（默认）
python convert-image-to-doc.py /path/to/image.jpg ./output.docx

# 转换为PDF文档
python convert-image-to-doc.py /path/to/image.jpg ./output.pdf pdf
```

### 3. 参数说明
- **image_path**: 输入图片路径（支持PNG/JPG）
- **output_path**: 输出文档路径
- **format**: 输出格式（word 或 pdf，默认为word）

## 💡 使用场景

### 场景1：超长终端截图
- 将超长终端日志转换为可编辑的Word文档
- 便于后续的文本提取和分析

### 场景2：聊天记录截图
- 将长聊天记录转换为PDF存档
- 保持原始格式和可读性

### 场景3：网页截图
- 将长网页截图转换为文档格式
- 便于内容整理和分享

## 📊 性能指标

| 指标 | 目标 | 实际 |
|------|------|------|
| 处理速度 | < 5秒/图 | 取决于图片大小 |
| 支持格式 | PNG/JPG | ✅ |
| 最大尺寸 | 10000px+ | ✅ |
| 输出质量 | 保持原图质量 | ✅ |

## 🔧 技术实现

### 核心功能
1. **图片分割**：按指定高度自动分割超长图片
2. **Word生成**：使用python-docx库创建文档
3. **PDF生成**：使用reportlab库创建PDF
4. **质量保持**：保持原始图片的宽高比和清晰度

### 文件结构
```
image-to-doc/
├── convert-image-to-doc.py    # 主脚本
├── README.md                 # 使用说明
└── doc-env/                  # Python虚拟环境
```

## 🚀 未来计划

### 短期
- [ ] 批量处理支持
- [ ] OCR文本提取集成
- [ ] 错误处理优化

### 中期
- [ ] Web界面开发
- [ ] 移动端适配
- [ ] 云存储集成

### 长期
- [ ] 实时转换
- [ ] 多语言支持
- [ ] 与OpenClaw深度集成

---
*让超长图片变得可读！*
*创建时间：2026-03-05*