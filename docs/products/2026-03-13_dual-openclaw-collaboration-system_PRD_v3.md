# 产品需求文档 - 双 OpenClaw 协作系统（MemOS 方案）

**文档版本**：v3.0  
**创建日期**：2026-03-13  
**创建者**：小米辣（PM 代理）  
**状态**：待开发  
**Issue**：#1  
**官家指令**：2026-03-13 12:57  
**开发者**：小米粒（Dev 代理）

---

## 1. 需求概述

### 1.1 背景

**核心需求**：设计双 OpenClaw 协作系统，让两个智能体（小米辣 PM + 小米粒 Dev）能够：
- ✅ 各司其职（创意策划 vs 执行落地）
- ✅ 无缝衔接（B 能读到 A 的产出）
- ✅ 24/7 高效协作（无需人工复制粘贴）
- ✅ 跨环境部署（家里 NAS + 公司服务器）

### 1.2 目标

**核心目标**：基于 MemOS 插件实现双 OpenClaw 实例记忆共享和协作。

**具体目标**：
1. ✅ 部署两个独立 OpenClaw 实例（不同环境）
2. ✅ 安装 MemOS 插件（两个实例都装）
3. ✅ 配置共享 user_id（实现记忆池共享）
4. ✅ 定义两个智能体的角色和技能
5. ✅ 实现自动记忆召回和写回
6. ✅ 支持异步协作（A 今天产出，B 明天接力）

### 1.3 范围

**包含**：
- 双 OpenClaw 实例部署
- MemOS 插件安装配置
- 智能体角色定义和技能配置
- 共享记忆池配置
- 协作流程设计
- 默认策略配置

**不包含**（后续版本）：
- 权限控制（A 可读 B，B 不可改 A）
- 记忆检索精度优化
- 复用模板系统

---

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────┐         ┌─────────────────────┐
│   家里 NAS          │         │   公司服务器        │
│                     │         │                     │
│  OpenClaw A         │         │  OpenClaw B         │
│  (小米辣 - PM)      │         │  (小米粒 - Dev)     │
│  Port 3000          │         │  Port 3000          │
│                     │         │                     │
│  技能：             │         │  技能：             │
│  - 需求分析         │         │  - 技术设计         │
│  - 方案设计         │         │  - 开发实现         │
│  - Review 验收       │         │  - 测试修复         │
│  - 项目管理         │         │  - 部署运维         │
│                     │         │                     │
│  MemOS 插件         │         │  MemOS 插件         │
└──────────┬──────────┘         └──────────┬──────────┘
           │                               │
           │  互联网（HTTPS）              │  互联网（HTTPS）
           │                               │
           └────────────┬──────────────────┘
                        │
                ┌───────▼───────┐
                │ MemOS Cloud   │
                │ (共享记忆池)  │
                │ user_id=xxx   │
                └───────────────┘
