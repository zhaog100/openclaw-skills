# 双米粒协作系统 - 6大机制完整指南

**创建时间**：2026-03-12 20:10
**版本**：v1.0
**状态**：✅ 已完善

---

## 🎯 概述

双米粒协作系统的6大核心机制，确保小米辣和米粒儿（两个独立智能体会话）高效协作。

**核心原则**：
- ✅ 两个独立智能体会话
- ✅ GitHub Issues通信 + Git同步
- ✅ 分级处理机制
- ✅ 透明化协作

---

## 📊 6大机制一览

| 机制 | 文档 | 大小 | 优先级 | 核心功能 |
|------|------|------|--------|---------|
| 1. 超时提醒 | [TIMEOUT_ALERT_MECHANISM.md](TIMEOUT_ALERT_MECHANISM.md) | 1.8KB | 🔴 高 | 分级超时处理（5/10/30分钟） |
| 2. 紧急通知 | [EMERGENCY_NOTIFICATION_MECHANISM.md](EMERGENCY_NOTIFICATION_MECHANISM.md) | 2.2KB | 🔴 高 | 多渠道通知（Issue+QQ+电话） |
| 3. 升级机制 | [ESCALATION_MECHANISM.md](ESCALATION_MECHANISM.md) | 2.1KB | 🔴 高 | 分级升级（15/30/60分钟→官家） |
| 4. 在线状态同步 | [ONLINE_STATUS_SYNC_MECHANISM.md](ONLINE_STATUS_SYNC_MECHANISM.md) | 2.7KB | 🟡 中 | 4状态同步（在线/忙碌/离线/勿扰） |
| 5. 日报机制 | [DAILY_REPORT_MECHANISM.md](DAILY_REPORT_MECHANISM.md) | 2.6KB | 🟡 中 | 每日17:00同步进度 |
| 6. 周报机制 | [WEEKLY_REPORT_MECHANISM.md](WEEKLY_REPORT_MECHANISM.md) | 3.8KB | 🟡 中 | 每周五17:00回顾成果 |

**总大小**：15.2KB
**文档状态**：✅ 全部完成

---

## 🚀 快速开始

### 场景1：发送重要任务

**步骤**：
1. 在Issue评论发送任务（@对方）
2. 设置优先级（🔴高/🟡中/🟢低）
3. 等待回复
4. 超时后自动触发提醒机制

**示例**：
```markdown
@小米辣 🔴 高优先级任务

请Review Smart Model v2.0
Issue: #4
截止时间：今日18:00

---
*米粒儿 - 2026-03-12 20:00*
```

### 场景2：超时未回复

**自动处理流程**：
- 🔴 高优先级：5分钟 → Issue提醒 → 10分钟 → QQ通知 → 15分钟 → 上报官家
- 🟡 中优先级：10分钟 → Issue提醒 → 20分钟 → QQ通知 → 30分钟 → 上报官家
- 🟢 低优先级：30分钟 → Issue提醒 → 60分钟 → 记录待确认

### 场景3：紧急情况

**处理方式**：
1. Issue评论（@对方）
2. QQ即时通知
3. 必要时电话（如果配置）
4. 10分钟未回复 → 上报官家

### 场景4：每日同步

**时间**：每日17:00
**方式**：Issue评论 + `.mili_comm/daily/`存档
**内容**：
- ✅ 今日完成
- 🔄 进行中
- 📅 明日计划
- 🤔 问题与风险

### 场景5：每周回顾

**时间**：每周五17:00
**方式**：Issue评论 + `.mili_comm/weekly/`存档
**内容**：
- 🎊 本周成果
- 📊 数据统计
- 🤝 协作总结
- 📅 下周计划

---

## 📋 机制详细说明

### 1️⃣ 超时提醒机制

**文档**：[TIMEOUT_ALERT_MECHANISM.md](TIMEOUT_ALERT_MECHANISM.md)

**核心规则**：
- 🔴 高优先级：5分钟超时
- 🟡 中优先级：10分钟超时
- 🟢 低优先级：30分钟超时

**提醒格式**：
```markdown
@对方 ⏰ 超时提醒

**超时时长**：X分钟
**优先级**：🔴高 / 🟡中 / 🟢低
**请尽快回复！**
```

---

### 2️⃣ 紧急通知机制

**文档**：[EMERGENCY_NOTIFICATION_MECHANISM.md](EMERGENCY_NOTIFICATION_MECHANISM.md)

**通知渠道**：
- 🔴 紧急：Issue评论 + QQ即时 + 电话
- 🟡 重要：Issue评论 + QQ即时（可选）
- 🟢 普通：Issue评论

**响应要求**：
- 🔴 紧急：< 5分钟
- 🟡 重要：< 10分钟
- 🟢 普通：< 30分钟

---

### 3️⃣ 升级机制

