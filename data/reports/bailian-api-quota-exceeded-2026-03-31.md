# 百炼 API 配额超限报告 - 2026-03-31

_报告生成时间: 2026-03-31 02:56 PDT_

## ⚠️ 问题：配额不足

### 测试结果

**API Key**: `sk-sp-ea64****...****d723` (已脱敏)
**端点**: `https://coding.dashscope.aliyuncs.com/v1/chat/completions`
**状态**: HTTP 429 Too Many Requests

---

### 错误信息
```json
{
  "error": {
    "code": "insufficient_quota",
    "message": "month allocated quota exceeded"
  }
}
```

---

## 🔍 问题分析
### ✅ 好消息
1. **API Key 有效** - 不再是 401 错误
2. **端点可达** - 连接成功
3. **配置正确** - OpenAI 兼容端点工作正常

### ❌ 问题
**配额已用完**: "month allocated quota exceeded"

---

## 💡 解决方案
### 方案 1: 充值或升级配额
访问百炼控制台：
- https://dashscope.console.aliyun.com/
- 检查配额使用情况
- 充值或升级套餐

### 方案 2: 等待配额重置
- 如果是免费额度，可能每月重置
- 查看重置时间

### 方案 3: 使用其他 API
暂时使用其他模型：
- **Gemini** (已有 API Key)
- **OpenAI** (如需要)
- **其他百炼地域** (北京/新加坡/美国)

---

## 📋 配置状态
| 项目 | 状态 | 说明 |
|------|------|------|
| **API Key** | ✅ 有效 | 已验证 |
| **OpenAI 端点** | ✅ 可用 | 配额不足 |
| **Anthropic 端点** | ⏳ 待测 | 应该也有相同问题 |
| **配置文件** | ✅ 已保存 | `.env` |

---

## 🔄 下一步
1. 检查百炼控制台的配额状态
2. 充值或等待配额重置
3. 配额恢复后立即可用

---

_报告生成时间: 2026-03-31 02:56 PDT_
