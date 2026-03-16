---
name: ai-deterministic-control
description: AI 确定性控制工具。管理 temperature/top_p/seed 参数，多场景预设，一致性检查（编辑距离+TF-IDF），监控趋势分析与异常检测，模型参数注入与恢复。
---

# AI 确定性控制工具（ai-deterministic-control）

**版本**: v1.0.0  
**作者**: 思捷娅科技 (SJYKJ)  
**许可**: MIT License  

---

## 🎯 功能概述

控制 AI 模型的随机性，确保输出的确定性和一致性。

### 核心能力
- **参数管理**: temperature / top_p / seed 精确控制
- **场景预设**: 6 个内置预设（代码生成、配置生成、对话、创意写作、数据分析、翻译）
- **一致性检查**: Levenshtein 编辑距离 + TF-IDF 语义相似度，综合评分告警
- **监控引擎**: 滑动窗口趋势分析 + Z-score 异常检测
- **模型桥接**: 自动备份 → 注入参数 → JSON 验证 → 失败恢复

---

## 📋 CLI 命令

```bash
# 设置参数
detcontrol set --temp 0.1 --top-p 0.85 --seed 42

# 应用预设
detcontrol preset apply code_generation
detcontrol preset list

# 一致性检查
detcontrol check --prompt "写一个排序函数" --samples 5

# 监控报告
detcontrol report --format markdown --days 7
detcontrol monitor trend
detcontrol monitor anomalies

# 参数注入到 openclaw.json
detcontrol inject --model glm-5

# 恢复默认参数
detcontrol reset --all
```

### 预设列表

| 预设 | Temperature | 说明 |
|------|------------|------|
| code_generation | 0.1 | 代码/SQL/正则生成 |
| config_generation | 0.2 | JSON/YAML 配置文件 |
| data_analysis | 0.15 | 数据分析报告 |
| translation | 0.1 | 翻译任务 |
| conversation | 0.5 | 日常对话 |
| creative_writing | 0.8 | 创意写作/头脑风暴 |

---

## 🔧 信号文件联动

预设应用时自动生成 `~/.openclaw/workspace/.detcontrol_signal.json`，供 `smart-model-switch` 读取。

---

## 📐 算法

- **字符相似度**: Levenshtein 编辑距离（纯 Python）
- **语义相似度**: TF-IDF 余弦相似度（纯本地，无外部依赖）
- **综合评分**: 0.4 × 字符相似度 + 0.6 × 语义相似度
- **告警阈值**: ≥0.8 OK | 0.6-0.8 WARN | <0.6 CRITICAL
- **异常检测**: Z-score > 2.0

---

*Copyright © 2026 思捷娅科技 (SJYKJ). All rights reserved.*

---

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/xiaomili-skills
- ClawHub: https://clawhub.com
- 创建者: 思捷娅科技 (SJYKJ)

**商业使用授权**：
- 个人/开源：免费
- 小微企业（<10人）：¥999/年
- 中型企业（10-50人）：¥4,999/年
- 大型企业（>50人）：¥19,999/年
- 企业定制版：¥99,999一次性（源码买断）
