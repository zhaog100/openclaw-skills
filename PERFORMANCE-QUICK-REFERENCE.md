# OpenClaw性能优化快速参考

## 🎯 三大优化方向

### 1. Token节省

**当前**：7.8k in / 446 out
**目标**：<5k in / <300 out
**节省**：35%+

**方法**：
- ✅ 使用QMD精准检索（节省92.5%）
- ✅ 精简提示词（节省30%）
- ✅ 避免全量读取大文件

### 2. 模型选择

**策略**：
```
简单任务 → glm-4.7-flash（最快）
中等任务 → glm-5（当前，平衡）
复杂任务 → qwen3-max（最强）
```

**切换命令**：
```bash
/model zai/glm-4.7-flash  # 快速
/model zai/glm-5          # 平衡（当前）
/model aihubmix/coding-glm-5-free  # 代码
```

### 3. 响应速度

**当前**：
- 简单任务：1-2秒
- 复杂任务：2-5秒

**优化后**：
- 简单任务：<1秒（提升50%）
- 复杂任务：1-3秒（提升40%）

**方法**：
- ✅ 使用Flash模型
- ✅ 启用缓存（当前93%命中率）
- ✅ 并行处理

## 📊 性能监控

### 会话状态
```bash
/session_status
```

### 查看输出示例
```
🧠 Model: zai/glm-5
🧮 Tokens: 7.8k in / 446 out
🗄️ Cache: 93% hit · 99k cached
📊 Usage: Monthly 99% left
```

## 💡 优化技巧

### 提示词优化

**❌ 冗长**：
```
"好的，让我帮您检查一下系统状态，稍等片刻..."
```
**✅ 精简**：
```
"检查系统状态"
```
**节省**：60% tokens

### 检索优化

**❌ 低效**：
```
读取整个MEMORY.md（2000+ tokens）
```
**✅ 高效**：
```
memory_search("关键词")
memory_get("特定片段")
```
**节省**：92.5% tokens

### 模型优化

**❌ 单一模型**：
```
所有任务都用glm-5
```
**✅ 分层选择**：
```
闲聊 → flash（0.5秒）
工作 → glm-5（1秒）
分析 → qwen-max（3秒）
```
**节省**：50%时间

## 🔧 配置文件

### 优化后的openclaw.json

```json5
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "zai/glm-5",
        "routing": {
          "simple": "zai/glm-4.7-flash",
          "complex": "zai/glm-5",
          "coding": "aihubmix/coding-glm-5-free"
        }
      }
    }
  },
  "features": {
    "cache": {
      "enabled": true,
      "ttl": 3600
    },
    "streaming": {
      "enabled": true,
      "minTokens": 50
    }
  }
}
```

## 📈 性能对比表

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| Token输入 | 7.8k | <5k | 35%+ |
| Token输出 | 446 | <300 | 32%+ |
| 简单任务速度 | 1-2秒 | <1秒 | 50%+ |
| 复杂任务速度 | 2-5秒 | 1-3秒 | 40%+ |
| 缓存命中率 | 93% | 95%+ | 2%+ |
| 成本 | $0.0000 | $0.0000 | 免费 |

## 🎯 快速优化清单

### 立即执行（5分钟）

- [ ] 切换到Flash模型测试
- [ ] 精简提示词
- [ ] 使用QMD检索

### 短期优化（1天）

- [ ] 配置模型路由
- [ ] 启用流式输出
- [ ] 优化缓存策略

### 长期优化（1周）

- [ ] 实现并行处理
- [ ] 预加载常用内容
- [ ] 性能监控仪表板

## 🔗 相关文档

- `PERFORMANCE-OPTIMIZATION.md` - 完整优化方案
- `MODEL-SELECTION-GUIDE.md` - 模型选择指南
- `optimize-performance.sh` - 优化工具脚本
- `test-performance.sh` - 性能测试脚本

## 💬 使用建议

### 日常使用

```bash
# 1. 检查当前状态
/session_status

# 2. 根据任务选择模型
/model zai/glm-4.7-flash  # 简单任务

# 3. 使用QMD精准检索
memory_search("关键词")

# 4. 精简提示词
"检查状态" 而不是 "请帮我检查一下状态"
```

### 性能监控

```bash
# 定期检查
openclaw status
openclaw usage

# 查看缓存
openclaw status | grep Cache
```

## 🆘 故障排查

### 响应慢

1. 检查缓存命中率（应>90%）
2. 切换到Flash模型
3. 精简提示词

### Token消耗快

1. 使用QMD检索代替全量读取
2. 精简提示词
3. 避免重复查询

### 成本超预算

1. 切换到免费模型
2. 优化Token使用
3. 使用缓存

---

**创建时间**：2026-03-03 15:45
**版本**：v1.0
**作者**：米粒儿
