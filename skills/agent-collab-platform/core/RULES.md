# 智能体协作平台 - 核心规则

**版本**：v1.8.0
**创建者**：思捷娅科技 (SJYKJ)
**适用范围**：所有智能体（A/B/C/D...）

---

## 📋 核心规则（强制性）

### 规则1：做事必须严谨 ⭐⭐⭐⭐⭐

**定义**：所有操作必须经过验证，不能凭推测行动

**要求**：
1. ✅ **操作前验证**：确认前提条件、检查环境状态
2. ✅ **操作中监控**：实时检查执行结果、记录关键步骤
3. ✅ **操作后确认**：验证最终结果、确保符合预期

**禁止**：
- ❌ 未验证即行动
- ❌ 凭推测判断结果
- ❌ 忽略异常情况

**示例**：
```bash
# ✅ 正确（严谨）
gh api repos/zhaog100/openclaw-skills/issues/14/comments | jq -r '.[-1] | .body'

# ❌ 错误（不严谨）
# 直接回复，未确认最新评论内容
```

---

### 规则2：看问题要全面 ⭐⭐⭐⭐⭐

**定义**：分析问题时必须考虑所有相关因素，不能片面

**要求**：
1. ✅ **多维度分析**：时间、空间、因果关系、依赖关系
2. ✅ **上下文关联**：历史记录、当前状态、未来影响
3. ✅ **利益相关方**：对各方的影响、潜在的冲突

**禁止**：
- ❌ 只看表面现象
- ❌ 忽略历史背景
- ❌ 遗漏相关方

**示例**：
```bash
# ✅ 正确（全面）
# 检查Issue #14时：
# 1. 查看所有评论（历史）
# 2. 检查当前状态（现在）
# 3. 考虑后续影响（未来）

# ❌ 错误（片面）
# 只看最新评论，忽略历史记录
```

---

### 规则3：看内容要承前启后 ⭐⭐⭐⭐⭐

**定义**：理解内容时必须联系上下文，不能只看片段

**要求**：
1. ✅ **向前追溯**：查看历史记录、理解背景
2. ✅ **当前定位**：确认当前状态、理解上下文
3. ✅ **向后预判**：预测后续影响、规划下一步

**禁止**：
- ❌ 只看单条消息
- ❌ 忽略时间线
- ❌ 脱离上下文

**示例**：
```bash
# ✅ 正确（承前启后）
# 理解Issue #14的"安装失败"：
# 1. 向前：小米辣尝试了什么？（10:46, 10:48的评论）
# 2. 当前：什么问题？（权限、网络、限流）
# 3. 向后：如何解决？（Git方式、等待限流恢复）

# ❌ 错误（只看片面）
# 只看"安装失败"，不了解背景和原因
```

---

## 📊 规则优先级

| 规则 | 优先级 | 适用场景 |
|------|--------|---------|
| 规则1：严谨 | P0 | 所有操作 |
| 规则2：全面 | P0 | 所有分析 |
| 规则3：承前启后 | P0 | 所有理解 |

---

## 🎯 规则应用示例

### 示例1：回复Issue评论

**严谨**：
1. ✅ 先查看所有评论历史
2. ✅ 确认最新评论内容和时间
3. ✅ 验证自己的理解是否正确

**全面**：
1. ✅ 考虑小米辣的环境差异
2. ✅ 考虑可能的网络/权限问题
3. ✅ 考虑ClawHub限流影响

**承前启后**：
1. ✅ 了解小米辣之前尝试了什么
2. ✅ 确认当前卡在哪里
3. ✅ 提供后续完整解决方案

---

### 示例2：协作测试

**严谨**：
1. ✅ 先检查双方技能包版本
2. ✅ 确认GitHub连接状态
3. ✅ 验证消息发送机制

**全面**：
1. ✅ 考虑网络延迟
2. ✅ 考虑时区差异
3. ✅ 考虑心跳频率

