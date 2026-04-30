# Image Compressor API 调研报告 - 图片压缩转换

**调研时间**: 2026-04-11 14:45
**API名称**: Smart Adaptive Ultra-Fast Image Compressor & Converter
**官网**: https://rapidapi.com/vintarok-vintarok-default/api/smart-adaptive-ultra-fast-image-compressor-converter
**GitHub**: https://github.com/AndriiPiatakha/image-compressor-converter
**维护**: 小米椒 🌶️‍🔥

---

## 📊 基本信息

| 项目 | 信息 |
|------|------|
| 核心功能 | 图片压缩、调整大小、格式转换（AI自适应调优） |
| 支持格式 | JPEG, PNG, WebP, GIF, BMP, XPM |
| 集成方式 | REST API（multipart/form-data） |
| 认证方式 | 代理密钥（Header或Body） |
| 引擎 | 专有原生引擎（高性能） |
| 安全性 | 无状态（内存处理），无数据存储 |

---

## 🎯 核心特性

### 1. 极速处理
- 毫秒级响应
- 原生优化引擎
- 适合生产级负载

### 2. 多格式支持
- **输入**: 所有常见图片格式
- **输出**: JPEG, PNG, WebP, GIF, BMP, XPM
- **自动检测**: 默认WebP（现代浏览器），优雅降级

### 3. 灵活参数
- **分辨率控制**: max_width, max_height（像素级）
- **质量控制**: quality（0-100，默认82）
- **格式控制**: format（auto/jpeg/png/webp/lossless）
- **调整模式**: mode（fit/fill/stretch）
- **自适应缩放**: 自动平衡质量与文件大小

### 4. 智能增强
- **EXIF自动旋转**: 自动修复手机拍照的横向图片
- **预测性控制**: 每个输出都是确定性的
- **AI自适应**: 自动平衡视觉质量与文件大小

### 5. 安全隔离
- **无状态**: 不存储任何文件
- **内存处理**: 所有操作在内存中完成
- **零外部依赖**: 无第三方库或系统调用

---

## 🔧 API使用方法

### cURL
```bash
# 基础压缩
curl -X POST https://api.yourdomain.com/image-compressor/v1/compress.php \
  -F "image=@/path/to/image.jpg" \
  -F "quality=80" \
  -F "format=webp" \
  -F "return=json"

# 调整大小（固定宽度）
curl -X POST https://api.yourdomain.com/image-compressor/v1/compress.php \
  -F "image=@/path/to/image.jpg" \
  -F "max_width=1200" \
  -F "quality=80"

# 调整大小（固定高度）
curl -X POST https://api.yourdomain.com/image-compressor/v1/compress.php \
  -F "image=@/path/to/image.jpg" \
  -F "max_height=1600" \
  -F "quality=80"

# 填充模式（cover）
curl -X POST https://api.yourdomain.com/image-compressor/v1/compress.php \
  -F "image=@/path/to/image.jpg" \
  -F "mode=fill" \
  -F "quality=80"

# 拉伸模式
curl -X POST https://api.yourdomain.com/image-compressor/v1/compress.php \
  -F "image=@/path/to/image.jpg" \
  -F "mode=stretch" \
  -F "quality=80"
```

### Python
```python
import requests

API_URL = "https://api.yourdomain.com/image-compressor/v1/compress.php"

# 基础压缩
files = {'image': open('input.jpg', 'rb')}
data = {'format': 'webp', 'quality': '80', 'return': 'json'}

response = requests.post(API_URL, files=files, data=data)
print(response.json())
```

### Node.js
```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const form = new FormData();
form.append('image', fs.createReadStream('Krakow.jpg'));
form.append('quality', '80');
form.append('format', 'webp');

axios.post('https://api.yourdomain.com/image-compressor/v1/compress.php', form, {
  headers: form.getHeaders()
})
.then(res => console.log(res.data))
.catch(err => console.error(err.response.data));
```

### PHP
```php
$files = ['image' => new CURLFile('Krakow.jpg', 'image/jpeg')];
$data = ['format' => 'webp', 'quality' => '80', 'return' => 'json'];

$ch = curl_init('https://api.yourdomain.com/image-compressor/v1/compress.php');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
curl_setopt($ch, CURLOPT_SAFE_UPLOAD, true);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
curl_close($ch);

$res = json_decode($response, true);
console.log($res);
```

---

## ⚙️ 参数选项

### 基础参数
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| image | file | ✅ | 图片文件（multipart/form-data） |
| return | string | ❌ | 响应类型：json或file（默认json） |

