---
name: context-manager-v2
description: 高级上下文管理技能 - 自动会话切换、token监控、启动优化
version: 2.2.2
author: zhaog100
---

# Context Manager V2

## 🌟 核心功能

### 无感自动切换
- 监控上下文使用率超过60%时自动创建新会话
- 完全零用户干预的自动化管理

### 真实API监控  
- 精确计算token使用率
- 分层读取优化，节省90%token

### 启动优化
- 智能分层读取策略
- 预加载常用资源

## 📊 配置参数

```json
{
  "threshold": 60,
  "auto_switch": true,
  "monitor_interval": 10,
  "save_tokens": 90
}
```

## 🚀 使用方法

```bash
# 启动监控
context-manager start

# 查看状态
context-manager status

# 手动切换
context-manager switch
```
