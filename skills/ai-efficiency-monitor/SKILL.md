---
name: ai-efficiency-monitor
description: AI效率监控工具。监控AI任务执行效率，识别浪费模式（重复查询/过长上下文/无效重试/过度生成/低质量循环），生成优化建议和成本节省报告。支持OpenClaw日志解析、多模型成本计算、ASCII趋势图。
---

# AI Efficiency Monitor (aiemon)

**版本**: v1.1.0 | **创建者**: 思捷娅科技 (SJYKJ) | **日期**: 2026-03-16

## 🎯 功能概述

监控 AI 任务执行效率，识别浪费模式，生成优化建议和成本节省报告。

### 核心能力
- **数据收集**: 解析 OpenClaw 日志，提取 Token 用量、API 调用、执行时间
- **浪费模式识别**: 5 种内置模式检测（重复查询/过长上下文/无效重试/过度生成/低质量循环）
- **成本计算**: 多模型价格表（智谱/DeepSeek/OpenAI 等）
- **报告生成**: Markdown/JSON 格式，含 ASCII 趋势图
- **趋势分析**: 日/周/月效率趋势

## 📦 安装

```bash
# 确保 error-handler 已就绪
source ~/.openclaw/workspace/skills/utils/error-handler.sh
```

## 🚀 CLI 使用

```bash
# 收集数据（从 OpenClaw 日志）
aiemon collect --source openclaw --days 7

# 分析浪费模式
aiemon analyze --patterns all

# 生成报告
aiemon report --format markdown --days 7
aiemon report --format json --days 30

# 计算成本
aiemon cost --model glm-5-turbo --tokens 10000

# 趋势分析
aiemon trends --days 30

# 列出内置模式
aiemon patterns list
```

## 📁 文件结构

```
ai-efficiency-monitor/
├── SKILL.md              # 本文档
├── aiemon                # CLI 入口
├── src/
│   ├── collector.sh      # 数据收集
│   ├── analyzer.sh       # 浪费模式分析
│   ├── reporter.sh       # 报告生成
│   ├── cost_calc.sh      # 成本计算（含模型价格表+上下文字典）
│   ├── patterns_list.sh  # 模式列表展示
│   └── patterns/
│       └── definitions.sh # 浪费模式定义（5种模式）
├── data/                 # 运行时数据
├── tests/test_all.sh
└── package.json
```

## 📄 许可证与版权声明
MIT License
Copyright (c) 2026 思捷娅科技 (SJYKJ)
免费使用、修改和重新分发时，需注明出处。
出处：GitHub: https://github.com/zhaog100/xiaomili-skills | ClawHub: https://clawhub.com | 创建者: 思捷娅科技 (SJYKJ)
商业使用授权：个人免费 | 小微¥999/年 | 中型¥4,999/年 | 大型¥19,999/年
