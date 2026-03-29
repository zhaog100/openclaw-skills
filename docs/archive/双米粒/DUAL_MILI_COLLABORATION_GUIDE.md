
---

## 📝 Review提交标准格式（2026-03-12 12:36）

### 方式1：GitHub Issue评论（推荐）⭐⭐⭐⭐⭐

**位置**：Issue #2评论区

**格式**：
```markdown
@小米粒 Review完成！

## ✅ Review结果：批准 / 需要修改 / 拒绝

### 功能完整性
- ✅ 命令1：[评价]
- ✅ 命令2：[评价]
- ✅ 命令3：[评价]
- ✅ 命令4：[评价]

### 代码质量
- ✅ Bash代码规范：[评价]
- ✅ 错误处理：[评价]
- ✅ 注释完整度：[评价]

### 文档质量
- ✅ SKILL.md：[评价]
- ✅ README.md：[评价]
- ✅ package.json：[评价]

### 测试质量
- ✅ 测试覆盖率：[评价]
- ✅ 测试用例：[评价]
- ✅ 边界场景：[评价]

### 用户体验
- ✅ 命令易用性：[评价]
- ✅ 输出清晰度：[评价]
- ✅ 错误提示：[评价]

## 📊 12维度Review评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 功能完整性 | 5/5 | [说明] |
| 代码质量 | 5/5 | [说明] |
| 文档质量 | 5/5 | [说明] |
| 测试质量 | 5/5 | [说明] |
| 用户体验 | 5/5 | [说明] |

**总分**：25/25 ⭐⭐⭐⭐⭐

## ⚠️ 必须修改项

1. [修改项1]
2. [修改项2]

## 💡 建议改进项

1. [建议1]
2. [建议2]

## 🎯 下一步

✅ 批准发布到ClawHub

---
*米粒儿 - 2026-03-12*
```

---

### 方式2：Review文档

**位置**：`docs/reviews/demo-skill_review_YYYYMMDD.md`

**格式**：与Issue评论格式相同

---

### 方式3：通知文件

**文件**：`/tmp/review_approved.txt`

**内容**：
```
SKILL_NAME=demo-skill
REVIEW_RESULT=approved
REVIEWER=米粒儿
REVIEW_TIME=2026-03-12 12:30
ISSUE_NUMBER=2
NEXT_STEP=publish_to_clawhub

# Review评分
FUNCTIONALITY=5
CODE_QUALITY=5
DOCUMENTATION=5
TESTING=5
USER_EXPERIENCE=5
TOTAL_SCORE=25/25

# 必须修改项
MODIFICATION_1=[修改项1]
MODIFICATION_2=[修改项2]
```

---

### 方式4：Git提交

**提交信息**：
```
review(demo-skill): 米粒儿Review完成 - 批准发布（25/25分）
```

**包含文件**：
- `docs/reviews/demo-skill_review_20260312.md`
- `docs/reviews/demo-skill_acceptance_20260312.md`

---

## 🎯 推荐方式

**方式1：GitHub Issue评论**（最简单）⭐⭐⭐⭐⭐

**优势**：
- ✅ 小米粒自动检测到
- ✅ 历史记录完整
- ✅ 无需额外文件

**用法**：
1. 米粒儿在Issue #2中评论Review结果
2. 小米粒自动检测到新评论
3. 小米粒根据Review结果执行下一步

---

## 📋 小米粒检测机制

**自动检测**：
- ✅ 每5分钟检查GitHub Issues新评论
- ✅ 检测签名：`*米粒儿 -`
- ✅ 关键词：`Review完成`、`批准`、`需要修改`、`拒绝`

**手动检查**：
```bash
bash scripts/check_mili_messages.sh
```

---

## 🔄 完整协作流程

1. **小米粒开发完成** → Issue评论"开发完成，请求Review"
2. **米粒儿Review** → Issue评论"Review完成，批准/需要修改"
3. **小米粒检测** → 自动检测到Review结果
4. **小米粒执行** → 根据结果发布到ClawHub或修改

---

*更新时间：2026-03-12 12:36*

