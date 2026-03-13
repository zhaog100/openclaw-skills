# 双米粒协作系统执行脚本

**版本**：v3.1 - 社区启发增强版
**发布日期**：2026-03-12

---

## 📋 脚本概览

| 脚本 | 角色 | 文件大小 | 功能数 |
|------|------|---------|--------|
| **mili_product_v3.sh** | 米粒儿（产品经理+质量官） | 10.6KB | 10个 |
| **xiaomi_dev_v3.sh** | 小米辣（开发者+测试者） | 11KB | 10个 |

---

## 🎭 米粒儿脚本（mili_product_v3.sh）

### 基本信息

```bash
#!/bin/bash
# 米粒儿协作脚本 v3.1 - 社区启发增强版
# 角色：产品经理 + 质量官
# 功能：产品构思、需求文档、并行分析、12维度Review（含反对意见）、5层验收、系统状态检查
```

### 核心功能（10个）

#### 1. 产品构思（concept）
```bash
bash scripts/mili_product_v3.sh <功能名> concept
```
- 创建产品构思文档
- 定义核心价值
- 描述用户场景
- 评估风险

#### 2. 需求文档（prd）
```bash
bash scripts/mili_product_v3.sh <功能名> prd
```
- 编写PRD文档
- 详细功能需求
- 技术要求
- 验收标准

#### 3. 并行分析（analyze）
```bash
bash scripts/mili_product_v3.sh <功能名> analyze
```
- 与小米辣同时分析方案
- 产品视角分析
- 用户需求分析
- 商业价值分析

#### 4. Review评价（review）
```bash
bash scripts/mili_product_v3.sh <功能名> review
```
- 12维度Review清单
- 包含反对意见（社区启发）
- Review思路记录
- 改进建议

#### 5. 5层验收（accept）
```bash
bash scripts/mili_product_v3.sh <功能名> accept
```
- Layer 1: 需求完整性
- Layer 2: 设计合理性
- Layer 3: 代码质量
- Layer 4: 功能完整性
- Layer 5: 用户体验

#### 6. 通知小米辣（notify）
```bash
bash scripts/mili_product_v3.sh <功能名> notify
```
- 创建通知文件
- 告知小米辣开始工作
- 传递产品构思

#### 7. 发布批准（release）
```bash
bash scripts/mili_product_v3.sh <功能名> release
```
- 批准发布
- 创建发布标记
- 通知小米辣发布

#### 8. 查看Review（view-review）
```bash
bash scripts/mili_product_v3.sh <功能名> view-review
```
- 查看Review文档
- 学习Review思路
- 提取改进点

#### 9. 系统状态检查（check）
```bash
bash scripts/mili_product_v3.sh <功能名> check
```
- Git状态检查
- 网络连接检查
- 依赖检查

#### 10. 帮助信息（help）
```bash
bash scripts/mili_product_v3.sh help
```
- 显示所有命令
- 使用说明

---

## 🔧 小米辣脚本（xiaomi_dev_v3.sh）

### 基本信息

```bash
#!/bin/bash
# 小米辣协作脚本 v3.1 - 社区启发增强版
# 角色：开发者 + 测试者
# 功能：并行分析、开发实现、开发前自检、Review后思考（含质疑清单）、Git管理、ClawHub发布、系统状态检查
```

### 核心功能（10个）

#### 1. 并行分析（analyze）
```bash
bash scripts/xiaomi_dev_v3.sh <功能名> analyze
```
- 与米粒儿同时分析方案
- 技术视角分析
- 架构设计
- 风险评估

#### 2. 开发实现（dev）
```bash
bash scripts/xiaomi_dev_v3.sh <功能名> dev
```
- 创建Git分支
- 开发功能代码
- 编写单元测试
- 本地测试

#### 3. 开发前自检（check）
```bash
bash scripts/xiaomi_dev_v3.sh <功能名> check
```
- 技术可行性检查
- 风险评估检查
- 时间估算检查
- 替代方案准备

#### 4. Review后思考（think）
```bash
bash scripts/xiaomi_dev_v3.sh <功能名> think
```
- 质疑清单（社区启发）
- 反向思考
- 补充建议
- 改进方案

#### 5. Git管理（git）
```bash
bash scripts/xiaomi_dev_v3.sh <功能名> git
```
- 提交代码
- 推送到GitHub
- 创建PR（可选）

#### 6. ClawHub发布（publish）
```bash
bash scripts/xiaomi_dev_v3.sh <功能名> publish
```
- 发布到ClawHub
- 版本管理
- 发布确认

#### 7. 学习Review（learn）
```bash
bash scripts/xiaomi_dev_v3.sh <功能名> learn
```
- 读取Review文档
- 学习Review思路
- 提取学习要点

#### 8. 等待通知（wait）
```bash
bash scripts/xiaomi_dev_v3.sh <功能名> wait
```
- 等待米粒儿通知
- 检查通知文件
- 开始工作

#### 9. 系统状态检查（check）
```bash
bash scripts/xiaomi_dev_v3.sh <功能名> check
```
- Git状态检查
- 网络连接检查
- 依赖检查

#### 10. 帮助信息（help）
```bash
bash scripts/xiaomi_dev_v3.sh help
```
- 显示所有命令
- 使用说明

