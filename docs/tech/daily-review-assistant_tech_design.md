# 定时回顾更新助手 - 技术设计文档

**版本**：v1.0
**创建时间**：2026-03-16 10:10
**创建者**：小米辣（PM+Dev代理）🌶️
**Issue**：#16

---

## 1. 架构设计

### 1.1 整体架构

```
daily-review-assistant/
├── skill.sh                    # CLI入口（Bash）
├── lib/
│   ├── scheduler.py           # 定时任务调度器
│   ├── reviewer.py            # 回顾分析器
│   ├── memory_updater.py      # 记忆更新器
│   ├── knowledge_updater.py   # 知识库更新器
│   └── git_manager.py         # Git管理器
├── config/
│   └── config.yaml            # 配置文件
├── logs/
│   ├── review-YYYY-MM-DD.log  # 回顾日志
│   └── error-YYYY-MM-DD.log   # 错误日志
├── templates/
│   ├── daily-summary.md       # 日报模板
│   └── commit-message.txt     # 提交信息模板
├── tests/
│   └── test_all.py            # 测试套件
├── install.sh                 # 安装脚本
├── SKILL.md                   # 技能说明
└── README.md                  # 使用文档
```

### 1.2 技术栈

| 组件 | 技术选型 | 理由 |
|------|---------|------|
| **定时任务** | Crontab | 系统自带，稳定可靠，易于监控 |
| **脚本入口** | Bash | 轻量级，易于调用系统命令 |
| **核心逻辑** | Python 3.10+ | 字符串处理、文件操作强大 |
| **Git操作** | Git CLI + GitPython | 双模式，稳定可靠 |
| **配置管理** | PyYAML | 灵活配置，易于维护 |
| **日志记录** | Python logging | 分级日志，便于调试 |
| **锁机制** | fcntl | 避免重复执行，线程安全 |

### 1.3 系统架构图

```
┌─────────────────────────────────────────────────────┐
│                   Crontab定时触发                    │
│              (12:00 / 23:50)                        │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   skill.sh (入口)     │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  检查锁文件(避免重复)  │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Scheduler.py        │
         │  (定时任务调度器)      │
         └───────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│Reviewer  │  │ Memory   │  │ Knowledge│
│ (回顾器) │  │ Updater  │  │ Updater  │
└─────┬────┘  └─────┬────┘  └─────┬────┘
      │             │             │
      └─────────────┼─────────────┘
                    │
                    ▼
         ┌───────────────────────┐
         │    Git Manager        │
         │   (Git提交推送)        │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   记录日志 + 释放锁    │
         └───────────────────────┘
```

---

## 2. 核心模块设计

### 2.1 Scheduler（定时任务调度器）

**职责**：调度回顾任务，区分中午/晚间模式

**核心功能**：
- ✅ 识别当前时间模式（中午/晚间）
- ✅ 计算回顾时间范围
- ✅ 协调各模块执行顺序

**Python实现**：
```python
class Scheduler:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.reviewer = Reviewer()
        self.memory_updater = MemoryUpdater()
        self.knowledge_updater = KnowledgeUpdater()
        self.git_manager = GitManager()

    def run(self, mode='auto'):
        """
        主调度器
        mode: 'auto'（自动识别）, 'morning', 'evening'
        """
        # 1. 识别模式
        if mode == 'auto':
            mode = self._detect_mode()

        # 2. 计算时间范围
        time_range = self._get_time_range(mode)

        # 3. 执行回顾
        review_data = self.reviewer.review(time_range)

        # 4. 更新记忆
        self.memory_updater.update(review_data, mode)

        # 5. 更新知识库（仅晚间）
        if mode == 'evening':
            self.knowledge_updater.update(review_data)

        # 6. Git提交推送
        self.git_manager.commit_and_push(review_data, mode)

        return review_data

    def _detect_mode(self):
        """根据当前时间自动识别模式"""
        from datetime import datetime
        hour = datetime.now().hour
        return 'morning' if 11 <= hour <= 13 else 'evening'
```

