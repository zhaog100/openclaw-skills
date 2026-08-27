---
name: daily-review-assistant
version: 1.1.0
---

# 定时回顾更新助手 (daily-review-assistant) v1.1.0

> 定时回顾今日工作，查漏补缺，智能更新记忆和知识库

---

## 🎯 功能特性

- **🕐 智能定时回顾** - 中午 12:00 和晚上 23:50 自动回顾
- **📊 PR状态监控** - 实时监控GitHub PR状态，统计收益
- **💰 财务跟踪** - 自动统计Bounty收益和待收款项目
- **🎓 学习总结** - 智能提取学习笔记和经验教训
- **🔍 全面查漏补缺** - 7大维度全方位检查遗漏
- **🧠 智能MEMORY更新** - 自动提炼重要内容到长期记忆
- **📱 QQ Bot通知** - 执行完成后推送通知到QQ

---

## 🚀 快速开始

### 安装

```bash
cd $(pwd)/skills/daily-review-assistant
bash install.sh
```

### 使用

```bash
# 执行完整回顾
./skill.sh review

# 指定日期回顾
./skill.sh review --date 2026-05-08

# 全天回顾
./skill.sh review --mode full

# 查看状态
./skill.sh status

# 管理定时任务
./skill.sh cron-add        # 添加定时任务
./skill.sh cron-remove     # 删除定时任务
./skill.sh cron-status     # 查看定时任务状态
```

---

## 📁 文件结构

```
daily-review-assistant/
├── skill.sh                          # 主入口脚本 ⭐
├── scripts/
│   ├── lib/
│   │   └── config.sh                 # 配置加载库 ⭐
│   ├── gap-analyzer.sh               # 查漏补缺分析器 ⭐
│   └── memory-updater.sh             # 记忆更新器 ⭐
├── config/
│   └── config.json                   # 主配置文件 ⭐
├── logs/
│   └── daily-review.log              # 运行日志
├── SKILL.md                          # 技能说明
├── README.md                         # 详细文档
└── package.json                      # ClawHub配置
```

---

## ⏰ Crontab 配置

```bash
# 编辑 Crontab
 crontab -e

# 添加定时任务（修改路径为你的实际路径）
0 12 * * * /path/to/daily-review-assistant/skill.sh review --mode morning >> /path/to/logs/daily-review.log 2>&1
50 23 * * * /path/to/daily-review-assistant/skill.sh review --mode full >> /path/to/logs/daily-review.log 2>&1
```

### Provider 配置（v1.1.0 新增）

**问题**：2026-08-03 发现 daily-review cron 连续 timeout，根因是 agnesai provider (apihub.agnes-ai.com) 频繁 cooldown。

**解决方案**：
- cron 任务建议使用 `custom-apihub` provider（apihub.agnes-ai.cn，国内节点）
- 主力：`custom-apihub/agnes-2.5-flash`
- fallback：`agnesai/agnes-2.5-flash`

**timeout 配置建议**：
- 默认 timeout 3600s 过长，建议调整为 1800s
- cron 任务执行时间建议在 12:00 和 23:50，避开高峰期

**v1.1.0 更新记录（2026-08-03）**：
- 新增 Provider 配置说明
- 新增 cron timeout 根因分析
- 新增 timeout 配置建议

---

## 📊 输出示例

```
╔════════════════════════════════════════════════════════╗
║  定时回顾更新助手 v2.0 - 小米辣 (思捷娅科技 (SJYKJ)/zhaog100)              ║
╠════════════════════════════════════════════════════════╣
║  日期：2026-05-09
║  身份：思捷娅科技 (SJYKJ)/zhaog100 | GitHub: 思捷娅科技 (SJYKJ)/zhaog100
╚════════════════════════════════════════════════════════╝

🔍 步骤 1/7: 身份和工作区确认...
  ✅ 身份：思捷娅科技 (SJYKJ)/zhaog100 | GitHub: 思捷娅科技 (SJYKJ)/zhaog100
  ✅ 工作区：${OPENCLAW_WORKSPACE:-~/.openclaw/workspace}

📊 步骤 2/7: PR状态监控...
  📊 Open PRs: 300 个
  ✅ Merged PRs: 15 个
  📋 重要PR状态：
   #125 - permit-generation ($600) - 2026-05-08
   #87 - plugins-wishlist ($450) - 2026-05-08

💰 步骤 3/7: 财务状态汇总...
  💰 Bounty收益统计：
  🎯 Bounty PRs: 29 个
  ⏳ 待收款: 约$830 USD + 202 RTC

📋 步骤 4/7: 今日任务回顾...
  ✅ 完成 5 个任务

💻 步骤 5/7: Git提交回顾...
  ✅ 3 个 Git 提交

🎓 步骤 6/7: 学习总结和经验教训...
  📝 今日学习笔记：已记录
  💡 经验教训：3 条

🔄 步骤 7/7: 查漏补缺和MEMORY更新...
  🔍 查漏补缺分析...
  📚 MEMORY.md更新...
  🧠 智能更新MEMORY.md...

✅ 回顾完成！

📊 执行摘要：
✅ 完成任务: 5 个
💻 Git提交: 3 个
📊 Open PRs: 300 个
🎓 学习笔记: 1 条
💡 经验教训: 3 条
🔍 发现遗漏: 2 个
📊 总体评价: 🟡 良好
```

---

## 🔍 查漏补缺维度

### 1. 记忆系统检查
- ✅ 今日日志完整性
- ✅ MEMORY.md更新状态
- ✅ HEARTBEAT.md更新状态

### 2. 知识库检查
- ✅ 知识文档更新频率
- ✅ 索引文件完整性
- ✅ 知识库结构

### 3. Git状态检查
- ✅ 未提交文件
- ✅ 未推送提交
- ✅ 分支管理
- ✅ 大文件检查

### 4. PR状态检查
- ✅ Open PR数量
- ✅ PR审核状态
- ✅ PR冲突检查
- ✅ PR描述完整性

### 5. 财务状态检查
- ✅ Bounty收益记录
- ✅ 待收款项目
- ✅ 付款状态跟踪

### 6. 系统状态检查
- ✅ 磁盘空间
- ✅ 内存使用
- ✅ OpenClaw服务
- ✅ 定时任务配置

### 7. 学习进度检查
- ✅ 学习笔记完整性
- ✅ 经验教训记录
- ✅ 技能学习进度

---

## 📝 许可证

MIT License  
Copyright (c) 2026 思捷娅科技 (SJYKJ)

---

*版本：v2.0*  
*最后更新：2026-05-09*  
*创建者：小米辣 (思捷娅科技 (SJYKJ)/zhaog100)*