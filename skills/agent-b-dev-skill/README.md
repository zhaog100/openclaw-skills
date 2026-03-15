# agent-b-dev-skill - 智能体B（Dev代理）技能包

**版本**：v1.0.0
**状态**：✅ 开发完成
**创建者**：小米粒（Dev代理）
**创建时间**：2026-03-15 01:05-01:18（13分钟）

---

## 📋 简介

agent-b-dev-skill是智能体B（小米粒Dev代理）使用的技能包，负责技术设计、开发实现、集成发布和沟通协作。

---

## 🎯 核心功能

### 1. 技术设计（Tech Designer）
- **架构设计**：创建、编辑、删除技术设计
- **技术选型**：选择合适的技术栈
- **工作量评估**：评估开发工作量
- **风险识别**：识别技术风险

### 2. 开发实现（Developer）
- **功能开发**：开发新功能
- **代码编写**：编写代码
- **单元测试**：测试代码
- **代码集成**：集成代码

### 3. 集成发布（Publisher）
- **发布准备**：准备发布
- **发布执行**：执行发布
- **发布验证**：验证发布

### 4. 沟通协作（Communicator）
- **消息发送**：发送消息到飞书群
- **消息接收**：接收飞书群消息
- **消息路由**：路由消息到对应处理模块

---

## 🚀 快速开始

### 安装
```bash
cd skills/agent-b-dev-skill
bash install.sh
```

### 使用
```bash
# 技术设计
agent-b-dev-skill tech create --prd-id prd_1
agent-b-dev-skill tech evaluate --design-id design_1
agent-b-dev-skill tech identify-risks --design-id design_1

# 开发实现
agent-b-dev-skill dev develop --design-id design_1 --feature "用户认证"
agent-b-dev-skill dev write-code --project-id dev_1 --code "..."
agent-b-dev-skill dev test --project-id dev_1 --test-cases '[...]'
agent-b-dev-skill dev integrate --project-id dev_1

# 集成发布
agent-b-dev-skill publish prepare --project-id dev_1 --version 1.0.0
agent-b-dev-skill publish checklist --release-id release_1 --item code_review
agent-b-dev-skill publish execute --release-id release_1
agent-b-dev-skill publish verify --release-id release_1

# 沟通协作
agent-b-dev-skill comm send --to agent-a-pm --content "技术设计完成"
agent-b-dev-skill comm receive
agent-b-dev-skill comm route --message "..."
```

---

## 📦 项目结构

```
agent-b-dev-skill/
├── SKILL.md              # 技能说明
├── README.md             # 本文档
├── package.json          # 包信息
├── skill.py              # 核心模块（Python）
├── skill.sh              # CLI入口（Bash）
├── modules/
│   ├── tech_designer.py      # 技术设计模块
│   ├── developer.py          # 开发实现模块
│   ├── publisher.py          # 集成发布模块
│   └── communicator.py       # 沟通协作模块
├── install.sh            # 安装脚本
└── test.sh               # 测试脚本
```

---

## 🧪 测试

```bash
bash test.sh
```

---

## 📄 许可证

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/xiaomili-personal-skills
- ClawHub: https://clawhub.com
- 创建者: 思捷娅科技 (SJYKJ)

---

*最后更新：2026-03-15 01:18*