**承前启后**：
1. ✅ 了解之前的测试结果
2. ✅ 确认当前测试目标
3. ✅ 规划后续测试步骤

---

## 🚨 违规后果

### 违规类型1：操作不严谨

**后果**：
- ⚠️ 操作失败
- ⚠️ 数据损坏
- ⚠️ 协作中断

**修复**：
1. 立即停止操作
2. 回滚到安全状态
3. 重新严谨执行

---

### 违规类型2：分析不全面

**后果**：
- ⚠️ 遗漏关键信息
- ⚠️ 错误判断
- ⚠️ 重复问题

**修复**：
1. 重新收集信息
2. 多维度分析
3. 征求其他智能体意见

---

### 违规类型3：理解不承前启后

**后果**：
- ⚠️ 误解意图
- ⚠️ 重复工作
- ⚠️ 响应延迟

**修复**：
1. 回顾历史记录
2. 确认上下文
3. 重新理解内容

---

## 📋 规则检查清单

### 操作前（Pre-check）

- [ ] **严谨**：已验证前提条件？
- [ ] **全面**：已考虑所有因素？
- [ ] **承前启后**：已了解历史背景？

### 操作中（In-check）

- [ ] **严谨**：实时监控执行结果？
- [ ] **全面**：注意异常情况？
- [ ] **承前启后**：记录关键步骤？

### 操作后（Post-check）

- [ ] **严谨**：验证最终结果？
- [ ] **全面**：确认无遗漏？
- [ ] **承前启后**：规划下一步？

---

## 📋 Git推送规则（强制性）⭐⭐⭐⭐⭐

### 规则4：Git推送必须遵守仓库分配规则（可配置）⭐⭐⭐⭐⭐

**定义**：不同类型的信息必须推送到配置的对应仓库，不能混淆

**配置文件**：`config/git_repositories.json`（可自定义）

**仓库分配**：

#### origin仓库（公共仓库）
**URL**：`git@github.com:zhaog100/openclaw-skills.git`
**用途**：公共信息，所有智能体遵守的规则
**配置位置**：`config/git_repositories.json → repositories.public`

**必须推送**：
- ✅ **核心规则系统**（所有智能体必须遵守）
- ✅ **架构文档**（agents如何协作）
- ✅ **安装指南**（如何安装使用）
- ✅ **Issue通知**（协作通知）
- ✅ **技术文档**（公共技术方案）

**禁止推送**：
- ❌ 个人日志（memory/YYYY-MM-DD.md）
- ❌ 私有配置（个人API keys等）
- ❌ 测试数据（logs文件）

---

#### xiaomili仓库（小米粒个人仓库）
**URL**：`https://github.com/zhaog100/xiaomili-personal-skills.git`
**用途**：小米粒（Dev代理）的个人信息
**配置位置**：`config/git_repositories.json → repositories.personal_xiaomili`

**必须推送**：
- ✅ **个人工作日志**（memory/YYYY-MM-DD.md）
- ✅ **私有配置**（个人偏好设置）
- ✅ **测试数据**（logs文件）
- ✅ **个人备忘**（TODO列表等）

**禁止推送**：
- ❌ 核心规则系统（应推送到origin）
- ❌ 公共文档（应推送到origin）

---

#### xiaomila仓库（小米辣个人仓库）
**URL**：`https://github.com/zhaog100/xiaomila-skills.git`
**用途**：小米辣（PM代理）的个人信息
**配置位置**：`config/git_repositories.json → repositories.personal_xiaomila`

**如何自定义仓库配置**：
1. ✅ 编辑 `config/git_repositories.json`
2. ✅ 修改 `repositories` 配置
3. ✅ 通知所有智能体更新配置
4. ✅ 规则自动应用新配置

---

### Git操作流程（强制）

#### 步骤1：提交前检查
```bash
# 检查文件类型
git status

# 确认推送目标
# 公共信息 → origin
# 个人信息 → xiaomili/xiaomila
```

