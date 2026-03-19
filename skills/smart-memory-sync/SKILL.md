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