```

### 2.2 智能体角色定义

#### 智能体 A：小米辣（PM 代理）

**角色**：产品经理/项目经理

**职责**：
- 需求分析和方案设计
- PRD 文档创建
- Review 验收
- 项目管理
- 创意策划

**技能配置**：
```json
{
  "agent": {
    "name": "小米辣",
    "role": "产品经理/项目经理",
    "skills": [
      "requirement-analysis",
      "prd-creator",
      "reviewer",
      "project-manager",
      "creative-planner"
    ],
    "personality": "严谨细致，注重质量把控",
    "environment": "家里 NAS"
  }
}
```

**默认策略**：
- 收到需求后先分析并创建 PRD
- 开发完成后进行 Review（12 维度 + 5 层验收）
- 通过 Review 后批准发布
- 定期同步项目进度

#### 智能体 B：小米粒（Dev 代理）

**角色**：开发工程师/DevOps

**职责**：
- 技术设计和开发实现
- 测试和修复
- 部署和运维
- 执行落地

**技能配置**：
```json
{
  "agent": {
    "name": "小米粒",
    "role": "开发工程师/DevOps",
    "skills": [
      "tech-designer",
      "developer",
      "tester",
      "devops-engineer",
      "executor"
    ],
    "personality": "务实高效，注重代码质量",
    "environment": "公司服务器"
  }
}
```

**默认策略**：
- 收到 PRD 后进行技术设计
- 开发实现并自测
- 提交 Review 请求
- 根据 Review 反馈修复
- 发布到 ClawHub

### 2.3 核心机制

#### 记忆隔离机制
```
user_id="openclaw-dual-collaboration"（共享配置）
├─ 小米辣（PM）的对话记录和输出
│   ├─ PRD 文档
│   ├─ Review 报告
│   └─ 项目计划
├─ 小米粒（Dev）的对话记录和输出
│   ├─ 技术设计
│   ├─ 代码实现
│   └─ 测试报告
└─ 所有共享的上下文
```

#### 召回机制
1. 智能体启动后，MemOS 自动分析用户问题意图
2. 去共享记忆池检索相关上下文
3. 精简后注入给智能体作为背景知识
4. 智能体基于上下文继续工作

#### 写回机制
1. 小米辣的产出（PRD/Review）自动写回 MemOS
2. 小米粒的产出（设计/代码）自动写回 MemOS
3. 自动分类和索引，支持后续检索

---

## 3. 功能需求

### 3.1 核心功能（P0）

#### 功能 1：双实例部署 ⭐⭐⭐⭐⭐
- **描述**：部署两个独立 OpenClaw 实例
- **环境**：
  - 实例 A：家里 NAS（小米辣 - PM）
  - 实例 B：公司服务器（小米粒 - Dev）
- **验收标准**：
  - [ ] 两个实例运行在不同环境
  - [ ] 独立工作目录
  - [ ] 共享同一个 MemOS API Key 和 user_id

#### 功能 2：MemOS 插件安装 ⭐⭐⭐⭐⭐
- **描述**：两个实例都安装 MemOS 插件
- **验收标准**：
  - [ ] 插件安装成功
  - [ ] 插件启用（"enabled": true）
  - [ ] Gateway 重启成功

#### 功能 3：智能体角色配置 ⭐⭐⭐⭐⭐
- **描述**：为两个实例配置不同的角色和技能
- **配置文件**：
  - 实例 A：`~/.openclaw-home/openclaw.json`（小米辣 - PM）
  - 实例 B：`~/.openclaw-work/openclaw.json`（小米粒 - Dev）
- **验收标准**：
  - [ ] 角色定义清晰
  - [ ] 技能配置正确
  - [ ] 默认策略生效

#### 功能 4：记忆共享 ⭐⭐⭐⭐⭐
- **描述**：两个实例共享同一个记忆池
- **验收标准**：
  - [ ] 小米辣的产出自动写入 MemOS
  - [ ] 小米粒能读到小米辣的产出
  - [ ] 无需手动复制粘贴

#### 功能 5：自动召回 ⭐⭐⭐⭐⭐
- **描述**：智能体启动后自动检索相关上下文
- **验收标准**：
  - [ ] 理解完整背景信息
  - [ ] 召回准确率 > 90%
  - [ ] 召回延迟 < 3 秒

#### 功能 6：自动写回 ⭐⭐⭐⭐⭐
- **描述**：产出自动写回 MemOS
- **验收标准**：
  - [ ] 小米辣的产出自动保存
  - [ ] 小米粒的产出自动保存
  - [ ] 自动分类和索引

### 3.2 辅助功能（P1）

#### 功能 7：协作流程自动化
- **描述**：PRD→设计→开发→Review→发布的自动化流程
- **验收标准**：
  - [ ] 流程清晰可追溯
  - [ ] 状态自动更新
  - [ ] 通知及时

#### 功能 8：进度同步
- **描述**：两个智能体定期同步项目进度
- **验收标准**：
  - [ ] 每日进度报告
  - [ ] 问题及时沟通
  - [ ] 风险提前预警

### 3.3 可选功能（P2）

#### 功能 9：权限控制
- **描述**：更灵活的权限管理
- **验收标准**：
  - [ ] 小米辣可读小米粒的输出
  - [ ] 小米粒不可修改小米辣的记忆

#### 功能 10：记忆检索优化
- **描述**：提升复杂场景的检索精度
- **验收标准**：
  - [ ] 支持调整检索参数
  - [ ] 检索准确率 > 95%

---

## 4. 技术需求

### 4.1 环境要求
- **OpenClaw**：最新版本
- **Node.js**：v18+
- **MemOS 插件**：github:MemTensor/MemOS-Cloud-OpenClaw-Plugin
- **操作系统**：Linux（Ubuntu/Debian/CentOS）

### 4.2 性能要求
- **召回延迟**：< 3 秒
- **写回延迟**：< 1 秒
- **检索准确率**：> 90%

### 4.3 安全要求
- **API Key 管理**：存储在 .env 文件，不要提交到 Git
- **user_id 管理**：自定义 user_id 避免冲突
- **SSH 认证**：使用 SSH 密钥进行 Git 操作

---

## 5. 部署配置

### 5.1 环境变量（.env 文件）

#### 实例 A（家里 NAS - 小米辣）
```bash
# MemOS API Key（两个实例必须相同）
MEMOS_API_KEY=mpg-your_key_here