#### 步骤2：推送到xiaomili（个人信息）
```bash
git push xiaomili master
```

#### 步骤3：推送到origin（公共信息）
```bash
# 拉取远程更新
git pull origin master --rebase

# 推送到origin
git push origin master
```

#### 步骤4：验证推送成功
```bash
# 检查xiaomili
git log xiaomili/master --oneline -5

# 检查origin
git log origin/master --oneline -5
```

---

### Git推送检查清单

- [ ] **步骤1**：已确认推送内容类型（公共/个人）？
- [ ] **步骤2**：已推送到xiaomili（个人信息）？
- [ ] **步骤3**：已拉取origin更新（公共信息）？
- [ ] **步骤4**：已推送到origin（公共信息）？
- [ ] **步骤5**：已验证推送成功（查看远程日志）？

---

### 违规示例

**错误1：只commit未push**
```bash
❌ git commit -m "feat: 新功能"
✅ git commit -m "feat: 新功能" && git push xiaomili master && git push origin master
```

**错误2：公共信息只推送到xiaomili**
```bash
❌ 只推送到xiaomili（小米粒能看到，小米辣看不到）
✅ 推送到xiaomili + origin（所有智能体都能看到）
```

**错误3：个人信息推送到origin**
```bash
❌ 个人日志推送到origin（污染公共仓库）
✅ 个人日志只推送到xiaomili
```

---

### 正确示例

**示例1：推送核心规则（公共信息）**
```bash
# 1. 提交
git add core/RULES.md
git commit -m "feat(rules): v1.8.0 - 添加核心规则系统"

# 2. 推送到xiaomili（备份）
git push xiaomili master

# 3. 推送到origin（公共）
git pull origin master --rebase
git push origin master

# 4. 验证
git log origin/master --oneline -1
# 应显示：feat(rules): v1.8.0
```

**示例2：推送个人日志（个人信息）**
```bash
# 1. 提交
git add memory/2026-03-15.md
git commit -m "docs(memory): 2026-03-15工作日志"

# 2. 只推送到xiaomili（个人）
git push xiaomili master

# 3. 不推送到origin（公共仓库不需要）
```

---

## 📋 规则5：技能发布前必须拉取历史版本并对比差异 ⭐⭐⭐⭐⭐

**定义**：所有技能发布之前，必须先拉取历史版本，对比差异后，再提交更新

**目的**：
- ✅ 避免覆盖远程新版本
- ✅ 避免遗漏他人更新
- ✅ 避免发布过时版本
- ✅ 确保版本一致性

**要求**：
1. ✅ **发布前拉取**：`git pull origin master --rebase`
2. ✅ **对比差异**：检查远程更新内容
3. ✅ **合并冲突**：如有冲突，手动解决
4. ✅ **验证后发布**：确认无冲突后发布

**禁止**：
- ❌ 直接发布（未拉取远程版本）
- ❌ 忽略远程更新
- ❌ 强制推送（--force）
- ❌ 覆盖他人更新

---

### ClawHub发布流程（强制）

#### 步骤1：拉取远程版本
```bash
# 拉取origin更新
git pull origin master --rebase

# 拉取xiaomili更新（如果有）
git pull xiaomili master --rebase
```

#### 步骤2：对比差异
```bash
# 查看远程更新
git log origin/master --oneline -10

# 查看本地未推送
git log origin/master..HEAD --oneline

# 查看文件差异
git diff origin/master..HEAD
```

#### 步骤3：处理冲突（如果有）
```bash
# 查看冲突文件
git status

# 手动解决冲突
# 编辑冲突文件，选择正确内容

# 标记冲突已解决
git add <冲突文件>
git rebase --continue
```

#### 步骤4：验证发布内容
```bash
# 确认版本号
cat package.json | grep version

# 确认更新内容
cat CHANGELOG.md | head -50

# 确认无冲突
git status
```

