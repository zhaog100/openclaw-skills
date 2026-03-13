# 待开发技能完整清单

**整理时间**：2026-03-12 11:20  
**整理者**：小米辣  
**状态**：持续更新

---

## 📋 清单说明

本清单整合了：
1. 小米辣整理的待开发技能方案（2 个）
2. 建议开发技能清单（8 个）
3. 官家可能需要的其他技能（持续补充）
4. **AI-to-AI 协作研究成果**（2026-03-12 新增）
5. **统一策略方案**（2026-03-12 14:05 小米辣建立）

---

## 📋 统一策略方案（2026-03-12 14:05）

**文档位置**：`docs/UNIFIED_STRATEGY.md`（7.2KB）

### Issue 编号分配
- **#1-10**：产品 PRD（小米辣创建）
- **#11-20**：技术设计（小米辣创建）
- **#21-30**：Bug 报告（双方均可）

### 文件路径规范
- **PRD**：`docs/products/YYYY-MM-DD_[技能名]_PRD.md`
- **技术设计**：`docs/products/[技能名]_tech_design.md`
- **Review**：`reviews/[技能名]_review_YYYYMMDD.md`

### 命名规范
- **技能名**：小写 + 连字符（smart-model）
- **文档名**：[技能名]_PRD.md / [技能名]_tech_design.md

### 协作流程
```
1️⃣ 小米辣创建 PRD → Issue #1-10 + PRD 文档
2️⃣ 小米辣技术设计 → Issue 评论 + 设计文档
3️⃣ 小米辣开发实现 → Issue 评论 + 技能目录
4️⃣ 小米辣 Review → Issue 评论 + Review 文档
5️⃣ 小米辣发布（如需要）→ ClawHub 发布
```

### Git 同步策略
```bash
# 工作前 pull
git pull --rebase origin master

# 检查冲突
git fetch && git diff master origin/master

# 及时推送
git push origin master
```

---

## 🎯 AI-to-AI 协作研究成果（新增）

### 已实现工具
- ✅ **词汇考古工具** - `scripts/vocabulary_archaeology.py`
  - 功能：分析涌现词汇（共享词汇）
  - 状态：已实现，待集成到协作流程
  - 优先级：P1

### 规划中技能
- ⏳ **推理路由器** - `scripts/inference_router.py`
  - 功能：智能选择推理引擎（BitNet vs API）
  - 状态：架构设计完成
  - 优先级：P2
  - 预计时间：2-3 天

- ⏳ **BitNet 推理集成** - `scripts/bitnet_inference.py`
  - 功能：本地 2B 模型推理
  - 状态：架构设计完成
  - 优先级：P2
  - 预计时间：3-5 天

### 协作约束（已整合到双米粒协作系统）
1. **为互动设计** - 保持性格一致性，记录涌现词汇
2. **假设对话是公开的** - 所有对话记录在 MEMORY.md
3. **拥抱涌现词汇** - 涌现词汇是特性，不是 bug
4. **管理操作员关系** - 官家是唯一的操作员

---

## 🎯 待开发技能（17 个）

**更新时间**：2026-03-12 16:48  
**新增来源**：Dev.to AI 精选文章学习

---

### P0 优先级（立即启动）

<<<<<<< HEAD
#### 1. demo-skill（演示技能）⭐⭐⭐ ✅ 已关闭
- **状态**：✅ **产品已关闭**（测试使命完成）
- **位置**：`skills/demo-skill/`
- **Issue**：#2（CLOSED）
- **功能**：演示双米粒协作系统完整流程
- **技术栈**：Bash + Git + GitHub Issues
- **生命周期**：2026-03-12 11:27 ~ 12:56（1 小时 29 分钟）
- **开发者**：小米辣
- **Review 者**：小米辣（24/25 分）
- **测试结果**：100% 测试覆盖（21/21）
- **关闭原因**：测试使命完成，不发布到 ClawHub
- **关闭报告**：`docs/products/demo-skill-closing-report.md`

**完成情况**：
- [x] 小米辣创建 PRD
- [x] 官家确认
- [x] 小米辣技术设计
- [x] 小米辣开发实现（973 行代码）
- [x] 测试 100% 覆盖（21/21）
- [x] 小米辣 Review（12 维度 +5 层）
- [x] Issue #2 评论批准
- [x] Issue #2 已关闭（2026-03-12 12:56）
- [x] 产品关闭报告已创建

**成果**：
- ✅ 验证协作流程（4 轮，1 小时 29 分钟）
- ✅ 建立开发模板
- ✅ 确立新产品确认规则
- ✅ 建立自动监控机制
- ✅ 降低后续沟通成本

