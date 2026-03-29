# PRD: 技能自动开发流水线（auto-pipeline）

**状态**：🔧 v1.0开发中（PM辅助工具，Review不通过后调整范围）  
**优先级**：P0  
**版本**：v1.2（明确版本规划：v1.0 PM工具 → v2.0 半自动化 → v3.0 全自动化）  
**创建时间**：2026-03-16 22:35  
**更新时间**：2026-03-16 23:07  
**创建者**：小米粒（PM代理）  
**版权**：思捷娅科技 (SJYKJ)

---

## 1. 背景

今天验证了完整的"PM派发→子代理开发→Review→修复→发布"流程，但全程需要PM手动调度。调研发现业界已形成成熟的 **"Ralph Loop"模式**（PRD→实现→检查→修复→循环），关键差异在于"检查"环节的设计质量。

### 调研来源（2026-03-16）
- **Hacker News**: 6篇高相关文章（300 Founders/0 Engineers、Goal.md、Kelos、Ralph Wiggum Loop等）
- **关键发现**: Plan-Review预审、Baseline Delta、分数驱动、双模型互审、状态外置JSON、3次上限+Escalate

## 2. 目标

将今天手动执行的步骤**自动化为一条流水线**，并融入业界最佳实践：

```
PRD → Plan预审 → 开发 → Review(量化评分) → 修复(循环≤3次) → 发布
```

PM只需说"开发这个技能"，剩下的自动完成。

## 3. 核心功能

### 功能1：自动开发流水线 ⭐⭐⭐⭐⭐

**验收标准**：
- [ ] 输入PRD文件路径，自动完成全流程
- [ ] 支持手动指定技能名跳过PRD读取
- [ ] 子代理超时（5分钟）自动拆分任务
- [ ] Review不通过自动派发修复子代理
- [ ] 修复后自动再次Review（**最多3轮，超限升级给官家**）
- [ ] 全程输出进度到终端

**命令**：
```bash
auto-pipeline run --prd docs/products/2026-03-12_xxx_PRD.md
auto-pipeline run --skill test-case-generator --priority P1
```

### 功能2：Plan预审阶段 🆕（调研融入）⭐⭐⭐⭐⭐

**调研依据**：Goal.md（23分HN）、300 Founders/0 Engineers — 在开发前让reviewer子代理审查实现计划，循环直到建议冗余，大幅降低返工率。

**验收标准**：
- [ ] 解析PRD后，先生成结构化任务声明（JSON格式）
- [ ] 每个任务明确：输入/输出/验收标准
- [ ] spawn Plan-Reviewer子代理审查任务声明
- [ ] Plan-Reviewer循环改进直到"无新建议"或达到2轮上限
- [ ] 为每个任务生成"实现信心度评分"（1-10）
- [ ] 信心度<7的任务拆分为更细粒度子任务

**任务声明格式**：
```json
{
  "task_id": "T1",
  "name": "实现命令解析模块",
  "input": "PRD第3节功能1的验收标准",
  "output": "src/parser.sh，含3个子命令解析",
  "acceptance": ["--help正常显示", "未知命令返回错误码1"],
  "confidence": 8
}
```

### 功能3：自动化Review（量化评分）⭐⭐⭐⭐⭐

**验收标准**：
- [ ] 对照PRD逐项检查功能覆盖（**Baseline Delta原则：只检查新增代码**）
- [ ] 实际运行每个命令验证
- [ ] **12维度评分**，每项1-5分，满分60分
- [ ] 为每个PRD功能项输出通过/未通过/部分通过
- [ ] 评分≥50/60 → 通过；<50 → 返回修复清单
- [ ] **双模型交叉Review**（开发模型≠Review模型，减少盲区）

