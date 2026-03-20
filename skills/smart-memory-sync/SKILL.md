---
name: smart-memory-sync
description: 主动智能记忆管理技能。实时分析聊天、三库同步（MEMORY+QMD+Git）、主动切换、预防性保护。与Context Manager互补，双保险机制。
version: 1.0.0
author: 米粒儿
created: 2026-03-06
updated: 2026-03-06
---

# Smart Memory Sync - 主动智能记忆管理

预防性保护 + 三库同步 + 主动切换 + 双保险机制

## 🎯 核心功能

- **主动监控**：实时监控上下文使用率，每5分钟检查
- **三库同步**：MEMORY.md + QMD知识库 + Git库
- **主动切换**：85%阈值触发Context Manager切换
- **双保险**：Smart Memory Sync（预防50%/75%/85%）+ Context Manager（应急85%）

## 📊 三级阈值

- **< 50%**：正常对话
- **≥ 50%**：提醒用户同步记忆
- **≥ 75%**：自动同步三库（MEMORY + QMD + Git）
- **≥ 85%**：主动触发切换，创建新会话

## 🚀 使用方式

```bash
# 后台守护（每5分钟检查）
python3 scripts/smart-sync.py --daemon

# 手动同步三库
python3 scripts/smart-sync.py --sync

# 单次检查
python3 scripts/smart-sync.py --check

# 查看状态
python3 scripts/smart-sync.py --status
```

## 🏗️ 文件结构

```
smart-memory-sync/
├── scripts/smart-sync.py   # 主入口
├── syncers/sync-all.py     # 三库同步
├── triggers/auto-check.py  # 上下文监控
├── config/sync-config.json # 配置
└── logs/monitor.log        # 日志
```

## 🔧 配置（sync-config.json）

```json
{
  "thresholds": { "remind": 50, "auto_sync": 75, "auto_switch": 85 },
  "intervals": { "check": 300, "sync": 3600 },
  "integrations": {
    "context_manager": { "enabled": true },
    "qmd": { "enabled": true, "collection": "knowledge" },
    "git": { "enabled": true, "auto_push": false }
  }
}
```

## ⚠️ 注意

- 每个动作后10分钟冷却期，避免重复触发
- 与Context Manager互补，不替代
- 日志：`logs/monitor.log`

> 详细的技术架构、性能指标、使用场景、版本规划见 `references/skill-details.md`

---

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者：小米辣 (PM + Dev)

**商业使用授权**：
- 个人/开源：免费
- 小微企业（<10 人）：¥999/年
- 中型企业（10-50 人）：¥4,999/年
- 大型企业（>50 人）：¥19,999/年
- 源码买断：¥99,999 一次性

详情请查看：[LICENSE](../../LICENSE)
