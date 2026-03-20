---
name: daily-review-assistant
description: 定时回顾更新助手。定时（中午 12 点、晚上 23:50）自动回顾今日工作，查漏补缺，更新记忆和知识库。
---

# 定时回顾更新助手 (daily-review-assistant)

**版本**: v1.1  
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

## 🛡️ 容错规则（重要！）

**记忆文件编辑失败时，跳过继续完成回顾并发送报告。** 回顾流程中的任何文件写入操作（MEMORY-LITE.md、MEMORY.md、daily log 等）都可能因并发写入、权限、磁盘等原因失败。这些失败**绝不能阻断消息发送**。

### 执行规则
1. **回顾分析优先**：先完成所有回顾分析（任务、Git、学习等），生成报告内容
2. **记忆更新是可选的**：尝试更新记忆文件，失败则跳过，在报告中标注"⚠️ 记忆更新失败，已跳过"
3. **报告必须送达**：无论记忆更新是否成功，回顾报告必须发送出去
4. **不要重试失败的文件编辑**：失败一次就跳过，不要反复重试导致流程卡住

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

# 管理定时任务
./skill.sh cron-add                 # 添加默认定时任务（中午 12:00 + 晚上 23:50）
./skill.sh cron-add morning         # 仅添加上午任务（中午 12:00）
./skill.sh cron-add full            # 仅添加全天任务（晚上 23:50）
./skill.sh cron-add custom          # 自定义定时任务（交互式）
./skill.sh cron-remove              # 删除定时任务
./skill.sh cron-status              # 查看定时任务状态
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
0 12 * * * $(pwd)/skills/daily-review-assistant/skill.sh review --mode morning

# 晚上 23:50 - 回顾全天
50 23 * * * $(pwd)/skills/daily-review-assistant/skill.sh review --mode full
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