### 2.2 Reviewer（回顾分析器）

**职责**：回顾今日工作，分析已完成/进行中/待办任务

**核心功能**：
- ✅ 读取今日日志（memory/YYYY-MM-DD.md）
- ✅ 读取Git提交记录
- ✅ 读取GitHub Issues状态
- ✅ 分析查漏补缺

**Python实现**：
```python
class Reviewer:
    def review(self, time_range):
        """
        回顾指定时间范围的工作
        time_range: {'start': '07:00', 'end': '12:00'}
        """
        review_data = {
            'time_range': time_range,
            'memory': self._read_memory(time_range),
            'git_commits': self._read_git_commits(time_range),
            'github_issues': self._read_github_issues(),
            'gaps': self._find_gaps()
        }
        return review_data

    def _read_memory(self, time_range):
        """读取今日日志"""
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        memory_file = f'memory/{today}.md'

        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析内容（按时间范围过滤）
        return self._parse_memory(content, time_range)

    def _find_gaps(self):
        """查漏补缺分析"""
        gaps = {
            'memory_gaps': [],  # 未记录的重要事件
            'knowledge_gaps': [],  # 未归档的新知识
            'git_gaps': []  # 未提交的文件
        }

        # 1. 对比MEMORY.md和memory/YYYY-MM-DD.md
        # 2. 检查知识库文档数量
        # 3. 检查Git状态

        return gaps
```

### 2.3 MemoryUpdater（记忆更新器）

**职责**：更新记忆文件（memory/YYYY-MM-DD.md + MEMORY.md）

**核心功能**：
- ✅ 更新今日日志（memory/YYYY-MM-DD.md）
- ✅ 更新长期记忆（MEMORY.md，仅晚间）
- ✅ 补充遗漏事件

**Python实现**：
```python
class MemoryUpdater:
    def update(self, review_data, mode):
        """更新记忆文件"""
        # 1. 更新今日日志
        self._update_daily_memory(review_data)

        # 2. 更新长期记忆（仅晚间）
        if mode == 'evening':
            self._update_long_term_memory(review_data)

    def _update_daily_memory(self, review_data):
        """更新今日日志"""
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        memory_file = f'memory/{today}.md'

        # 读取现有内容
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 补充遗漏内容
        for gap in review_data['gaps']['memory_gaps']:
            content += f"\n\n## 补充记录\n\n{gap}"

        # 添加回顾总结
        summary = self._generate_summary(review_data)
        content += f"\n\n## 回顾总结\n\n{summary}"

        # 写回文件
        with open(memory_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def _update_long_term_memory(self, review_data):
        """更新长期记忆（MEMORY.md）"""
        # 提炼今日精华
        essence = self._extract_essence(review_data)

        # 追加到MEMORY.md
        with open('MEMORY.md', 'a', encoding='utf-8') as f:
            f.write(f"\n\n## {review_data['time_range']['date']}\n\n{essence}")
```

### 2.4 KnowledgeUpdater（知识库更新器）

**职责**：更新知识库（knowledge/）

**核心功能**：
- ✅ 创建知识文档（knowledge/YYYY-MM-DD/）
- ✅ 更新知识索引（KNOWLEDGE-INDEX.md）
- ✅ 分类归档（按主题分类）

**Python实现**：
```python
class KnowledgeUpdater:
    def update(self, review_data):
        """更新知识库"""
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')

        # 1. 创建知识文档目录
        knowledge_dir = f'knowledge/{today}'
        os.makedirs(knowledge_dir, exist_ok=True)

        # 2. 提取新知识
        new_knowledge = self._extract_knowledge(review_data)

        # 3. 写入知识文档
        for i, knowledge in enumerate(new_knowledge, 1):
            doc_file = f'{knowledge_dir}/{knowledge["topic"]}.md'
            self._write_knowledge_doc(doc_file, knowledge)

        # 4. 更新知识索引
        self._update_index(today, new_knowledge)
```