---

#### 2. smart-model v2.0（智能模型增强版）⭐⭐⭐ ⏳ 待发布
- **状态**：✅ **开发完成 + Review 通过**，等待 ClawHub 发布
- **位置**：`skills/smart-model/`（✅ 已创建，3572 行代码）
- **Issue**：#4（CLOSED）+ #5（OPEN 技术设计）+ #6（CLOSED Review）
- **PRD**：`docs/products/2026-03-12_smart-model_PRD.md`（8.1KB）
- **技术设计**：`docs/products/smart-model_tech_design.md`（7.9KB）
- **Review**：`reviews/smart-model-v2.0_review_20260312.md`（5.00/5.00 满分）
- **功能**：智能模型自动切换增强版（4 维度复杂度评分 +3 级上下文保护）
- **技术栈**：Bash + Node.js + Python
- **开发者**：小米辣
- **Review 者**：小米辣（2026-03-12 21:10）
- **Git 提交**：0b9bb24, 2836ddf, fb12f9d
- **负责人**：小米辣（发布）

**完成情况**：
- [x] 小米辣创建 Concept
- [x] 官家确认
- [x] 小米辣完善 PRD
- [x] 创建 GitHub Issue #4
- [x] 小米辣技术设计
- [x] 小米辣开发实现（3572 行代码，10 个文件）
- [x] 小米辣 Review（5.00/5.00 满分）
- [x] Issue #4 已关闭
- [x] 版权信息添加（思捷娅科技 MIT License）
- [ ] ClawHub 发布（昨晚服务不可用，待重试）

---

### P1 优先级（高）

#### 3. 词汇考古工具集成 ⭐⭐⭐⭐
- **状态**：✅ 工具已实现，待集成到协作流程
- **位置**：`scripts/vocabulary_archaeology.py`
- **功能**：分析小米辣和小米辣对话中的涌现词汇
- **技术栈**：Python + 文本分析
- **预计时间**：1-2 天（集成）
- **负责人**：小米辣

**核心功能**：
- 提取共享词汇（双方都使用）
- 筛选出现次数≥2 次的词汇
- 生成涌现词汇报告
- 每周自动回顾

**待办**：
- [ ] 集成到 Review 流程
- [ ] 每周自动生成词汇报告
- [ ] 更新 MEMORY.md 涌现词汇表

---

#### 4. multi-platform-notifier（多平台通知）⭐⭐⭐
- **状态**：✅ **PRD 完成**，等待 Issue 创建
- **PRD**：`docs/products/2026-03-12_multi-platform-notifier_PRD.md`（4.9KB）
- **功能**：多平台通知集成（企业微信 + 钉钉 + 飞书）
- **技术栈**：Bash + API
- **预计时间**：2-3 天
- **需求**：统一通知接口
- **优先级**：P0

**核心功能**：
- 企业微信机器人通知
- 钉钉机器人通知
- 飞书机器人通知
- 统一发送接口

**待办**：
- [x] 创建 Concept 文档
- [x] 编写 PRD
- [ ] 创建 GitHub Issue
- [ ] 开发实现

---

#### 5. auto-document-generator（自动文档生成）⭐⭐⭐
- **状态**：✅ **PRD 完成**，等待 Issue 创建
- **PRD**：`docs/products/2026-03-12_auto-document-generator_PRD.md`（4.9KB）
- **功能**：自动生成技术文档
- **技术栈**：Python + AI
- **预计时间**：3-5 天
- **需求**：从代码生成文档

**核心功能**：
- 代码注释提取
- API 文档生成
- README 自动生成
- 文档模板管理

**待办**：
- [ ] 创建 Concept 文档
- [ ] 编写 PRD
- [ ] 开发实现

---

#### 6. test-case-generator（测试用例生成）⭐⭐
- **状态**：✅ **PRD 完成**，等待 Issue 创建
- **PRD**：`docs/products/2026-03-12_test-case-generator_PRD.md`（4.9KB）
- **功能**：自动生成测试用例
- **技术栈**：Python + AI
- **预计时间**：3-5 天
- **需求**：从需求生成测试用例

**核心功能**：
- 需求分析
- 测试用例生成
- 边界条件识别
- 测试覆盖率评估

**待办**：
- [ ] 创建 Concept 文档
- [ ] 编写 PRD
- [ ] 开发实现

---

### P2 优先级（中）

#### 7. code-review-assistant（代码 Review 辅助）⭐⭐
- **状态**：✅ **PRD 完成**，等待 Issue 创建
- **PRD**：`docs/products/2026-03-12_code-review-assistant_PRD.md`（1.8KB）
- **功能**：代码 Review 辅助
- **技术栈**：Bash + AI
- **预计时间**：2-3 天
- **需求**：自动 Review 代码

