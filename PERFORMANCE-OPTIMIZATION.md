# OpenClaw性能优化方案

## 📊 当前性能分析

**会话状态**：
- 缓存命中率：93% ✅（优秀）
- Tokens使用：7.8k in / 446 out
- 上下文：108k/203k (53%)
- 成本：$0.0000（免费额度内）

**模型配置**：
- 主力模型：zai/glm-5
- 备用模型：22个（百炼8 + AIHubMix 14）

## 🎯 Token节省策略

### 1. 上下文管理

**当前策略**：
- ✅ 使用QMD精准检索（节省92.5% tokens）
- ✅ 避免全量读取MEMORY.md（2000+ tokens）
- ✅ 使用memory_search + memory_get组合

**优化建议**：
```json5
{
  "features": {
    "context": {
      "maxTokens": 120000,  // 降低最大上下文
      "compactionThreshold": 0.7,  // 70%时压缩
      "preserveSystemPrompts": true
    }
  }
}
```

### 2. 模型分层

**分层策略**：
```
简单任务 → Flash模型（快速、便宜）
├─ 日常对话：glm-4.7-flash（免费）
├─ 简单查询：gemini-3-flash（免费）
└─ 快速回复：coding-glm-5-free

复杂任务 → 主力模型（强大、准确）
├─ 项目管理：glm-5（当前）
├─ 代码生成：qwen-coder-plus
└─ 文档分析：qwen3-max

特殊任务 → 专用模型
├─ 图像识别：gemini-vision
├─ 长文档：kimi（200k上下文）
└─ 英文任务：gpt-4.1-mini
```

### 3. 提示词优化

**精简原则**：
- ❌ 避免："我来帮您..."、"让我..."等填充词
- ✅ 使用：直接行动、简洁回复
- ✅ 使用：命令式语言（"检查..."、"执行..."）

**示例对比**：
```
❌ 低效（25 tokens）：
"好的，让我帮您检查一下系统状态，稍等片刻..."

✅ 高效（10 tokens）：
"检查系统状态"
```

### 4. 缓存优化

**当前缓存策略**：
- 缓存命中率：93%（优秀）
- 缓存大小：99k tokens
- 策略：自动缓存

**优化建议**：
```json5
{
  "cache": {
    "enabled": true,
    "ttl": 3600,  // 1小时
    "maxSize": "100MB",
    "strategy": "lru"
  }
}
```

## 🚀 响应速度提升

### 1. 模型选择

**速度排名**（从快到慢）：
1. glm-4.7-flash（最快，免费）
2. gemini-3-flash（快速，免费）
3. coding-glm-5-free（快速，免费）
4. glm-5（当前，平衡）
5. qwen3-max（强大，较慢）

**场景匹配**：
- 闲聊/简单查询 → Flash模型（<1秒）
- 日常任务 → GLM-5（1-2秒）
- 复杂分析 → Qwen3-Max（2-5秒）

### 2. 并行处理

**可并行任务**：
- ✅ 多个独立查询
- ✅ 文件读取 + 网络请求
- ✅ 日志分析 + 状态检查

**示例**：
```python
# 并行执行多个检查
results = await asyncio.gather(
    check_gateway_status(),
    check_qmd_status(),
    check_disk_space()
)
```

### 3. 预加载策略

**预加载内容**：
- 常用文档（MEMORY.md、USER.md）
- 系统状态（Gateway、QMD）
- 最近记忆（memory/YYYY-MM-DD.md）

### 4. 流式输出

**启用流式**：
```json5
{
  "features": {
    "streaming": {
      "enabled": true,
      "minTokens": 50  // 超过50 tokens启用流式
    }
  }
}
```

## 💡 成本优化

### 1. 免费模型优先

**免费模型列表**：
- ✅ glm-4.7-flash
- ✅ coding-glm-5-free
- ✅ gemini-3-flash
- ✅ qwen-coder（AIHubMix）

**使用策略**：
- 简单任务 → 100%免费模型
- 中等任务 → 80%免费模型
- 复杂任务 → 按需选择

### 2. 上下文压缩

**压缩策略**：
- 定期压缩历史消息
- 保留关键信息
- 删除重复内容

**压缩时机**：
- 上下文超过70%
- 历史消息超过100条
- 会话时长超过1小时

### 3. 批量处理

**批量场景**：
- 多个文档索引
- 批量文件处理
- 批量API调用

## 📈 性能监控

### 关键指标

**Token使用**：
- 当前：7.8k in / 446 out
- 目标：<5k in / <300 out

**响应时间**：
- 简单查询：<1秒
- 日常任务：1-2秒
- 复杂分析：<5秒

**缓存命中率**：
- 当前：93%
- 目标：>95%

### 监控工具

**OpenClaw内置**：
```bash
openclaw status
openclaw usage
```

**会话状态**：
```bash
/session_status
```

## 🔧 优化配置

### 推荐配置

```json5
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "zai/glm-5",
        "fallback": "aihubmix/coding-glm-5-free",
        "routing": {
          "simple": "zai/glm-4.7-flash",
          "complex": "zai/glm-5",
          "coding": "bailian/qwen3-coder-plus",
          "vision": "aihubmix/gemini-3.1-flash-image-preview-free"
        }
      }
    }
  },
  "features": {
    "cache": {
      "enabled": true,
      "ttl": 3600,
      "maxSize": "100MB"
    },
    "context": {
      "maxTokens": 120000,
      "compactionThreshold": 0.7
    },
    "streaming": {
      "enabled": true,
      "minTokens": 50
    }
  },
  "optimization": {
    "tokenSaving": true,
    "parallelProcessing": true,
    "preloadDocs": true
  }
}
```

## 🎯 实施计划

### 阶段1：立即优化（0成本）
- ✅ 使用QMD精准检索
- ✅ 精简提示词
- ✅ 使用免费模型

### 阶段2：配置优化（1天）
- [ ] 配置模型路由
- [ ] 启用流式输出
- [ ] 优化缓存策略

### 阶段3：深度优化（1周）
- [ ] 实现并行处理
- [ ] 预加载常用内容
- [ ] 性能监控仪表板

## 📊 预期效果

**Token节省**：
- 当前：7.8k in
- 优化后：<5k in
- 节省：35%+

**响应速度**：
- 简单任务：<1秒（提升50%）
- 复杂任务：<3秒（提升40%）

**成本节省**：
- 当前：$0.0000（免费额度内）
- 优化后：持续保持免费

---

**创建时间**：2026-03-03 15:45
**版本**：v1.0
**作者**：米粒儿
