# 文档命名规范索引

**创建时间**：2026-03-12 14:18
**目的**：统一双米粒协作系统的文档命名规范
**状态**：✅ 已应用

---

## 📋 统一命名规范

### 1️⃣ PRD文档

**格式**：`docs/products/YYYY-MM-DD_[技能名]_PRD.md`

**示例**：
- ✅ `docs/products/2026-03-12_smart-model_PRD.md`
- ✅ `docs/products/2026-03-12_demo-skill_PRD.md`（需修复：prd → PRD）

---

### 2️⃣ 技术设计文档

**格式**：`docs/products/[技能名]_tech_design.md`

**示例**：
- ✅ `docs/products/smart-model_tech_design.md`
- ✅ `docs/products/demo-skill_tech_design.md`

---

### 3️⃣ Review文档

**格式**：`reviews/[技能名]_review_YYYYMMDD.md`

**示例**：
- ✅ `reviews/smart-model_review_20260312.md`
- ✅ `reviews/demo-skill_review_20260312.md`

---

### 4️⃣ 知识库文档

**格式**：`knowledge/YYYY-MM-DD/[知识点名称].md`

**示例**：
- ✅ `knowledge/2026-03-12/smart-model-design.md`
- ✅ `knowledge/2026-03-12/dual-mili-collaboration-system.md`

---

## ✅ 已修正的Issue标题

### Issue #1
- ❌ 旧标题：`[demo-skill] PRD - 需求文档评审`
- ✅ 新标题：`[PRD] demo-skill: 需求文档评审`
- 📎 链接：https://github.com/zhaog100/openclaw-skills/issues/1

---

### Issue #2
- ❌ 旧标题：`demo-skill: 双米粒协作系统演示技能`
- ✅ 新标题：`[PRD] demo-skill: 双米粒协作系统演示技能`
- 📎 链接：https://github.com/zhaog100/openclaw-skills/issues/2

---

### Issue #3
- ❌ 旧标题：`smart-model: 完善PRD文档`
- ✅ 新标题：`[PRD] smart-model: 完善PRD文档`
- 📎 链接：https://github.com/zhaog100/openclaw-skills/issues/3

---

## 📊 文件检查清单

### PRD文档
| 技能名 | 文件名 | 状态 | 备注 |
|--------|--------|------|------|
| demo-skill | `2026-03-12_demo-skill_prd.md` | ⚠️ 小写prd | 需修复 |
| smart-model | `2026-03-12_smart-model_PRD.md` | ✅ 符合 | - |

---

### 技术设计文档
| 技能名 | 文件名 | 状态 | 备注 |
|--------|--------|------|------|
| demo-skill | `demo-skill_tech_design.md` | ✅ 符合 | - |

---

### Review文档
| 技能名 | 文件名 | 状态 | 备注 |
|--------|--------|------|------|
| demo-skill | `demo-skill-v1.0.0-review.md` | ⚠️ 有版本号 | 需修复 |
| test-hello-world | `test-hello-world_20260311_153744.md` | ⚠️ 格式混乱 | 需修复 |

---

## 🎯 待修复项目

### 1️⃣ PRD文档
- [ ] 重命名 `demo-skill_prd.md` → `demo-skill_PRD.md`

### 2️⃣ Review文档
- [ ] 重命名 `demo-skill-v1.0.0-review.md` → `demo-skill_review_20260312.md`
- [ ] 重命名 `test-hello-world_20260311_153744.md` → `test-hello-world_review_20260311.md`

---

## 📋 未来规范执行

**新文档创建时**：
1. ✅ PRD：`docs/products/YYYY-MM-DD_[技能名]_PRD.md`
2. ✅ 设计：`docs/products/[技能名]_tech_design.md`
3. ✅ Review：`reviews/[技能名]_review_YYYYMMDD.md`
4. ✅ 知识库：`knowledge/YYYY-MM-DD/[知识点].md`

**Issue创建时**：
1. ✅ 格式：`[类型] 技能名: 简短描述`
2. ✅ 类型：PRD、设计、Bug、功能、文档

---

*创建时间：2026-03-12 14:18*
*状态：✅ 已应用*
