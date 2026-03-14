# agent-b-dev-skill - 智能体B（Dev代理）技能包

**版本**：v1.0.0
**创建者**：小米粒（Dev代理）
**创建时间**：2026-03-15 01:05-01:16（11分钟）
**状态**：✅ 开发完成

---

## 📋 技能说明

智能体B（小米粒Dev代理）使用的技能包，负责技术设计、开发实现、集成发布和沟通协作。

---

## 🎯 核心功能

### 1. 技术设计模块（tech_designer.py）
- **架构设计**：创建、编辑、提交技术设计
- **技术选型**：评估技术方案
- **工作量评估**：预估开发工作量
- **风险识别**：识别技术风险

### 2. 开发实现模块（developer.py）
- **代码编写**：编写代码实现
- **单元测试**：编写和执行测试
- **代码集成**：集成代码到项目

### 3. 集成发布模块（publisher.py）
- **发布准备**：准备发布清单
- **发布执行**：执行发布流程
- **发布验证**：验证发布结果

### 4. 沟通协作模块（communicator.py）
- **消息发送**：发送消息到飞书群
- **消息接收**：接收飞书群消息
- **消息路由**：路由消息到对应处理模块

---

## 🚀 使用方法

### 安装
```bash
bash install.sh
```

### 使用
```bash
# 技术设计
agent-b-dev tech create --prd-id PRD_1 --architecture "..."
agent-b-dev tech evaluate --design-id design_1
agent-b-dev tech identify-risks --design-id design_1
agent-b-dev tech submit --design-id design_1

# 开发实现
agent-b-dev dev develop --design-id design_1 --feature "核心功能"
agent-b-dev dev write-code --project-id dev_1 --code "..."
agent-b-dev dev test --project-id dev_1 --test-cases "[...]"
agent-b-dev dev integrate --project-id dev_1

# 集成发布
agent-b-dev publish prepare --project-id dev_1 --version 1.0.0
agent-b-dev publish checklist --release-id release_1 --item code_review --status true
agent-b-dev publish execute --release-id release_1
agent-b-dev publish verify --release-id release_1

# 沟通协作
agent-b-dev comm send --to agent-a-pm --content "技术设计完成"
agent-b-dev comm receive
agent-b-dev comm route --message "..."
```

---

## 📦 依赖

- Python 3.12+
- lark-oapi >= 1.5.3
- SQLite 3

---

## 📄 许可证

MIT License

Copyright (c) 2026 米粒儿 (miliger)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/xiaomili-personal-skills
- ClawHub: https://clawhub.com
- 创建者: 米粒儿 (miliger)

---

*最后更新：2026-03-15 01:16*
