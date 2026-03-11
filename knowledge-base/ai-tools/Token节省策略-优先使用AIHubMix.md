# Token节省策略 - 优先使用AIHubMix

_以减少token消耗为核心的模型选择策略_

---

## 一、策略原则

### 1.1 核心目标

**一切以减少token消耗为主**

### 1.2 优先级顺序

```
1. aihubmix/gpt-4.1-free（首选）
   ↓ 用完额度或失败
2. aihubmix/gemini-3-flash-free（次选）
   ↓ 用完额度或失败
3. zai/glm-5（保底）
```

---

## 二、模型配置

### 2.1 主力模型（Primary）

**模型**：`aihubmix/gpt-4.1-free`
**别名**：GPT
**特点**：
- ✅ 完全免费
- ✅ 无RPM限制
- ✅ 128K上下文
- ✅ GPT-4.1能力

**适用场景**：
- 所有日常对话
- 知识检索
- 代码生成
- 文档编写

---

### 2.2 补充模型

**模型**：`aihubmix/gemini-3-flash-free`
**别名**：Gemini
**特点**：
- ✅ 完全免费
- ⚠️ 250次/天限制
- ✅ 32K上下文
- ✅ Gemini 3 Flash能力

**适用场景**：
- GPT额度用完后
- 需要Gemini特性时
- 多样化尝试

---

### 2.3 保底模型

**模型**：`zai/glm-5`
**别名**：GLM
**特点**：
- ✅ 智谱官方API
- ✅ 无限制
- ✅ 204K上下文
- ⚠️ 可能消耗官方额度

**适用场景**：
- AIHubMix全部失败时
- 需要官方API稳定性时
- 处理敏感数据时

---

## 三、自动切换机制

### 3.1 配置实现

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "aihubmix/gpt-4.1-free"
      },
      "models": {
        "aihubmix/gpt-4.1-free": {
          "alias": "GPT"
        },
        "aihubmix/gemini-3-flash-free": {
          "alias": "Gemini"
        },
        "zai/glm-5": {
          "alias": "GLM"
        }
      }
    }
  }
}
```

### 3.2 工作原理

**每次会话启动时**：
1. 优先尝试 `aihubmix/gpt-4.1-free`
2. 如果失败，自动切换到 `aihubmix/gemini-3-flash-free`
3. 如果仍失败，最终使用 `zai/glm-5`

---

## 四、成本对比

### 4.1 Token消耗对比

| 模型 | 输入成本 | 输出成本 | 缓存读取 | 总成本 |
|------|---------|---------|---------|--------|
| AIHubMix GPT | $0 | $0 | $0 | **$0** |
| AIHubMix Gemini | $0 | $0 | $0 | **$0** |
| 智谱GLM-5 | $0 | $0 | $0 | **$0** |

**结论**：所有模型都是免费的，- 但AIHubMix可能更稳定（无官方API限流风险）
- GPT-4.1能力更强（国际模型）

### 4.2 RPM限制对比

| 模型 | RPM限制 | RPD限制 | 稳定性 |
|------|---------|---------|--------|
| AIHubMix GPT | ✅ 无限制 | ✅ 无限制 | ⭐⭐⭐ |
| AIHubMix Gemini | - | ⚠️ 250/天 | ⭐⭐⭐ |
| 智谱GLM-5 | ✅ 无限制 | ✅ 无限制 | ⭐⭐⭐⭐⭐ |

---

## 五、使用建议

### 5.1 日常使用

**推荐**：默认使用GPT（无需手动切换）

**系统自动**：
- 新会话自动使用 `aihubmix/gpt-4.1-free`
- 失败时自动切换
- 无需人工干预

### 5.2 特殊场景

**需要Gemini时**：
```
"用Gemini模型回答这个问题"
```

**需要官方API时**：
```
"用GLM模型处理这个敏感数据"
```

---

## 六、监控与维护

### 6.1 状态监控

**检查模型使用情况**：
```powershell
# 查看日志
openclaw logs | grep "model"
```

**检查AIHubMix额度**：
- 访问 https://aihubmix.com/
- 登录查看使用情况

### 6.2 故障处理

**如果GPT失败**：
1. 检查AIHubMix服务状态
2. 检查网络连接
3. 系统自动切换到Gemini或GLM

**如果全部失败**：
1. 检查配置文件
2. 重启服务：`openclaw gateway restart`
3. 查看日志排查问题

---

## 七、优化效果

### 7.1 成本节省

**相比直接使用官方API**：
- ✅ 无token消耗风险
- ✅ 无API限流风险
- ✅ 享受GPT-4.1能力

### 7.2 稳定性提升

**三层保障**：
1. AIHubMix GPT（主力）
2. AIHubMix Gemini（补充）
3. 智谱GLM-5（保底）

---

## 八、总结

### 核心策略

> **优先AIHubMix，保底官方API，一切以减少token消耗为主**

### 配置状态

✅ **Primary**: aihubmix/gpt-4.1-free
✅ **Fallback 1**: aihubmix/gemini-3-flash-free
✅ **Fallback 2**: zai/glm-5

### 预期效果

- 🎯 **Token消耗**：$0（全部免费模型）
- 🎯 **稳定性**：⭐⭐⭐⭐（三层保障）
- 🎯 **能力提升**：GPT-4.1 > GLM-5

---

**最后更新**：2026年2月27日 12:05
**适用对象**：所有OpenClaw用户
**核心目标**：减少token消耗，优先免费模型
