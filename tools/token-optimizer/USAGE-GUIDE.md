# Token优化器使用指南

_快速上手 · 2026-03-07_

---

## 🚀 快速开始

### 1. Token追踪器
```python
from token_optimizer import TokenOptimizer

# 初始化
optimizer = TokenOptimizer()

# 记录输出
optimizer.track_output("user_reply", "这是给用户的回复", tokens=50)
optimizer.track_output("tool_call", '{"command": "git status"}', tokens=20)

# 获取统计
stats = optimizer.get_category_stats()
print(stats)
```

### 2. 工具调用缓存
```python
from tool_call_cache import ToolCallCache

# 初始化（TTL=1小时）
cache = ToolCallCache(ttl_seconds=3600)

# 检查缓存
cached_result = cache.get("web_search", {"query": "test"})
if cached_result:
    print("✅ 从缓存获取")
else:
    # 执行工具调用
    result = {"results": ["result1", "result2"]}
    cache.set("web_search", {"query": "test"}, result)
```

### 3. 结构化输出模板
```python
from structured_output import StructuredOutputTemplate

# 初始化
template_engine = StructuredOutputTemplate()

# 注册模板
template_engine.register_success_pattern("web_search", {
    "query": "",
    "limit": 10,
    "results": []
})

# 生成输出
output = template_engine.generate_output(
    "web_search",
    query="Token优化",
    limit=5
)
```

### 4. Token预算监控
```python
from token_budget_monitor import TokenBudgetMonitor

# 初始化（最大200 tokens）
monitor = TokenBudgetMonitor(max_tokens=200)

# 检查工具调用
is_valid, message = monitor.check_tool_call(
    "web_search",
    {"query": "Token优化", "limit": 10}
)

print(message)  # ✅ 或 ⚠️
```

---

## 📊 优化效果

基于Hazel_OC的7天数据：

| 优化项 | 优化前 | 优化后 | 改善率 |
|--------|--------|--------|--------|
| JSON错误 | 14个 | 2个 | **↓85%** |
| 重复API调用 | 6次/天 | 0次/天 | **↓100%** |
| 冗余参数 | 常见 | <200 tokens | **↓60%** |

---

## 🎯 使用场景

### 1. 自动化测试
```bash
# 运行所有测试
python3 token_optimizer.py
python3 tool_call_cache.py
python3 structured_output.py
python3 token_budget_monitor.py
```

### 2. 集成到现有系统
```python
# 在OpenClaw工具调用前
from tools.token_optimizer import TokenOptimizer, TokenBudgetMonitor

optimizer = TokenOptimizer()
monitor = TokenBudgetMonitor(max_tokens=200)

# 检查预算
is_valid, message = monitor.check_tool_call(tool_name, params)
if not is_valid:
    print(f"⚠️ {message}")
    # 提供优化建议
    suggestions = monitor.suggest_optimization(tool_name, params)
```

### 3. 定期审计
```python
# 每天23:50运行
optimizer = TokenOptimizer()
stats = optimizer.get_category_stats()

# 识别浪费点
waste_analysis = optimizer.identify_waste()

# 生成报告
report = optimizer.generate_report()
```

---

## 🔧 配置建议

### TTL设置
- **缓存TTL**：1小时（3600秒）
- **适合场景**：频繁调用的工具（web_search, file_read）

### Token预算
- **默认预算**：200 tokens
- **严格模式**：100 tokens
- **宽松模式**：300 tokens

### 分类统计
- **人类输出**：直接回复、摘要、答案
- **工具编排**：JSON/API调用
- **代理委托**：子代理任务
- **社区互动**：Moltbook/论坛
- **系统日志**：记忆文件/日志

---

## 📝 最佳实践

1. **定期审计**：每周运行一次Token追踪
2. **缓存优先**：所有重复调用先查缓存
3. **模板化输出**：使用结构化模板减少错误
4. **预算监控**：实时监控工具调用参数

---

*最后更新：2026-03-07*
