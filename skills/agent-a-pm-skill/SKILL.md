# agent-a-pm-skill - 智能体A（PM代理）技能包

**版本**：v1.0.0
**创建者**：小米粒（Dev代理）
**创建时间**：2026-03-15
**状态**：开发中

---

## 📋 技能说明

智能体A（小米辣）使用的技能包，负责产品管理、测试验证、状态管理和沟通协作。

---

## 🎯 核心功能

### 1. 产品管理模块（product_manager.py）
- **产品构思**：创建、编辑、删除产品需求
- **PRD编写**：生成产品需求文档
- **需求评审**：评审产品需求

### 2. Review验证模块（reviewer.py）
- **代码审查**：Review代码实现
- **测试验证**：验证功能完整性
- **发布评审**：评审发布准备

### 3. 状态管理模块（state_manager.py）
- **状态流转**：管理产品状态流转
- **状态查询**：查询产品当前状态
- **状态通知**：状态变更通知

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
# 产品管理
agent-a-pm product create <name>
agent-a-pm product edit <id>
agent-a-pm product delete <id>

# Review验证
agent-a-pm review code <pr_number>
agent-a-pm review test <test_result>
agent-a-pm review publish <version>

# 状态管理
agent-a-pm state transition <id> <new_state>
agent-a-pm state query <id>
agent-a-pm state notify <id>

# 沟通协作
agent-a-pm comm send <message>
agent-a-pm comm receive
agent-a-pm comm route <message>
```

---

## 📦 依赖

- Python 3.12+
- lark-oapi >= 1.5.3
- SQLite 3

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

*最后更新：2026-03-15 01:16*
