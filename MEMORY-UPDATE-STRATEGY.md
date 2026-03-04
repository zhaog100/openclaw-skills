# 记忆与知识库定时更新策略

_系统化、自动化的知识管理方案_

---

## 📊 当前定时任务概览

### ✅ 已配置任务（4个）

| 任务名称 | 频率 | 时间 | 功能 | 下次运行 |
|----------|------|------|------|----------|
| **daily-review** | 每天 | 23:50 | 每日回顾与记忆更新 | 今晚23:50 |
| **config-backup** | 每天 | 03:00 | 配置备份 | 明早03:00 |
| **disk-check** | 每周日 | 09:00 | 磁盘空间检查 | 6天后 |
| **model-health-check** | 每周一 | 10:00 | 模型健康检查 | 7天后 |

---

## 🧠 记忆系统更新策略

### 1. 短期记忆（Daily Logs）

**更新频率：** 实时 + 每日汇总

**文件位置：** `memory/YYYY-MM-DD.md`

**更新机制：**
```
实时更新：
- 重要事件发生时立即记录
- 对话结束后记录关键信息
- 任务完成时记录结果

每日汇总（23:50 daily-review）：
- 回顾今日完成的工作
- 更新 memory/YYYY-MM-DD.md
- 整理临时文件
- 检查遗漏事项
```

**更新内容：**
- ✅ 任务完成情况
- ✅ 重要决策
- ✅ 遇到的问题
- ✅ 学到的教训
- ✅ 待办事项更新

### 2. 长期记忆（MEMORY.md）

**更新频率：** 每周 + 重大事件

**文件位置：** `MEMORY.md`

**更新机制：**
```
每周维护（建议：周日晚23:50）：
- 回顾本周 daily logs
- 提炼重要事件
- 更新 MEMORY.md
- 清理过时信息
- 补充新知识

重大事件时：
- 立即更新 MEMORY.md
- 记录决策和影响
- 更新系统状态
```

**更新原则：**
- 🎯 **精炼**：只保留精华，删除冗余
- 🔄 **更新**：及时更新过时信息
- 📊 **分类**：按类别组织（里程碑、教训、洞察）
- 🗑️ **清理**：定期清理过期内容

---

## 📚 知识库更新策略

### 1. 知识库文件管理

**当前知识库：** 18个文件（`knowledge/`目录）

**文件分类：**
```
knowledge/
├── project-management/    # 项目管理（6个）
├── software-testing/      # 软件测试（4个）
├── ai-system-design/      # AI系统设计（4个）
├── content-creation/      # 内容创作（3个）
└── README.md              # 知识库索引
```

### 2. 知识库更新频率

**建议频率：**
- **实时更新**：学习新知识时立即添加
- **每周整理**：整理碎片化知识
- **每月回顾**：评估知识库质量

**具体策略：**
```
实时更新（官家要求时）：
- 学习新技能后添加文档
- 发现好文章时归档
- 解决问题后记录方案

每周整理（建议：周日）：
- 整理本周学习的知识
- 更新知识库索引
- 删除过时内容
- 补充缺失领域

每月回顾（建议：每月最后一天）：
- 评估知识库覆盖度
- 识别薄弱领域
- 制定学习计划
- 更新学习路径
```

### 3. QMD索引更新（待安装）

**当前状态：** ❌ QMD未安装

**安装后策略：**
```bash
# 每日自动更新（建议：23:55）
openclaw cron add \
  --name "qmd-update" \
  --cron "55 23 * * *" \
  --tz "Asia/Shanghai" \
  --system-event "qmd update"

# 每周向量生成（建议：周日凌晨）
openclaw cron add \
  --name "qmd-embed" \
  --cron "0 2 * * 0" \
  --tz "Asia/Shanghai" \
  --system-event "qmd embed"
```

---

## 🔄 完整更新流程

### 每日流程

```
23:50 - daily-review（已配置）
  ├─ 回顾今日工作
  ├─ 更新 memory/YYYY-MM-DD.md
  ├─ 检查遗漏配置
  └─ 整理临时文件

23:55 - qmd-update（待配置）
  └─ 更新QMD索引

03:00 - config-backup（已配置）
  ├─ 备份 openclaw.json
  ├─ 备份 MEMORY.md
  └─ 检查备份完整性
```

### 每周流程

