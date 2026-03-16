---
name: daily-review-assistant
description: 定时回顾更新助手。定时（中午 12 点、晚上 23:50）自动回顾今日工作，查漏补缺，更新记忆和知识库。
---

# 定时回顾更新助手 (daily-review-assistant)

**版本**: v1.0  
**创建时间**: 2026-03-16  
**创建者**: 思捷娅科技 (SJYKJ)  
**用途**: 定时回顾今日工作，查漏补缺，更新记忆和知识库

---

## 🎯 核心功能

### 1. 定时触发
- ✅ 中午 12:00 - 回顾上午工作
- ✅ 晚上 23:50 - 回顾全天工作
- ✅ Crontab 自动触发

### 2. 回顾今日工作
- ✅ 回顾任务完成情况
- ✅ 回顾 Git 提交
- ✅ 回顾 Issues 状态
- ✅ 回顾学习知识

### 3. 查漏补缺
- ✅ 检查记忆遗漏
- ✅ 检查知识遗漏
- ✅ 检查 Git 遗漏

### 4. 自动更新
- ✅ 更新今日日志
- ✅ 更新 MEMORY.md
- ✅ 更新知识库索引
- ✅ Git 提交和推送

---

## 🚀 使用方法

```bash
# 执行回顾
./skill.sh review

# 指定日期回顾
./skill.sh review --date 2026-03-16

# 全天回顾
./skill.sh review --mode full

# 查看状态
./skill.sh status

# 显示帮助
./skill.sh help
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
├── README.md             # 使用文档
└── package.json          # ClawHub 配置
```

---

## ⏰ Crontab 配置

```bash
# 中午 12:00 - 回顾上午
0 12 * * * /home/zhaog/.openclaw/workspace/skills/daily-review-assistant/skill.sh review --mode morning

# 晚上 23:50 - 回顾全天
50 23 * * * /home/zhaog/.openclaw/workspace/skills/daily-review-assistant/skill.sh review --mode full
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
  ⏳ Issues 回顾（待实现）
📚 步骤 4/4: 回顾学习...
  ✅ 2 个知识文档

✅ 回顾完成！
```

---

## 📝 许可证

MIT License  
Copyright (c) 2026 思捷娅科技 (SJYKJ)

---

*版本：v1.0*  
*最后更新：2026-03-16*  
*创建者：思捷娅科技 (SJYKJ)*
