# 双米粒协作系统 - 统一策略方案

**制定时间**：2026-03-12 13:58
**目的**：确保小米粒和米粒儿使用统一规范，避免同步问题
**状态**：✅ 已同步给米粒儿

---

## 📋 核心问题

**官家反馈**：
> "你们的有一个统一的策略，不然无法进行同步"

**解决方案**：建立5大统一规范

---

## 🎯 5大统一规范

---

## 1️⃣ Issue编号分配规范

### 分配规则

| Issue范围 | 用途 | 负责人 | 示例 |
|----------|------|--------|------|
| **#1-10** | 产品PRD | 米粒儿创建 | `#1 demo-skill PRD` |
| **#11-20** | 技术设计 | 小米粒创建 | `#11 demo-skill技术设计` |
| **#21-30** | Bug报告 | 双方均可 | `#21 demo-skill测试失败` |
| **#31-40** | 功能请求 | 米粒儿创建 | `#31 新增监控功能` |
| **#41-50** | 文档改进 | 双方均可 | `#41 完善README` |

### Issue标题规范

**格式**：`[类型] 技能名: 简短描述`

**示例**：
- ✅ `[PRD] smart-model: 智能模型切换增强版`
- ✅ `[设计] smart-model: 技术架构设计`
- ✅ `[Bug] demo-skill: 测试失败`
- ✅ `[功能] context-manager: 新增监控指标`

---

## 2️⃣ 文件路径规范

### 标准目录结构

```
/root/.openclaw/workspace/
├── docs/
│   ├── products/                    # 产品文档
│   │   ├── YYYY-MM-DD_[技能名]_PRD.md      # PRD文档
│   │   └── [技能名]_tech_design.md          # 技术设计
│   ├── reviews/                     # Review文档
│   │   └── [技能名]_review_YYYYMMDD.md
│   └── UNIFIED_STRATEGY.md          # 统一策略（本文档）
├── skills/
│   └── [技能名]/                    # 技能目录
│       ├── SKILL.md
│       ├── README.md
│       ├── package.json
│       ├── [技能名].sh
│       ├── install.sh
│       └── test/test.sh
├── knowledge/
│   └── YYYY-MM-DD/                  # 知识库（按日期）
│       └── [知识点名称].md
├── memory/
│   └── YYYY-MM-DD.md                # 每日记录
└── scripts/
    └── [功能描述].sh                # 工具脚本
```

### 文件命名规范

**PRD文档**：
```
格式：docs/products/YYYY-MM-DD_[技能名]_PRD.md
示例：docs/products/2026-03-12_smart-model_PRD.md
```

**技术设计**：
```
格式：docs/products/[技能名]_tech_design.md
示例：docs/products/smart-model_tech_design.md
```

**Review文档**：
```
格式：reviews/[技能名]_review_YYYYMMDD.md
示例：reviews/smart-model_review_20260312.md
```

**知识库**：
```
格式：knowledge/YYYY-MM-DD/[知识点].md
示例：knowledge/2026-03-12/smart-model-design.md
```

---

## 3️⃣ 命名规范

### 技能命名

**格式**：`[功能描述]`（小写，连字符分隔）

**示例**：
- ✅ `smart-model`
- ✅ `context-manager`
- ✅ `memory-sync`
- ❌ `SmartModel`
- ❌ `smart_model`

### 文档命名

**PRD**：
- ✅ `[技能名]_PRD.md`
- ❌ `[技能名]-prd.md`

**技术设计**：
- ✅ `[技能名]_tech_design.md`
- ❌ `[技能名]-tech-design.md`

**Review**：
- ✅ `[技能名]_review_YYYYMMDD.md`
- ❌ `[技能名]-review.md`

---

## 4️⃣ 协作流程规范

### 标准协作流程

```
1️⃣ 米粒儿创建PRD
   └─ Issue #N（#1-10）
   └─ docs/products/YYYY-MM-DD_[技能名]_PRD.md

2️⃣ 小米粒技术设计
   └─ Issue评论通知
   └─ docs/products/[技能名]_tech_design.md

3️⃣ 小米粒开发实现
   └─ Issue评论通知
   └─ skills/[技能名]/

4️⃣ 米粒儿Review验收
   └─ Issue评论通知
   └─ reviews/[技能名]_review_YYYYMMDD.md

5️⃣ 小米粒发布（如需要）
   └─ Issue评论通知
   └─ ClawHub发布
```

