# Meeting Minutes Generator

将会议文本（聊天记录/会议笔记）转为结构化会议纪要。零外部依赖，纯 Python 标准库实现。

## 触发场景

当用户需要：
- 将会议记录整理成纪要
- 从聊天记录中提取行动项
- 生成结构化的会议文档

## 用法

```python
from skills.meeting-minutes-generator.src.pipeline import generate_minutes

text = """
议题：Q1产品规划讨论
时间：2026-03-17 14:00
参与者：张三、李四、@王五

张三负责完成需求文档，下周五前提交。
李四跟进后端接口开发，明天完成。
"""

# 输出 Markdown 格式（默认）
markdown_output = generate_minutes(text)

# 输出纯文本
plain_output = generate_minutes(text, fmt="plain")

# 输出 JSON
json_output = generate_minutes(text, fmt="json")
```

## 输出结构

| 字段 | 说明 |
|------|------|
| meeting_info | 议题、时间、地点、参会人员 |
| summary | 会议概述（自动生成） |
| discussion_points | 讨论要点列表 |
| decisions | 决策记录 |
| action_items | 行动项（任务/负责人/截止日期/优先级） |

## 支持的格式

- **Markdown**（默认）：带标题和列表的结构化文档
- **Plain**：纯文本，适合粘贴到聊天
- **JSON**：结构化数据，适合程序处理

## 特性

- 中文会议场景优化
- 自动识别 @提及、负责人、截止日期
- 相对日期解析（明天/下周五/3天后等）
- 优先级推断（高/中/低）
- 零外部依赖

## 测试

```bash
python skills/meeting-minutes-generator/tests/test_all.py -v
```