# 共享 user_id（两个实例必须相同）
MEMOS_USER_ID=openclaw-dual-collaboration

# 智能体角色
AGENT_NAME=小米辣
AGENT_ROLE=pm
```

#### 实例 B（公司服务器 - 小米粒）
```bash
# MemOS API Key（同一个 Key）
MEMOS_API_KEY=mpg-your_key_here

# 共享 user_id（同一个 user_id）
MEMOS_USER_ID=openclaw-dual-collaboration

# 智能体角色
AGENT_NAME=小米粒
AGENT_ROLE=dev
```

### 5.2 智能体配置（openclaw.json）

#### 实例 A（小米辣 - PM）
```json
{
  "agent": {
    "name": "小米辣",
    "role": "产品经理/项目经理",
    "skills": [
      "requirement-analysis",
      "prd-creator",
      "reviewer",
      "project-manager",
      "creative-planner"
    ],
    "personality": "严谨细致，注重质量把控",
    "default_strategy": {
      "on_new_request": "analyze_and_create_prd",
      "on_development_complete": "review_and_approve",
      "on_pr_approved": "publish_to_clawhub"
    }
  },
  "memos": {
    "enabled": true,
    "user_id": "openclaw-dual-collaboration"
  }
}
```

#### 实例 B（小米粒 - Dev）
```json
{
  "agent": {
    "name": "小米粒",
    "role": "开发工程师/DevOps",
    "skills": [
      "tech-designer",
      "developer",
      "tester",
      "devops-engineer",
      "executor"
    ],
    "personality": "务实高效，注重代码质量",
    "default_strategy": {
      "on_prd_received": "tech_design",
      "on_design_approved": "develop_and_test",
      "on_review_requested": "fix_and_resubmit",
      "on_review_approved": "publish_to_clawhub"
    }
  },
  "memos": {
    "enabled": true,
    "user_id": "openclaw-dual-collaboration"
  }
}
```

---

## 6. 协作流程

### 6.1 标准协作流程

```
1. 官家提出需求
   ↓
2. 小米辣（PM）分析需求 → 创建 PRD → 写入 MemOS
   ↓
3. 小米粒（Dev）检索 MemOS → 读取 PRD → 技术设计
   ↓
4. 小米粒 开发实现 → 自测 → 提交 Review 请求
   ↓
5. 小米辣 检索 MemOS → 读取设计/代码 → Review
   ↓
6. Review 通过 → 小米粒 发布到 ClawHub
   ↓
7. 双方同步进度 → 等待下一个需求
```

### 6.2 异步协作示例

```
20:00（家里）
小米辣：收到官家需求，创建 PRD
→ 自动写入 MemOS
→ 通知小米粒（Issue 评论）

09:00（第二天，公司）
小米粒：启动后自动检索 MemOS
→ 读取昨晚的 PRD
→ 开始技术设计

12:00（公司）
小米粒：开发完成，提交 Review
→ 自动写入 MemOS
→ 通知小米辣

20:00（家里）
小米辣：启动后自动检索 MemOS
→ 读取设计和代码
→ 进行 Review

