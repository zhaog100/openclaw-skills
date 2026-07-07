# Poof API 调研报告 - 背景移除

**调研时间**: 2026-04-11 14:05 → 14:23（更新）
**API名称**: Poof - Background Removal API
**官网**: https://poof.bg/
**文档**: https://docs.poof.bg/
**Dashboard**: https://dash.poof.bg
**GitHub**: https://github.com/poof-bg
**维护**: 小米椒 🌶️‍🔥

---

## 📊 基本信息

| 项目 | 信息 |
|------|------|
| 核心功能 | 图片背景移除（AI驱动） |
| 支持格式 | PNG（透明）、JPEG、WebP |
| 集成方式 | REST API + Python SDK + TypeScript SDK |
| 认证方式 | API Key（Header: x-api-key） |
| API Key格式 | `pk_xxxxxxxx`（官家确认） |
| API端点 | `https://api.poof.bg/v1/remove` |
| 账户查询 | `https://api.poof.bg/v1/me` |

---

## 🎯 核心特性

### 1. 精准边缘检测
- AI处理头发、皮毛、透明度、复杂边缘
- 像素级精准度

### 2. 快速处理
- 亚秒级响应时间
- 可处理数千张图片

### 3. 灵活输出
- PNG（透明背景）
- JPEG（自定义背景色）
- WebP（Web优化）
- 支持裁剪、调整大小、自定义

### 4. 简单集成
- 单一端点
- 单一API Key
- Python/TypeScript SDK可用

---

## 🔧 API使用方法

### cURL
```bash
curl -X POST https://api.poof.bg/v1/remove \
  -H "x-api-key: pk_YOUR_API_KEY" \
  -F "image_file=@photo.jpg" \
  -o result.png
```

### Python SDK
```bash
# 安装
pip install poofbg

# 使用
from poofbg import Poof

client = Poof(api_key="pk_YOUR_API_KEY")

# 从文件
result = client.remove("input.jpg")
result.save("output.png")

# 从bytes
with open("input.jpg", "rb") as f:
    result = client.remove(f.read())
    result.save("output.png")
```

### TypeScript SDK
```bash
# 安装
npm install @poof-bg/js

# 使用
import { Poof } from '@poof-bg/js';

const poof = new Poof({ apiKey: 'pk_YOUR_API_KEY' });
```

---

## ⚙️ 参数选项

### 基础参数
| 参数 | 类型 | 说明 |
|------|------|------|
| image_file | file | 图片文件（必需） |
| x-api-key | header | API密钥（必需，格式：pk_xxxxxxxx） |

### 可选参数
| 参数 | 类型 | 说明 |
|------|------|------|
| format | string | 输出格式：png/jpeg/webp |
| channels | string | 颜色通道：rgb/rgba |
| bg_color | string | 背景色（hex，如#ffffff） |
| size | string | 尺寸：preview（预览，更快更少积分） |
| crop | boolean | 裁剪到主体边界 |

### 常用示例
```bash
# JPEG白色背景
curl -X POST https://api.poof.bg/v1/remove \
  -H "x-api-key: pk_YOUR_API_KEY" \
  -F "image_file=@photo.jpg" \
  -F "format=jpg" \
  -F "channels=rgb" \
  -F "bg_color=#ffffff" \
  -o result.jpg

# 预览尺寸（更快，更少积分）
curl -X POST https://api.poof.bg/v1/remove \
  -H "x-api-key: pk_YOUR_API_KEY" \
  -F "image_file=@photo.jpg" \
  -F "size=preview" \
  -o preview.png

# 裁剪到主体边界
curl -X POST https://api.poof.bg/v1/remove \
  -H "x-api-key: pk_YOUR_API_KEY" \
  -F "image_file=@photo.jpg" \
  -F "crop=true" \
  -o cropped.png
```

---

## 📊 账户信息API

### 查询账户余额
```bash
curl https://api.poof.bg/v1/me \
  -H "x-api-key: pk_YOUR_API_KEY"
```

### 响应字段
| 字段 | 类型 | 说明 |
|------|------|------|
| organizationId | string | 唯一组织标识符 |
| plan | string | 当前订阅计划（Free/Pro/Enterprise） |
| maxCredits | integer | 当前计费周期总积分 |
| usedCredits | integer | 当前计费周期已用积分 |
| autoRechargeThreshold | integer | 自动充值阈值（null表示禁用） |

---

## 🔒 安全注意事项

1. **API Key保密**:
   - 像密码一样对待
   - 不提交到版本控制
   - 不在客户端代码暴露

2. **错误处理**:
   - 401: 认证失败（API Key无效）
   - 413: 图片太大
   - 429: 请求超限
   - 500: 内部服务器错误

---

## 🚀 集成建议

### 场景1：1688产品图优化
- **输入**: 供应商原始产品图（可能有复杂背景）
- **处理**: 批量调用Poof API去背景
- **输出**: 透明PNG或白底JPEG
- **适用**: 小红书首图、闲鱼商品图

### 场景2：小红书图片优化
- **输入**: 9:16竖版图
- **处理**: `size=preview` + `crop=true`
- **优势**: 更快、更少积分、自动裁剪
- **适用**: 封面图、内页图

### 场景3：批量处理脚本
```python
#!/usr/bin/env python3
import os
from poofbg import Poof

client = Poof(api_key="pk_YOUR_API_KEY")

input_dir = "products/raw"
output_dir = "products/processed"

for filename in os.listdir(input_dir):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        result = client.remove(input_path)
        result.save(output_path)

        print(f"Processed: {filename}")
```

---

## ✅ 已确认

- [x] API文档调研
- [x] 使用方法整理
- [x] 集成场景设计
- [x] API Key格式确认（pk_开头）
- [x] 官家提供API Key

---

## ⏳ 待完成

- [ ] 编写测试脚本（使用官家提供的API Key）
- [ ] 执行测试验证
- [ ] 集成到工作流程

---

*小米椒 🌶️‍🔥 | 2026-04-11*
