# DeepSeek模型添加指南

_2026-02-28 09:55_

---

## ✅ 发现：已有DeepSeek模型

### 当前配置（腾讯云API）

**Provider**: `qcloudlkeap`
**API**: 腾讯云 LKEAP（DeepSeek代理）
**Base URL**: `https://api.lkeap.cloud.tencent.com/v1`
**API Key**: 已配置

#### 已有DeepSeek模型（4个）

1. **DeepSeek V3.2**
   - ID: `deepseek-v3.2`
   - 上下文: 200K tokens
   - 最大输出: 8192 tokens
   - 成本: 免费

2. **DeepSeek V3.1 Terminus**
   - ID: `deepseek-v3.1-terminus`
   - 上下文: 200K tokens
   - 最大输出: 8192 tokens
   - 成本: 免费

3. **DeepSeek V3 0324**
   - ID: `deepseek-v3-0324`
   - 上下文: 200K tokens
   - 最大输出: 8192 tokens
   - 成本: 免费

4. **DeepSeek R1 0528**
   - ID: `deepseek-r1-0528`
   - 上下文: 200K tokens
   - 最大输出: 8192 tokens
   - 成本: 免费

---

## 🎯 两种添加方案

### 方案A: 使用已有腾讯云DeepSeek（推荐）⭐

**优势**:
- ✅ 已配置完成
- ✅ API Key已就绪
- ✅ 无需额外申请

**使用方式**:
```json
{
  "primary": "qcloudlkeap/deepseek-v3.2"
}
```

**模型列表**:
- `qcloudlkeap/deepseek-v3.2` ✅
- `qcloudlkeap/deepseek-v3.1-terminus` ✅
- `qcloudlkeap/deepseek-v3-0324` ✅
- `qcloudlkeap/deepseek-r1-0528` ✅

---

### 方案B: 添加官方DeepSeek API

**需要**:
1. DeepSeek官方API Key
2. 申请地址: https://platform.deepseek.com/

**配置步骤**:

#### 1. 申请API Key
```
访问: https://platform.deepseek.com/
注册账号 → API Keys → 创建新密钥
```

#### 2. 添加Provider配置
```json
{
  "deepseek": {
    "baseUrl": "https://api.deepseek.com/v1",
    "apiKey": "YOUR_DEEPSEEK_API_KEY",
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

## 📊 方案对比

| 特性 | 腾讯云DeepSeek | 官方DeepSeek |
|------|---------------|-------------|
| **配置** | ✅ 已完成 | ❌ 需配置 |
| **API Key** | ✅ 已有 | ❌ 需申请 |
| **模型数量** | 4个 | 3个（官方） |
| **上下文** | 200K | 64K |
| **稳定性** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 💡 推荐使用

### 方案A: 立即可用 ⭐
```
使用已有的腾讯云DeepSeek模型
无需额外配置，直接可用
```

**模型**:
- `qcloudlkeap/deepseek-v3.2` ✅ 推荐
- `qcloudlkeap/deepseek-r1-0528` ✅ 推理增强

---

## 🎯 立即可用模型（无需配置）

### 当前可用的DeepSeek模型

1. **DeepSeek V3.2**（推荐）⭐
   ```
   qcloudlkeap/deepseek-v3.2
   ```
   - 最新版本
   - 200K上下文
   - 综合能力最强

2. **DeepSeek R1**（推理增强）
   ```
   qcloudlkeap/deepseek-r1-0528
   ```
   - 推理能力强
   - 适合复杂任务

3. **DeepSeek V3.1 Terminus**
   ```
   qcloudlkeap/deepseek-v3.1-terminus
   ```
   - 稳定版本

4. **DeepSeek V3 0324**
   ```
   qcloudlkeap/deepseek-v3-0324
   ```
   - 历史版本

---

## 🔧 如何使用

### 方法1: 设置为主模型
修改 `openclaw.json`:
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "qcloudlkeap/deepseek-v3.2"
      }
    }
  }
}
```

### 方法2: 临时切换模型
在对话中回复：
```
切换到DeepSeek V3.2
```

### 方法3: 指定模型调用
```
使用deepseek-r1-0528模型帮我分析这个问题
```

---

## 📝 下一步

### 官家，您想要：

#### 选项1: 立即使用现有DeepSeek ⭐
```
使用 qcloudlkeap/deepseek-v3.2
无需额外配置
```

#### 选项2: 添加官方DeepSeek API
```
需要提供DeepSeek官方API Key
我将协助配置
```

#### 选项3: 查看当前所有可用模型
```
列出所有24个模型
帮助您选择
```

---

## 🎓 核心要点

### ✅ 已经有DeepSeek
- 通过腾讯云API
- 4个模型可用
- 无需额外配置

### 🆕 如需官方API
- 需申请API Key
- 添加provider配置
- 可获得官方支持

---

**创建时间**: 2026-02-28 09:55
**状态**: 等待官家选择
**推荐**: 使用现有腾讯云DeepSeek（立即可用）
