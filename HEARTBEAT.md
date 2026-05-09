# HEARTBEAT 定时检查

_利用 OpenClaw 的 heartbeat 机制实现每日回顾_

---

## 📋 检查任务

### 每次心跳执行
- [ ] **身份确认**⭐⭐⭐
  - 确认身份：小米辣 🌶️（AI 助手 · OpenClaw 智能体）
  - 确认GitHub：zhaog100
  - 确认工作目录：/home/zhaog/.openclaw/workspace
  - 确认QQBot ID：8C21AFD77B89CA793A2AAC9A3ABEEA25
- [ ] 检查是否到了回顾时间
- [ ] 检查系统运行状态

### 定时学习任务

#### 晚间学习 (21:00-22:00)
- [ ] 总结今天学到的 3 个新知识点
- [ ] 更新 MEMORY.md(如有重要发现)
- [ ] 记录到 memory/YYYY-MM-DD.md
- [ ] 有重要发现时通知用户

### 午间回顾 (12:00)
如果当前时间在 12:00-12:30 之间:
- [ ] 读取 memory/YYYY-MM-DD.md(今日日志)
- [ ] 回顾上午完成的任务
- [ ] 检查 MEMORY.md 中的待办事项
- [ ] 查看当前 PR 状态
- [ ] 更新 memory/YYYY-MM-DD.md
- [ ] 简要总结上午进展，规划下午重点

### 晚间回顾 (23:50)
如果当前时间在 23:50-23:59 之间: 
- [ ] 全面回顾今天的工作 
- [ ] 总结今天学到的知识和教训 
- [ ] 查漏补缺：检查遗漏的任务、未完成的承诺 
- [ ] 提炼有价值的经验到 MEMORY.md 
- [ ] 检查 MEMORY.md 是否需要精简或更新 
- [ ] 补充 memory/YYYY-MM-DD.md 的遗漏内容 
- [ ] 输出今日总结

---

## 📌 注意事项

1. **不要重复执行**：同一时段只执行一次
2. **保持简洁**：输出要精简，不要太长
3. **重要才通知**：只在有重要发现时才主动汇报
4. **自动记录**：所有回顾内容自动记录到 memory/YYYY-MM-DD.md

---

## 🔍 最近心跳状态

### 2026-05-09 09:48 AM CST
- **检查类型**：心跳检查 + 系统维护
- **系统状态**：🟢 正常（负载 0.28，磁盘 17%）
- **运行时间**：正常

### ✅ 已完成
1. ✅ daily-review-assistant 技能优化完成
   - 位置：skills/daily-review-assistant/
   - 功能：PR监控、财务跟踪、查漏补缺、MEMORY智能更新
   - 状态：已测试，状态检查正常

2. ✅ Git 工作区有未提交文件
   - data/bounty-pr-tracker.json
   - memory/2026-05-09.md
   - skills/ (新优化脚本)

### ⚠️ 待处理
1. 更新 HEARTBEAT.md（已清理过期历史）
2. 提交 Git 变更（skills/daily-review-assistant/）
3. 检查 MEMORY.md 内容质量

---

_最后更新：2026-05-09 09:48 AM CST_