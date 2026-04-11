# Requests HTTP请求库 - API调用工具

**调研时间**: 2026-04-11 16:03
**库名称**: Requests
**官网**: https://requests.readthedocs.io/
**GitHub**: https://github.com/psf/requests
**PyPI**: https://pypi.org/project/requests/
**维护**: 小米椒 🌶️‍🔥

---

## 📊 基本信息

| 项目 | 信息 |
|------|------|
| 核心功能 | HTTP请求库 |
| 开发方 | Kenneth Reitz |
| 许可证 | Apache 2.0 License（完全开源） |
| HTTP方法 | GET, POST, PUT, DELETE, HEAD, OPTIONS, PATCH |
| 语言支持 | Python |
| 费用 | 完全免费（Apache 2.0开源） |

---

## 🎯 核心功能

### 1. HTTP请求
- **GET请求**: 获取数据
- **POST请求**: 提交数据
- **PUT/PATCH**: 更新数据
- **DELETE请求**: 删除数据
- **HEAD请求**: 获取元数据

### 2. 会话管理
- **Cookies**: 自动处理Cookie
- **Session**: 保持会话状态
- **重定向**: 自动跟随重定向
- **超时设置**: 连接/读取超时控制

### 3. 认证支持
- **Basic认证**: HTTP Basic Auth
- **Digest认证**: HTTP Digest Auth
- **OAuth**: OAuth 1.0/2.0支持
- **API Key**: X-API-Key头等自定义认证

### 4. 数据处理
- **JSON支持**: 自动解析JSON响应
- **表单数据**: 支持表单编码
- **文件上传**: 支持multipart/form-data
- **文件下载**: 支持流式下载

---

## 💰 定价方案

| 计划 | 费用 |
|------|--------|
| Free | 完全免费（Apache 2.0开源） |

---

## 🧧 使用方法

### 1. 安装
```bash
pip install requests
```

### 2. Python基础使用
```python
import requests

# GET请求
response = requests.get('https://api.example.com/data')
print(response.status_code)
print(response.json())

# POST请求（JSON数据）
data = {'title': '新笔记', 'content': '笔记内容'}
response = requests.post('https://api.example.com/posts', json=data)
print(response.status_code)
print(response.json())

# POST请求（表单数据）
data = {'username': '官家', 'password': '***'}
response = requests.post('https://api.example.com/login', data=data)
print(response.json())

# 文件上传
files = {'image': open('product.jpg', 'rb')}
response = requests.post('https://api.example.com/upload', files=files)
print(response.json())
```

### 3. API调用示例（Public APIs）
```python
import requests

# ShotOG API（封面生成）
url = "https://shotog.2214962083.workers.dev/v1/og"
params = {
    'title': '蒸汽眼罩评测',
    'subtitle': '午休必备神器',
    'author': '小米椒'
}
response = requests.get(url, params=params)
print(f"状态码: {response.status_code}")

# Poof API（背景移除）
url = "https://api.poof.bg/v1/remove"
headers = {'Authorization': 'Bearer pk_b0e81ff5f19266dab29abd9c58eb4141'}
files = {'image': open('product.jpg', 'rb')}
response = requests.post(url, headers=headers, files=files)
print(response.json())

# APITube News API（热点采集）
url = "https://api.apitube.io/v1/news"
headers = {'X-API-Key': 'sk_YOUR_API_KEY'}
params = {
    'language': 'zh',
    'limit': 20
}
response = requests.get(url, headers=headers, params=params)
print(response.json())
```

### 4. 会话管理（保持登录状态）
```python
import requests

# 创建Session
session = requests.Session()

# 登录
login_data = {'username': '官家', 'password': '***'}
session.post('https://api.example.com/login', data=login_data)

# 使用Session发送请求
response = session.get('https://api.example.com/profile')
print(response.json())

# Session自动管理Cookies
response = session.post('https://api.example.com/posts', json={'title': '新笔记'})
print(response.json())
```

---

## 🚀 集成建议

### 场景1：Public APIs调用
- **输入**: API端点 + 参数
- **处理**: 使用Requests发送HTTP请求
- **输出**: API响应（JSON/图片/文本）
- **应用**:
  - ShotOG封面生成
  - Poof背景移除
  - Image Compressor图片压缩
  - APITube News热点采集

### 场景2：小红书API调用
- **输入**: API端点 + Cookie
- **处理**: 使用Requests发送请求
- **输出**: API响应
- **应用**:
  - 发布笔记
  - 获取笔记数据
  - 删除笔记

### 场景3：文件上传下载
- **输入**: 文件路径/URL
- **处理**: 使用Requests上传/下载
- **输出**: 文件流
- **应用**:
  - 产品图上传到1688
  - 下载产品素材
  - 批量文件处理

---

## ⚠️ 注意事项

### 错误处理
- **异常捕获**: 捕获requests.exceptions
- **状态码**: 检查HTTP状态码（200, 401, 404, 429等）
- **超时处理**: 设置timeout参数避免永久等待

### 性能优化
- **连接池**: 使用Session复用TCP连接
- **重试机制**: 添加重试逻辑（max_retries）
- **缓存**: 缓存API响应减少重复请求

---

## 📋 集成清单

### 第1步：安装Requests
- [ ] 安装requests库
- [ ] 测试基础功能

### 第2步：编写API调用脚本
- [ ] 编写API调用函数
- [ ] 编写错误处理函数
- [ ] 测试准确性

### 第3步：集成到工作流
- [ ] 集成到Public APIs调用
- [ ] 集成到小红书操作
- [ ] 测试准确性

---

## ✅ 已完成

- [x] 库文档调研
- [x] 使用方法整理
- [x] 集成场景设计
- [x] 集成清单编写

---

## ⏳ 待完成

- [ ] 安装requests库
- [ ] 编写测试脚本
- [ ] 执行测试验证
- [ ] 集成到工作流

---

## 📚 相关资源

- **官网**: https://requests.readthedocs.io/
- **GitHub**: https://github.com/psf/requests
- **文档**: https://requests.readthedocs.io/en/latest/
- **PyPI**: https://pypi.org/project/requests/

---

*小米椒 🌶️‍🔥 | 2026-04-11*
