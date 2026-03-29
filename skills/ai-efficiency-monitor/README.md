# AI Efficiency Monitor (aiemon)

> 📊 监控 AI 任务执行效率，识别浪费模式，节省 API 成本

**版本**: v1.0.0 | **创建者**: 思捷娅科技 (SJYKJ) | **日期**: 2026-03-16

## 📋 简介

AI Efficiency Monitor 是一个专门用于监控 AI 任务执行效率的工具。通过分析 OpenClaw 日志，识别浪费模式（重复查询、过长上下文、无效重试等），生成优化建议和成本节省报告。

## ✨ 核心特性

- 📈 **数据收集** - 解析 OpenClaw 日志，提取 Token 用量、API 调用、执行时间
- 🔍 **浪费识别** - 5 种内置浪费模式检测
- 💰 **成本计算** - 多模型价格表（智谱/DeepSeek/OpenAI 等）
- 📊 **报告生成** - Markdown/JSON 格式，含 ASCII 趋势图
- 📉 **趋势分析** - 日/周/月效率趋势
- 💡 **优化建议** - 针对性改进方案

## 🚀 快速开始

### 运行效率分析

```bash
cd $(pwd)/skills/ai-efficiency-monitor
./aiemon analyze --date 2026-03-16
```

### 生成成本报告

```bash
./aiemon report --format markdown --output report.md
```

### 查看实时状态

```bash
./aiemon status
```

## 📖 CLI 命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `analyze` | 分析指定日期的 AI 任务 | `aiemon analyze --date 2026-03-16` |
| `report` | 生成效率报告 | `aiemon report --format markdown` |
| `status` | 查看当前状态 | `aiemon status` |
| `cost` | 计算 API 成本 | `aiemon cost --model qwen3.5-plus` |
| `waste` | 识别浪费模式 | `aiemon waste --threshold 50` |

## 📦 安装

```bash
# 克隆或复制到本地
cd $(pwd)/skills/ai-efficiency-monitor

# 添加执行权限
chmod +x aiemon

# 安装依赖（Python 版本）
pip install -r requirements.txt
```

## 🧪 测试

```bash
# 运行完整测试
cd tests/
bash test_all.sh
```

## 📁 项目结构

```
ai-efficiency-monitor/
├── aiemon              # 主脚本
├── package.json        # 包配置
├── SKILL.md           # 技能文档
├── README.md          # 使用说明
├── src/               # 源代码
│   ├── analyzer.py    # 分析器
│   ├── waste.py       # 浪费检测
│   ├── cost.py        # 成本计算
│   └── report.py      # 报告生成
├── data/              # 数据
│   ├── prices.json    # 模型价格表
│   └── patterns.json  # 浪费模式定义
└── tests/             # 测试
    └── test_all.sh
```

## 🎯 浪费模式检测

### 1️⃣ 重复查询
检测相同的查询在短时间内的重复执行。

```
⚠️ 发现 3 次重复查询 "如何配置 QMD"
💡 建议：添加查询缓存，TTL=5 分钟
💰 节省：约 150 tokens/次
```

### 2️⃣ 过长上下文
检测超出必要长度的上下文窗口。

```
⚠️ 上下文窗口 100K，实际使用 12K
💡 建议：使用自适应上下文管理
💰 节省：约 88K tokens
```

### 3️⃣ 无效重试
检测因网络错误等原因的重复 API 调用。

```
⚠️ 发现 5 次无效重试（API rate limit）
💡 建议：添加指数退避重试策略
💰 节省：约 500 tokens/次
```

### 4️⃣ 过度生成
检测生成长度远超需求的响应。

```
⚠️ 用户问"在吗"，AI 回复 800 tokens
💡 建议：根据问题复杂度调整 max_tokens
💰 节省：约 750 tokens
```

### 5️⃣ 低质量循环
检测因质量不佳导致的重复生成。

```
⚠️ 同一任务重复生成 4 次（质量不达标）
💡 建议：优化 prompt 或提高 temperature
💰 节省：约 3000 tokens
```

## 💡 使用示例

### 示例 1：分析今日效率

```bash
./aiemon analyze --date today --output today_report.md
```

输出：
```
📊 AI 效率报告 - 2026-03-16

总任务数：88
总 Token 消耗：125,430
总成本：¥12.54

浪费检测：
- 重复查询：3 次（浪费 450 tokens）
- 过长上下文：2 次（浪费 176K tokens）
- 无效重试：5 次（浪费 2,500 tokens）

优化建议：
1. 启用查询缓存（预计节省 15%）
2. 使用自适应上下文（预计节省 40%）
3. 添加重试退避策略（预计节省 8%）

预计每月节省：¥150+
```

### 示例 2：计算模型成本

```bash
./aiemon cost --model qwen3.5-plus --tokens 100000
```

输出：
```
模型：qwen3.5-plus
输入：100,000 tokens
输出：¥10.00（输入 ¥0.0001/1K tokens）
```

### 示例 3：生成趋势图

```bash
./aiemon report --format ascii --days 7
```

输出：
```
Token 使用趋势（最近 7 天）

3 月 10 日  ████████████░░░░░░░░  85K
3 月 11 日  ██████████████░░░░░░  95K
3 月 12 日  ████████████████████  142K ⭐
3 月 13 日  ██████████████░░░░░░  98K
3 月 14 日  ████████████░░░░░░░░  88K
3 月 15 日  ██████████████████░░  128K
3 月 16 日  ████████████████████  145K ⭐

平均：111K/天
趋势：+12% 📈
```

## 📊 模型价格表

| 模型 | 输入价格 | 输出价格 | 提供商 |
|------|---------|---------|--------|
| qwen3.5-plus | ¥0.0001/1K | ¥0.0001/1K | 百炼 |
| glm-5 | ¥0.00005/1K | ¥0.00015/1K | 智谱 |
| deepseek-chat | ¥0.0001/1K | ¥0.0002/1K | DeepSeek |
| gpt-4o | ¥0.00035/1K | ¥0.00105/1K | OpenAI |
| claude-3-sonnet | ¥0.00022/1K | ¥0.00066/1K | Anthropic |

*价格仅供参考，以官方为准*

## 📄 许可证

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/xiaomila-skills
- ClawHub: https://clawhub.com
- 创建者：思捷娅科技 (SJYKJ)

**商业使用授权**：
- 小微企业（<10 人）：¥999/年
- 中型企业（10-50 人）：¥4,999/年
- 大型企业（>50 人）：¥19,999/年
- 企业定制版：¥99,999 一次性（源码买断）

详情请查看：[LICENSE](../../LICENSE)

---

*aiemon - 让 AI 使用更高效* 💡