---

## 📊 功能对比

| 功能 | 米粒儿 | 小米辣 |
|------|--------|--------|
| **产品构思** | ✅ concept | - |
| **需求文档** | ✅ prd | - |
| **并行分析** | ✅ analyze | ✅ analyze |
| **开发实现** | - | ✅ dev |
| **Review评价** | ✅ review | - |
| **Review思考** | - | ✅ think |
| **5层验收** | ✅ accept | - |
| **开发自检** | - | ✅ check |
| **Git管理** | - | ✅ git |
| **ClawHub发布** | - | ✅ publish |
| **通知机制** | ✅ notify | ✅ wait |
| **学习Review** | ✅ view-review | ✅ learn |

---

## 🎯 使用流程

### 标准协作流程（9步）

```
1. 米粒儿：产品构思
   bash scripts/mili_product_v3.sh feature concept

2. 米粒儿：通知小米辣
   bash scripts/mili_product_v3.sh feature notify

3. 双方：并行分析
   # 米粒儿
   bash scripts/mili_product_v3.sh feature analyze
   # 小米辣
   bash scripts/xiaomi_dev_v3.sh feature analyze

4. 小米辣：开发前自检
   bash scripts/xiaomi_dev_v3.sh feature check

5. 小米辣：开发实现
   bash scripts/xiaomi_dev_v3.sh feature dev

6. 米粒儿：Review评价
   bash scripts/mili_product_v3.sh feature review

7. 小米辣：Review后思考
   bash scripts/xiaomi_dev_v3.sh feature think

8. 米粒儿：5层验收
   bash scripts/mili_product_v3.sh feature accept

9. 小米辣：ClawHub发布
   bash scripts/xiaomi_dev_v3.sh feature publish
```

---

## 🔧 核心特性

### 社区启发增强（v3.1新增）

#### 1. 反对意见机制（米粒儿）
```bash
# Review时必须提出反对意见
- 为什么不应该做？
- 有什么潜在风险？
- 有没有更好的替代方案？
```

#### 2. 质疑清单（小米辣）
```bash
# Review后必须质疑
- Review思路是否合理？
- 是否有遗漏的点？
- 是否有更好的实现方式？
```

#### 3. 系统状态检查（双方）
```bash
# 执行前检查系统状态
- Git状态检查
- 网络连接检查
- 依赖检查
```

---

## 📂 生成的文件

### 米粒儿生成的文件

```
docs/products/
├── 2026-03-12_feature_concept.md    # 产品构思
└── 2026-03-12_feature_prd.md        # PRD文档

docs/reviews/
└── 2026-03-12_feature_review.md     # Review文档

/tmp/
├── notify_mili.txt                   # 通知小米辣
├── review_approved.txt               # Review批准
└── release_approved.txt              # 发布批准
```

### 小米辣生成的文件

```
skills/
└── feature/                          # 技能目录
    ├── SKILL.md
    ├── scripts/
    └── docs/

Git仓库/
├── feature/feature-name              # Git分支
└── commits                           # Git提交

ClawHub/
└── package-id                        # ClawHub包
```

---

## 🎯 核心优势

### 1. 专业分工
- 米粒儿：产品视角 + 质量保证
- 小米辣：技术视角 + 实现能力

### 2. 双向思考
- 开发前：自检（技术可行性）
- Review后：质疑（反向思考）

### 3. 质量保证
- 12维度Review
- 5层验收
- 开发前自检

### 4. 社区启发
- 反对意见机制
- 质疑清单
- 系统状态检查

---

## 💡 使用建议

### 初次使用

```bash
# 1. 检查系统状态
bash scripts/mili_product_v3.sh demo-skill check

# 2. 创建产品构思
bash scripts/mili_product_v3.sh demo-skill concept

# 3. 查看帮助
bash scripts/mili_product_v3.sh help
```

### 日常使用

```bash
# 使用编排器（推荐）
bash scripts/dual_mili_orchestrator.sh feature start
bash scripts/dual_mili_orchestrator.sh feature dev
bash scripts/dual_mili_orchestrator.sh feature review

# 或直接使用脚本
bash scripts/mili_product_v3.sh feature concept
bash scripts/xiaomi_dev_v3.sh feature dev
```

---

## 📊 统计数据

### 代码统计
- **mili_product_v3.sh**：10.6KB，350行
- **xiaomi_dev_v3.sh**：11KB，380行
- **总计**：21.6KB，730行

### 功能统计
- **米粒儿**：10个功能
- **小米辣**：10个功能
- **共享功能**：3个（并行分析、系统检查、通知机制）

---

## 🎊 总结

**双米粒协作系统**提供了完整的产品开发流程：

- ✅ **产品构思** → 需求文档 → 并行分析
- ✅ **开发自检** → 开发实现 → Review评价
- ✅ **Review思考** → 5层验收 → ClawHub发布

**核心特点**：
- 专业分工（产品+技术）
- 双向思考（自检+质疑）
- 质量保证（Review+验收）
- 社区启发（反对意见+质疑清单）

---

*发布时间：2026-03-12*
*版本：v3.1 - 社区启发增强版*
*作者：米粒儿（官家的智能助理）*
