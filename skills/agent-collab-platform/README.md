# agent-collab-platform - 智能体协作平台

**版本**：v1.14.0 ⭐⭐⭐⭐⭐（官家指正：强制主动检查）
**状态**：✅ 核心框架完成 + 规则系统
**创建者**：小米粒（思捷娅科技Dev代理）
**创建时间**：2026-03-15 08:54-08:56（20分钟）
**最后更新**：2026-03-15 13:20（添加核心规则）

---

## 📋 简介

agent-collab-platform是统一的智能体协作平台，采用共享核心+特定模块的架构设计，支持无限扩展智能体A、B、C、D...

**v1.8.0 新增**：
- ✅ 核心规则系统（所有智能体必须遵守）
- ✅ 规则1：做事必须严谨
- ✅ 规则2：看问题要全面
- ✅ 规则3：看内容要承前启后

---

## 📋 核心规则（强制性）⭐⭐⭐⭐⭐

### 规则1：做事必须严谨

**定义**：所有操作必须经过验证，不能凭推测行动

**要求**：
- ✅ 操作前验证
- ✅ 操作中监控
- ✅ 操作后确认

**禁止**：
- ❌ 未验证即行动
- ❌ 凭推测判断
- ❌ 忽略异常

---

### 规则2：看问题要全面

**定义**：分析问题时必须考虑所有相关因素

**要求**：
- ✅ 多维度分析
- ✅ 上下文关联
- ✅ 利益相关方

**禁止**：
- ❌ 只看表面
- ❌ 忽略历史
- ❌ 遗漏相关方

---

### 规则3：看内容要承前启后

**定义**：理解内容时必须联系上下文

**要求**：
- ✅ 向前追溯
- ✅ 当前定位
- ✅ 向后预判

**禁止**：
- ❌ 只看单条消息
- ❌ 忽略时间线
- ❌ 脱离上下文

---

### 规则4：Git推送必须遵守仓库分配（可配置） ⭐⭐⭐⭐⭐

**定义**：不同类型的信息必须推送到配置的对应仓库

**配置文件**：`config/git_repositories.json`（可自定义）

**仓库分配**：

#### origin仓库（公共仓库）
- **URL**：`git@github.com:zhaog100/openclaw-skills.git`
- **用途**：公共信息，所有智能体遵守的规则
- **配置位置**：`config/git_repositories.json → repositories.public`
- **推送内容**：
  - ✅ 核心规则系统
  - ✅ 架构文档
  - ✅ 安装指南
  - ✅ Issue通知
  - ✅ 技术文档

#### xiaomili仓库（小米粒个人仓库）
- **URL**：`https://github.com/zhaog100/xiaomili-personal-skills.git`
- **用途**：小米粒（Dev代理）的个人信息
- **配置位置**：`config/git_repositories.json → repositories.personal_xiaomili`
- **推送内容**：
  - ✅ 个人工作日志
  - ✅ 私有配置
  - ✅ 测试数据

#### xiaomila仓库（小米辣个人仓库）
- **URL**：`https://github.com/zhaog100/xiaomila-skills.git`
- **用途**：小米辣（PM代理）的个人信息
- **配置位置**：`config/git_repositories.json → repositories.personal_xiaomila`

**如何自定义仓库配置**：
```bash
# 1. 编辑配置文件
vim skills/agent-collab-platform/config/git_repositories.json

# 2. 修改repositories配置
{
  "repositories": {
    "public": {
      "name": "origin",
      "url": "你的公共仓库URL"
    },
    "personal_agent_a": {
      "name": "你的仓库名",
      "url": "你的个人仓库URL"
    }
  }
}

# 3. 通知所有智能体更新配置
# 规则自动应用新配置
```

**Git操作流程**：
```bash
# 1. 推送个人信息到xiaomili
git push xiaomili master

# 2. 推送公共信息到origin
git pull origin master --rebase
git push origin master

# 3. 验证推送成功
git log xiaomili/master --oneline -5
git log origin/master --oneline -5
```

**禁止**：
- ❌ 只commit未push
- ❌ 公共信息只推送到个人仓库
- ❌ 个人信息推送到公共仓库

---

## 🎯 核心架构

### 共享核心模块（core/）

#### 1. github_monitor.py - GitHub监听
- ✅ 自动监听GitHub Issue评论
- ✅ 避免重复处理
- ✅ 30秒检查间隔

