# 百炼模型智能切换策略

_根据实际任务类型智能选择最适合的模型_

---

## 📊 百炼模型分类

### 通用型模型
| 模型 | 上下文 | 多模态 | 适用场景 |
|------|--------|--------|----------|
| **qwen3.5-plus** | 100 万 | ✅ | 默认推荐、长文本、多模态 |
| **qwen3-max-2026-01-23** | 26 万 | ❌ | 复杂推理、高难度任务 |
| **MiniMax-M2.5** | 20 万 | ❌ | 快速响应、简单任务 |
| **glm-5** | 20 万 | ❌ | 通用对话 |
| **glm-4.7** | 20 万 | ❌ | 通用对话 |

### 编程专用模型
| 模型 | 上下文 | 适用场景 |
|------|--------|----------|
| **qwen3-coder-next** | 26 万 | 快速编程、代码补全 |
| **qwen3-coder-plus** | 100 万 | 复杂编程、代码审查、长代码 |

### 长文本模型
| 模型 | 上下文 | 多模态 | 适用场景 |
|------|--------|--------|----------|
| **qwen3.5-plus** | 100 万 | ✅ | 长文档、多模态 |
| **qwen3-coder-plus** | 100 万 | ❌ | 长代码 |
| **kimi-k2.5** | 26 万 | ✅ | 长文本、多模态 |

---

## 🎯 智能切换规则

### 1. 默认模型（当前）
```
默认：bailian/qwen3.5-plus
原因：100 万上下文，多模态支持，性价比最高
```

### 2. 任务类型判断
```python
if 任务类型 == "编程":
    if 代码长度 < 10K:
        使用 qwen3-coder-next（快速响应）
    else:
        使用 qwen3-coder-plus（100 万上下文）

elif 任务类型 == "复杂推理":
    使用 qwen3-max-2026-01-23（最强推理）

elif 任务类型 == "图像理解":
    使用 qwen3.5-plus 或 kimi-k2.5（多模态）

elif 任务类型 == "长文本":
    if 需要多模态:
        使用 qwen3.5-plus（100 万上下文 + 多模态）
    else:
        使用 qwen3-coder-plus（100 万上下文）

elif 任务类型 == "快速对话":
    使用 MiniMax-M2.5 或 glm-4.7（快速响应）

else:
    使用 qwen3.5-plus（默认推荐）
```

### 3. 上下文判断
```
上下文 < 20K：任意模型
上下文 20K-200K：qwen3.5-plus / qwen3-coder-plus / kimi-k2.5
上下文 > 200K：qwen3.5-plus（100 万）
```

---

## 🔄 手动切换命令

### 切换到编程模型
```bash
# 快速编程
openclaw config set agents.defaults.model.primary bailian/qwen3-coder-next

# 复杂编程
openclaw config set agents.defaults.model.primary bailian/qwen3-coder-plus
```

### 切换到推理模型
```bash
openclaw config set agents.defaults.model.primary bailian/qwen3-max-2026-01-23
```

### 切换回默认
```bash
openclaw config set agents.defaults.model.primary bailian/qwen3.5-plus
```

---

## 📝 使用建议

### 日常对话
- **推荐**：qwen3.5-plus
- **原因**：100 万上下文，多模态支持

### 编程任务
- **快速编程**：qwen3-coder-next（26 万上下文）
- **复杂编程**：qwen3-coder-plus（100 万上下文）

### 复杂推理
- **推荐**：qwen3-max-2026-01-23
- **原因**：最强推理能力

### 图像理解
- **推荐**：qwen3.5-plus 或 kimi-k2.5
- **原因**：支持多模态

### 长文本处理
- **推荐**：qwen3.5-plus（100 万上下文）
- **备选**：kimi-k2.5（26 万上下文）

---

## 🎯 智能推荐

### 官家常见任务
1. **项目管理** → qwen3.5-plus（长文档、多模态）
2. **软件测试** → qwen3.5-plus（通用）
3. **内容创作** → qwen3.5-plus（多模态）
4. **代码审查** → qwen3-coder-plus（100 万上下文）
5. **知识检索** → qwen3.5-plus（长上下文）

---

## 📊 成本优化

### 免费 vs 收费
- **百炼 Coding Plan Lite**：已配置，具体计费待确认
- **建议**：先用 qwen3.5-plus，根据实际成本调整

### Token 节省
- 使用 QMD 精准检索（节省 90%+ tokens）
- 避免全量读取大文件
- 优先使用快速模型处理简单任务

---

## 🔧 配置文件

### 当前配置（openclaw.json）
```json
"agents": {
  "defaults": {
    "model": {
      "primary": "bailian/qwen3.5-plus"
    }
  }
}
```

### 模型别名
```json
"bailian/qwen3.5-plus": {"alias": "Qwen3.5+"},
"bailian/qwen3-max-2026-01-23": {"alias": "Qwen3-Max"},
"bailian/qwen3-coder-next": {"alias": "Qwen-Coder-Next"},
"bailian/qwen3-coder-plus": {"alias": "Qwen-Coder+"},
"bailian/MiniMax-M2.5": {"alias": "MiniMax"},
"bailian/glm-5": {"alias": "Bailian-GLM5"},
"bailian/glm-4.7": {"alias": "Bailian-GLM4.7"},
"bailian/kimi-k2.5": {"alias": "Kimi"}
```

---

## 🚀 未来优化

### 自动切换（待实现）
- [ ] 创建任务类型识别脚本
- [ ] 实现自动模型切换
- [ ] 监控模型性能
- [ ] 记录切换日志

### 手动切换（当前）
- ✅ 定义切换规则
- ✅ 提供切换命令
- ⏸️ 等待实际使用反馈

---

*创建时间：2026-03-02 18:56*
*最后更新：2026-03-02 18:56*