### 2.5 GitManager（Git管理器）

**职责**：Git提交和推送

**核心功能**：
- ✅ Git Add（添加所有更新文件）
- ✅ Git Commit（提交更改）
- ✅ Git Push（推送到远程仓库）
- ✅ 冲突处理（自动合并）

**Python实现**：
```python
class GitManager:
    def commit_and_push(self, review_data, mode):
        """Git提交和推送"""
        # 1. Git Add
        subprocess.run(['git', 'add', '.'], cwd=workspace_path)

        # 2. 生成提交信息
        commit_message = self._generate_commit_message(review_data, mode)

        # 3. Git Commit
        subprocess.run(['git', 'commit', '-m', commit_message], cwd=workspace_path)

        # 4. Git Push（带重试）
        for attempt in range(3):
            try:
                subprocess.run(['git', 'push'], cwd=workspace_path, check=True)
                break
            except subprocess.CalledProcessError as e:
                if attempt == 2:
                    logging.error(f"Git push failed after 3 attempts: {e}")
                    raise
                time.sleep(2)
```

---

## 3. 工作流程

### 3.1 中午回顾流程（12:00）

```
1. Crontab 12:00触发
   ↓
2. skill.sh执行
   ↓
3. 检查锁文件（/tmp/daily-review.lock）
   ↓
4. Scheduler.run('morning')
   ↓
5. Reviewer.review('07:00-12:00')
   - 读取memory/2026-03-16.md（07:00-12:00部分）
   - 读取Git提交记录（git log --since="07:00" --until="12:00"）
   - 查漏补缺（未记录的重要事件）
   ↓
6. MemoryUpdater.update(review_data, 'morning')
   - 更新memory/2026-03-16.md（补充遗漏）
   - 添加回顾总结
   ↓
7. GitManager.commit_and_push(review_data, 'morning')
   - git add .
   - git commit -m "chore(daily): 2026-03-16 中午回顾更新"
   - git push
   ↓
8. 记录日志 + 释放锁
   ↓
9. 完成（耗时<60秒）
```

### 3.2 晚间回顾流程（23:50）

```
1. Crontab 23:50触发
   ↓
2. skill.sh执行
   ↓
3. 检查锁文件（/tmp/daily-review.lock）
   ↓
4. Scheduler.run('evening')
   ↓
5. Reviewer.review('07:00-23:50')
   - 读取memory/2026-03-16.md（全天）
   - 读取Git提交记录（git log --since="07:00" --until="23:50"）
   - 读取GitHub Issues状态（gh issue list）
   - 查漏补缺（记忆遗漏 + 知识遗漏 + Git遗漏）
   ↓
6. MemoryUpdater.update(review_data, 'evening')
   - 更新memory/2026-03-16.md（补充遗漏 + 总结）
   - 更新MEMORY.md（提炼今日精华）
   ↓
7. KnowledgeUpdater.update(review_data)
   - 创建knowledge/2026-03-16/目录
   - 提取今日学习知识（3-5个文档）
   - 更新KNOWLEDGE-INDEX.md
   ↓
8. GitManager.commit_and_push(review_data, 'evening')
   - git add .
   - git commit -m "chore(daily): 2026-03-16 晚间回顾更新"
   - git push
   ↓
9. 记录日志 + 释放锁
   ↓
10. 完成（耗时<120秒）
```

---

## 4. 性能指标

### 4.1 核心性能指标

| 指标 | 目标值 | 测量方法 |
|------|--------|---------|
| **中午回顾时间** | <60秒 | 记录开始/结束时间 |
| **晚间回顾时间** | <120秒 | 记录开始/结束时间 |
| **内存占用** | <100MB | ps命令监控 |
| **CPU使用峰值** | <50% | top命令监控 |
| **Git推送成功率** | >99% | 记录成功/失败次数 |
| **日志大小** | <1MB/天 | du命令 |

### 4.2 准确性指标

