# Image Compressor API 集成说明 - 图片压缩转换

**更新时间**: 2026-04-11 15:15
**API名称**: Image Compressor API（Smart Adaptive Ultra-Fast）
**官网**: https://rapidapi.com/vintarok-vintarok-default/api/smart-adaptive-ultra-fast-image-compressor-converter
**GitHub**: https://github.com/AndriiPiatakha/image-compressor-converter
**维护**: 小米椒 🌶️‍🔥

---

## 📊 API概览

| 项目 | 信息 |
|------|------|
| 核心功能 | 智能压缩、转换、优化图片（AI自适应调优） |
| 引擎 | 专有原生引擎（高性能） |
| 支持格式 | JPEG, PNG, WebP, GIF, BMP, XPM |
| 安全性 | 无状态（内存处理），无数据存储 |
| 认证 | 代理密钥（RapidAPI） |

---

## 🎯 核心特性

### 1. 极速处理
- 毫秒级响应
- 原生优化引擎
- 适合生产级负载

### 2. AI自适应调优
- 自动平衡质量与文件大小
- 智能压缩率预测
- 视觉质量保证

### 3. 灵活输出
- 多格式转换（JPEG/PNG/WebP）
- 尺寸控制（max_width/max_height）
- 调整模式（fit/fill/stretch）
- 格式自适应（auto检测WebP）

---

## 🧧 API集成状态

### 已完成
- [x] API文档调研
- [x] 参数说明整理
- [x] 使用方法编写（cURL/Python/Node.js/PHP）
- [x] 集成场景设计（小红书/闲鱼）
- [x] 测试脚本编写

### 待完成
- [ ] 准备测试图片（products/raw/xiaohongshu_test.jpg）
- [ ] 配置环境变量（IMAGE_COMPRESSOR_API_KEY）
- [ ] 执行测试验证
- [ ] 集成到工作流程

---

## 💡 应用场景

### 场景1：小红书图片优化
- **输入**: 9:16竖版产品图
- **处理**: `format=webp`, `quality=75`
- **输出**: 自动优化图片，文件更小，加载更快
- **优势**: 移动端友好，小红书加载速度提升

### 场景2：闲鱼商品图优化
- **输入**: 方形产品图
- **处理**: `mode=fit`, `quality=75`
- **输出**: WebP格式，平衡质量与大小
- **优势**: 清晰度与文件大小平衡

### 场景3：批量处理脚本
```python
#!/usr/bin/env python3
import os
import requests

API_URL = "https://api.yourdomain.com/image-compressor/v1/compress.php"

INPUT_DIR = "products/raw"
OUTPUT_DIR = "products/compressed"

for filename in os.listdir(INPUT_DIR):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, f"opt_{filename}")

        files = {'image': open(input_path, 'rb')}
        data = {
            'format': 'webp',
            'quality': '75',
            'return': 'json'
        }

        response = requests.post(API_URL, files=files, data=data)
        result = response.json()

        if result['ok']:
            import base64
            image_data = base64.b64decode(result['file_base64'])
            with open(output_path, 'wb') as f:
                f.write(image_data)

            original_size = result['meta']['input']['size_bytes']
            compressed_size = result['meta']['output']['size_bytes']
            compression = result['meta']['output']['compression_percent']

            print(f"✅ {filename}: {original_size/1024:.1f}KB → {compressed_size/1024:.1f}KB ({compression:.1f}%)")
```

---

## ⚙️ 参数配置

### 基础参数
| 参数 | 类型 | 必需 | 说明 |
|------|--------|--------|------|
| image | file | ✅ | 图片文件（multipart/form-data） |
| return | string | ❌ | json（Base64+meta）或file（二进制） |

### 压缩控制
| 参数 | 类型 | 范围 | 说明 |
|------|--------|--------|------|
| quality | integer | 0-100 | 压缩级别（默认82，值越小文件越小） |
| format | string | - | auto/jpeg/png/webp/lossless |
| mode | string | - | fit（等比）/fill（填）/stretch（拉伸） |

### 尺寸限制
| 参数 | 类型 | 范围 | 说明 |
|------|--------|--------|------|
| max_width | integer | - | 最大输出宽度（像素），留空保持原宽 |
| max_height | integer | - | 最大输出高度（像素），留空保持原高 |

---

## 📊 响应格式

### 成功响应
```json
{
  "ok": true,
  "content_type": "image/webp",
  "filename": "compressed.webp",
  "meta": {
    "input": {
      "width": 3024,
      "height": 4032,
      "size_bytes": 1850000
    },
    "output": {
      "width": 1200,
      "height": 1600,
      "size_bytes": 290000,
      "format": "webp",
      "quality": 75,
      "compression_percent": 84.3
    }
  },
  "file_base64": "UklGRiZAAABXRUJQVlA4WAoAAAA..."
}
```

### 错误处理
- 400错误：图片未上传或无效
- 403错误：API密钥无效或不正确
- 415错误：编码失败（格式不支持或损坏）
- 500错误：服务器配置错误

---

## 🔒 安全注意事项

### API Key管理
- **获取方式**: 访问 https://rapidapi.com/
- **格式**: sk_开头（如：sk_live_...）
- **安全原则**: 像密码一样对待，不提交到版本控制
- **环境变量**: 使用 `IMAGE_COMPRESSOR_API_KEY` 存储
- **有效期**: 需查看RapidAPI定价页面

### 请求限制
- **免费层**: 20,000请求/月
- **建议**: 批量调用 + 缓存机制
- **速率限制**: 50请求/分钟（Basic层）

---

## ✅ 测试准备

### 测试图片
- **路径**: `products/raw/xiaohongshu_test.jpg`
- **尺寸**: 1080x1080（1:1）
- **大小**: 约500KB
- **格式**: JPEG

### 测试场景
1. **基础压缩**: WebP格式，quality=80
2. **固定宽度**: max_width=1080，保持竖版比例
3. **批量优化**: quality=75，WebP格式

---

## ⏳ 待集成

### 测试阶段
- [ ] 准备测试图片
- [ ] 配置环境变量
- [ ] 执行测试脚本
- [ ] 验证响应格式
- [ ] 测试不同参数组合

### 工作流集成
- [ ] 集成到xiaohongshu-ops-skill
- [ ] 添加到定图流程
- [ ] 添加到发布流程
- [ ] 添加到数据复盘

---

## 📋 检查清单

### API Key
- [ ] 注册RapidAPI账户
- [ ] 获取API Key（sk_开头）
- [ ] 配置环境变量

### 功能验证
- [ ] 基础压缩测试
- [ ] 格式转换测试
- [ ] 尺寸控制测试
- [ ] 质量调优测试

---

*小米椒 🌶️‍🔥 | 2026-04-11*
