# 百炼 API 配置状态 - 2026-03-31

## ✅ 已配置

### 端点信息

| 类型 | 环境变量 | URL |
|------|---------|-----|
| **OpenAI 兼容** | `BAILIAN_OPENAI_URL` | `https://coding.dashscope.aliyuncs.com/v1` |
| **Anthropic 兼容** | `BAILIAN_ANTHROPIC_URL` | `https://coding.dashscope.aliyuncs.com/apps/anthropic` |

### API Key

- **环境变量**: `BAILIAN_API_KEY`
- **值**: `sk-sp-****...****` （已脱敏）
- **状态**: ❌ **无效**（HTTP 401）

---

## ❌ 当前问题

### API Key 无效

**错误信息**:
```json
{
  "error": {
    "code": "invalid_api_key",
    "message": "invalid access token or token expired"
  }
}
```

**状态码**: 401 Unauthorized

---

## 🔧 解决方案

### 方案 1: 获取有效的 API Key

#### 步骤：

1. **访问百炼控制台**
   - URL: https://dashscope.console.aliyun.com/
   - 登录阿里云账号

2. **检查 API Key 状态**
   - 进入「API Key 管理」
   - 查看当前 API Key 是否有效
   - 检查是否过期或被撤销

3. **创建新的 API Key**（如需要）
   - 点击「创建 API Key」
   - 确保勾选「编程 API 访问权限」
   - 复制新 Key

4. **提供新 Key**
   - 格式: `sk-xxxxxxxxxxxxxxxxxxxxxxxx`
   - 我会更新配置并测试

---

### 方案 2: 检查服务权限

#### 可能需要的权限：

- ✅ 百炼服务已开通
- ✅ 账户有余额或免费额度
- ✅ API Key 有编程 API 访问权限
- ✅ 没有访问限制（IP 白名单等）

---

## 📋 待办清单

- [ ] 检查百炼控制台中的 API Key 状态
- [ ] 确认是否开通了编程 API 访问权限
- [ ] 创建新的 API Key（如需要）
- [ ] 提供有效的 API Key
- [ ] 测试两个端点连接
- [ ] 确认可用模型列表

---

## 💡 使用说明

### OpenAI 兼容端点

**用途**: 使用百炼模型，但通过 OpenAI SDK 调用

**示例**:
```python
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key",
    base_url="https://coding.dashscope.aliyuncs.com/v1"
)

response = client.chat.completions.create(
    model="qwen-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Anthropic 兼容端点

**用途**: 使用百炼模型，但通过 Anthropic SDK 调用

**示例**:
```python
from anthropic import Anthropic

client = Anthropic(
    api_key="your-api-key",
    base_url="https://coding.dashscope.aliyuncs.com/apps/anthropic"
)

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=10,
    messages=[{"role": "user", "content": "Hello"}]
)
```

---

_配置更新时间: 2026-03-31 02:52 PDT_