### 可选参数
| 参数 | 类型 | 范围 | 说明 |
|------|------|--------|------|
| max_width | integer | - | 最大输出宽度（像素），留空保持原宽 |
| max_height | integer | - | 最大输出高度（像素），留空保持原高 |
| quality | integer | 0-100 | 压缩级别（默认82），越高文件越小但质量越低 |
| format | string | auto/jpeg/png/webp/lossless | 输出格式（默认auto，通常WebP） |
| mode | string | fit/fill/stretch | 调整模式 |

### 调整模式说明
| 模式 | 说明 | 使用场景 |
|------|--------|------|
| fit | 等比缩放 | 保持宽高比，适应边界 |
| fill | 填充 | 填充到指定尺寸，可能留白 |
| stretch | 拉伸 | 拉伸到指定尺寸，可能变形 |

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
      "quality": 80,
      "compression_percent": 84.3
    }
  },
  "file_base64": "UklGRiZAAABXRUJQVlA4WAoAAAAA..."
}
```

### 错误代码
| 状态 | 代码 | 说明 |
|------|------|------|
| 400 | - | 图片未上传或无效 |
| 403 | - | 代理密钥（API Secret）无效或不正确 |
| 415 | - | 编码失败（格式不支持或损坏） |
| 500 | - | 服务器配置错误 |

---

## 💰 定价模式

| 计划 | 说明 |
|------|------|
| Free | 个人和实验性使用仅 |
| Pro | 商业、业务、创收项目所需 |
| Ultra | 最大吞吐量需求 |

- **订阅**: RapidAPI平台订阅
- **免费限制**: 需查看RapidAPI定价页面
- **企业级**: 生产环境适用

---

## 🚀 集成建议

### 场景1：小红书图片压缩
- **输入**: 9:16竖版产品图
- **处理**: `max_width=1080`（保持竖版比例）
- **输出**: WebP格式（高压缩比，现代浏览器支持）
- **优势**: 文件更小，加载更快，移动端友好

### 场景2：闲鱼商品图优化
- **输入**: 方形产品图
- **处理**: `mode=fit` + `quality=75`（平衡质量与大小）
- **输出**: JPEG格式（广泛兼容）
- **优势**: 保持清晰度，显著减小文件大小

### 场景3：批量处理脚本
```python
#!/usr/bin/env python3
import os
import requests

API_URL = "https://api.yourdomain.com/image-compressor/v1/compress.php"
INPUT_DIR = "products/raw"
OUTPUT_DIR = "products/optimized"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir(INPUT_DIR):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, f"opt_{filename}")

        files = {'image': open(input_path, 'rb')}
        data = {'format': 'webp', 'quality': '75', 'return': 'json'}

        response = requests.post(API_URL, files=files, data=data)
        result = response.json()

        if result['ok']:
            # 保存base64图片
            import base64
            image_data = base64.b64decode(result['file_base64'])
            with open(output_path, 'wb') as f:
                f.write(image_data)

            original_size = result['meta']['input']['size_bytes']
            compressed_size = result['meta']['output']['size_bytes']
            compression = result['meta']['output']['compression_percent']

            print(f"✅ {filename}: {original_size/1024:.1f}KB → {compressed_size/1024:.1f}KB ({compression:.1f}%)")
        else:
            print(f"❌ {filename}: 失败")
```

### 场景4：智能质量平衡
- **输入**: 高清图片
- **处理**: `quality=82`（默认值，AI自适应调优）
- **输出**: AI平衡后的优化图片
- **优势**: 自动在质量与文件大小间找到最佳平衡点

---

## ⚠️ 注意事项

### 1. 认证方式
- **代理密钥**: 需要从RapidAPI获取
- **Header方式**: 可能在Header中传递
- **参数方式**: 可能需要在Body中传递

### 2. 文件大小限制
- 需确认单张图片最大限制
- 超大文件可能被拒绝

### 3. 质量参数
- **默认值**: 82（中等质量）
- **高压缩**: quality=60（文件更小，质量下降）
- **高保真**: quality=90+（文件较大，质量提升）

### 4. 格式选择
- **WebP**: 推荐现代Web使用（高压缩比）
- **JPEG**: 通用兼容（广泛支持）
- **PNG**: 无损（文件较大）

---

## ✅ 已完成

- [x] API文档调研
- [x] 参数整理
- [x] 使用方法编写
- [x] 集成场景设计

---

## ⏳ 待完成

- [ ] 获取API密钥（RapidAPI订阅）
- [ ] 编写测试脚本
- [ ] 执行测试验证
- [ ] 集成到工作流程

---

*小米椒 🌶️‍🔥 | 2026-04-11*
