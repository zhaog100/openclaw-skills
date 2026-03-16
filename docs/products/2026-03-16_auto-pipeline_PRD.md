# PRD: 技能自动开发流水线（auto-pipeline）

**状态**：📋 待评审  
**优先级**：P0  
**创建时间**：2026-03-16 22:35  
**创建者**：小米粒（PM代理）  
**版权**：思捷娅科技 (SJYKJ)

---

## 1. 背景

今天验证了完整的"PM派发→子代理开发→Review→修复→发布"流程，但全程需要PM手动调度。智能体协作平台概念PRD已暂停，改用**集成到OpenClaw工作流**的方案——一个能自己开发技能的技能。

## 2. 目标

将今天手动执行的6个步骤**自动化为一条流水线**：

```
PRD → 开发 → Review → 修复(循环) → 发布
```

PM只需说"开发这个技能"，剩下的自动完成。

## 3. 核心功能

### 功能1：自动开发流水线 ⭐⭐⭐⭐⭐

**验收标准**：
- [ ] 输入PRD文件路径，自动完成全流程
- [ ] 支持手动指定技能名跳过PRD读取
- [ ] 子代理超时（5分钟）自动拆分任务
- [ ] Review不通过自动派发修复子代理
- [ ] 修复后自动再次Review（最多3轮）
- [ ] 全程输出进度到终端

**命令**：
```bash
auto-pipeline run --prd docs/products/2026-03-12_xxx_PRD.md
auto-pipeline run --skill test-case-generator --priority P1
```

### 功能2：自动化Review ⭐⭐⭐⭐⭐

**验收标准**：
- [ ] 对照PRD逐项检查功能覆盖
- [ ] 实际运行每个命令验证
- [ ] 12维度评分（PRD覆盖/测试/代码/文档/CLI/错误处理/安全/性能/维护/扩展/测试覆盖/一致性）
- [ ] 输出评分+问题列表+通过/不通过结论
- [ ] 评分≥50/60自动通过，<50返回修复清单

### 功能3：自动化修复 ⭐⭐⭐⭐

**验收标准**：
- [ ] 接收Review问题列表，自动派发修复子代理
- [ ] 修复后自动运行测试验证
- [ ] 修复失败后提供详细错误信息
- [ ] 最多3轮修复-Review循环

### 功能4：自动化发布 ⭐⭐⭐⭐

**验收标准**：
- [ ] Review通过后自动执行：Git提交→推送到xiaomili→ClawHub发布
- [ ] 更新PRD状态为"已完成"
- [ ] 发布失败自动重试（最多2次，间隔10s防限流）
- [ ] 输出最终报告（技能名/版本/ClawHub ID/评分）

### 功能5：PRD看板管理 ⭐⭐⭐

**验收标准**：
- [ ] `auto-pipeline list` 列出所有PRD及状态
- [ ] `auto-pipeline status <skill>` 查看某个技能的开发状态
- [ ] 状态流转：待开发→开发中→待Review→修复中→已完成
- [ ] 自动更新 docs/products/PRD_status_summary.md

### 功能6：并行开发 ⭐⭐⭐

**验收标准**：
- [ ] `auto-pipeline batch --priority P0` 并行开发所有P0技能
- [ ] 最多同时3个子代理（避免资源耗尽）
- [ ] 每个子代理独立运行，互不干扰

## 4. 技术栈

- **语言**：Bash（主逻辑）+ 调用 OpenClaw 子代理API
- **通信**：共享文件系统（PRD/代码/Review报告）
- **版本管理**：Git（xiaomili仓库）
- **发布**：clawhub CLI
- **外部依赖**：零（纯Bash+OpenClaw内置能力）

## 5. 文件结构

```
skills/auto-pipeline/
├── SKILL.md              # 技能描述（供OpenClaw Agent读取）
├── README.md             # 用户文档
├── package.json
├── pipeline.sh           # 主入口
├── src/
│   ├── prd_reader.sh     # PRD解析+功能提取
│   ├── task_planner.sh   # 任务规划（拆分PRD为开发任务）
│   ├── review_engine.sh  # Review引擎（12维度对照PRD检查）
│   ├── fix_engine.sh     # 修复引擎（接收问题列表→派发修复）
│   ├── publish_engine.sh # 发布引擎（Git+ClawHub+PRD更新）
│   └── status_manager.sh # 状态管理（PRD看板）
├── templates/
│   ├── review_report.md  # Review报告模板
│   └── final_report.md   # 最终报告模板
└── tests/
    └── test_all.sh
```

## 6. 关键流程

### 6.1 完整流水线

```
1. 读取PRD → 提取功能清单+验收标准
2. 规划开发任务（拆分为<5分钟的子任务）
3. spawn开发子代理 → 等待完成
4. spawn Review子代理 → 12维度评分
5. if 评分≥50:
     → spawn发布子代理 → Git+ClawHub+PRD更新
   else:
     → spawn修复子代理（传入问题列表）
     → 回到步骤4（最多3轮）
6. 输出最终报告
```

### 6.2 子代理超时处理

```
开发超时（5分钟）:
  → 分析已完成部分
  → 生成修复任务（未完成的功能+已知bug）
  → 派发修复子代理继续
```

### 6.3 并行开发

```
batch --priority P0:
  → 读取所有P0 PRD
  → 同时spawn最多3个开发子代理
  → 逐个Review+修复+发布
```

## 7. 成功指标

| 指标 | 目标 |
|------|------|
| 端到端时间 | P0技能<15分钟（含Review+修复） |
| Review准确率 | ≥90%（能发现真实问题） |
| 自动化率 | ≥80%（PM只需发起+确认最终结果） |
| 发布成功率 | ≥95% |

## 8. 风险与约束

- **子代理超时**：复杂技能需拆分为多个<5分钟任务
- **ClawHub限流**：连续发布需间隔10-15秒
- **Review质量**：AI Review可能有遗漏，PM可手动介入
- **PRD质量依赖**：流水线效果取决于PRD的完整性

---

*版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)*
*GitHub: https://github.com/zhaog100/openclaw-skills*