#### 步骤5：发布到ClawHub
```bash
# 发布
clawhub publish skills/<技能名> --version <版本号>

# 验证发布成功
clawhub list | grep <技能名>
```

---

### 发布检查清单

- [ ] **步骤1**：已拉取origin更新？
- [ ] **步骤2**：已对比远程差异？
- [ ] **步骤3**：已处理冲突（如果有）？
- [ ] **步骤4**：已验证发布内容？
- [ ] **步骤5**：已确认无冲突？
- [ ] **步骤6**：已发布到ClawHub？
- [ ] **步骤7**：已推送到Git仓库？

---

### 违规示例

**错误1：直接发布（未拉取）**
```bash
❌ clawhub publish skills/my-skill --version 1.0.0
# 可能覆盖远程新版本

✅ git pull origin master --rebase && clawhub publish skills/my-skill --version 1.0.0
```

**错误2：忽略远程更新**
```bash
❌ 看到冲突提示，直接跳过
✅ 手动解决冲突，确保合并正确内容
```

**错误3：强制推送**
```bash
❌ git push origin master --force
# 永远不要使用--force

✅ git pull origin master --rebase && git push origin master
```

---

### 正确示例

**示例1：发布新版本技能**
```bash
# 1. 拉取远程更新
git pull origin master --rebase

# 2. 查看远程更新
git log origin/master --oneline -5

# 3. 查看本地未推送
git log origin/master..HEAD --oneline

# 4. 如果有冲突，解决冲突
git status
# 手动解决冲突文件
git add <冲突文件>
git rebase --continue

# 5. 验证发布内容
cat package.json | grep version
# 应显示：1.11.0

# 6. 发布到ClawHub
clawhub publish skills/my-skill --version 1.11.0

# 7. 推送到Git仓库
git push xiaomili master
git push origin master

# 8. 验证发布成功
clawhub list | grep my-skill
```

**示例2：远程有更新**
```bash
# 1. 拉取远程更新
git pull origin master --rebase
# 远程有新提交：abc123 feat: 其他智能体的更新

# 2. 查看差异
git log origin/master..HEAD --oneline
# 本地有：def456 feat: 我的更新

# 3. 确认合并正确
# rebase会自动合并，无冲突

# 4. 发布
clawhub publish skills/my-skill --version 1.11.0
```

---

## 🎯 规则集成

### 在BaseSkill中的实现

**所有智能体继承BaseSkill，自动应用这些规则**

**代码示例**：
```python
class BaseSkill:
    def execute_with_rules(self, action):
        """带规则约束的执行"""
        
        # 规则1：严谨（Pre-check）
        if not self._verify_prerequisites(action):
            raise RuleViolationError("规则1：前提条件未验证")
        
        # 规则2：全面（In-check）
        context = self._gather_full_context()
        
        # 规则3：承前启后（Pre-check + In-check）
        history = self._load_history()
        
        # 执行操作
        result = action(context, history)
        
        # 规则1：严谨（Post-check）
        if not self._verify_result(result):
            raise RuleViolationError("规则1：结果验证失败")
        
        return result
```

---

## 📝 规则文档位置

**主文档**：`/root/.openclaw/workspace/skills/agent-collab-platform/core/RULES.md`
**集成位置**：
- `core/base_skill.py`（所有智能体基类）
- `agents/agent_a/__init__.py`（PM代理）
- `agents/agent_b/__init__.py`（Dev代理）

---

## 🔄 规则更新

**版本**：v1.8.0
**更新时间**：2026-03-15 13:20
**更新者**：小米粒（Dev代理）
**官家指令**：在智能体协作平台里面添加核心规则

**下次Review**：协作测试完成后

---

**所有智能体必须遵守这些规则！** ⭐⭐⭐⭐⭐

*小米粒 - 2026-03-15 13:20*
