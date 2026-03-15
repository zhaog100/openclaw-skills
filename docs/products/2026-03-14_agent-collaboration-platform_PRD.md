# 产品需求文档 - 智能体协作平台

**文档版本**：v4.0  
**创建日期**：2026-03-14  
**更新日期**：2026-03-15 00:55  
**创建者**：小米辣（PM 代理）  
**状态**：待技术设计  
**优先级**：P0

---

## 1. 项目愿景

构建一个**基于敏捷项目管理的智能体协作平台**，实现从产品构思到产品交付的完整闭环。

### 1.1 核心角色

### 1.0 竞品分析（2026-03-15 21:27）

**论坛调研发现**：

| 项目 | 特点 | 链接 | 可借鉴点 |
|------|------|------|---------|
| **Everdone CodeReview** | AI 代码审查作为可追踪的工作流 | https://everdone.ai/ | 工作流追踪 |
| **Bottleneck** | AI 原生团队的代码审查工具 | https://github.com/areibman/bottleneck | AI 原生协作 |
| **Open Code Review** | AI 审查员互相辩论后再给反馈 | https://github.com/spencermarx/open-code-review | AI 辩论机制 |
| **AgentVerse** | 多智能体协作框架 | https://github.com/OpenBMB/AgentVerse | 多智能体架构 |
| **OxyGent** | 智能体工作流引擎 | https://github.com/jd-opensource/OxyGent | 工作流引擎 |

**我们的优势**：
1. ✅ 完全开源（代码透明，可自定义）
2. ✅ 本地执行（代码不上传云端，安全）
3. ✅ 规则系统（7 条核心规则，规范协作流程）
4. ✅ 状态流转（4 阶段 26 状态，完整的生命周期管理）
5. ✅ 心跳轮询（2 分钟自动检查，主动发现问题）
6. ✅ 双智能体协作（PM+Dev 明确分工）

**我们的劣势**：
1. ❌ 起步晚（其他项目已经运行 1-3 年）
2. ❌ 用户少（没有实际用户反馈）
3. ❌ 功能单一（目前只支持双智能体，不支持多智能体）
4. ❌ 依赖 GitHub（深度绑定 GitHub Issues）

**借鉴策略**：
- ✅ **AI 辩论机制**：已应用到 ai-code-reviewer PRD
- ✅ **工作流追踪**：已应用到 ai-code-reviewer PRD
- ⏳ **多智能体架构**：未来扩展（支持智能体 C/D/E）
- ⏳ **工作流引擎**：未来优化（状态流转自动化）

---

### 1.1 核心角色

| 角色 | 智能体 | 职责 | 技能包 |
|------|--------|------|--------|
| **智能体 A** | 小米辣 | 项目管理、产品设计、测试验证、客户对接 | `agent-a-pm-skill` |
| **智能体 B** | 小米粒 | 技术设计、开发实现、集成发布 | `agent-b-dev-skill` |

### 1.2 核心流程

```
产品构思 → 技术设计 → 开发实现 → 集成发布 → Review 验证 → 发布交付
   ↓           ↓           ↓           ↓           ↓           ↓
小米辣     小米粒      小米粒      小米粒      小米辣      小米粒
```

---

## 2. 技能包架构 ⭐⭐⭐⭐⭐

### 2.1 双技能包设计

**设计原则**：
- ✅ 智能体 A 和智能体 B 各自独立的技能包
- ✅ 职责分离，互不干扰
- ✅ 通过 GitHub Issues 协作
- ✅ 通过 inbox/outbox 紧急通信

### 2.2 智能体 A 技能包（PM Skill）

**技能包名**：`agent-a-pm-skill`

**核心功能**：
1. **产品管理模块**
   - 产品构思与需求定义
   - 产品设计文档编写
   - 需求优先级排序
   - 客户沟通与反馈收集

2. **Review 验证模块**
   - 技术设计 Review
   - 开发成果 Review
   - 测试验证
   - 发布审批

3. **状态管理模块**
   - 定义各阶段状态
   - 状态流转管理
   - 状态通知接收

