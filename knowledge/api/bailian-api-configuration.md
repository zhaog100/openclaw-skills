# 阿里云百炼 API 配置

## 📋 API 概述

**提供商**: 阿里云
**服务名称**: 百炼（Bailian）
**用途**: 提供大语言模型 API，**兼容性**: OpenAI + Anthropic 接口协议

---

## 🌐 API 端点

### OpenAI 兼容端点
```
URL: https://coding.dashscope.aliyuncs.com/v1
兼容: OpenAI SDK
用途: 使用 OpenAI SDK 调用百炼模型
```

**支持的操作**:
- `/v1/chat/completions` - 对话补全
- `/v1/models` - 列出可用模型

### Anthropic 兼容端点
```
URL: https://coding.dashscope.aliyuncs.com/apps/anthropic
兼容: Anthropic SDK
用途: 使用 Anthropic SDK 调用百炼模型
```

**支持的操作**:
- `/v1/messages` - Anthropic 消息 API

---

## 🔑 API Key 管理

### 格式
```
前缀: sk-sp-
长度: 38 字符
示例: sk-sp-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 安全规则
1. ✅ **存储**: `.env` 文件（不提交到 Git）
2. ✅ **脱敏**: 只显示 `sk-sp-****...****`（前缀 + 后 4 位）
3. ⚠️ **泄露**: 如已泄露，立即撤销并重新创建

### 环境变量配置
```bash
# ~/.openclaw/workspace/.env
BAILIAN_API_KEY=sk-sp-xxxxxxxxxxxxxxxxxxxxxxxx
BAILIAN_OPENAI_URL=https://coding.dashscope.aliyuncs.com/v1
BAILIAN_ANTHROPIC_URL=https://coding.dashscope.aliyuncs.com/apps/anthropic
```

---

## 💻 使用示例

### OpenAI SDK
```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-sp-xxxxx",
    base_url="https://coding.dashscope.aliyuncs.com/v1"
)

response = client.chat.completions.create(
    model="qwen-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Anthropic SDK
```python
from anthropic import Anthropic

client = Anthropic(
    api_key="sk-sp-xxxxx",
    base_url="https://coding.dashscope.aliyuncs.com/apps/anthropic"
)

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello"}]
)
```

---

## ⚠️ 配额管理

### 配额类型
- **免费额度**: 新用户可能有免费额度
- **按月配额**: 每月重置
- **付费充值**: 可充值购买额外配额

### 常见错误

#### HTTP 429: 配额不足
```json
{
  "error": {
    "code": "insufficient_quota",
    "message": "month allocated quota exceeded"
  }
}
```

**解决方案**:
1. 等待配额重置（每月初）
2. 充值购买额外配额
3. 切换到其他 API（如 Gemini、OpenAI）

#### HTTP 401: API Key 无效
```json
{
  "error": {
    "code": "invalid_api_key",
    "message": "invalid access token or token expired"
  }
}
```

**解决方案**:
1. 检查 API Key 是否正确
2. 检查是否过期或被撤销
3. 创建新的 API Key

---

## 📊 测试状态（2026-03-31）

### 当前配置
- **API Key**: `sk-sp-ea64****...****d723` ✅ 有效
- **OpenAI 端点**: ✅ 可达
- **Anthropic 端点**: ⏳ 待测试
- **配额状态**: ⚠️ 不足（HTTP 429）

### 下一步
1. ⏳ 等待配额重置
2. ⏳ 或充值购买额外配额
3. ⏳ 配额恢复后测试 Anthropic 端点

---

## 🔧 故障排除

### 问题 1: 连接超时
- **检查**: 网络连接
- **检查**: 防火墙设置
- **解决**: 使用代理或切换网络

### 问题 2: 模型不可用
- **检查**: 是否在支持列表中
- **检查**: 是否有访问权限
- **解决**: 切换到支持的模型

### 问题 3: 响应格式错误
- **检查**: SDK 版本
- **检查**: API 版本兼容性
- **解决**: 更新 SDK 或使用兼容版本

---

## 📚 相关资源

- **控制台**: https://dashscope.console.aliyun.com/
- **文档**: https://help.aliyun.com/zh/model-studio/
- **API 参考**: https://dashscope.aliyuncs.com/api

---

_创建时间: 2026-03-31_