```
周日 09:00 - disk-check（已配置）
  ├─ 检查磁盘空间
  ├─ 清理临时文件
  └─ 清理旧日志

周日 23:50 - weekly-memory-maintenance（建议添加）
  ├─ 回顾本周 daily logs
  ├─ 更新 MEMORY.md
  ├─ 清理过时信息
  └─ 整理知识库

周一 10:00 - model-health-check（已配置）
  └─ 检查百炼模型状态
```

### 每月流程

```
每月最后一天 23:50 - monthly-review（建议添加）
  ├─ 评估系统完整性
  ├─ 更新长期记忆
  ├─ 评估知识库覆盖度
  ├─ 制定下月计划
  └─ 清理过期内容
```

---

## 📋 建议新增任务

### 1. 每周记忆维护（建议）
```bash
openclaw cron add \
  --name "weekly-memory-maintenance" \
  --cron "50 23 * * 0" \
  --tz "Asia/Shanghai" \
  --message "执行每周记忆维护：回顾本周daily logs、更新MEMORY.md、清理过时信息、整理知识库。要求：(1) 回顾本周工作 (2) 提炼重要事件 (3) 更新长期记忆 (4) 不要回复HEARTBEAT_OK (5) 不要解释你是谁 (6) 直接输出维护结果" \
  --session "isolated" \
  --wake "now" \
  --channel "qqbot" \
  --to "C099848DC9A60BF60A7BE31626822790" \
  --announce
```

### 2. 每月系统回顾（建议）
```bash
openclaw cron add \
  --name "monthly-review" \
  --cron "50 23 28-31 * *" \
  --tz "Asia/Shanghai" \
  --message "执行每月系统回顾：评估系统完整性、更新长期记忆、评估知识库覆盖度、制定下月计划。要求：(1) 回顾本月工作 (2) 评估系统状态 (3) 制定下月计划 (4) 不要回复HEARTBEAT_OK (5) 不要解释你是谁 (6) 直接输出回顾结果" \
  --session "isolated" \
  --wake "now" \
  --channel "qqbot" \
  --to "C099848DC9A60BF60A7BE31626822790" \
  --announce
```

### 3. QMD索引更新（待QMD安装后）
```bash
openclaw cron add \
  --name "qmd-update" \
  --cron "55 23 * * *" \
  --tz "Asia/Shanghai" \
  --system-event "qmd update"

openclaw cron add \
  --name "qmd-embed" \
  --cron "0 2 * * 0" \
  --tz "Asia/Shanghai" \
  --system-event "qmd embed"
```

---

## 📊 更新策略总览

### 记忆系统
| 类型 | 频率 | 机制 | 状态 |
|------|------|------|------|
| **Daily Logs** | 实时 + 每日 | 23:50 daily-review | ✅ 已配置 |
| **MEMORY.md** | 每周 + 事件 | 建议添加周维护 | ⏳ 建议配置 |
| **配置备份** | 每天 | 03:00 config-backup | ✅ 已配置 |

### 知识库
| 任务 | 频率 | 机制 | 状态 |
|------|------|------|------|
| **知识添加** | 实时 | 手动添加 | ✅ 可用 |
| **知识整理** | 每周 | 建议添加周维护 | ⏳ 建议配置 |
| **QMD索引** | 每天 | 待QMD安装 | ❌ 待安装 |
| **向量生成** | 每周 | 待QMD安装 | ❌ 待安装 |

### 系统维护
| 任务 | 频率 | 机制 | 状态 |
|------|------|------|------|
| **磁盘检查** | 每周日 | 09:00 disk-check | ✅ 已配置 |
| **模型检查** | 每周一 | 10:00 model-health-check | ✅ 已配置 |
| **每月回顾** | 每月 | 建议添加 | ⏳ 建议配置 |

---

## 🎯 优化建议

### 立即执行
1. ✅ 已配置4个定时任务
2. ⏳ 建议添加：每周记忆维护
3. ⏳ 建议添加：每月系统回顾

### 近期优化
1. [ ] 完成QMD安装
2. [ ] 配置QMD自动更新
3. [ ] 创建知识库更新提醒

### 长期优化
1. [ ] 建立知识库评分机制
2. [ ] 创建自动归档脚本
3. [ ] 实现智能推荐更新

---

## 📝 使用说明

### 查看当前任务
```bash
openclaw cron list
```

### 手动触发任务
```bash
# 触发每日回顾
openclaw cron run daily-review

# 触发配置备份
openclaw cron run config-backup
```

### 查看任务详情
```bash
openclaw cron show daily-review
```

---

*创建时间：2026-03-02 19:13*
*最后更新：2026-03-02 19:13*
*版本：v1.0*
