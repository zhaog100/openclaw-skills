# MEMORY.md - 长期记忆

_持续更新，记录重要信息_

---

## 👤 用户信息

- **称呼**: 待确认
- **时区**: America/Los_Angeles (PDT)
- **沟通渠道**: QQ机器人
- **工作内容**: 开源项目 bounty 扫描、安全漏洞挖掘
- **工作策略**: ⭐⭐⭐ **全自动执行模式（智能过滤）** - 只完成评分 > 50 的高价值任务，自动按顺序全部完成，无需询问用户确认

---

## 🎯 当前项目

### 1. Bounty 扫描系统
**目的**: 自动扫描 GitHub issues，寻找有价值的 bounty 机会（特别是安全相关）

**关键文件**:
- `data/bounty-master-list.md` - 56个任务总清单 ⭐
- `data/bounty-pr-tracker.json` - PR状态跟踪系统 ⭐
- `data/bounty-known-issues.txt` - 已处理issues黑名单
- `data/bounty-scan-results.md` - 扫描结果汇总

**知识库**:
- `knowledge/bounty/` - Bounty知识库（模板+策略）
- `knowledge/github-bounty/` - 实现文档+经验教训
- `skills/github-bounty-hunter/` - 自动化扫描技能

**工作流**:
1. 扫描 GitHub issues（标签：bounty, security, bug-bounty等）
2. 过滤已处理 issues
3. 评估价值并分类
4. 提交 PR/Issue

**已完成**:
- ✅ PR #198: The-Pantseller/StarEscrow - 添加 SECURITY.md

---

## 🧠 重要知识

### Bounty 类型分类
1. **🔒 安全漏洞赏金** - 负责任披露、SECURITY.md
2. **💡 功能开发** - 新功能实现
3. **🐛 Bug 修复** - 问题修复
4. **📚 文档改进** - 文档完善

### 高价值仓库特征
- 有 `bug-bounty`, `security`, `help wanted` 标签
- 活跃维护（近期提交）
- 明确的奖励机制

### 系统优化知识
- **macOS 性能调优** - `knowledge/system-optimization/macos-performance-tuning.md`
  - 小部件管理（防止自动重启）
  - 媒体分析服务（临时停止）
  - 缓存清理（安全方法）
  - 进程管理（识别和关闭）
  - 系统监控（实时命令）

### 敏感信息处理
- **脱敏规则** - `AGENTS.md`
  - 密码只显示最后4位：`****bwyn`
  - 邮箱掩码处理：`z***@gmail.com`
  - Token 掩码：`ghp_***...P0B`
- **安全存储** - `~/.openclaw/workspace/.env`（已在 .gitignore）

### API 配置
- **阿里云百炼**
  - OpenAI 兼容: `https://coding.dashscope.aliyuncs.com/v1`
  - Anthropic 兼容: `https://coding.dashscope.aliyuncs.com/apps/anthropic`
  - 状态: ⚠️ **配额已用完**（HTTP 429）
  - 错误: "month allocated quota exceeded"
  - 解决: 充值或等待配额重置
  - 配置文件: `~/.openclaw/workspace/.env`

---

## 📌 待办事项

- [ ] 获取有效的百炼 API Key
- [ ] 测试百炼 API 连接
- [ ] 确认用户称呼和偏好
- [ ] 完善身份设定（IDENTITY.md）
- [ ] 自动化 bounty 扫描流程
- [ ] 建立质量评估标准

---

## 🔍 经验教训

_每次工作后更新_

1. **避免重复工作** - 维护黑名单 (bounty-known-issues.txt)
2. **质量优先** - 高质量 PR 比数量更重要
3. **安全第一** - 只做负责任披露，不利用漏洞
4. **项目选择策略** - 中小型活跃项目 > 大型项目（竞争少、易合并）
5. **模板复用** - SECURITY.md 等标准化文档可复用，提升 80% 效率
6. **持续跟进** - PR 提交后需定期检查状态，及时响应反馈

### 2026-03-29 学习要点

#### Bounty 扫描优化
- **过滤关键词**: `bounty`, `security`, `bug-bounty`, `responsible disclosure`
- **优先级排序**: 安全类（⭐⭐⭐⭐⭐）> 功能类 > Bug 类 > 文档类
- **评分算法**: 活跃度(30%) + Issue价值(40%) + 工作量(20%) + 学习价值(10%)

