# ClawHub技能发布标准流程

> 确保每次发布都经过检查、对比、整合，避免重复和遗漏

---

## 📋 标准流程

### 步骤1：检查技能是否存在
```bash
clawhub inspect <slug>
```

### 步骤2：根据存在性和所有权处理

#### 情况A：不存在
```bash
# 直接发布
clawhub publish /path/to/skill --version 1.0.0
```

#### 情况B：存在但所有者不是自己
```bash
# 选项1：使用不同slug
miliger-<功能名>

# 选项2：放弃发布（避免重复）
```

#### 情况C：存在且所有者是自己
```bash
# 1. 下载最新版本
mkdir -p /tmp/clawhub-compare
cd /tmp/clawhub-compare
clawhub install <slug>

# 2. 对比差异
diff -r ~/.openclaw/workspace/skills/<slug>/ \
        /tmp/clawhub-compare/<slug>/

# 3. 合并重要变更
# - 检查远程新增功能
# - 整合到本地版本
# - 保留本地优化

# 4. 更新版本号
# 根据版本管理规则

# 5. 发布
clawhub publish /path/to/skill --version x.x.x
```

---

## 🏷️ 命名规范

### 官方技能
```
格式：<功能名>
示例：qmd, playwright-scraper, context-manager
```

### 个人定制技能
```
格式：miliger-<功能名>
示例：miliger-qmd-manager, miliger-playwright-scraper
```

### 命名规则
- ✅ 使用小写字母
- ✅ 使用连字符分隔
- ✅ 简洁有意义
- ❌ 避免特殊字符
- ❌ 避免过长名称

---

## 📊 版本管理规则

### 版本号格式
```
主版本.次版本.修订号
x.y.z
```

### 更新规则

#### 首次发布
```
1.0.0
```

#### 功能更新（新功能、重构）
```
x.y.0 → x.(y+1).0

示例：
1.0.0 → 1.1.0（新增功能）
1.1.0 → 1.2.0（重构架构）
```

#### Bug修复（小改进）
```
x.y.z → x.y.(z+1)

示例：
1.1.0 → 1.1.1（修复bug）
1.1.1 → 1.1.2（优化文档）
```

#### 重大变更（不兼容）
```
x.y.z → (x+1).0.0

示例：
1.5.2 → 2.0.0（架构重构）
```

---

## 🔧 实用命令

### 查看技能信息
```bash
# 查看远程技能
clawhub inspect <slug>

# 查看所有者
clawhub inspect <slug> | grep Owner

# 查看版本
clawhub inspect <slug> | grep Latest
```

### 对比工具
```bash
# 快速对比
diff -u local/SKILL.md remote/SKILL.md

# 详细对比
diff -r local/ remote/

# 仅对比核心文件
diff local/{SKILL.md,package.json,README.md} \
     remote/{SKILL.md,package.json,README.md}
```

### 发布命令
```bash
# 首次发布
clawhub publish /path/to/skill --version 1.0.0

# 功能更新
clawhub publish /path/to/skill --version 1.1.0

# Bug修复
clawhub publish /path/to/skill --version 1.1.1
```

---

## ✅ 发布检查清单

发布前检查：
- [ ] 检查技能是否已存在
- [ ] 确认所有权
- [ ] 下载远程版本对比
- [ ] 合并重要变更
- [ ] 更新版本号（遵循规则）
- [ ] 更新文档（README、CHANGELOG）
- [ ] 测试安装脚本
- [ ] 确认package.json完整

发布后验证：
- [ ] clawhub inspect确认版本
- [ ] clawhub install测试安装
- [ ] 检查ClawHub页面显示

---

## 📝 发布记录模板

```markdown
## vX.X.X (YYYY-MM-DD)

### 新增功能
- 功能1
- 功能2

### 改进
- 优化1
- 优化2

### 修复
- 修复bug1
- 修复bug2

### 致谢
- 整合自：<其他技能名>
```

---

## ⚠️ 常见问题

### Q1：技能已存在但不是我的，怎么办？
**A**：使用不同slug（如miliger-xxx）或放弃发布，避免重复。

### Q2：如何判断是否需要更新主版本？
**A**：不兼容的API修改、架构重构、重大功能变更时更新主版本。

### Q3：对比时发现远程版本更新，如何处理？
**A**：
1. 分析远程更新内容
2. 整合重要功能到本地
3. 保留本地优化
4. 更新版本号后发布

### Q4：发布失败怎么办？
**A**：
1. 检查package.json格式
2. 确认版本号有效（semver）
3. 验证SKILL.md存在
4. 检查网络连接

---

## 📚 相关资源

- **ClawHub**: https://clawhub.com
- **ClawHub CLI**: https://github.com/openclaw/clawhub-cli
- **语义化版本**: https://semver.org/lang/zh-CN/

---

**版本**: 1.0.0
**作者**: 小米辣
**创建**: 2026-03-06
**更新**: 2026-03-06

**标准化的发布流程，确保技能质量，避免重复和遗漏** 🌟
