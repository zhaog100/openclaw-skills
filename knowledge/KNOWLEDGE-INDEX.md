# 📚 知识库索引

_最后更新: 2026-04-01_

---

## 🗂️ 知识库结构

```
knowledge/
├── bounty/                    # Bounty系统知识
│   ├── strategies/            # 策略文档
│   │   ├── auto-workflow.md   # ⭐ 自动工作流程
│   │   ├── filters.md         # 过滤策略
│   │   └── scoring.md         # 评分算法
│   └── templates/             # 标准模板
│       └── SECURITY.md        # 安全文档模板
│
├── github-bounty/             # GitHub Bounty实现
│   ├── implementation.md      # 实现细节
│   ├── lessons-learned.md     # 经验教训
│   └── best-practices.md      # 最佳实践
│
├── multi-agent-collaboration/ # 多智能体协作
│   ├── MULTI_AGENT_BEST_PRACTICES.md
│   └── patterns.md            # 协作模式
│
├── software-testing/          # 软件测试
│   ├── testing-projects/      # 测试项目
│   └── test-management/       # 测试管理
│
└── tools/                     # 工具指南
    ├── plantuml-guide.md      # PlantUML使用
    └── openclaw-sessions-api.md # OpenClaw API
```

---

## 📌 核心知识点

### 1. Bounty 系统

#### 🎯 自动工作流 (⭐ 重要)
- **位置**: `bounty/strategies/auto-workflow.md`
- **用途**: 定义自动完成策略
- **关键点**:
  - 无需询问用户
  - 按优先级顺序执行
  - 质量优先于数量

#### 📊 评分策略
- **位置**: `bounty/strategies/scoring.md`
- **算法**: 活跃度(30%) + 价值(40%) + 工作量(20%) + 学习(10%)

#### 🔍 过滤策略
- **位置**: `bounty/strategies/filters.md`
- **关键词**: bounty, security, bug-bounty, responsible disclosure

#### 📝 模板
- **SECURITY.md**: 标准安全文档模板
- **PR模板**: Pull Request 标准格式

### 2. GitHub Bounty 实现

#### 💡 经验教训
- **urllib3降级**: v2 → v1.26.20 (LibreSSL兼容)
- **SSH→HTTPS**: 解决推送问题
- **黑名单维护**: 避免重复工作

#### ✅ 最佳实践
- 项目选择: 中小型活跃项目
- 模板复用: 提升80%效率
- 持续跟进: 定期检查PR状态

### 3. 多智能体协作

#### 🤝 协作模式
- **位置**: `multi-agent-collaboration/`
- **模式**:
  - 主从模式
  - 对等模式
  - 层级模式

#### 📋 最佳实践
- 明确分工
- 通信协议
- 错误处理
- 结果聚合

### 4. 软件测试

#### 🧪 测试项目
- **traveler-platform**: 旅行平台测试
- **测试用例**: 三端测试方案
- **测试报告**: 第一轮测试报告

#### 📚 测试管理
- 测试计划模板
- 测试用例设计
- 测试报告格式

### 5. 工具使用

#### 🎨 PlantUML
- **位置**: `tools/plantuml-guide.md`
- **用途**: UML图表生成
- **示例**: 序列图、类图、流程图

#### 🔌 OpenClaw Sessions API
- **位置**: `tools/openclaw-sessions-api.md`
- **功能**: Session管理
- **用途**: 多会话协作

---

## 🔍 快速查找

### 按场景查找

| 场景 | 查找位置 |
|------|---------|
| **开始新任务** | `bounty/strategies/auto-workflow.md` |
| **评估任务价值** | `bounty/strategies/scoring.md` |
| **过滤重复任务** | `bounty/strategies/filters.md` |
| **使用模板** | `bounty/templates/` |
| **学习经验** | `github-bounty/lessons-learned.md` |
| **多智能体协作** | `multi-agent-collaboration/` |
| **测试方法** | `software-testing/` |
| **工具使用** | `tools/` |

### 按关键词查找

```
bounty → knowledge/bounty/
github → knowledge/github-bounty/
协作 → knowledge/multi-agent-collaboration/
测试 → knowledge/software-testing/
工具 → knowledge/tools/
```

---

## 📈 知识库统计

- **总文档数**: 50+
- **核心策略**: 5
- **模板**: 3
- **测试项目**: 1
- **工具指南**: 2

---

## 🔄 最近更新

- **2026-03-29**: 添加 auto-workflow 策略
- **2026-03-28**: 更新测试报告
- **2026-03-27**: 添加 SECURITY.md 模板

---

## 🎯 待添加的知识

- [ ] GitHub API 高级用法
- [ ] 网络韧性策略
- [ ] 功耗优化知识
- [ ] Python 最佳实践

---

_本索引由 OpenClaw Agent 维护_
_建议定期更新_

---

### 2026-04-01 新增知识

#### 🔒 Git 安全审计
- **位置**: `git-security/2026-04-01-security-audit-and-config-management.md`
- **用途**: 安全审计、API Key 轮换、配置管理
- **关键点**:
  - 配置文件权限管理
  - API Key 轮换流程
  - Git 分支合并策略
  - Docker 配置同步
  - Vulkan GPU 支持

#### 📝 今日工作记录
- **位置**: `memory/2026-04-01.md`
- **用途**: 日常工作和学习记录
- **关键点**:
  - 安全审计完成
  - API Key 轮换（4/6）
  - QQ Bot 配置更新
  - Git 仓库整理
  - Docker 同步

