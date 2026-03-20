# Token优化集成方案

_2026-03-07 14:04_

---

## 📋 集成目标

将Token优化器集成到现有工作流：
1. **Context Monitor**（上下文监控）→ 集成Token追踪
2. **工具调用流程** → 集成缓存+预算监控
3. **定期审计** → 自动运行优化检查

---

## 🔧 集成点

### 1. Context Monitor集成

**文件位置**：`skills/miliger-context-manager/`

**集成方式**：
- 在context-monitor.sh中添加Token统计
- 在stop-reason监控中添加浪费识别

**代码示例**：
```python
# 在context-monitor中添加
from tools.token_optimizer import TokenOptimizer

optimizer = TokenOptimizer()

# 每次监控时统计Token分类
def monitor_with_token_tracking():
    # 原有监控逻辑
    context_usage = check_context_usage()

    # 新增：Token分类统计
    token_stats = optimizer.get_category_stats()

    # 生成综合报告
    report = {
        "context": context_usage,
        "tokens": token_stats
    }

    return report
```

---

### 2. 工具调用流程集成

**集成点**：所有工具调用前后

**集成方式**：
- 调用前：检查预算
- 调用后：记录统计

**代码示例**：
```python
from tools.token_optimizer import TokenBudgetMonitor, ToolCallCache

monitor = TokenBudgetMonitor(max_tokens=200)
cache = ToolCallCache(ttl_seconds=3600)

def optimized_tool_call(tool_name, params):
    # 1. 检查预算
    is_valid, message = monitor.check_tool_call(tool_name, params)
    if not is_valid:
        print(f"⚠️ {message}")
        return None

    # 2. 检查缓存
    cached_result = cache.get(tool_name, params)
    if cached_result:
        print("✅ 从缓存获取")
        return cached_result

    # 3. 执行工具调用
    result = execute_tool(tool_name, params)

    # 4. 缓存结果
    cache.set(tool_name, params, result)

    return result
```

---

### 3. 定期审计集成

**集成方式**：定时任务

**Cron配置**：
```bash
# 每周一10:00运行Token审计
0 10 * * 1 python3 /root/.openclaw/workspace/tools/token-optimizer/token_optimizer.py

# 每天清理过期缓存
0 0 * * * python3 /root/.openclaw/workspace/tools/token-optimizer/tool_call_cache.py
```

---

## 📊 预期效果

| 集成点 | 效果 |
|--------|------|
| Context Monitor | 实时Token追踪，发现浪费点 |
| 工具调用流程 | 缓存复用，减少重复调用 |
| 定期审计 | 持续优化，监控效果 |

---

## 🚀 实施步骤

1. ✅ **修改Context Monitor**（添加Token追踪）
2. ✅ **创建工具调用包装器**（集成缓存+预算）
3. ✅ **配置定时任务**（自动审计）
4. ✅ **更新MEMORY.md**（记录集成）
5. ✅ **Git提交**（保存集成）

---

## 🔍 监控指标

**关键指标**：
- Token分类比例（人类/机器）
- 缓存命中率（目标>60%）
- 预算超限次数（目标<5次/周）
- JSON错误率（目标<3%）

**报告频率**：
- 实时：预算超限警告
- 每周：Token审计报告
- 每月：优化效果总结

---

*最后更新：2026-03-07*