4. **沟通协作模块**
   - GitHub Issues 集成
   - inbox/outbox 集成
   - 1 分钟检查机制

**文件结构**：
```
agent-a-pm-skill/
├── SKILL.md
├── README.md
├── package.json
├── install.sh
├── src/
│   ├── product_manager.py      # 产品管理
│   ├── review_validator.py     # Review 验证
│   ├── state_manager.py        # 状态管理
│   └── communication.py        # 沟通协作
├── tests/
│   ├── test_product_manager.py
│   ├── test_review_validator.py
│   ├── test_state_manager.py
│   └── test_communication.py
└── docs/
    ├── user_guide.md
    └── api_reference.md
```

---

### 2.3 智能体 B 技能包（Dev Skill）

**技能包名**：`agent-b-dev-skill`

**核心功能**：
1. **技术实现模块**
   - 技术架构设计
   - 代码开发实现
   - 功能集成测试
   - 产品发布部署

2. **沟通协作模块**
   - 提交技术设计供 Review
   - 提交开发成果供 Review
   - 接收 Review 反馈
   - 修复问题后重新提交

3. **状态通知模块**
   - 发布状态通知
   - 暂停状态通知
   - 取消状态通知
   - 删除状态通知

**文件结构**：
```
agent-b-dev-skill/
├── SKILL.md
├── README.md
├── package.json
├── install.sh
├── src/
│   ├── tech_designer.py        # 技术设计
│   ├── developer.py            # 开发实现
│   ├── tester.py               # 测试验证
│   ├── publisher.py            # 发布部署
│   ├── state_notifier.py       # 状态通知
│   └── communication.py        # 沟通协作
├── tests/
│   ├── test_tech_designer.py
│   ├── test_developer.py
│   ├── test_tester.py
│   ├── test_publisher.py
│   ├── test_state_notifier.py
│   └── test_communication.py
└── docs/
    ├── user_guide.md
    └── api_reference.md
```

---

## 3. 功能需求

### 3.1 智能体 A（小米辣）职责

#### 产品管理
- [ ] 产品构思与需求定义
- [ ] 产品设计文档编写
- [ ] 需求优先级排序
- [ ] 客户沟通与反馈收集

#### Review 验证
- [ ] 技术设计 Review
- [ ] 开发成果 Review
- [ ] 测试验证
- [ ] 发布审批

#### 状态管理
- [ ] 定义各阶段状态
- [ ] 状态流转管理
- [ ] 状态通知接收

### 3.2 智能体 B（小米粒）职责

#### 技术实现
- [ ] 技术架构设计
- [ ] 代码开发实现
- [ ] 功能集成测试
- [ ] 产品发布部署

#### 沟通协作
- [ ] 提交技术设计供 Review
- [ ] 提交开发成果供 Review
- [ ] 接收 Review 反馈
- [ ] 修复问题后重新提交

#### 状态通知
- [ ] 发布状态通知
- [ ] 暂停状态通知
- [ ] 取消状态通知
- [ ] 删除状态通知

---

## 4. 状态定义（闭环管理）

### 4.1 产品构思阶段（Product Conception）

| 状态 | 代码 | 说明 | 负责方 | 可达到的状态 | 触发条件 |
|------|------|------|--------|-------------|---------|
| **草稿** | `draft` | 产品构思草稿阶段 | 小米辣 | `pending_review` | 产品文档完成 |
| **待评审** | `pending_review` | 等待小米粒评审 | 小米辣 | `approved`, `rejected` | 提交评审 |
| **已批准** | `approved` | 产品构思已批准 | 小米辣 | `designing` | 评审通过 |
| **已拒绝** | `rejected` | 产品构思被拒绝 | 小米辣 | `draft` | 评审不通过 |
| **已暂停** | `paused` | 产品构思暂停 | 小米辣 | `draft`, `cancelled` | 主动暂停 |
| **已取消** | `cancelled` | 产品构思已取消 | 小米辣 | - | 主动取消 |

**状态流转图**：
```
draft → pending_review → approved → designing
              ↓              ↓
           rejected      paused
              ↓              ↓
            draft        cancelled
```

---

### 4.2 技术设计阶段（Technical Design）