#### GitHub 工作流
- PR 状态需持续跟进（未合并前都算进行中）
- 黑名单维护至关重要（避免重复扫描）
- 自动化工具可大幅提升效率（目标：2小时 → 30分钟）

### 2026-03-30 学习要点

#### 敏感信息处理
- **问题**: 在消息中显示了完整的应用密码
- **解决**: 建立 AGENTS.md 安全规则，自动脱敏
- **规则**: 密码只显示最后4位，邮箱掩码处理
- **承诺**: 未来所有敏感信息自动脱敏，不再完整显示

#### macOS 系统优化
- **小部件管理**: macOS 会自动重启小部件，需通过通知中心配置禁用
- **媒体分析**: mediaanalysisd 消耗大量 CPU 和内存，可临时停止
- **缓存清理**: 定期清理 ~/Library/Caches 可释放磁盘空间
- **优化效果**: 负载降低 85%，可用内存增加 337%

#### 自动执行模式建立
- **策略升级**: ⭐⭐⭐ 全自动执行模式（智能过滤）
- **过滤规则**: 只完成评分 > 50 的高价值任务
- **执行流程**: 认领 → 开发 → 测试 → 提交 → 更新队列 → 下一个
- **无需确认**: 用户授权后自动完成所有剩余任务
- **质量保证**: 保持高质量标准，不因自动化而降低要求

#### Bounty 任务筛选优化
- **高价值定义**: 评分 > 50 的任务（安全类、功能类、文档类）
- **跳过低价值**: ≤50 分的简单任务，避免浪费时间
- **网络问题处理**: 记录问题仓库，自动跳过
- **统计**: 51 个高价值任务，已完成 6 个，剩余 45 个

#### 工作效率提升
- **系统优化**: 先优化系统性能，再开始高强度工作
- **知识沉淀**: 及时创建知识文档（macOS 优化、安全处理等）
- **自动化工具**: 充分利用自动执行模式，减少人工干预
- **进度跟踪**: 实时更新队列状态和工作日志

---

## 📈 工作统计

### 累计数据（截至2026-03-30）
- **任务总数**: 56个（来自bounty-master-list.md）
- **已提交PR**: 20个（等待审核）
- **预估总金额**: $5,280

### PR状态分布
- 🟢 等待审核: 29个
- ❌ 已关闭: 26个
- 🚫 已屏蔽: 1个

### 本周工作（2026-03-29 至 2026-03-30）

**2026-03-29**:
- 扫描 issues: 56+
- 提交新PR: 多个（需从bounty-pr-tracker.json确认）
- 系统配置: Python扫描器、Bash扫描器

**2026-03-30**（完整统计）:
- **系统优化**: 负载从 4.44 → 0.67 (-85%)
- **安全配置**: Gmail 集成、敏感信息脱敏规则
- **进程管理**: 清理小部件、停止媒体分析、缓存清理
- **结构化整理**: 记忆系统更新、知识库去重
- **Bounty 任务**: 6 个完成（$450+）
  - #5: n8n workflow ($200) ⭐
  - #4: PR Review Agent ($150) ⭐
  - #3: Pre-tool Hook ($100) ⭐
  - #24530: Security Fix (HIGH)
  - #297: Gitcoin Grants (Case Study)
  - #1324: Daily Briefing
- **知识产出**: 3 个文档（macOS 优化、敏感信息、n8n workflow）
- **Git 提交**: 14 个 | **代码**: +4,500 行
- **工作时长**: 16 小时（07:43 - 23:35）
- Bounty 任务: 1 个完成（$200）
- Git 提交: 6 个
- 知识产出: 2 个新文档
- 功耗监控: 第 2 天（200+ 样本）

---

## 🛠️ 技能系统

**已开发技能**: 60个（见skills/目录）

**核心技能**:
- `github-bounty-hunter` - 自动化bounty扫描
- `agent-collab-platform` - 多智能体协作
- `autoflow` - 工作流自动化
- `daily-review-assistant` - 每日回顾
- `context-manager-v2` - 上下文管理

**完整列表**: 见 [skills/README.md](skills/README.md)

---

_最后更新: 2026-03-30_
