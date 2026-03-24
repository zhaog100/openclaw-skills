# OpenClaw Workspace 结构化索引

**更新时间**: 2026-03-21 21:30  
**版本**: v1.0

---

## 📁 目录结构

```
workspace/
├── 📄 核心文档
│   ├── README.md          # 项目说明
│   ├── INDEX.md           # 总索引
│   ├── INDEX_STRUCTURE.md # 结构化索引（本文件）
│   ├── SOUL.md            # 身份定义
│   ├── IDENTITY.md        # 身份信息
│   ├── USER.md            # 用户信息
│   ├── AGENTS.md          # Agent 规范
│   ├── HEARTBEAT.md       # 心跳检查清单
│   └── MEMORY.md          # 长期记忆
│
├── 📚 知识库 (docs/)
│   ├── products/          # 产品 PRD
│   ├── plans/             # 项目计划
│   ├── reports/           # 报告文档
│   └── learning/          # 学习资料
│
├── 🤖 技能库 (skills/)
│   ├── multi-article-scraper/    # 多平台爬取技能
│   ├── github-bounty-hunter/     # GitHub 赏金猎人
│   ├── agent-collab-platform/    # Agent 协作平台
│   └── ... (共 52 个技能)
│
├── 📝 记忆库 (memory/)
│   ├── INDEX.md           # 记忆索引
│   ├── README.md          # 记忆说明
│   ├── 2026-03-10.md      # 每日记忆
│   ├── 2026-03-11.md
│   ├── ...
│   └── 2026-03-21.md      # 最新记忆
│
├── 🎯 Agent 工作区 (agents/)
│   ├── xiaomila-pm/       # PM Agent
│   └── xiaomila-dev/      # Dev Agent
│
└── 📊 其他
    ├── qmd/               # QMD 知识库
    └── scripts/           # 工具脚本
```

---

## 📊 统计数据

| 类别 | 数量 | 说明 |
|------|------|------|
| **技能** | 52 个 | 包含爬取、论坛、Bounty 等 |
| **记忆文件** | 17 个 | 2026-03-10 至今 |
| **文档** | 100+ | docs/目录 |
| **Git 提交** | 200+ | 历史提交记录 |

---

## 🔍 快速索引

### 技能索引
- [多平台爬取技能](skills/multi-article-scraper/) - 微信/小红书/Dev.to/Hacker News
- [论坛冲浪功能](skills/multi-article-scraper/scripts/forum_scraper.py) - Dev.to + Hacker News
- [小红书爬取](skills/multi-article-scraper/scripts/xiaohongshu_scraper.py) - 小红书笔记
- [GitHub 赏金猎人](skills/github-bounty-hunter/) - Bounty 自动收割

### 文档索引
- [产品 PRD](docs/products/) - 产品需求文档
- [项目计划](docs/plans/) - 项目计划文档
- [报告文档](docs/reports/) - 各类报告

### 记忆索引
- [记忆总览](memory/INDEX.md) - 记忆文件索引
- [最新记忆](memory/2026-03-21.md) - 今日记忆

---

## 📝 更新日志

### 2026-03-21
- ✅ 整理记忆文件（17 个）
- ✅ 整理知识库索引
- ✅ 整理 Git 仓库
- ✅ 创建结构化索引文档

---

*最后更新：2026-03-21 21:30*  
*维护者：小米辣 (PM + Dev)*