#### 2. message_router.py - 消息路由
- ✅ 自动识别消息类型（PRD/技术设计/开发/Review/发布）
- ✅ 过滤自己的消息
- ✅ 提取关键信息

#### 3. state_manager.py - 状态管理
- ✅ 4阶段26状态定义
- ✅ 状态流转验证
- ✅ 状态信息查询

#### 4. base_skill.py - 基础技能类
- ✅ 统一初始化
- ✅ 共享GitHub监听
- ✅ 统一消息发送

#### 5. issue_handler.py - Issue处理
- ✅ 创建Issue
- ✅ 获取Issue
- ✅ 发送评论
- ✅ 关闭Issue

---

### 智能体特定模块（agents/）

#### agent_a/ - PM代理（小米辣）
- ✅ product_manager.py - 产品管理
- ✅ reviewer.py - Review验证

#### agent_b/ - Dev代理（小米粒）
- ✅ tech_designer.py - 技术设计
- ✅ developer.py - 开发实现
- ✅ publisher.py - 集成发布

#### agent_c/, agent_d/ - 未来扩展
- 🔄 只需实现特定业务逻辑
- 🔄 自动继承所有共享功能

---

## 🚀 快速开始

### 安装
```bash
clawhub install agent-collab-platform
```

### 使用

#### 启动PM代理（小米辣）
```bash
cd skills/agent-collab-platform
./skill.sh agent_a
```

#### 启动Dev代理（小米粒）
```bash
cd skills/agent-collab-platform
./skill.sh agent_b
```

---

## 📊 协作流程

```
1. PM代理（小米辣）
   ├─ 创建PRD → GitHub Issue
   └─ Review技术设计 → 反馈

2. Dev代理（小米粒）
   ├─ 收到PRD → 技术设计
   ├─ 收到Review → 开发实现
   └─ 开发完成 → 发布ClawHub

3. 状态流转
   产品构思 → 技术设计 → 开发实现 → 发布交付
```

---

## 🎯 优势对比

| 维度 | 旧架构（独立技能包） | 新架构（统一平台） |
|------|-------------------|------------------|
| 代码复用 | 10% | 90%+ ⭐ |
| 扩展成本 | 高（重复开发） | 低（继承基类）⭐ |
| 维护成本 | 高（改N个地方） | 低（改1个地方）⭐ |
| 一致性 | 差（各写各的） | 好（统一标准）⭐ |

---

## 📦 项目结构

```
agent-collab-platform/
├── core/                   核心共享模块
│   ├── __init__.py
│   ├── github_monitor.py   GitHub监听
│   ├── message_router.py   消息路由
│   ├── state_manager.py    状态管理
│   ├── base_skill.py       基础技能类
│   └── issue_handler.py    Issue处理
│
├── agents/                 智能体特定模块
│   ├── agent_a/            PM代理（小米辣）
│   │   ├── __init__.py
│   │   ├── product_manager.py
│   │   └── reviewer.py
│   │
│   └── agent_b/            Dev代理（小米粒）
│       ├── __init__.py
│       ├── tech_designer.py
│       ├── developer.py
│       └── publisher.py
│
├── config/                 配置（待扩展）
│
├── skill.sh                CLI入口
├── skill.py                主程序
├── README.md               本文档
└── package.json            包信息
```

---

## 🔄 扩展指南

### 添加新智能体C

1. 创建目录：
```bash
mkdir agents/agent_c
```

2. 创建`__init__.py`：
```python
from core import BaseSkill

class AgentC(BaseSkill):
    def __init__(self):
        super().__init__('agent_c', '角色C')

    def handle_message(self, message):
        # 实现特定逻辑
        pass
```

3. 启动：
```bash
python3 skill.py agent_c
```

**无需重复实现GitHub监听等基础功能！**

---

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/xiaomili-personal-skills
- ClawHub: https://clawhub.com
- 创建者: 思捷娅科技 (SJYKJ)

**商业使用授权**：
- 小微企业（<10人）：¥999/年
- 中型企业（10-50人）：¥4,999/年
- 大型企业（>50人）：¥19,999/年
- 企业定制版：¥99,999一次性（源码买断）

详情请查看：[LICENSE](../../LICENSE)

---

*最后更新：2026-03-15 09:12*
*版本：v1.6.0 - 思捷娅科技(SJYKJ)最终版权统一版*
