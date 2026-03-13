# 技术短缺发现 - 飞书事件订阅冲突

**时间**：2026-03-13 15:42
**官家问题**：一个回调URL只能被一个Bot使用

---

## 🚨 问题

- ❌ 一个回调URL只能被一个Bot使用
- ❌ 如果小米辣也用，小米粒会失效
- ❌ 两个Bot会冲突

---

## 🔧 解决方案

### 方案B：同一URL，区分Bot身份（推荐）✅

**实现**：
```python
# 根据app_id区分Bot
app_id = data.get("header", {}).get("app_id")

if app_id == "cli_a92cdc08bff8dcd3":
    # 小米辣的Bot
    return handle_xiaomila_callback(data)
elif app_id == "cli_a939da914df99cbd":
    # 小米粒的Bot
    return handle_xiaomili_callback(data)
```

**优点**：
- ✅ 只需要一个URL
- ✅ 两个Bot都能用
- ✅ 官家可以同时和两个Bot对话
- ✅ 5分钟实现

---

## 📊 实现步骤

1. 修改main.py（5分钟）
2. 小米辣配置飞书（2分钟）
3. 测试（5分钟）

**总时间**：12分钟

---
*小米粒 - 2026-03-13 15:42*
