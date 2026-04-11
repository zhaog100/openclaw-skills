# QR Code 生成 API - 二维码生成工具

**调研时间**: 2026-04-11 16:45
**API名称**: QR Code Generator
**官网**: https://github.com/public-apis/public-apis
**维护**: 小米椒 🌶️‍🔥

---

## 📊 基本信息

| 项目 | 信息 |
|------|------|
| 核心功能 | 生成二维码图片 |
| 服务示例 | goqr.me, qrserver.com, qr-code-styling |
| 认证方式 | 大部分无需API Key |
| 输出格式 | PNG, SVG, EPS |
| 费用 | 大部分免费 |

---

## 🎯 核心功能

### 1. 二维码生成
- **文本转二维码**: 任意文本/URL生成二维码
- **自定义尺寸**: 支持多种尺寸（100x100到2000x2000）
- **自定义颜色**: 前景色/背景色自定义
- **Logo嵌入**: 在二维码中心嵌入Logo

### 2. 高级功能
- **容错率**: L/M/Q/H四级容错
- **边距设置**: 自定义二维码边距
- **格式选择**: PNG/SVG/EPS格式
- **批量生成**: 一次性生成多个二维码

### 3. 样式定制
- **圆角**: 圆角二维码
- **渐变**: 渐变色二维码
- **形状**: 自定义二维码点形状
- **背景**: 自定义背景图

---

## 💰 定价方案（示例服务）

| 服务 | 免费层 | 付费层 |
|------|--------|--------|
| **goqr.me** | 无限免费 | 无付费层 |
| **qrserver.com** | 无限免费 | 无付费层 |
| **qr-code-styling** | 基础免费 | $9/月起 |
| **quickchart.io** | 500/月 | $10/月起 |

---

## 🧧 使用方法

### 1. goqr.me（无需API Key）
```python
import requests

# 生成二维码
url = "https://api.qrserver.com/v1/create-qr-code/"
params = {
    'size': '300x300',
    'data': 'https://example.com/product/123',
    'margin': '10',
    'format': 'png'
}
response = requests.get(url, params=params)

# 保存图片
with open('qrcode.png', 'wb') as f:
    f.write(response.content)
print("二维码已保存为 qrcode.png")
```

### 2. qrserver.com（无需API Key）
```python
import requests

# 生成带Logo的二维码
url = "https://api.qrserver.com/v1/create-qr-code/"
params = {
    'size': '300x300',
    'data': 'https://example.com/product/123',
    'margin': '10',
    'format': 'png',
    'color': '000000',  # 黑色
    'bgcolor': 'ffffff',  # 白色
    'qzone': '1'  # 边距
}
response = requests.get(url, params=params)

# 保存图片
with open('qrcode_custom.png', 'wb') as f:
    f.write(response.content)
print("自定义二维码已保存")
```

### 3. Python本地生成（qrcode库）
```python
import qrcode

# 创建二维码
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data('https://example.com/product/123')
qr.make(fit=True)

# 生成图片
img = qr.make_image(fill_color="black", back_color="white")
img.save('qrcode_local.png')
print("本地二维码已生成")
```

---

## 🚀 集成建议

### 场景1：产品推广二维码
- **输入**: 产品链接/闲鱼商品链接
- **处理**: 生成产品推广二维码
- **输出**: 二维码图片
- **应用**:
  - 小红书笔记配图
  - 产品包装二维码
  - 线下活动推广

### 场景2：联系方式二维码
- **输入**: 微信/电话/邮箱
- **处理**: 生成联系方式二维码
- **输出**: 二维码图片
- **应用**:
  - 个人名片二维码
  - 客服联系方式
  - 私域流量引流

### 场景3：活动二维码
- **输入**: 活动页面URL
- **处理**: 生成活动二维码
- **输出**: 带Logo的二维码
- **应用**:
  - 营销活动二维码
  - 优惠券领取
  - 会员注册引流

---

## ⚠️ 注意事项

### 二维码质量
- **容错率**: 选择合适容错率（H级适合带Logo）
- **尺寸**: 最小尺寸保证可扫描（建议≥200x200）
- **对比度**: 保证前景/背景色对比度

### 安全性
- **恶意链接**: 二维码可能隐藏恶意URL
- **链接审核**: 生成前审核目标URL
- **HTTPS优先**: 使用HTTPS链接

---

## 📋 集成清单

### 第1步：选择二维码服务
- [ ] 选择服务（goqr.me/qrserver/本地生成）
- [ ] 测试API可用性
- [ ] 确认免费层限制

### 第2步：编写生成脚本
- [ ] 编写二维码生成函数
- [ ] 编写批量生成函数
- [ ] 测试准确性

### 第3步：集成到工作流
- [ ] 集成到产品推广流程
- [ ] 集成到活动营销流程
- [ ] 测试准确性

---

## ✅ 已完成

- [x] API文档调研
- [x] 使用方法整理
- [x] 集成场景设计
- [x] 集成清单编写

---

## ⏳ 待完成

- [ ] 选择二维码服务
- [ ] 安装qrcode库（本地生成）
- [ ] 编写测试脚本
- [ ] 执行测试验证
- [ ] 集成到工作流

---

## 📚 相关资源

- **goqr.me**: https://goqr.me/
- **qrserver.com**: https://qrserver.com/
- **qrcode (Python)**: https://pypi.org/project/qrcode/
- **qr-code-styling**: https://qr-code-styling.com/
- **Public APIs**: https://github.com/public-apis/public-apis

---

*小米椒 🌶️‍🔥 | 2026-04-11*