| 状态 | 代码 | 说明 | 负责方 | 可达到的状态 | 触发条件 |
|------|------|------|--------|-------------|---------|
| **设计中** | `designing` | 技术设计进行中 | 小米粒 | `pending_review` | 设计完成 |
| **待评审** | `pending_review` | 等待小米辣评审 | 小米粒 | `approved`, `rejected` | 提交评审 |
| **已批准** | `approved` | 技术设计已批准 | 小米辣 | `developing` | 评审通过 |
| **需修改** | `needs_revision` | 需要修改设计 | 小米辣 | `designing` | 评审不通过 |
| **已暂停** | `paused` | 技术设计暂停 | 双方 | `designing`, `cancelled` | 主动暂停 |
| **已取消** | `cancelled` | 技术设计已取消 | 双方 | - | 主动取消 |

**状态流转图**：
```
designing → pending_review → approved → developing
                ↓                ↓
          needs_revision     paused
                ↓                ↓
            designing       cancelled
```

---

### 4.3 开发阶段状态（Development）

| 状态 | 代码 | 说明 | 负责方 | 可达到的状态 | 触发条件 |
|------|------|------|--------|-------------|---------|
| **开发中** | `developing` | 代码开发进行中 | 小米粒 | `testing` | 开发完成 |
| **测试中** | `testing` | 功能测试进行中 | 小米粒 | `pending_review`, `developing` | 测试完成/发现问题 |
| **待评审** | `pending_review` | 等待小米辣评审 | 小米粒 | `approved`, `rejected` | 提交评审 |
| **已批准** | `approved` | 开发成果已批准 | 小米辣 | `publishing` | 评审通过 |
| **需修复** | `needs_fix` | 需要修复问题 | 小米辣 | `developing`, `testing` | 评审不通过 |
| **已暂停** | `paused` | 开发暂停 | 双方 | `developing`, `testing`, `cancelled` | 主动暂停 |
| **已取消** | `cancelled` | 开发已取消 | 双方 | - | 主动取消 |

**状态流转图**：
```
developing → testing → pending_review → approved → publishing
               ↓            ↓               ↓
           developing  testing       needs_fix
                                             ↓
                                      developing/testing
```

---

### 4.4 发布交付阶段（Release & Delivery）

| 状态 | 代码 | 说明 | 负责方 | 可达到的状态 | 触发条件 |
|------|------|------|--------|-------------|---------|
| **发布中** | `publishing` | 发布部署进行中 | 小米粒 | `published`, `failed` | 发布完成 |
| **已发布** | `published` | 已成功发布 | 小米粒 | `paused`, `deprecated`, `deleted` | 发布成功 |
| **发布失败** | `failed` | 发布失败 | 小米粒 | `publishing`, `cancelled` | 发布失败 |
| **已暂停** | `paused` | 已暂停服务 | 小米粒 | `publishing`, `published`, `cancelled` | 主动暂停 |
| **已废弃** | `deprecated` | 已废弃版本 | 小米粒 | `deleted` | 标记废弃 |
| **已删除** | `deleted` | 已删除产品 | 小米粒 | - | 主动删除 |
| **已取消** | `cancelled` | 发布已取消 | 小米粒 | - | 主动取消 |

**状态流转图**：
```
publishing → published → deprecated → deleted
     ↓          ↓           ↓
  failed    paused     deleted
     ↓          ↓
publishing  published/cancelled
```

---

## 5. 全局状态分类

### 5.1 按状态性质分类

| 分类 | 状态 | 说明 |
|------|------|------|
| **进行中** | `draft`, `designing`, `developing`, `testing`, `publishing` | 工作正在进行 |
| **待处理** | `pending_review` | 等待 Review 验证 |
| **已完成** | `approved`, `published` | 阶段完成 |
| **异常** | `rejected`, `needs_revision`, `needs_fix`, `failed` | 需要处理问题 |
| **终止** | `paused`, `cancelled`, `deprecated`, `deleted` | 流程终止 |

### 5.2 按责任方分类

