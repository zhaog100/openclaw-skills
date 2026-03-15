# agent-a-pm-skill - 智能体A（PM代理）技能包

**版本**：v1.0.0  
**状态**：✅ 开发完成  
**创建者**：小米粒（Dev代理）  
**创建时间**：2026-03-15 01:05-01:22（17分钟）

---

## 📋 简介

agent-a-pm-skill是智能体A（小米辣PM代理）使用的技能包，负责产品管理、Review验证、状态管理和沟通协作。

---

## 🎯 核心功能

### 1. 产品管理（Product Manager）
- 创建/编辑/删除产品
- PRD编写和评审
- 需求管理

### 2. Review验证（Reviewer）
- 代码审查
- 测试验证
- 发布评审

### 3. 状态管理（State Manager）
- 4阶段26状态管理
- 状态流转控制
- 状态通知

### 4. 沟通协作（Communicator）
- 消息发送/接收
- 消息路由
- 飞书集成

---

## 🚀 快速开始

### 安装
```bash
cd skills/agent-a-pm-skill
bash install.sh
```

### 使用
```bash
# 产品管理
./skill.sh product create --name "新产品" --description "产品描述"

# Review验证
./skill.sh review code --pr 123

# 状态管理
./skill.sh state transition --id prod_1 --state designing

# 沟通协作
./skill.sh comm send --to agent-b-dev --content "测试消息"
```

---

## 📦 项目结构

```
agent-a-pm-skill/
├── SKILL.md              # 技能说明
├── README.md             # 本文档
├── package.json          # 包信息
├── skill.py              # 核心模块（Python）
├── skill.sh              # CLI入口（Bash）
├── modules/
│   ├── product_manager.py    # 产品管理模块
│   ├── reviewer.py           # Review验证模块
│   ├── state_manager.py      # 状态管理模块
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

*最后更新：2026-03-15 01:22*