| 指标 | 目标值 | 测量方法 |
|------|--------|---------|
| **查漏补缺准确率** | >95% | 人工抽样检查 |
| **记忆更新完整性** | >98% | 对比实际工作和记录 |
| **知识提取准确率** | >90% | 人工审核知识文档 |

---

## 5. 配置文件设计

### 5.1 config.yaml

```yaml
# 定时回顾更新助手配置

schedule:
  morning: "12:00"   # 中午12:00
  evening: "23:50"   # 晚上23:50

paths:
  workspace: "/root/.openclaw/workspace"
  memory: "memory/"
  knowledge: "knowledge/"
  logs: "skills/daily-review-assistant/logs/"
  lock_file: "/tmp/daily-review.lock"

review:
  morning_range:
    start: "07:00"
    end: "12:00"
  evening_range:
    start: "07:00"
    end: "23:50"

update:
  memory: true
  knowledge: true
  git: true
  remote: true

git:
  commit_message_template: "templates/commit-message.txt"
  auto_push: true
  max_retries: 3

logging:
  level: "INFO"  # DEBUG/INFO/WARN/ERROR
  max_size_mb: 1
  backup_count: 7

performance:
  timeout_seconds: 300  # 超时控制
  max_memory_mb: 100    # 内存限制
```

---

## 6. 测试计划

### 6.1 单元测试

**测试文件**：`tests/test_all.py`

**测试模块**：
1. **TestScheduler** - 测试调度器
   - ✅ 测试模式识别（中午/晚间）
   - ✅ 测试时间范围计算

2. **TestReviewer** - 测试回顾器
   - ✅ 测试记忆文件读取
   - ✅ 测试Git提交记录读取
   - ✅ 测试查漏补缺识别

3. **TestMemoryUpdater** - 测试记忆更新器
   - ✅ 测试今日日志更新
   - ✅ 测试长期记忆更新

4. **TestKnowledgeUpdater** - 测试知识库更新器
   - ✅ 测试知识提取
   - ✅ 测试索引更新

5. **TestGitManager** - 测试Git管理器
   - ✅ 测试Git提交
   - ✅ 测试Git推送（Mock远程仓库）

### 6.2 集成测试

**测试场景**：
1. ✅ **中午回顾完整流程**
   - 模拟12:00触发
   - 验证所有步骤执行
   - 检查Git提交

2. ✅ **晚间回顾完整流程**
   - 模拟23:50触发
   - 验证所有步骤执行
   - 检查知识库更新

3. ✅ **并发控制测试**
   - 模拟同时触发2次
   - 验证锁文件机制
   - 确保只执行1次

### 6.3 性能测试

**测试指标**：
- ✅ 中午回顾执行时间 < 60秒
- ✅ 晚间回顾执行时间 < 120秒
- ✅ 内存占用 < 100MB
- ✅ CPU峰值 < 50%

---

## 7. Phase 1 / Phase 2 实现方案

### 7.1 Phase 1：MVP（1天，2026-03-16）

**目标**：基础功能可运行

**核心功能**：
1. ✅ **定时触发机制**
   - Crontab配置（12:00和23:50）
   - 锁文件机制（避免重复执行）

2. ✅ **回顾今日工作**
   - 读取memory/YYYY-MM-DD.md
   - 读取Git提交记录
   - 基础查漏补缺

3. ✅ **更新记忆**
   - 更新memory/YYYY-MM-DD.md
   - 添加回顾总结

4. ✅ **Git提交和推送**
   - Git Add
   - Git Commit
   - Git Push（带重试）

**交付物**：
- ✅ skill.sh（入口脚本）
- ✅ lib/scheduler.py（调度器）
- ✅ lib/reviewer.py（回顾器）
- ✅ lib/memory_updater.py（记忆更新器）
- ✅ lib/git_manager.py（Git管理器）
- ✅ config/config.yaml（配置文件）
- ✅ 基础测试用例