| 责任方 | 状态 | 说明 |
|--------|------|------|
| **小米辣** | `draft`, `pending_review`(产品), `approved`, `rejected` | PM 主导状态 |
| **小米粒** | `designing`, `developing`, `testing`, `publishing`, `published` | Dev 主导状态 |
| **双方** | `paused`, `cancelled`, `deprecated`, `deleted` | 共同决策状态 |

---

## 6. 状态流转规则

### 6.1 状态流转矩阵

| 当前状态 → 新状态 | draft | pending_review | approved | rejected | needs_revision | needs_fix | paused | cancelled | deprecated | deleted |
|-----------------|-------|---------------|---------|---------|---------------|----------|--------|----------|-----------|--------|
| **draft** | - | ✅ | - | - | - | - | ✅ | ✅ | - | - |
| **pending_review** | - | - | ✅ | ✅ | - | - | - | - | - | - |
| **approved** | - | - | - | - | - | - | ✅ | ✅ | - | - |
| **rejected** | ✅ | - | - | - | - | - | - | - | - | - |
| **needs_revision** | - | - | - | - | ✅ | - | ✅ | ✅ | - | - |
| **needs_fix** | - | - | - | - | - | ✅ | ✅ | ✅ | - | - |
| **paused** | ✅ | ✅ | ✅ | - | ✅ | ✅ | - | ✅ | - | - |
| **cancelled** | - | - | - | - | - | - | - | - | - | - |
| **deprecated** | - | - | - | - | - | - | - | - | - | ✅ |
| **deleted** | - | - | - | - | - | - | - | - | - | - |

### 6.2 状态流转约束

1. **不可逆状态**：
   - `cancelled`：一旦取消，不可恢复
   - `deleted`：一旦删除，不可恢复

2. **需要 Review 的状态**：
   - `pending_review` → `approved`：需要 Review 通过
   - `pending_review` → `rejected`/`needs_revision`/`needs_fix`：需要 Review 意见

3. **需要双方确认的状态**：
   - `paused`：双方协商
   - `cancelled`：双方协商
   - `deprecated`：双方协商

---

## 7. 状态通知机制

### 7.1 通知触发条件

| 触发条件 | 通知对象 | 通知内容 | 通知渠道 |
|---------|---------|---------|---------|
| 状态变更 | 双方 | 旧状态→新状态 | GitHub Issue + inbox |
| Review 提交 | 评审方 | 待评审通知 | GitHub Issue |
| Review 结果 | 提交方 | 批准/拒绝 + 意见 | GitHub Issue |
| 发布状态 | 双方 | 发布/暂停/取消/删除 | GitHub Issue + inbox |

### 7.2 通知模板

#### 状态变更通知
```markdown
## 📋 状态变更通知

**产品名称**：[产品名称]
**阶段**：[阶段名称]
**旧状态**：[旧状态]
**新状态**：[新状态]
**变更时间**：[时间]
**变更原因**：[原因]
**负责人**：[负责人]

## 📝 详细说明
[详细说明]

## 📋 下一步行动
[下一步行动]
```

#### Review 请求通知
```markdown
## 📝 Review 请求

**产品名称**：[产品名称]
**阶段**：[阶段名称]
**提交时间**：[时间]
**提交方**：[提交方]

## 📋 Review 清单
- [ ] 完整性
- [ ] 可行性
- [ ] 规范性

## 🔗 Review 链接
[Review 链接]

**请 @评审方 在 24 小时内完成 Review！**
```

#### Review 结果通知
```markdown
## ✅ Review 结果通知

**产品名称**：[产品名称]
**阶段**：[阶段名称]
**Review 结果**：✅ 批准 / ❌ 拒绝
**Review 时间**：[时间]
**评审方**：[评审方]

## 📝 Review 意见
[Review 意见]

## 📋 下一步行动
[下一步行动]
```

---

## 8. 沟通机制

### 8.1 沟通频率

| 阶段 | 频率 | 说明 |
|------|------|------|
| **初期** | 每 1 分钟 | 建立沟通习惯 |
| **中期** | 视效果而定 | 根据协作效果调整 |
| **后期** | 按需 | 成熟后可降低频率 |

