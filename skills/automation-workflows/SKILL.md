---
name: automation-workflows
description: Design and implement automation workflows to save time and scale operations as a solopreneur. Use when identifying repetitive tasks to automate, building workflows across tools, setting up triggers and actions, or optimizing existing automations. Trigger on "automate", "automation", "workflow automation", "save time", "reduce manual work", "no-code automation".
---

# Automation Workflows

个人创业者自动化工作流设计指南。

## 📊 Step 1: 识别自动化机会

- 记录一周所有任务，计算 Time Cost = (分钟×频率)/60
- 好候选：重复、规则化、高频、耗时10+分钟的任务
- ROI：回本<3个月值得做，>6个月不值得

## 🛠️ Step 2: 选择工具

| 工具 | 适合 | 价格 | 学习曲线 |
|------|------|------|----------|
| **Zapier** | 简单2-3步 | $20-50/月 | 低 |
| **Make** | 可视化多步 | $9-30/月 | 中 |
| **n8n** | 复杂/自托管 | 免费/月 | 高 |

**建议**：从Zapier开始，遇到限制后升级到Make或n8n

## 📋 Step 3: 设计工作流

```
TRIGGER → CONDITIONS(可选) → ACTIONS → ERROR HANDLING
```

## 🔧 Step 4: 构建测试

1. 连接账户 → 2. 测试触发器 → 3. 添加动作映射字段 → 4. 测试边缘情况 → 5. 开启

## 📈 Step 5: 监控维护

- 每周5分钟：扫描错误日志
- 每月15分钟：审计工作流，清理无用

## ⚠️ 常见错误

- 先优化流程再自动化（不要自动化烂流程）
- 不要过度自动化
- 始终配置错误通知
- 充分测试后再上线

> 详细的步骤说明、高级工作流示例见 `references/skill-details.md`