22:00（家里）
小米辣：Review 通过，批准发布
→ 小米粒 发布到 ClawHub
```

---

## 7. 开发计划

### 阶段 1：部署（预计 1 小时）
- [ ] 获取 MemOS API Key
- [ ] 部署 OpenClaw A（小米辣 - PM）
- [ ] 部署 OpenClaw B（小米粒 - Dev）
- [ ] 安装 MemOS 插件
- [ ] 配置智能体角色

### 阶段 2：配置（预计 30 分钟）
- [ ] 配置 openclaw.json（两个实例）
- [ ] 配置默认策略
- [ ] 验证记忆共享

### 阶段 3：测试（预计 30 分钟）
- [ ] 测试双实例协作流程
- [ ] 验证自动召回和写回
- [ ] 测试异步协作

### 阶段 4：验收（预计 30 分钟）
- [ ] 完成一次完整协作（PRD→开发→Review→发布）
- [ ] 验证所有功能正常
- [ ] 文档整理

**总计**：约 2.5 小时

---

## 8. 验收标准

### 8.1 功能验收
- [ ] 两个 OpenClaw 实例正常运行（不同环境）
- [ ] MemOS 插件已启用
- [ ] 智能体角色配置正确
- [ ] 默认策略生效
- [ ] 小米辣的产出自动写入 MemOS
- [ ] 小米粒能读到小米辣的产出
- [ ] 无需人工复制粘贴

### 8.2 性能验收
- [ ] 召回延迟 < 3 秒
- [ ] 写回延迟 < 1 秒
- [ ] 检索准确率 > 90%

### 8.3 协作验收
- [ ] 完成一次完整协作流程
- [ ] 小米粒基于小米辣的 PRD 无缝接力
- [ ] 小米辣能 Review 小米粒的产出
- [ ] 支持异步协作（晚上→白天）

---

## 9. 风险与依赖

### 9.1 风险
- **MemOS 服务稳定性**：依赖云服务可用性
- **检索精度**：复杂场景可能需要调整参数
- **权限控制**：目前不支持细粒度权限

### 9.2 依赖
- MemOS Cloud 服务
- OpenClaw Gateway
- MemOS 插件

---

## 10. 下一步行动

### 立即执行（小米粒）
1. ⏳ **获取 MemOS API Key**（访问 https://memos.openmem.net）
2. ⏳ **部署双 OpenClaw 实例**（家里 NAS + 公司服务器）
3. ⏳ **安装 MemOS 插件**（两个实例都装）
4. ⏳ **配置智能体角色**（openclaw.json）
5. ⏳ **验证记忆共享**（测试 A 产出 B 读取）

### 本周完成
1. ⏳ **测试协作流程**（完整 PRD→开发→Review→发布）
2. ⏳ **创建协作模板**（可复用案例）
3. ⏳ **优化配置**（默认策略调整）

---

## 11. 参考资源

- **MemOS 官网**：https://memos.openmem.net
- **MemOS GitHub**：https://github.com/MemTensor/MemOS
- **MemOS 插件**：https://github.com/MemTensor/MemOS-Cloud-OpenClaw-Plugin
- **OpenClaw 文档**：https://docs.openclaw.ai
- **部署方案**：`docs/deployment/dual-openclaw-cross-environment-deployment.md`

---

## 12. 交付物

### 文档
- [ ] PRD v3.0（本文档）
- [ ] 技术设计文档
- [ ] 部署报告
- [ ] 测试报告

### 配置
- [ ] 实例 A 配置（~/.openclaw-home/）
- [ ] 实例 B 配置（~/.openclaw-work/）
- [ ] MemOS 插件配置

### 验证
- [ ] 完整协作流程录屏
- [ ] 性能测试报告
- [ ] 验收报告

---

**PRD 版本**：v3.0  
**创建时间**：2026-03-13 12:58  
**创建者**：小米辣（PM 代理）  
**开发者**：小米粒（Dev 代理）  
**状态**：待开发

---

*请 @小米粒 查看 PRD v3.0 并立即开始开发！*

**官家指令**：把双米粒系统设计成一个方案，通过 PRD 传递给小米粒，让她开发，每个智能体分别使用自己的技能，把策略默认放入进去