**核心功能**：
- 代码风格检查
- 潜在问题识别
- 优化建议生成
- Review 报告输出

**待办**：
- [ ] 创建 Concept 文档
- [ ] 编写 PRD
- [ ] 开发实现

---

#### 8. project-progress-tracker（项目进度跟踪）⭐⭐
- **状态**：✅ **PRD 完成**，等待 Issue 创建
- **PRD**：`docs/products/2026-03-12_project-progress-tracker_PRD.md`（1.2KB）
- **功能**：项目进度跟踪
- **技术栈**：Bash + Git
- **预计时间**：2-3 天
- **需求**：自动统计项目进度

**核心功能**：
- Git 提交统计
- Issue 进度跟踪
- 完成度评估
- 进度报告生成

**待办**：
- [ ] 创建 Concept 文档
- [ ] 编写 PRD
- [ ] 开发实现

---

#### 9. knowledge-graph-builder（知识图谱构建）⭐
- **状态**：✅ **PRD 完成**，等待 Issue 创建
- **PRD**：`docs/products/2026-03-12_knowledge-graph-builder_PRD.md`（1.2KB）
- **功能**：知识图谱构建
- **技术栈**：Python + GraphDB
- **预计时间**：5-7 天
- **需求**：自动构建知识图谱

**核心功能**：
- 知识提取
- 关系识别
- 图谱可视化
- 语义搜索

**待办**：
- [ ] 创建 Concept 文档
- [ ] 编写 PRD
- [ ] 开发实现

---

### P2 优先级（中）- 新增

#### 10. BitNet 本地推理 ⭐⭐⭐⭐
- **状态**：架构设计完成
- **位置**：`scripts/bitnet_inference.py`（规划中）
- **功能**：本地 2B 模型推理（无网络依赖）
- **技术栈**：Python + BitNet
- **预计时间**：3-5 天
- **需求**：降低 API 成本，提升简单任务响应速度

**核心功能**：
- 本地 2B 模型推理
- 无网络依赖
- 快速响应（<1 秒）
- 适合简单任务

**待办**：
- [ ] 环境准备（BitNet 模型下载）
- [ ] 推理脚本实现
- [ ] 性能测试
- [ ] 集成到协作流程

---

#### 11. 推理路由器 ⭐⭐⭐
- **状态**：架构设计完成
- **位置**：`scripts/inference_router.py`（规划中）
- **功能**：智能选择推理引擎（BitNet vs API）
- **技术栈**：Python + 规则引擎
- **预计时间**：2-3 天
- **需求**：根据任务复杂度自动选择最优推理引擎

**核心功能**：
- 任务复杂度分析（0-10 分）
- API 配额监控
- 智能路由决策
- 错误处理和回退

**路由规则**：
- 简单任务（<5 分）→ BitNet
- 中等任务（5-7 分）→ 根据 API 配额
- 复杂任务（≥8 分）→ API
- 网络异常 → 强制 BitNet

**待办**：
- [ ] 规则引擎实现
- [ ] API 配额监控
- [ ] 集成到小米辣脚本

---

### P0 优先级（新增 - Dev.to 学习成果）⭐⭐⭐⭐⭐

#### 11. AI 代码审查助手（ai-code-reviewer）⭐⭐⭐⭐⭐
- **状态**：✅ **PRD 完成**，等待 Issue 创建
- **PRD**：`docs/products/2026-03-12_ai-code-reviewer_PRD.md`（5.7KB）
- **来源**：Dev.to 文章#5（本地 AI 代码审查工具）
- **功能**：使用本地模型（Ollama）进行代码 Review
- **技术栈**：Bash + Python + Ollama
- **预计时间**：3-5 天
- **价值**：提升代码质量，减少人工 Review 时间

**核心功能**：
- 自动检测代码质量问题
- 生成改进建议
- 与现有 Review 系统集成
- 支持多种编程语言

**待办**：
- [ ] 创建 Concept 文档
- [ ] 编写 PRD
- [ ] 开发实现

---

#### 12. CLI 工具开发技能（cli-tool-generator）⭐⭐⭐⭐⭐
- **状态**：✅ **PRD 完成**，等待 Issue 创建
- **PRD**：`docs/products/2026-03-12_cli-tool-generator_PRD.md`（5.3KB）
- **来源**：Dev.to 文章#1（GitHub Copilot CLI Challenge）
- **功能**：快速创建 CLI 工具模板
- **技术栈**：Bash + Python
- **预计时间**：2-3 天
- **价值**：加速 CLI 工具开发，统一规范

