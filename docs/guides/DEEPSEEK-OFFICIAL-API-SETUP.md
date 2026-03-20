# DeepSeek官方API配置指南

_2026-02-28 09:57_

---

## 📋 配置步骤

### 步骤1: 获取DeepSeek API Key

#### 官方申请地址
```
https://platform.deepseek.com/
```

#### 申请流程
1. 访问 https://platform.deepseek.com/
2. 注册账号（邮箱注册）
3. 登录后进入控制台
4. 点击 "API Keys"
5. 点击 "创建新密钥"
6. 复制API Key（格式：sk-xxxxxxxx）

#### API Key格式
```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### 步骤2: 提供API Key

**官家，请提供您的DeepSeek API Key：**

#### 方式A: 直接提供
```
我的DeepSeek API Key: sk-xxxxxxxx
```

#### 方式B: 如未申请
```
请先访问 https://platform.deepseek.com/ 申请API Key
获得后发送给我
```

---

### 步骤3: 我将配置

**配置内容**:
```json
{
  "deepseek": {
    "baseUrl": "https://api.deepseek.com/v1",
    "apiKey": "YOUR_API_KEY",
    "api": "openai-completions",
    "models": [
      {
        "id": "deepseek-chat",
        "name": "DeepSeek Chat",
        "reasoning": false,
        "input": ["text"],
        "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
        "contextWindow": 64000,
        "maxTokens": 4096
      },
      {
        "id": "deepseek-coder",
        "name": "DeepSeek Coder",
        "reasoning": false,
        "input": ["text"],
        "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
        "contextWindow": 64000,
        "maxTokens": 4096
      },
      {
        "id": "deepseek-reasoner",
        "name": "DeepSeek Reasoner",
        "reasoning": true,
        "input": ["text"],
        "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
        "contextWindow": 64000,
        "maxTokens": 4096
      }
    ]
  }
}
```

---

## 📊 官方模型列表

### DeepSeek官方模型（3个）

1. **DeepSeek Chat**
   - ID: `deepseek-chat`
   - 用途: 通用对话
   - 上下文: 64K tokens
   - 特点: 平衡性能

2. **DeepSeek Coder**
   - ID: `deepseek-coder`
   - 用途: 编程任务
   - 上下文: 64K tokens
   - 特点: 代码能力强

3. **DeepSeek Reasoner**
   - ID: `deepseek-reasoner`
   - 用途: 复杂推理
   - 上下文: 64K tokens
   - 特点: 推理增强

---

## 🎯 完成后效果

### 可用模型总数
```
腾讯云DeepSeek: 4个
官方DeepSeek: 3个
AIHubMix: 14个
其他: 7个
-------------------
总计: 28个模型
```

### 使用方式
```bash
# 使用官方DeepSeek
deepseek/deepseek-chat
deepseek/deepseek-coder
deepseek/deepseek-reasoner

# 使用腾讯云DeepSeek
qcloudlkeap/deepseek-v3.2
qcloudlkeap/deepseek-r1-0528
```

---

## 💡 推荐配置

### 主力模型推荐
```
1. AIHubMix GPT-4.1 Free（免费）
2. DeepSeek Chat（官方，稳定）
3. GLM-5（中文优秀）
```

### 编程任务推荐
```
1. DeepSeek Coder（专业）
2. Coding GLM-5（免费）
3. AIHubMix GPT-4.1 Free
```

### 推理任务推荐
```
1. DeepSeek Reasoner（官方）
2. DeepSeek R1（腾讯云）
3. AIHubMix GPT-4o Free
```

---

## 📝 配置文件位置

### OpenClaw配置文件
```
C:\Users\zhaog\.openclaw\openclaw.json
```

### 修改位置
```json
{
  "models": {
    "providers": {
      "deepseek": {
        // 我将在这里添加配置
      }
    }
  }
}
```

---

## 🔐 安全提醒

### API Key安全
- ✅ API Key将存储在本地配置文件
- ✅ 不会上传到云端
- ✅ 仅在本地使用
- ⚠️ 请勿分享给他人

---

## 🎯 下一步

### 官家，请选择：

#### 选项1: 已有API Key ⭐
```
请提供您的DeepSeek API Key
我将立即配置
```

#### 选项2: 需要申请
```
请访问 https://platform.deepseek.com/ 申请
获得API Key后发送给我
```

#### 选项3: 使用现有腾讯云DeepSeek
```
无需配置，直接可用
qcloudlkeap/deepseek-v3.2
```

---

## 📊 对比：官方 vs 腾讯云

| 特性 | 官方DeepSeek | 腾讯云DeepSeek |
|------|-------------|---------------|
| **配置** | 需要API Key | ✅ 已配置 |
| **稳定性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **上下文** | 64K | 200K |
| **模型数量** | 3个 | 4个 |
| **官方支持** | ✅ | ❌ |
| **推荐度** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 💡 建议

### 推荐方案：双配置 ⭐
```
1. 保留腾讯云DeepSeek（200K上下文）
2. 添加官方DeepSeek（官方支持）
3. 根据任务需求灵活选择
```

### 主力使用
```
日常: AIHubMix免费模型
中文: 腾讯云DeepSeek
编程: 官方DeepSeek Coder
推理: DeepSeek Reasoner
```

---

**创建时间**: 2026-02-28 09:57
**状态**: 等待官家提供API Key
**下一步**: 配置DeepSeek官方Provider
