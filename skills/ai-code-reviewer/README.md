# AI 代码审查助手

> 基于本地 AI 模型的代码质量自动检测工具

---

## 🎯 功能特性

- **5 层代码质量检查**：语法、规范、逻辑、性能、安全
- **改进建议生成**：基于规则/AI 生成可执行的改进建议
- **Markdown 报告输出**：清晰易读的审查报告
- **纯本地执行**：无需外部 API，代码不上传云端

---

## 🚀 快速开始

### 安装
```bash
cd skills/ai-code-reviewer
pip install -r requirements.txt  # Phase 2 需要
```

### 使用
```bash
# 审查单个文件
./bin/code-review.sh test.py

# 审查目录
./bin/code-review.sh src/

# 输出报告到文件
./bin/code-review.sh -o report.md test.py
```

---

## 📊 示例输出

```markdown
# 代码审查报告

**审查时间**：2026-03-15 23:45:00
**审查文件**：test.py

## 摘要
- **文件数**：1
- **问题总数**：3
- **严重程度**：高

## 详细问题
### 安全问题（1 个）
**1. 检测到硬编码密码**
- 行号：10
- 严重程度：high

## 改进建议
**1. 使用环境变量或配置文件存储密码**
- 优先级：high

```python
import os
password = os.getenv('DB_PASSWORD')
```
```

---

## 📅 开发计划

- [x] Phase 1（MVP）：基础功能
- [ ] Phase 2（集成）：AI 引擎 + 协作系统

---

## 📝 许可证

MIT License