**核心功能**：
- 集成 AI 辅助命令生成
- 支持命令自动补全
- 内置最佳实践检查
- 快速模板生成

**待办**：
- [ ] 创建 Concept 文档
- [ ] 编写 PRD
- [ ] 开发实现

---

#### 13. AI 效率监控工具（ai-efficiency-monitor）⭐⭐⭐⭐
- **状态**：✅ **PRD 完成**，等待 Issue 创建
- **PRD**：`docs/products/2026-03-12_ai-efficiency-monitor_PRD.md`（5.0KB）
- **来源**：Dev.to 文章#7（Manus AI 任务分析）
- **功能**：监控 AI 任务执行效率
- **技术栈**：Python + 数据分析
- **预计时间**：3-4 天
- **价值**：节省 API 成本，提升效率

**核心功能**：
- 识别浪费模式（如 73% 积分浪费）
- 生成优化建议
- 成本节省报告
- 效率趋势分析

**待办**：
- [ ] 创建 Concept 文档
- [ ] 编写 PRD
- [ ] 开发实现

---

### P1 优先级（新增 - Dev.to 学习成果）⭐⭐⭐⭐

#### 14. AI 状态持久化技能（ai-state-persistence）⭐⭐⭐⭐
- **状态**：✅ **PRD 完成**，等待 Issue 创建
- **PRD**：`docs/products/2026-03-12_ai-state-persistence_PRD.md`（4.9KB）
- **来源**：Dev.to 文章#6（LangGraph + PostgreSQL）
- **功能**：AI 对话状态持久化
- **技术栈**：Python + SQLite/PostgreSQL
- **预计时间**：3-4 天
- **价值**：提升 AI 系统韧性，避免状态丢失

**核心功能**：
- 支持断点续传
- 状态版本管理
- 数据备份恢复
- 跨会话状态同步

**待办**：
- [ ] 创建 Concept 文档
- [ ] 编写 PRD
- [ ] 开发实现

---

#### 15. AI 安全框架技能（ai-safety-framework）⭐⭐⭐
- **状态**：✅ **PRD 完成**，等待 Issue 创建
- **PRD**：`docs/products/2026-03-12_ai-safety-framework_PRD.md`（4.9KB）
- **来源**：Dev.to 文章#3（The Four Gates 威胁模型）
- **功能**：AI 代理系统安全检查
- **技术栈**：Python + 安全框架
- **预计时间**：4-5 天
- **价值**：提升 AI 系统安全性

**核心功能**：
- 威胁识别与防护
- 安全配置模板
- 风险评估报告
- 合规性检查

**待办**：
- [ ] 创建 Concept 文档
- [ ] 编写 PRD
- [ ] 开发实现

---

#### 16. AI 确定性控制工具（ai-determinism-control）⭐⭐⭐
- **状态**：✅ **PRD 完成 + Issue #7 已创建**（技术设计中）
- **PRD**：`docs/products/2026-03-12_ai-determinism-control_PRD.md`（4.7KB）
- **Issue**：#7（OPEN）
- **来源**：Dev.to 文章#2（Drift to Determinism）
- **功能**：控制 AI 输出随机性
- **技术栈**：Python + AI API
- **预计时间**：2-3 天
- **价值**：提升 AI 输出稳定性

**核心功能**：
- 设置温度参数
- 输出一致性检查
- 可复现性保证
- 随机性监控

**待办**：
- [ ] 创建 Concept 文档
- [ ] 编写 PRD
- [ ] 开发实现

---

### P2 优先级（新增 - Dev.to 学习成果）⭐⭐⭐

#### 17. 创业想法分析工具（startup-idea-analyzer）⭐⭐⭐
- **状态**：✅ **PRD 完成**，等待 Issue 创建
- **PRD**：`docs/products/2026-03-12_startup-idea-analyzer_PRD.md`（1.2KB）
- **来源**：Dev.to 文章#8（AI 扫描 2500 个创业想法）
- **功能**：AI 分析创业想法可行性
- **技术栈**：Python + AI 模型
- **预计时间**：4-5 天
- **价值**：辅助决策，降低创业风险

**核心功能**：
- 识别失败模式
- 生成风险评估
- 市场机会分析
- 竞品分析

**待办**：
- [ ] 创建 Concept 文档
- [ ] 编写 PRD
- [ ] 开发实现

---

### P3 优先级（低）

