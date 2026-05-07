---
name: smart-model-switch
description: 智能模型选择技能 - AI驱动的最优模型决策
version: 1.4.2
author: zhaog100
---

# Smart Model Switch

## 🤖 核心功能

### 智能模型选择
- 根据消息复杂度自动选择最优模型
- AI驱动的负载均衡算法

### 文件类型检测
- 自动识别文档类型
- 选择合适的处理模型

### 成本追踪
- 实时监控各模型使用成本
- 优化资源分配策略

## 📊 配置参数

```json
{
  "complexity_threshold": 85,
  "cost_tracking": true,
  "auto_balance": true,
  "model_priority": ["longcat", "bailian", "gemini"]
}
```

## 🚀 使用方法

```bash
# 启动智能切换
smart-model-switch enable

# 查看模型状态
smart-model-switch status

# 手动选择模型
smart-model-switch select <model_name>
```
