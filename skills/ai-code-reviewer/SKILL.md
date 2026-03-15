# AI 代码审查助手（ai-code-reviewer）

**版本**：v1.0  
**创建时间**：2026-03-15  
**创建者**：小米粒（Dev 代理）🌾  
**状态**：开发中（Phase 1）

---

## 📋 简介

AI 代码审查助手是一个基于本地 AI 模型的代码质量自动检测工具，支持 5 层代码质量检查。

---

## 🎯 核心功能

### Phase 1（MVP）
- ✅ 代码质量检测（5 层检查）
- ✅ 改进建议生成（基于规则）
- ✅ Markdown 报告输出
- ⏳ 协作系统集成（Phase 2）

### 5 层检查
1. **语法检查**：tree-sitter 解析（Phase 2）
2. **代码规范**：命名规范、格式规范
3. **逻辑检查**：潜在 bug、死代码（Phase 2）
4. **性能检查**：时间复杂度、内存泄漏（Phase 2）
5. **安全检查**：SQL 注入、XSS 漏洞、硬编码密码

---

## 🚀 使用方法

### CLI 方式
```bash
# 审查单个文件
code-review.sh test.py

# 审查目录
code-review.sh src/

# 输出报告到文件
code-review.sh -o report.md test.py
```

### Python 方式
```python
from lib.core.quality_detector import CodeQualityDetector

detector = CodeQualityDetector()
issues = detector.detect('test.py')
```

---

## 📊 性能指标

| 指标 | 目标 | 当前状态 |
|------|------|---------|
| 检测速度 | <5 秒/文件 | ✅ 已实现 |
| 准确率 | >90% | ⏳ Phase 2 实现 |
| 误报率 | <10% | ⏳ Phase 2 实现 |
| 内存占用 | <500MB | ✅ 已实现 |

---

## 📅 开发计划

### Phase 1（MVP）- 2026-03-16 ~ 2026-03-18
- ✅ CodeQualityDetector 基础框架
- ⏳ tree-sitter 集成
- ✅ 5 层检查基础实现
- ✅ SuggestionGenerator
- ✅ ReportGenerator
- ✅ CLI 入口

### Phase 2（集成）- 2026-03-19 ~ 2026-03-21
- ⏳ AIEngine 集成
- ⏳ AI 辩论机制
- ⏳ IntegrationManager
- ⏳ 协作系统集成

---

## 📝 许可证

MIT License

---

*最后更新：2026-03-15 23:45*
