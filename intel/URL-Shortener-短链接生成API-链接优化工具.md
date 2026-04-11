# URL Shortener 短链接生成 API - 链接优化工具

**调研时间**: 2026-04-11 16:40
**API名称**: URL Shortener
**官网**: https://github.com/public-apis/public-apis
**维护**: 小米椒 🌶️‍🔥

---

## 📊 基本信息

| 项目 | 信息 |
|------|------|
| 核心功能 | 长链接转短链接 |
| 服务示例 | bit.ly, tinyurl.com, is.gd |
| 认证方式 | 部分需要API Key，部分无需认证 |
| 语言支持 | REST API（所有语言可用） |
| 费用 | 大部分免费 |

---

## 🎯 核心功能

### 1. 短链接生成
- **长链接转短**: 将长URL转换为短URL
- **自定义别名**: 自定义短链接后缀
- **批量生成**: 一次性生成多个短链接
- **过期设置**: 设置短链接有效期

### 2. 链接管理
- **链接统计**: 查看点击次数、来源地区
- **链接编辑**: 修改目标URL
- **链接删除**: 删除不再需要的短链接
- **链接分组**: 按项目/活动分组管理

### 3. 数据分析
- **点击统计**: 总点击数、日点击数
- **来源分析**: 来源网站、来源APP
- **地域分析**: 用户所在地区
- **设备分析**: 手机/PC/平板比例

---

## 💰 定价方案（示例服务）

| 服务 | 免费层 | 付费层 |
|------|--------|--------|
| **bit.ly** | 1000链接/月 | $8/月起 |
| **tinyurl.com** | 无限免费 | 无付费层 |
| **is.gd** | 无限免费 | 无付费层 |
| **cutt.ly** | 1000链接/月 | $12/月起 |

---

## 🧧 使用方法

### 1. is.gd（无需API Key）
```python
import requests

# 生成短链接
url = "https://is.gd/create.php"
params = {
    'format': 'json',
    'url': 'https://example.com/very/long/url/path'
}
response = requests.get(url, params=params)
short_url = response.json()['shorturl']
print(f"短链接: {short_url}")
```

### 2. tinyurl.com（无需API Key）
```python
import requests

# 生成短链接
url = "https://tinyurl.com/api-create.php"
params = {
    'url': 'https://example.com/very/long/url/path'
}
response = requests.get(url, params=params)
short_url = response.text
print(f"短链接: {short_url}")
```

### 3. bit.ly（需要API Key）
```python
import requests

# 生成短链接
url = "https://api-ssl.bitly.com/v4/shorten"
headers = {
    'Authorization': 'Bearer YOUR_BITLY_TOKEN',
    'Content-Type': 'application/json'
}
data = {
    'long_url': 'https://example.com/very/long/url/path'
}
response = requests.post(url, headers=headers, json=data)
short_url = response.json()['link']
print(f"短链接: {short_url}")
```

---

## 🚀 集成建议

### 场景1：小红书笔记链接
- **输入**: 1688产品长链接
- **处理**: 转换为短链接
- **输出**: 短链接（适合小红书简介）
- **应用**:
  - 小红书简介链接优化
  - 闲鱼商品链接分享
  - 社交媒体链接分享

### 场景2：活动跟踪
- **输入**: 活动页面URL
- **处理**: 生成带跟踪参数的短链接
- **输出**: 短链接 + 点击统计
- **应用**:
  - 营销活动跟踪
  - 渠道效果分析
  - 转化率统计

### 场景3：批量链接管理
- **输入**: 多个产品链接
- **处理**: 批量生成短链接
- **输出**: 短链接列表
- **应用**:
  - 产品目录链接管理
  - 多平台链接统一
  - 链接过期管理

---

## ⚠️ 注意事项

### 链接稳定性
- **免费服务**: 可能不稳定，建议付费服务用于生产
- **链接过期**: 部分服务链接会过期，注意有效期
- **服务关闭**: 短链接服务可能关闭，建议自建服务

### 安全性
- **恶意链接**: 短链接可能隐藏恶意URL
- **链接审核**: 生成前审核目标URL
- **HTTPS优先**: 使用HTTPS短链接服务

---

## 📋 集成清单

### 第1步：选择短链接服务
- [ ] 选择服务（is.gd/tinyurl/bit.ly）
- [ ] 测试API可用性
- [ ] 确认免费层限制

### 第2步：编写生成脚本
- [ ] 编写短链接生成函数
- [ ] 编写批量生成函数
- [ ] 测试准确性

### 第3步：集成到工作流
- [ ] 集成到小红书内容发布
- [ ] 集成到闲鱼商品上架
- [ ] 测试准确性

---

## ✅ 已完成

- [x] API文档调研
- [x] 使用方法整理
- [x] 集成场景设计
- [x] 集成清单编写

---

## ⏳ 待完成

- [ ] 选择短链接服务
- [ ] 编写测试脚本
- [ ] 执行测试验证
- [ ] 集成到工作流

---

## 📚 相关资源

- **is.gd**: https://is.gd/
- **tinyurl**: https://tinyurl.com/
- **bit.ly**: https://bitly.com/
- **cutt.ly**: https://cutt.ly/
- **Public APIs**: https://github.com/public-apis/public-apis

---

*小米椒 🌶️‍🔥 | 2026-04-11*