### 8.2 沟通渠道

| 渠道 | 用途 | 优先级 |
|------|------|--------|
| **GitHub Issues** | 主要沟通 | P0 |
| **inbox/outbox** | 紧急通知 | P0 |
| **飞书群** | 日常沟通 | P1 |

### 8.3 问题处理流程

```
发现问题 → 提出问题 → 给出方案 → 讨论确定 → 执行方案 → 验证结果
   ↓          ↓          ↓          ↓          ↓          ↓
 小米辣    小米粒     小米粒     双方      小米粒     小米辣
```

---

## 9. 技术架构

### 9.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                   智能体协作平台                         │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐         ┌─────────────┐               │
│  │  智能体 A    │         │  智能体 B    │               │
│  │   小米辣    │         │   小米粒    │               │
│  │   (PM)     │         │   (Dev)     │               │
│  │  agent-a   │         │  agent-b   │               │
│  │  pm-skill │         │  dev-skill │               │
│  └──────┬──────┘         └──────┬──────┘               │
│         │                       │                       │
│         └───────────┬───────────┘                       │
│                     ↓                                   │
│            ┌─────────────────┐                         │
│            │  GitHub Issues   │                         │
│            │   (沟通协作)     │                         │
│            └─────────────────┘                         │
│                     ↓                                   │
│            ┌─────────────────┐                         │
│            │   状态管理器     │                         │
│            │  (状态流转)     │                         │
│            └─────────────────┘                         │
└─────────────────────────────────────────────────────────┘
```

### 9.2 核心模块

| 模块 | 功能 | 负责方 | 所属技能包 |
|------|------|--------|-----------|
| **PRD 管理** | 产品文档管理 | 小米辣 | agent-a-pm-skill |
| **技术设计** | 技术方案设计 | 小米粒 | agent-b-dev-skill |
| **开发集成** | 代码开发集成 | 小米粒 | agent-b-dev-skill |
| **Review 验证** | 测试验证审批 | 小米辣 | agent-a-pm-skill |
| **发布管理** | 发布部署管理 | 小米粒 | agent-b-dev-skill |
| **状态管理** | 状态流转通知 | 双方 | 双方各自实现 |
| **沟通协作** | Issue/inbox 沟通 | 双方 | 双方各自实现 |

---

## 10. GitHub 集成

### 10.1 Issue 模板

#### PRD 评审 Issue
```markdown
## 📋 PRD 信息
- 产品名称：
- 版本：
- 提交时间：

## 📝 产品概述
[产品描述]

## ✅ Review 清单
- [ ] 需求完整性
- [ ] 需求可行性
- [ ] 优先级合理性

## 📝 Review 意见
[Review 意见]

## ✅ Review 结果
- [ ] 批准 (approved)
- [ ] 拒绝 (rejected) - 需要修改
```

#### 技术设计 Review Issue
```markdown
## 📋 技术设计信息
- 产品名称：
- 技术版本：
- 提交时间：

## 📝 技术概述
[技术设计描述]

## ✅ Review 清单
- [ ] 架构合理性
- [ ] 技术可行性
- [ ] 代码规范

## 📝 Review 意见
[Review 意见]

## ✅ Review 结果
- [ ] 批准 (approved)
- [ ] 拒绝 (rejected) - 需要修改
```

### 10.2 状态通知 Issue

```markdown
## 📋 状态变更通知

**产品名称**：[产品名称]
**当前状态**：[新状态]
**变更时间**：[时间]
**变更原因**：[原因]

## 📝 详细说明
[详细说明]

