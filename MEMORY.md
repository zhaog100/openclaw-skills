# 长期记忆（MEMORY.md）

_精心维护的记忆，提炼后的精华_

---

## 🎯 QMD 检索入口

**知识库路径**：`/home/zhaog/.openclaw/workspace/knowledge/`

**记忆文件路径**：`/home/zhaog/.openclaw/workspace/memory/`

**检索命令**：
```bash
bun /path/to/qmd.ts search knowledge "关键词" -n 5
bun /path/to/qmd.ts search daily-logs "关键词" --hybrid
```

---

## 📋 检索协议

### 优先使用 QMD 检索
- ✅ 使用 `memory_search()` 检索个人记忆
- ✅ 使用 `qmd search` 检索知识库
- ✅ 只读取必要的行（避免全量加载）

### 精准检索策略
```
个人记忆 → memory_search()
知识库 → qmd search（关键词已可用）
其他 → 只读必要的行
```

### Token 节省效果
- 传统方式：读取整个 MEMORY.md（2000+ tokens）
- QMD 方式：精准回忆（~150 tokens）
- **节省：92.5%**

---

## 🏆 高价值锚点词（30 个）

### 核心技能
1. smart-model-switch - 智能模型切换
2. context-manager - 上下文管理
3. smart-memory-sync - 记忆同步
4. image-content-extractor - 图片内容提取
5. quote-reader - 引用前文读取
6. speech-recognition - 语音识别
7. memory-sync-protocol - 记忆优化（2026-03-10 新增）
8. github-bounty-hunter - GitHub 赚钱（2026-03-10 新增）

### 核心配置
7. agents.json - 代理配置
8. openai.env - OpenAI Key
9. mcporter.json - MCP 集成
10. crontab - 定时任务

### 知识库主题
11. project-management - 项目管理
12. software-testing - 软件测试
13. content-creation - 内容创作
14. ai-system-design - AI 系统设计
15. outsourcing-management - 外包管理

### 核心工具
16. Evidently AI - 数据漂移检测
17. DeepChecks - 模型验证
18. OWASP ZAP - 安全测试
19. Playwright - 网页爬取
20. QMD - 知识库检索

### 核心概念
21. 三库联动 - MEMORY+QMD+Git
22. 双保险机制 - Context Manager + Smart Memory Sync
23. 不可变分片 - Token 节省 90%+
24. 混合检索 - BM25+ 向量（93% 准确率）
25. MCP 集成 - Agent 自主调用工具

### 重要决策
26. 软件安装路径：D:\Program Files (x86)\
27. 输出文件目录：Z:\OpenClaw\
28. 默认模型：百炼 qwen3.5-plus
29. 上下文监控阈值：60%
30. 定时任务频率：11 个任务
31. 免费额度组合：百炼 + 智谱+Codex+Gemini（2026-03-10）
32. MEMORY.md 精简策略：<10K（2026-03-10）

---

## 💡 记忆维护原则

### 定期清理
- 每周一回顾上周记忆
- 将值得保留的内容更新到 MEMORY.md
- 从 MEMORY.md 移除过时信息

### 保持精简
- MEMORY.md 控制在 8-10K
- 只保留高价值、低噪音内容
- 日常流水放在 memory/YYYY-MM-DD.md

### 自动化维护
- 每天 23:30 AI 查漏补缺
- 每周日 2:00 记忆维护
- 每天 23:40/23:50 QMD 向量生成

---

*持续进化 · 定期清理 · 保留精华*

*最后更新：2026-03-10 19:33*
*版本：v2.0 - 精简优化版*