**12维度**：
| 维度 | 权重 | 说明 |
|------|------|------|
| PRD功能覆盖度 | 2x | 每个PRD功能是否实现 |
| 运行测试 | 1x | 测试通过率 |
| 代码质量 | 1x | bash -n、变量安全、错误处理 |
| 文档完整性 | 1x | SKILL.md/README.md/版权 |
| CLI设计 | 1x | --help清晰度 |
| 错误处理 | 1x | 边界情况覆盖 |
| 安全性 | 1x | 输入验证、无API Key泄露 |
| 性能 | 1x | 响应时间 |
| 可维护性 | 1x | 代码结构清晰度 |
| 可扩展性 | 1x | 是否易于添加功能 |
| 测试覆盖 | 1x | 正面+负面测试 |
| PRD一致性 | 1x | 实现与PRD描述一致 |

### 功能4：自动化修复（有限循环）⭐⭐⭐⭐

**验收标准**：
- [ ] 接收Review问题列表（含严重度排序）
- [ ] 自动派发修复子代理，传入精确的问题列表
- [ ] 修复后自动运行测试+Review
- [ ] **修复循环最多3轮**，超限则：
  - 暂停流水线
  - 生成详细报告（已修复/未修复/建议）
  - **升级给官家决策**
- [ ] **失败回退**：如Review发现根本性理解偏差，回退到Plan阶段而非代码层面修复

### 功能5：自动化发布 ⭐⭐⭐⭐

**验收标准**：
- [ ] Review通过后自动执行：Git提交→推送到xiaomili→ClawHub发布
- [ ] 更新PRD状态为"已完成"
- [ ] 发布失败自动重试（最多2次，间隔15s防限流）
- [ ] 输出最终报告（技能名/版本/ClawHub ID/Review评分/修复轮次）

### 功能6：PRD看板管理 ⭐⭐⭐

**验收标准**：
- [ ] `auto-pipeline list` 列出所有PRD及状态
- [ ] `auto-pipeline status <skill>` 查看某个技能的详细状态
- [ ] 状态流转：待开发→Plan预审→开发中→待Review→修复中→已完成/升级等待
- [ ] **状态外置到JSON文件**（不依赖模型上下文传递）

**状态文件格式**：
```json
{
  "skill": "cli-tool-generator",
  "status": "fixing",
  "round": 2,
  "review_score": 46,
  "issues_remaining": ["AI命令生成缺失"],
  "child_session": "agent:main:subagent:xxx",
  "started_at": "2026-03-16T22:00:00"
}
```

### 功能7：并行开发 ⭐⭐⭐

**验收标准**：
- [ ] `auto-pipeline batch --priority P0` 并行开发所有P0技能
- [ ] 最多同时**3个子代理**（避免资源耗尽）
- [ ] 每个子代理独立工作目录，互不干扰
- [ ] 逐个完成Review+修复+发布

## 4. 技术栈

- **语言**：Bash（主逻辑+流程编排）
- **通信**：共享文件系统（PRD/代码/Review报告/状态JSON）
- **版本管理**：Git（xiaomili仓库）
- **发布**：clawhub CLI
- **外部依赖**：零（纯Bash+OpenClaw内置子代理能力）

## 5. 文件结构

```
skills/auto-pipeline/
├── SKILL.md              # 技能描述（供OpenClaw Agent读取）
├── README.md             # 用户文档
├── package.json
├── pipeline.sh           # 主入口
├── src/
│   ├── prd_reader.sh     # PRD解析+功能提取+任务声明生成
│   ├── plan_reviewer.sh  # Plan预审（审查任务声明直到建议冗余）
│   ├── task_planner.sh   # 任务规划（拆分PRD为<5分钟的子任务）
│   ├── review_engine.sh  # Review引擎（12维度对照PRD检查+量化评分）
│   ├── fix_engine.sh     # 修复引擎（问题清单→修复子代理→循环）
│   ├── publish_engine.sh # 发布引擎（Git+ClawHub+PRD更新）
│   └── status_manager.sh # 状态管理（JSON文件+看板）
├── templates/
│   ├── task_declaration.json    # 任务声明模板
│   ├── review_report.md         # Review报告模板
│   └── final_report.md          # 最终报告模板
└── tests/
    └── test_all.sh
```

## 6. 关键流程

### 6.1 完整流水线（融入调研成果）