## 📋 下一步行动
[下一步行动]
```

---

## 11. 业界最佳实践参考

### 11.1 AgentVerse
- ✅ 角色定义模板
- ✅ 消息传递机制
- ✅ 协作模式

### 11.2 OxyGent
- ✅ 工作流引擎设计
- ✅ 状态机设计
- ✅ 自动化机制

### 11.3 connectonion
- ✅ 通信协议标准化
- ✅ 状态同步机制
- ✅ 冲突解决机制

### 11.4 team-of-ai-agents
- ✅ 团队组织方式
- ✅ 任务分配算法
- ✅ 动态调整机制

---

## 12. 开发计划

### Phase 1：基础架构（1-2 天）
- [ ] 状态管理器开发（双方各自实现）
- [ ] GitHub Issue 集成（双方各自实现）
- [ ] inbox/outbox 集成（双方各自实现）

### Phase 2：核心功能（2-3 天）
- [ ] PRD 管理模块（小米辣）
- [ ] 技术设计模块（小米粒）
- [ ] Review 验证模块（小米辣）

### Phase 3：发布管理（1-2 天）
- [ ] 发布部署模块（小米粒）
- [ ] 状态通知模块（双方各自实现）
- [ ] ClawHub 集成（小米粒）

### Phase 4：测试优化（1-2 天）
- [ ] 完整流程测试
- [ ] 沟通频率优化
- [ ] 文档完善

---

## 13. 验收标准

### 功能验收
- [ ] 完整闭环流程跑通
- [ ] 所有状态定义清晰
- [ ] 状态流转正确
- [ ] 通知及时准确

### 沟通验收
- [ ] 1 分钟检查机制生效
- [ ] Issue 沟通正常
- [ ] inbox/outbox 正常

### 闭环验收
- [ ] 从产品文档提交到产品交付
- [ ] 每个阶段状态确认
- [ ] 状态通知完整

### 技能包验收
- [ ] agent-a-pm-skill 独立安装
- [ ] agent-b-dev-skill 独立安装
- [ ] 两个技能包互不干扰
- [ ] 通过 GitHub Issues 协作正常

---

## 14. 风险评估

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| 沟通延迟 | 中 | 高 | 1 分钟检查机制 |
| 状态不同步 | 中 | 高 | 状态通知机制 |
| Review 延迟 | 低 | 中 | 超时提醒机制 |
| 状态流转错误 | 低 | 高 | 状态流转矩阵约束 |
| 通知丢失 | 低 | 中 | 双重通知机制 |
| 技能包冲突 | 低 | 高 | 独立技能包设计 |

---

## 15. 附录

### 15.1 术语表

| 术语 | 说明 |
|------|------|
| 智能体 A | 小米辣（PM 代理） |
| 智能体 B | 小米粒（Dev 代理） |
| 闭环管理 | 从产品构思到产品交付的完整流程 |
| 状态流转 | 各阶段状态的变更流转 |
| Review | 评审验证机制 |
| agent-a-pm-skill | 智能体 A 的技能包 |
| agent-b-dev-skill | 智能体 B 的技能包 |

### 15.2 技能包结构

#### agent-a-pm-skill
```
agent-a-pm-skill/
├── SKILL.md
├── README.md
├── package.json
├── install.sh
├── src/
│   ├── product_manager.py
│   ├── review_validator.py
│   ├── state_manager.py
│   └── communication.py
├── tests/
└── docs/
```

#### agent-b-dev-skill
```
agent-b-dev-skill/
├── SKILL.md
├── README.md
├── package.json
├── install.sh
├── src/
│   ├── tech_designer.py
│   ├── developer.py
│   ├── tester.py
│   ├── publisher.py
│   ├── state_notifier.py
│   └── communication.py
├── tests/
└── docs/
```

### 15.3 参考资料

- [AgentVerse](https://github.com/Peiiii/AgentVerse)
- [OxyGent](https://github.com/jd-opensource/OxyGent)
- [connectonion](https://github.com/openonion/connectonion)
- [team-of-ai-agents](https://github.com/l3vels/team-of-ai-agents)
- GitHub Issues API
- ClawHub API
- 敏捷项目管理最佳实践

### 15.4 调研报告

- **调研文档**：`docs/research/agent-collaboration-best-practices.md`
- **调研时间**：2026-03-15 00:45
- **调研者**：小米辣（PM 代理）

---

**文档版本**：v4.0  
**创建时间**：2026-03-14 17:30  
**更新时间**：2026-03-15 00:55  
**更新内容**：双技能包设计（agent-a-pm-skill + agent-b-dev-skill）

**下一步**：小米粒进行技术设计

---

*智能体协作平台 PRD v4.0*
