# 增强版Session-Memory Hook

## 🎯 功能

**自动更新知识库和Git库**，在OpenClaw原生session-memory hook基础上增强。

### ✅ 新增功能

1. **QMD知识库自动更新**
   - 每小时自动运行 `qmd update`
   - 索引新增和修改的记忆文件
   - 保持知识库最新状态

2. **Git库自动提交**
   - 每小时自动检查更改
   - 自动提交到本地Git库
   - 保留完整版本历史

3. **日志记录**
   - 详细记录每次更新
   - 便于追踪和调试

## 📊 工作流程

```
定时触发（每小时）
    ↓
等待session-memory hook完成（5秒）
    ↓
更新QMD知识库（qmd update）
    ↓
提交到Git（git add + commit）
    ↓
记录日志
```

## 🚀 使用方式

### 自动模式（推荐）

**已配置为定时任务**：
```bash
# 每小时自动运行
0 * * * * /root/.openclaw/workspace/scripts/enhanced-session-memory.sh
```

**查看日志**：
```bash
tail -f /root/.openclaw/workspace/logs/enhanced-session-memory.log
```

### 手动模式

```bash
# 手动触发
bash /root/.openclaw/workspace/scripts/enhanced-session-memory.sh
```

### 配合/new使用

```
官家：/new
→ session-memory hook自动保存会话
→ [等待下一小时]
→ enhanced-session-memory自动更新QMD + Git
```

## 📁 文件结构

```
/root/.openclaw/workspace/
├── scripts/
│   └── enhanced-session-memory.sh  # 增强版hook脚本
├── logs/
│   └── enhanced-session-memory.log # 运行日志
└── MEMORY.md                        # 长期记忆
```

## 🔧 配置说明

### 修改运行频率

**编辑crontab**：
```bash
crontab -e
```

**修改频率**（示例）：
```bash
# 每小时
0 * * * * /root/.openclaw/workspace/scripts/enhanced-session-memory.sh

# 每30分钟
*/30 * * * * /root/.openclaw/workspace/scripts/enhanced-session-memory.sh

# 每2小时
0 */2 * * * /root/.openclaw/workspace/scripts/enhanced-session-memory.sh
```

### 禁用自动更新

```bash
# 编辑crontab
crontab -e

# 注释掉相关行
# 0 * * * * /root/.openclaw/workspace/scripts/enhanced-session-memory.sh
```

## 📊 性能影响

| 操作 | 频率 | 耗时 | 影响 |
|------|------|------|------|
| QMD更新 | 1次/小时 | <10秒 | 极低 |
| Git提交 | 1次/小时 | <5秒 | 极低 |
| 总体 | 1次/小时 | <15秒 | 可忽略 |

## 💡 最佳实践

### ✅ 推荐做法

1. **保持自动模式**：每小时自动更新
2. **定期检查日志**：`tail -100 logs/enhanced-session-memory.log`
3. **定期推送Git**：`git push`（可选）

### ⚠️ 注意事项

1. **不要频繁运行**：建议最少30分钟间隔
2. **监控磁盘空间**：日志文件会逐渐增大
3. **定期清理日志**：`> logs/enhanced-session-memory.log`

## 🎯 对比原生Hook

| 特性 | 原生session-memory | 增强版 |
|------|-------------------|--------|
| 保存会话记忆 | ✅ | ✅ |
| 触发时机 | /new, /reset | 定时（每小时）|
| 更新QMD | ❌ | ✅ |
| 提交Git | ❌ | ✅ |
| 需要配置 | ❌ | ✅（crontab）|
| 自动化程度 | 半自动 | 全自动 |

## 📞 故障排查

### 问题1：没有自动更新

**检查crontab**：
```bash
crontab -l | grep enhanced-session
```

**检查脚本权限**：
```bash
ls -l /root/.openclaw/workspace/scripts/enhanced-session-memory.sh
```

### 问题2：更新失败

**查看日志**：
```bash
tail -50 /root/.openclaw/workspace/logs/enhanced-session-memory.log
```

**手动测试**：
```bash
bash /root/.openclaw/workspace/scripts/enhanced-session-memory.sh
```

## 🚀 未来优化

- [ ] 检测到记忆变更时立即更新（inotify）
- [ ] 自动推送到远程Git仓库
- [ ] 智能压缩历史提交
- [ ] 与Context Monitor联动（达到阈值时触发）

---

**创建时间**：2026-03-07 14:42
**版本**：1.0.0
**作者**：米粒儿
