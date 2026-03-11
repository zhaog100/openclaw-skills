# AIHubMix免费API方案分析

_多模型统一接入方案评估_

---

## 一、方案概述

### 1.1 平台信息

**AIHubMix**：https://aihubmix.com/

**提供的免费模型**：
- GPT-4.1 free
- GLM 5 free
- MiniMax m2.5
- Gemini 3 flash
- Claude系列（部分免费）
- 其他带`-free`关键字的模型

### 1.2 接入方式

```json
{
  "base_url": "https://aihubmix.com/v1",
  "api_key": "sk-xEAlqFr****2",
  "api": "openai-completions"
}
```

### 1.3 RPM限制

| 模型系列 | RPM限制 | RPD限制 | 说明 |
|---------|---------|---------|------|
| GPT系列 | 无限制 | 无限制 | 高频使用友好 |
| 国产系列 | 5次/分钟 | 500次/天 | 需要注意频率 |
| 谷歌系列 | - | 250次/天 | 日限制较低 |

---

## 二、当前配置对比

### 2.1 现有Provider

**当前配置**：
1. **zai** - 智谱GLM-5（免费）
   - baseUrl: https://api.z.ai/api/coding/paas/v4
   - 模型：GLM-5, GLM-4.7, GLM-4.7-flash, GLM-4.7-flashx
   - 状态：✅ 正常使用

2. **hunyuan** - 腾讯混元（免费）
   - baseUrl: https://api.hunyuan.cloud.tencent.com/v1
   - 模型：hunyuan-turbos-latest, hunyuan-t1-latest
   - 状态：✅ 已配置

3. **qcloudlkeap** - 腾讯云DeepSeek（免费）
   - baseUrl: https://api.lkeap.cloud.tencent.com/v1
   - 模型：deepseek-v3.2, deepseek-v3.1-terminus, deepseek-v3-0324, deepseek-r1-0528
   - 状态：✅ 已配置

### 2.2 对比分析

| 对比项 | 当前配置 | AIHubMix |
|--------|---------|----------|
| **模型数量** | 10个 | 20+个（含GPT/Gemini） |
| **GPT系列** | ❌ 无 | ✅ 有（GPT-4.1 free） |
| **Gemini系列** | ❌ 无 | ✅ 有（Gemini 3 flash） |
| **GLM-5** | ✅ 有（智谱官方） | ✅ 有（代理） |
| **DeepSeek** | ✅ 有（腾讯云） | ✅ 有（代理） |
| **统一接口** | ❌ 多个endpoint | ✅ 单一endpoint |
| **RPM限制** | 无明显限制 | 国产5/rpm, 500/rpd |
| **稳定性** | ⭐⭐⭐⭐⭐ 官方API | ⭐⭐⭐ 第三方代理 |

---

## 三、可行性评估

### 3.1 优势

✅ **模型多样性**
- 访问GPT-4.1、Gemini 3 flash等国际模型
- 无需分别注册多个平台

✅ **统一接入**
- 单一base_url
- OpenAI兼容格式
- 配置简单

✅ **免费使用**
- 所有`-free`模型完全免费
- GPT系列无RPM限制

✅ **即插即用**
- 复制配置即可使用
- 无需复杂设置

### 3.2 劣势

❌ **RPM限制**
- 国产模型：5次/分钟（可能影响体验）
- 日限制：500次/天（国产）、250次/天（谷歌）

❌ **稳定性风险**
- 第三方代理平台
- 依赖平台稳定性
- 可能随时调整政策

❌ **隐私考虑**
- API key由第三方管理
- 数据经过第三方服务器
- 需评估数据安全

❌ **功能限制**
- 可能有模型功能阉割
- 可能有响应延迟
- 可能有调用失败

---

## 四、配置建议

### 4.1 推荐方案：双轨并行

**保留现有配置** + **添加AIHubMix**

```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "zai": { ... },  // 保留：智谱官方API
      "hunyuan": { ... },  // 保留：腾讯混元
      "qcloudlkeap": { ... },  // 保留：腾讯云DeepSeek
      "aihubmix": {  // 新增：AIHubMix
        "baseUrl": "https://aihubmix.com/v1",
        "apiKey": "YOUR_API_KEY",
        "api": "openai-completions",
        "models": [
          {
            "id": "gpt-4.1-free",
            "name": "GPT-4.1 Free",
            "reasoning": true,
            "input": ["text"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 128000,
            "maxTokens": 4096
          },
          {
            "id": "gemini-3-flash-free",
            "name": "Gemini 3 Flash Free",
            "reasoning": false,
            "input": ["text"],
            "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
            "contextWindow": 32000,
            "maxTokens": 2048
          }
        ]
      }
    }
  }
}
```

### 4.2 使用策略

**主力模型**：
- 日常工作：`zai/glm-5`（智谱官方，稳定）
- 快速响应：`hunyuan/hunyuan-turbos-latest`（腾讯混元）
- 深度推理：`qcloudlkeap/deepseek-r1-0528`（DeepSeek R1）