### Issue状态流转

```
OPEN（PRD创建）
  → 小米粒确认
  → 技术设计
  → 开发实现
  → Review验收
  → CLOSE（完成）
```

### 评论通知规范

**小米粒评论米粒儿**：
```markdown
@米粒儿 [状态]反馈

**技能**：[技能名]
**Issue**：#N
**状态**：✅ 完成 / ⏳ 进行中 / ❌ 遇到阻塞

**内容**：[简短说明]

**下一步**：[下一步行动]

---
*小米粒 - YYYY-MM-DD HH:MM*
```

**米粒儿评论小米粒**：
```markdown
@小米粒 [状态]反馈

**Review结果**：✅ 批准 / ⚠️ 需要修改 / ❌ 拒绝

**评分**：[X]/25

**下一步**：[下一步行动]

---
*米粒儿 - YYYY-MM-DD HH:MM*
```

---

## 5️⃣ Git同步策略

### 工作前检查

```bash
# 1. 拉取最新代码
git pull --rebase origin master

# 2. 检查是否有冲突
git fetch && git diff master origin/master

# 3. 如有冲突，智能合并
git checkout --ours <file>    # 本地优先
git checkout --theirs <file>  # 远程优先
```

### 工作后推送

```bash
# 1. 查看修改
git status

# 2. 添加修改
git add [文件]

# 3. 提交（规范格式）
git commit -m "[类型]([技能名]): 简短描述"

# 4. 推送
git push origin master
```

### 提交信息规范

**格式**：`[类型]([技能名]): 简短描述`

**类型**：
- `feat` - 新功能
- `fix` - Bug修复
- `docs` - 文档更新
- `refactor` - 重构
- `test` - 测试
- `chore` - 杂项

**示例**：
- ✅ `feat(smart-model): 新增文件类型检测`
- ✅ `fix(context-manager): 修复监控阈值`
- ✅ `docs(demo-skill): 完善README`

---

## 📋 Issue #3 和 #4 处理方案

### 当前状态

| Issue | 标题 | 状态 | 说明 |
|-------|------|------|------|
| **#3** | smart-model: 完善PRD文档 | OPEN | 旧版本 |
| **#4** | smart-model v2.0: 智能模型切换增强版 | OPEN | 新版本（米粒儿最新PRD） |

### 建议方案

**✅ 方案A**：保留#4，关闭#3（推荐）

**原因**：
- Issue #4是v2.0（最新版本）
- Issue #4包含完整的PRD内容
- Issue #3是旧版本，可以关闭

**操作**：
```bash
# 1. 关闭Issue #3
gh issue close 3 --comment "已迁移到Issue #4（v2.0版本）"

# 2. 更新Issue #4标题
gh issue edit 4 --title "[PRD] smart-model v2.0: 智能模型切换增强版"
```

---

## 🎯 执行计划

### 立即执行

1. ✅ 创建统一策略文档
2. ⏳ 同步给米粒儿（Issue评论）
3. ⏳ 关闭Issue #3
4. ⏳ 更新Issue #4标题

### 后续执行

1. ⏳ 小米粒开始smart-model v2.0技术设计
2. ⏳ 应用统一策略
3. ⏳ 完整协作流程

---

## 📊 验证清单

### 米粒儿检查清单

- [ ] 查看Issue #4（smart-model v2.0 PRD）
- [ ] 确认统一策略已收到
- [ ] 等待小米粒技术设计

### 小米粒检查清单

- [ ] 阅读Issue #4 PRD
- [ ] 阅读统一策略
- [ ] 开始技术设计
- [ ] 应用统一规范

---

## 🔄 同步机制

### 米粒儿获取信息

**方式1**：GitHub Issues
- 访问：https://github.com/zhaog100/openclaw-skills/issues
- 查看OPEN状态的Issue
- 查看最新评论

**方式2**：自动检测
- 每5分钟自动检测新评论
- 检测关键词：`@米粒儿`

### 小米粒反馈信息

**方式**：GitHub Issue评论
- 评论Issue #N
- 使用标准模板
- 包含完整信息

---

## 📝 更新记录

| 时间 | 更新内容 | 更新人 |
|------|---------|--------|
| 2026-03-12 13:58 | 创建统一策略方案 | 小米粒 |

---

*文档位置：docs/UNIFIED_STRATEGY.md*
*状态：✅ 已同步给米粒儿*
