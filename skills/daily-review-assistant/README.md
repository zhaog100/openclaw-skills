# 定时回顾更新助手 (daily-review-assistant)

> 定时回顾今日工作，查漏补缺，更新记忆和知识库

---

## 🎯 功能特性

- **定时触发** - 中午 12:00 和晚上 23:50 自动回顾
- **工作回顾** - 任务、Git、Issues、学习全面回顾
- **查漏补缺** - 自动检查记忆、知识、Git 遗漏
- **自动更新** - 自动更新 MEMORY.md 和知识库

---

## 🚀 快速开始

### 安装

```bash
cd $(pwd)/skills/daily-review-assistant
bash install.sh
```

### 使用

```bash
# 执行回顾
./skill.sh review

# 指定日期回顾
./skill.sh review --date 2026-03-16

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

## ⏰ Crontab 配置

```bash
# 编辑 Crontab
crontab -e

# 添加定时任务
# 中午 12:00 - 回顾上午
0 12 * * * $(pwd)/skills/daily-review-assistant/skill.sh review --mode morning

# 晚上 23:50 - 回顾全天
50 23 * * * $(pwd)/skills/daily-review-assistant/skill.sh review --mode full
```

---

## 📁 文件结构

```
daily-review-assistant/
├── skill.sh              # 主入口
├── scripts/
│   ├── gap-analyzer.sh   # 查漏补缺分析器
│   └── memory-updater.sh # 记忆更新器
├── config/
│   └── config.json       # 配置文件
├── logs/
│   └── daily-review.log  # 运行日志
├── SKILL.md              # 技能说明
├── README.md             # 本文档
└── package.json          # ClawHub 配置
```

---

## 📊 输出示例

```
╔════════════════════════════════════════════════════════╗
║  定时回顾更新助手 v1.0                                  ║
╠════════════════════════════════════════════════════════╣
║  日期：2026-03-16
║  模式：full
╚════════════════════════════════════════════════════════╝

📋 步骤 1/4: 回顾今日任务...
  ✅ 完成 5 个任务
💻 步骤 2/4: 回顾 Git 提交...
  ✅ 3 个 Git 提交
📝 步骤 3/4: 回顾 Issues...
  ✅ 关闭 1 个 Issue
📚 步骤 4/4: 回顾学习...
  ✅ 2 个知识文档

✅ 回顾完成！
```

---

## 📝 许可证

MIT License  
Copyright (c) 2026 思捷娅科技 (SJYKJ)

---

*版本：v1.1*  
*最后更新：2026-03-16*  
*创建者：思捷娅科技 (SJYKJ)*