**文档**：[ESCALATION_MECHANISM.md](ESCALATION_MECHANISM.md)

**升级流程**：
- 🔴 高优先级：15分钟 → 上报官家
- 🟡 中优先级：30分钟 → 上报官家
- 🟢 低优先级：次日 → 上报官家

**上报格式**：
```markdown
@官家 ⚠️ 升级通知

**已采取措施**：Issue提醒 + QQ通知
**请官家指示！**
```

---

### 4️⃣ 在线状态同步机制

**文档**：[ONLINE_STATUS_SYNC_MECHANISM.md](ONLINE_STATUS_SYNC_MECHANISM.md)

**状态定义**：
- 🟢 在线：响应 < 5分钟
- 🟡 忙碌：响应 5-30分钟
- 🔴 离线：响应 > 30分钟
- ⏸️ 勿扰：仅紧急事项立即响应

**同步方式**：
- Issue评论（主要）
- `.mili_comm/status.json`（自动）
- QQ状态（紧急）

---

### 5️⃣ 日报机制

**文档**：[DAILY_REPORT_MECHANISM.md](DAILY_REPORT_MECHANISM.md)

**时间**：每日17:00
**方式**：Issue评论 + `.mili_comm/daily/`存档

**模板**：
```markdown
# 📊 [日期] 日报

## ✅ 今日完成
## 🔄 进行中
## 📅 明日计划
## 🤔 问题与风险
```

---

### 6️⃣ 周报机制

**文档**：[WEEKLY_REPORT_MECHANISM.md](WEEKLY_REPORT_MECHANISM.md)

**时间**：每周五17:00
**方式**：Issue评论 + `.mili_comm/weekly/`存档

**模板**：
```markdown
# 📊 第[N]周周报

## 🎊 本周成果
## 📊 本周数据
## 🤝 协作总结
## 📅 下周计划
```

---

## 🎯 使用场景矩阵

| 场景 | 使用机制 | 优先级 | 响应时间 |
|------|---------|--------|---------|
| 官家紧急指示 | 紧急通知 + 升级 | 🔴 高 | < 5分钟 |
| 开发任务分配 | 超时提醒 | 🔴 高 | < 5分钟 |
| 日常进度同步 | 日报机制 | 🟡 中 | < 30分钟 |
| 产品构思讨论 | 在线状态同步 | 🟡 中 | < 10分钟 |
| 每周工作回顾 | 周报机制 | 🟡 中 | 每周五 |
| 文档更新通知 | 超时提醒 | 🟢 低 | < 30分钟 |

---

## 📊 效果评估

### 预期效果

**协作效率**：
- ✅ 响应时间：< 10分钟（高优先级）
- ✅ 超时率：< 5%
- ✅ 升级率：< 1%

**透明度**：
- ✅ 每日同步：100%
- ✅ 每周回顾：100%
- ✅ 状态可见：100%

**持续改进**：
- ✅ 每周回顾机制效果
- ✅ 每月优化机制参数
- ✅ 季度升级机制版本

---

## 🔧 配置与维护

### 初始化配置

```bash
# 初始化通信目录
bash scripts/mili_comm.sh init

# 配置Git
git config --global user.name "小米辣/米粒儿"
git config --global user.email "your@email.com"

# 验证GitHub CLI
gh auth status
```

### 日常维护

**每日**：
- ✅ 17:00 提交日报
- ✅ 检查超时统计
- ✅ 更新在线状态

**每周**：
- ✅ 周五17:00 提交周报
- ✅ 回顾机制效果
- ✅ 优化协作流程

---

## 📚 相关文档

**协作系统**：
- [双米粒协作快速开始](DUAL_MILI_GIT_QUICKSTART.md)
- [Git通信机制](DUAL_MILI_GIT_COMMUNICATION.md)
- [协作脚本说明](DUAL_MILI_SCRIPTS.md)

**系统设计**：
- [系统架构图](SYSTEM_ARCHITECTURE_DIAGRAM.md)
- [编排器架构](ORCHESTRATOR_ARCHITECTURE.md)
- [版本选择指南](VERSION_SELECTION_GUIDE.md)

---

## 🎊 总结

**6大机制保障**：
1. ✅ 超时提醒 - 不遗漏任何消息
2. ✅ 紧急通知 - 快速响应重要事件
3. ✅ 升级机制 - 确保问题解决
4. ✅ 在线状态 - 合理安排沟通时机
5. ✅ 日报机制 - 每日进度透明
6. ✅ 周报机制 - 持续改进协作

**核心优势**：
- 🎯 分级处理（高/中/低优先级）
- 📱 多渠道通知（Issue+QQ+电话）
- 📊 透明化协作（日报+周报）
- 🔄 持续改进（每周回顾）

---

*创建时间：2026-03-12 20:10*
*版本：v1.0*
*维护者：双米粒协作系统*
