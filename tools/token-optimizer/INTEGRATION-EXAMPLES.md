# Token优化器集成示例

_展示如何在实际场景中使用优化器_

---

## 🔧 集成示例

### 示例1：Web搜索工具

```python
from tools.token_optimizer.optimized_tool_call import OptimizedToolCall

# 创建优化器
optimizer = OptimizedToolCall()

# 执行Web搜索（第一次调用）
result1 = optimizer.call(
    "web_search",
    {"query": "PMP认证", "limit": 10},
    executor=web_search_function  # 你的实际搜索函数
)
# 输出：⚙️ 执行工具调用: web_search
#       ✅ 结果已缓存: web_search

# 重复搜索（从缓存获取）
result2 = optimizer.call(
    "web_search",
    {"query": "PMP认证", "limit": 10}
)
# 输出：✅ 从缓存获取结果: web_search
```

---

### 示例2：文件读取工具

```python
from tools.token_optimizer.optimized_tool_call import OptimizedToolCall

optimizer = OptimizedToolCall()

# 读取文件（带预算检查）
result = optimizer.call(
    "file_read",
    {
        "path": "/knowledge/README.md",
        "offset": 0,
        "limit": 1000
    },
    executor=read_file_function  # 你的实际读取函数
)

# 如果参数过大（超过200 tokens）
large_result = optimizer.call(
    "file_read",
    {
        "path": "/huge/file.txt",
        "content": "very long content..." * 100  # 超长内容
    }
)
# 输出：⚠️ 工具调用 'file_read' 参数超预算：350 tokens > 200 tokens
#       💡 参数 'content' 过长（3500 字符），考虑精简
```

---

### 示例3：集成到Context Monitor

```python
# 在 context-monitor.sh 中添加

import sys
sys.path.append('/root/.openclaw/workspace/tools/token-optimizer')
from token_optimizer import TokenOptimizer

def monitor_with_token_tracking():
    # 原有上下文监控
    context_usage = check_context_usage()

    # 新增：Token分类统计
    optimizer = TokenOptimizer()

    # 统计最近一小时的输出
    recent_outputs = get_recent_outputs(hours=1)
    for content, context in recent_outputs:
        category = optimizer.classify_output(content, context)
        tokens = optimizer.count_tokens(content)
        optimizer.categories[category] += tokens
        optimizer.total_tokens += tokens

    # 生成报告
    stats = optimizer.get_category_stats()

    # 发送飞书通知
    send_notification(
        title="📊 上下文+Token监控",
        content=f"""
上下文使用率: {context_usage}%
Token分类统计:
- 人类输出: {stats['human']}%
- 工具编排: {stats['tool_orchestration']}%
- 代理委托: {stats['agent_delegation']}%
- 社区互动: {stats['community']}%
- 系统日志: {stats['logs']}%
        """
    )
```

---

### 示例4：全局集成

```python
# 在 AGENTS.md 或启动脚本中添加

from tools.token_optimizer.optimized_tool_call import get_optimizer

# 获取全局优化器
optimizer = get_optimizer()

# 所有工具调用都通过优化器
def safe_tool_call(tool_name, params):
    return optimizer.call(tool_name, params, executor=actual_executor)
```

---

## 📊 监控效果

### 实时监控

```python
# 查看实时统计
stats = optimizer.get_stats()

print("Token分类：")
for category, percentage in stats['token_stats'].items():
    print(f"  {category}: {percentage}%")

print(f"\n缓存命中：{stats['cache_stats']['total_entries']} 个")
print(f"预算警告：{stats['budget_stats']['total_alerts']} 次")
```

---

## 🚀 最佳实践

1. **全局使用**：所有工具调用都通过优化器
2. **定期审计**：每周运行一次完整审计
3. **监控指标**：关注缓存命中率和预算超限次数
4. **持续优化**：根据审计结果调整策略

---

*最后更新：2026-03-07*