**补充模型**（AIHubMix）：
- GPT能力：`aihubmix/gpt-4.1-free`（需要GPT特性时）
- Gemini测试：`aihubmix/gemini-3-flash-free`（尝鲜）
- 高频场景：`aihubmix/gpt-4.1-free`（无RPM限制）

### 4.3 注意事项

⚠️ **RPM限制管理**
```markdown
1. 国产模型（GLM/DeepSeek等）：
   - 限制：5次/分钟，500次/天
   - 建议：避免高频调用，分散使用

2. GPT系列：
   - 限制：无限制
   - 建议：可用于高频场景

3. 谷歌系列：
   - 限制：250次/天
   - 建议：谨慎使用，优先其他选项
```

⚠️ **故障转移**
```markdown
1. AIHubMix失败 → 自动切换到官方API
2. 官方API失败 → 尝试AIHubMix代理
3. 两者都失败 → 降级到其他provider
```

---

## 五、具体实施步骤

### 5.1 注册获取API Key

1. **访问**：https://aihubmix.com/
2. **注册**：
   - 使用邮箱注册
   - 或GitHub/Google账号登录
3. **获取API Key**：
   - 登录后自动生成
   - 复制`api_key`

### 5.2 添加配置

**方式1：手动编辑**（推荐）
```powershell
# 编辑配置文件
notepad C:\Users\zhaog\.openclaw\openclaw.json

# 在 "providers" 下添加：
"aihubmix": {
  "baseUrl": "https://aihubmix.com/v1",
  "apiKey": "YOUR_API_KEY_HERE",
  "api": "openai-completions",
  "models": [
    {
      "id": "gpt-4.1-free",
      "name": "GPT-4.1 Free",
      "reasoning": true,
      "input": ["text"],
      "cost": { "input": 0, "output": 0 },
      "contextWindow": 128000,
      "maxTokens": 4096
    },
    {
      "id": "gemini-3-flash-free",
      "name": "Gemini 3 Flash Free",
      "reasoning": false,
      "input": ["text"],
      "cost": { "input": 0, "output": 0 },
      "contextWindow": 32000,
      "maxTokens": 2048
    }
  ]
}

# 重启OpenClaw
openclaw restart
```

**方式2：使用我帮你配置**
```
告诉我：你注册后获得的API Key
我会帮你：
1. 更新配置文件
2. 重启服务
3. 测试连接
```

### 5.3 验证测试

```powershell
# 测试GPT-4.1
openclaw chat --model aihubmix/gpt-4.1-free "你好，请介绍一下你自己"

# 测试Gemini
openclaw chat --model aihubmix/gemini-3-flash-free "Hello, what can you do?"
```

---

## 六、风险评估

### 6.1 高风险

🔴 **平台稳定性**
- 第三方代理，可能随时关闭
- 建议：仅作为补充，不作为主力

🔴 **数据安全**
- API key由第三方管理
- 对话内容经过第三方服务器
- 建议：避免传输敏感信息

### 6.2 中风险

🟡 **RPM限制**
- 国产模型5次/分钟限制
- 可能影响工作流
- 建议：合理安排调用频率

🟡 **模型阉割**
- 可能功能不完整
- 可能性能下降
- 建议：对比测试后决定

### 6.3 低风险

🟢 **免费使用**
- 不涉及费用风险
- 建议：充分利用

🟢 **配置简单**
- 技术风险低
- 建议：快速试用

---

## 七、最终建议

### 7.1 推荐方案：谨慎试用

**第一阶段：测试期**（1-2周）
```
✅ 注册获取API Key
✅ 添加配置（不设置为主力）
✅ 间歇性测试GPT/Gemini
✅ 评估稳定性和质量
```

**第二阶段：评估期**（2-4周）
```
📊 统计成功率
📊 对比响应质量
📊 评估RPM影响
📊 决定是否深度使用
```

**第三阶段：决策期**
```
✅ 稳定且有用 → 保留配置
❌ 不稳定或限制多 → 移除配置
```

### 7.2 使用原则

1. **主力模型**：智谱GLM-5（官方API）
2. **补充模型**：AIHubMix（GPT/Gemini）
3. **备用模型**：腾讯混元/DeepSeek
4. **敏感场景**：仅用官方API
5. **高频场景**：优先GPT系列（无RPM限制）

### 7.3 不推荐场景

❌ **完全不推荐**：
- 将AIHubMix设为唯一provider
- 在AIHubMix上处理敏感数据
- 依赖AIHubMix做关键决策

✅ **合理使用**：
- 作为多provider之一
- 用于尝鲜GPT/Gemini
- 低频、非敏感场景

---

## 八、总结

### 核心价值

✅ **补充GPT/Gemini能力**
- 访问国际模型
- 统一接口
- 免费使用

⚠️ **谨慎使用**
- 第三方代理风险
- RPM限制
- 稳定性不确定

### 最佳实践

```
保留现有配置（主力）
    +
添加AIHubMix（补充）
    =
最优方案（双保险）
```

### 一句话建议

> **值得尝试，但不建议作为主力。作为补充provider体验GPT/Gemini，同时保持官方API为主。**

---

**最后更新**：2026年2月27日
**适用对象**：OpenClaw用户、AI工具爱好者
**风险等级**：中（第三方代理，需谨慎评估）