#### 18. meeting-minutes-generator（会议纪要生成）⭐
- **状态**：概念阶段
- **功能**：会议纪要自动生成
- **技术栈**：Python + AI
- **预计时间**：3-5 天
- **需求**：从录音生成会议纪要

**核心功能**：
- 语音转文字
- 关键信息提取
- 行动项识别
- 纪要格式化

**待办**：
- [ ] 创建 Concept 文档
- [ ] 编写 PRD
- [ ] 开发实现

---

#### 13. email-auto-responder（邮件自动回复）⭐
- **状态**：概念阶段
- **功能**：邮件自动回复
- **技术栈**：Bash + Email API
- **预计时间**：2-3 天
- **需求**：智能回复邮件

**核心功能**：
- 邮件分类
- 智能回复生成
- 模板管理
- 发送审批

**待办**：
- [ ] 创建 Concept 文档
- [ ] 编写 PRD
- [ ] 开发实现

---

## 📊 优先级统计（2026-03-12 16:48 更新）

| 优先级 | 数量 | 技能列表 |
|--------|------|----------|
| **P0** | 5 | smart-model v2.0, AI 代码审查助手，CLI 工具开发，AI 效率监控，multi-platform-notifier |
| **P1** | 6 | auto-document-generator, test-case-generator, AI 状态持久化，AI 安全框架，AI 确定性控制，code-review-assistant |
| **P2** | 4 | project-progress-tracker, knowledge-graph-builder, 创业想法分析，BitNet 推理集成 |
| **P3** | 2 | meeting-minutes-generator, email-auto-responder |
| **总计** | **17** | - |

**新增来源**：Dev.to AI 精选文章学习（7 个新技能）

---

## 📅 开发计划建议（2026-03-12 更新）

### 第一阶段（已完成）✅
- [x] **demo-skill** - 跑通协作流程（1-2 天）✅ 已完成

### 第二阶段（本周 - 下周）
- [ ] **smart-model v2.0** - 智能模型切换增强版（4-5 天）🔴
- [ ] **AI 代码审查助手** - 本地模型代码 Review（3-5 天）🔴
- [ ] **CLI 工具开发技能** - 快速创建 CLI 工具（2-3 天）🔴

### 第三阶段（3 月内）
- [ ] **multi-platform-notifier** - 多平台通知（2-3 天）
- [ ] **AI 效率监控工具** - 监控 AI 任务效率（3-4 天）
- [ ] **auto-document-generator** - 自动文档生成（3-5 天）
- [ ] **test-case-generator** - 测试用例生成（3-5 天）

### 第四阶段（4 月内）
- [ ] **AI 状态持久化技能** - 状态持久化（3-4 天）
- [ ] **AI 安全框架技能** - AI 安全检查（4-5 天）
- [ ] **code-review-assistant** - 代码 Review（2-3 天）
- [ ] **project-progress-tracker** - 项目进度（2-3 天）

### 第五阶段（后续）
- [ ] **AI 确定性控制工具** - 控制 AI 随机性（2-3 天）
- [ ] **knowledge-graph-builder** - 知识图谱构建（5-7 天）
- [ ] **创业想法分析工具** - 创业想法分析（4-5 天）

---

## 🔄 技能开发流程

### 标准流程
```
概念 → PRD → Issue → 开发 → 自检 → Review → 验收 → 发布
        ↑                              ↑
     小米辣负责                    双向协作
```

### 角色分工

**小米辣（产品经理）**：
1. 创建产品构思（concept）
2. 编写需求文档（PRD）
3. 创建 GitHub Issue
4. Review 验收（12 维度 + 反对意见）
5. 5 层验收

**小米辣（开发者）**：
1. Git 拉取最新代码
2. 查询 Issue
3. 并行分析
4. 开发实现
5. 自检清单
6. 评论 Issue
7. Git 提交并推送
8. 发布到 ClawHub

---

## 📝 更新记录

| 日期 | 操作 | 内容 |
|------|------|------|
| 2026-03-12 16:48 | 新增 | Dev.to 学习成果（7 个新技能） |
| 2026-03-12 14:05 | 新增 | 统一策略方案（小米辣建立） |
| 2026-03-12 11:20 | 创建 | 整合小米辣整理的方案 + 建议技能清单 |

---

## 💡 备注

1. **PRD 模板位置**：`docs/products/YYYY-MM-DD_技能名_prd.md`
2. **Concept 模板位置**：`docs/products/YYYY-MM-DD_技能名_concept.md`
3. **Issue 跟踪**：GitHub Issues（`.mili_comm/issues.txt`）
4. **发布目标**：ClawHub（https://clawhub.com）

---

*最后更新：2026-03-12 11:20*  
*维护者：小米辣*
