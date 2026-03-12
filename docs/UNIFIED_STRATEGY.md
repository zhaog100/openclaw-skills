# 双米粒协作系统 - 统一策略规范

**制定时间**：2026-03-12 13:54  
**目的**：确保小米粒和米粒儿使用统一规范，避免同步问题

---

## 📋 核心问题

**官家反馈**：
> "你们的有一个统一的策略，不然无法进行同步"

**问题原因**：
- ❌ Issue编号混乱
- ❌ 文件路径不一致
- ❌ 命名规范不统一

---

## 🎯 统一策略（5大规范）

---

## 1️⃣ Issue编号分配规范

### 分配规则

| Issue范围 | 用途 | 负责人 |
|----------|------|--------|
| **#1-10** | 产品PRD | 米粒儿创建 |
| **#11-20** | 技术设计 | 小米粒创建 |
| **#21-30** | Bug报告 | 双方均可 |
| **#31-40** | 功能请求 | 米粒儿创建 |
| **#41-50** | 文档改进 | 双方均可 |

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
│   └── STATUS_FEEDBACK_MECHANISM.md # 反馈机制
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
docs/products/YYYY-MM-DD_[技能名]_PRD.md
示例：docs/products/2026-03-12_smart-model_PRD.md
```

**技术设计**：
```
docs/products/[技能名]_tech_design.md
示例：docs/products/smart-model_tech_design.md
```

**Review文档**：
```
reviews/[技能名]_review_YYYYMMDD.md
示例：reviews/smart-model_review_20260312.md
```

**知识库**：
```
knowledge/YYYY-MM-DD/[知识点].md
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

### Git提交规范

**格式**：`<type>(<scope>): <description>`

**Type类型**：
- `feat` - 新功能
- `fix` - Bug修复
- `docs` - 文档更新
- `refactor` - 代码重构
- `test` - 测试相关
- `chore` - 构建/工具

**示例**：
- ✅ `feat(smart-model): 添加智能切换功能`
- ✅ `fix(context-manager): 修复内存泄漏`
- ✅ `docs(demo-skill): 完善README文档`

---

## 4️⃣ Issue与文件映射规范

### 标准映射关系

| Issue类型 | PRD位置 | 技术设计位置 | 技能目录 |
|----------|---------|-------------|---------|
| **新技能** | `docs/products/YYYY-MM-DD_[技能名]_PRD.md` | `docs/products/[技能名]_tech_design.md` | `skills/[技能名]/` |

### Issue描述必须包含

```markdown
## 任务描述
[任务简述]

## PRD 文档
位置：docs/products/YYYY-MM-DD_[技能名]_PRD.md

## 核心功能
1. 功能1
2. 功能2

## 技术栈
- 语言：
- 依赖：

## 验收标准
1. 标准1
2. 标准2
```

---

## 5️⃣ 同步机制规范

### Git同步策略

**原则**：合并优先，避免覆盖

**标准流程**：
1. ✅ 工作前先pull
   ```bash
   git pull --rebase origin master
   ```

2. ✅ 检查冲突
   ```bash
   git fetch
   git diff master origin/master
   ```

3. ✅ 智能合并
   ```bash
   # 本地优先（脚本、配置）
   git checkout --ours <file>

   # 远程优先（文档、README）
   git checkout --theirs <file>
   ```

4. ✅ 及时推送
   ```bash
   git push origin master
   ```

---

### Issue同步策略

**自动检测**：每5分钟

**检测内容**：
1. ✅ 新Issue创建
2. ✅ 新评论
3. ✅ 状态变化

**检测脚本**：
```bash
*/5 * * * * cd /root/.openclaw/workspace && bash scripts/check_mili_messages.sh
```

---

### 文件同步策略

**不同步的文件**（.gitignore）：
```
logs/
*.log
tmp/
*.tmp
memory/*.md
```

**必须同步的文件**：
```
docs/
skills/
scripts/
LICENSE
README.md
MEMORY.md
```

---

## 📊 Issue分配表（当前）

| Issue | 类型 | 技能名 | 状态 | PRD位置 |
|-------|------|--------|------|---------|
| **#1** | PRD | demo-skill | ⏳ OPEN | `docs/products/2026-03-12_demo-skill_prd.md` |
| **#2** | 开发 | demo-skill | ✅ CLOSED | 已完成 |
| **#3** | PRD | smart-model | ⏳ OPEN | `docs/products/2026-03-12_smart-model_PRD.md` |
| **#4** | PRD | smart-model v2.0 | ⏳ OPEN | **待确认** ⚠️ |

---

## ⚠️ 发现的问题

### Issue #3 vs #4 冲突

**问题**：
- Issue #3: smart-model PRD
- Issue #4: smart-model v2.0 PRD

**可能原因**：
1. ❓ 版本升级（v1 → v2）
2. ❓ 重复创建
3. ❓ 不同需求

**建议处理**：
1. ✅ **保留#4**（最新版本）
2. ✅ **关闭#3**（旧版本）
3. ✅ **在#4中说明**："替代#3"

---

## 🎯 统一策略执行

### 米粒儿必须遵守

1. ✅ **创建Issue前**：
   - 检查是否已存在相同Issue
   - 使用标准标题格式
   - 包含PRD文档位置

2. ✅ **PRD文档位置**：
   ```
   docs/products/YYYY-MM-DD_[技能名]_PRD.md
   ```

3. ✅ **Issue描述格式**：
   - 包含任务描述
   - 包含PRD位置
   - 包含验收标准

---

### 小米粒必须遵守

1. ✅ **开发前检查**：
   - 确认Issue编号
   - 确认PRD位置
   - 确认技术设计位置

2. ✅ **文件创建规范**：
   - 遵循标准路径
   - 遵循命名规范
   - Git提交使用规范格式

3. ✅ **状态反馈**：
   - GitHub Issue评论
   - 使用标准模板
   - 及时反馈（<5分钟）

---

## 📝 检查清单

### 米粒儿创建PRD时

- [ ] Issue编号是否正确？
- [ ] Issue标题是否规范？
- [ ] PRD文件路径是否正确？
- [ ] PRD命名是否规范？
- [ ] Issue描述是否完整？

---

### 小米粒开始开发时

- [ ] Issue是否存在？
- [ ] PRD文档是否存在？
- [ ] 文件路径是否标准？
- [ ] 命名是否规范？
- [ ] Git提交格式是否正确？

---

## 🔧 解决Issue #3/#4冲突

### 建议方案

**官家，Issue #3和#4都是smart-model PRD，需要统一：**

**方案A：保留#4，关闭#3**（推荐）
- Issue #4是v2.0版本（最新）
- Issue #3是旧版本
- 在#4中说明："替代#3"

**方案B：保留#3，关闭#4**
- Issue #3是原始PRD
- Issue #4是重复

**方案C：合并#3和#4**
- 保留一个Issue
- 合并两个PRD的内容

---

## 📂 统一后的文件结构

```
docs/products/
├── 2026-03-12_smart-model_PRD.md    # PRD（v2.0，统一版本）
├── smart-model_tech_design.md        # 技术设计
└── ...

skills/
├── smart-model/                      # 技能目录
│   ├── SKILL.md
│   ├── README.md
│   ├── package.json
│   ├── smart-model.sh
│   ├── install.sh
│   └── test/test.sh
└── ...
```

---

*制定时间：2026-03-12 13:54*
*状态：✅ 完成*
*下次更新：Issue #3/#4冲突解决后*