```
1. 读取PRD → 提取功能清单+验收标准
2. 生成结构化任务声明（JSON）
3. 🆕 Plan-Reviewer预审任务声明（循环直到无新建议）
4. 信心度<7的任务 → 拆分为更细粒度
5. spawn开发子代理 → 等待完成（5分钟超时自动拆分）
6. 🆕 spawn Review子代理（用不同于开发的模型）→ 12维度评分
7. if 评分≥50:
     → spawn发布子代理 → Git+ClawHub+PRD更新
   else if 修复轮次<3:
     → spawn修复子代理（传入精确问题列表）
     → 回到步骤6
   else:
     → 🆕 暂停+升级给官家（含详细报告）
8. 🆕 更新状态JSON文件
9. 输出最终报告
```

### 6.2 子代理超时处理

```
开发超时（5分钟）:
  → 分析已完成部分（读取已生成的文件）
  → 生成修复任务（未完成的功能+已知bug）
  → 派发修复子代理继续
```

### 6.3 失败回退机制 🆕

```
Review发现根本性偏差（如：完全理解错了PRD）:
  → 不进入修复循环
  → 回退到Plan阶段，重新生成任务声明
  → 重新Plan-Review → 重新开发
```

## 7. 成功指标

| 指标 | 目标 |
|------|------|
| 端到端时间 | P0技能<15分钟（含Plan预审+Review+修复） |
| Review准确率 | ≥90%（能发现真实问题，不产生幻觉通过） |
| 一次通过率 | ≥50%（经Plan预审后提升） |
| 3轮内通过率 | ≥90% |
| 自动化率 | ≥80%（PM只需发起+确认最终结果或处理升级） |
| 发布成功率 | ≥95% |

## 8. 风险与约束

- **子代理超时**：复杂技能需拆分为多个<5分钟任务
- **ClawHub限流**：连续发布需间隔15秒
- **Review幻觉**：双模型交叉Review+PRD逐项对照降低风险
- **PRD质量依赖**：流水线效果取决于PRD的完整性
- **资源限制**：并行最多3个子代理，避免内存/CPU耗尽
- **状态持久化**：所有进度外置到JSON文件，不依赖模型上下文

## 9. 与现有技能的关系

| 现有技能 | auto-pipeline中的角色 |
|---------|---------------------|
| sessions_spawn | 开发/Review/修复子代理的创建 |
| clawhub publish | 自动发布环节 |
| smart-model-switch | 双模型Review（切换不同模型） |
| error-handler | 子代理错误处理 |
| github (skill) | Git操作+Issue管理 |

## 10. 版本规划（更新：2026-03-16 23:07）

### v1.0 — PM辅助工具（当前版本）⭐
- **定位**：PM手动操作的质量保障工具，不自动spawn子代理
- 功能3：Review引擎（12维度评分+PRD逐项对照）
- 功能5：发布引擎（Git+ClawHub+PRD更新+重试）
- 功能6：PRD看板（list/status+状态JSON）
- 功能2：Plan预审（任务声明审查+信心度评分）
- 功能4：修复引擎（问题清单格式化+回退判断，PM手动派发修复）
- 手动触发，PM作为调度中心

### v2.0 — 半自动化（子代理集成）
- **定位**：集成OpenClaw sessions_spawn，自动spawn开发/修复子代理
- 功能1：自动开发流水线（spawn开发子代理+超时处理）
- 功能4升级：自动spawn修复子代理（≤3轮循环+升级）
- 子代理prompt模板引擎
- task_planner.sh（智能任务拆分）

### v3.0 — 全自动化（智能体协作）
- **定位**：一个能自己开发技能的技能
- 功能3升级：双模型Review（开发模型≠Review模型）
- 功能3升级：Baseline Delta（只检查新增代码）
- 功能7：并行开发（batch命令+3子代理并行）
- 失败回退机制（自动回退Plan阶段）
- 端到端自动化（PM只需发起+确认）

### 版本演进路线
```
v1.0 PM工具（手动调度）  →  v2.0 半自动化（spawn子代理）  →  v3.0 全自动化（智能体协作）
```

---

*版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)*
*GitHub: https://github.com/zhaog100/openclaw-skills*