**验收标准**：
- ✅ 12:00和23:50准时触发
- ✅ 中午回顾时间 < 60秒
- ✅ Git推送成功

### 7.2 Phase 2：完善（1天，2026-03-17）

**目标**：功能完善，质量提升

**新增功能**：
1. ✅ **查漏补缺分析增强**
   - 多维度检查（记忆+知识+Git）
   - 智能识别遗漏内容

2. ✅ **更新知识库**
   - 创建knowledge/YYYY-MM-DD/目录
   - 提取今日学习知识
   - 更新KNOWLEDGE-INDEX.md

3. ✅ **更新MEMORY.md**
   - 提炼今日精华
   - 追加到长期记忆

4. ✅ **错误处理和日志**
   - 完整的日志记录
   - 错误重试机制
   - 超时控制

**交付物**：
- ✅ lib/knowledge_updater.py（知识库更新器）
- ✅ templates/daily-summary.md（日报模板）
- ✅ templates/commit-message.txt（提交信息模板）
- ✅ 完整测试套件（单元测试+集成测试）
- ✅ SKILL.md（技能说明）
- ✅ README.md（使用文档）

**验收标准**：
- ✅ 晚间回顾时间 < 120秒
- ✅ 查漏补缺准确率 > 95%
- ✅ 测试覆盖率 > 80%

---

## 8. 安装和使用

### 8.1 安装

```bash
# 1. 安装技能
cd /root/.openclaw/workspace/skills
git clone <repo-url> daily-review-assistant
cd daily-review-assistant

# 2. 运行安装脚本
bash install.sh

# 3. 配置Crontab
crontab -e
# 添加以下两行：
# 0 12 * * * /root/.openclaw/workspace/skills/daily-review-assistant/skill.sh morning
# 50 23 * * * /root/.openclaw/workspace/skills/daily-review-assistant/skill.sh evening
```

### 8.2 使用

**自动模式**：
- 12:00和23:50自动触发（Crontab）

**手动模式**：
```bash
# 手动触发中午回顾
./skill.sh morning

# 手动触发晚间回顾
./skill.sh evening

# 查看日志
tail -f logs/review-2026-03-16.log
```

---

## 9. 风险和应对

### 9.1 技术风险

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| Crontab失效 | 高 | 添加日志监控，失败自动告警 |
| Git推送失败 | 中 | 自动重试3次，失败记录日志 |
| 磁盘空间不足 | 中 | 定期清理旧日志，保留7天 |
| 内存占用过高 | 低 | 限制处理文件数量，分批处理 |

### 9.2 业务风险

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| 回顾遗漏重要内容 | 中 | 多维度检查（Git+Issue+Memory） |
| 更新覆盖重要信息 | 高 | Git版本控制，可回滚 |
| 推送冲突 | 低 | 先pull再push，自动合并 |

---

## 10. 后续优化

### 10.1 短期优化（1周内）

- ✅ 添加飞书通知（回顾完成通知）
- ✅ 添加统计报表（每周总结）
- ✅ 优化性能（并行处理）

### 10.2 长期优化（1月内）

- ✅ AI辅助回顾（自动生成总结）
- ✅ 知识图谱构建（自动关联知识点）
- ✅ 多语言支持（中英文）

---

## 11. 参考资料

### 11.1 相关技能

- ✅ `context-manager` - 上下文管理（参考定时机制）
- ✅ `smart-memory-sync` - 记忆同步（参考更新策略）
- ✅ `session-memory-enhanced` - 会话记忆（参考日志记录）

### 11.2 相关文档

- ✅ `MEMORY.md` - 长期记忆
- ✅ `memory/YYYY-MM-DD.md` - 每日日志
- ✅ `knowledge/KNOWLEDGE-INDEX.md` - 知识索引
- ✅ `docs/products/2026-03-15_daily-review-assistant_PRD.md` - PRD文档

---

*文档版本：v1.0*
*创建时间：2026-03-16 10:10*
*创建者：小米辣（PM+Dev代理）🌶️*
*Issue：#16*
