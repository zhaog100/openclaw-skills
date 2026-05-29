# Context Manager v2.2.3 - 错误处理增强版

## 🚀 新增功能（v2.2.3）

### 1. 智能重试机制 ⭐⭐⭐⭐⭐

**解决问题**：`Request was aborted` 等网络错误

**实现**：
```bash
# 自动重试配置
MAX_RETRIES=3          # 最大重试次数
RETRY_DELAY=5          # 重试延迟（秒）
TIMEOUT=30             # 超时时间（秒）
```

**效果**：
- ✅ API调用失败自动重试（最多3次）
- ✅ 通知发送失败自动重试（最多3次）
- ✅ 网络超时自动处理
- ✅ 减少误报和临时性错误

---

### 2. 错误统计与告警 ⭐⭐⭐⭐⭐

**功能**：
- ✅ 记录所有错误类型
- ✅ 统计错误频率
- ✅ 达到阈值自动告警

**配置**：
```bash
ERROR_THRESHOLD=5      # 错误阈值（5次/小时）
```

**触发**：
- 每小时错误 ≥ 5次 → 飞书通知告警
- 记录错误类型和次数
- 自动清理旧数据

---

### 3. 错误日志管理 ⭐⭐⭐⭐

**日志文件**：
```
~/.openclaw/workspace/logs/
├── context-monitor.log         # 主日志
├── context-errors.log          # 错误日志
└── context-error-stats.txt     # 统计报告
```

**清理策略**：
- 保留最近7天错误日志
- 自动清理临时文件
- 定期生成统计报告

---

## 📋 使用指南

### 1. 使用增强版监控

**原版**（无重试）：
```bash
~/.openclaw/skills/context-manager-v2/scripts/context-monitor.sh
```

**增强版**（带重试和错误处理）：
```bash
~/.openclaw/skills/context-manager-v2/scripts/context-monitor-enhanced.sh
```

---

### 2. 查看错误统计

```bash
# 查看错误统计
bash ~/.openclaw/skills/context-manager-v2/scripts/error-stats.sh stats

# 清理旧数据
bash ~/.openclaw/skills/context-manager-v2/scripts/error-stats.sh cleanup

# 重置错误计数
bash ~/.openclaw/skills/context-manager-v2/scripts/error-stats.sh reset

# 全部操作
bash ~/.openclaw/skills/context-manager-v2/scripts/error-stats.sh all
```

---

### 3. 更新Crontab

**原配置**（使用原版）：
```bash
*/5 * * * * ~/.openclaw/skills/context-manager-v2/scripts/context-monitor.sh
```

**新配置**（使用增强版）：
```bash
*/5 * * * * ~/.openclaw/skills/context-manager-v2/scripts/context-monitor-enhanced.sh

# 每天凌晨2点清理错误日志
0 2 * * * ~/.openclaw/skills/context-manager-v2/scripts/error-stats.sh cleanup

# 每小时检查错误统计
0 * * * * ~/.openclaw/skills/context-manager-v2/scripts/error-stats.sh stats
```

---

## 🔧 配置说明

### 重试配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `MAX_RETRIES` | 3 | 最大重试次数 |
| `RETRY_DELAY` | 5 | 重试延迟（秒） |
| `TIMEOUT` | 30 | API超时时间（秒） |

---

### 告警配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `THRESHOLD` | 60% | 上下文使用率阈值 |
| `ERROR_THRESHOLD` | 5次/小时 | 错误频率阈值 |
| `NOTIFICATION_COOLDOWN` | 1小时 | 通知冷却期 |

---

## 📊 错误类型

### 1. API错误
- `API超时`：网络超时
- `API失败`：OpenClaw API调用失败

### 2. 通知错误
- `通知超时`：飞书通知发送超时
- `通知失败`：飞书通知发送失败

### 3. 解析错误
- `JSON解析失败`：API返回数据格式错误

---

## 🎯 效果对比

### 原版 vs 增强版

| 特性 | 原版 | 增强版 |
|------|------|--------|
| **重试机制** | ❌ 无 | ✅ 3次重试 |
| **错误统计** | ❌ 无 | ✅ 详细统计 |
| **告警阈值** | ❌ 无 | ✅ 5次/小时 |
| **日志管理** | 基础 | 完整 |
| **错误恢复** | ❌ 手动 | ✅ 自动 |

---

## 🚀 推荐配置

### Crontab配置（生产环境）

```bash
# 上下文监控（每5分钟）
*/5 * * * * ~/.openclaw/skills/context-manager-v2/scripts/context-monitor-enhanced.sh

# 错误统计（每小时）
0 * * * * ~/.openclaw/skills/context-manager-v2/scripts/error-stats.sh stats

# 日志清理（每天凌晨2点）
0 2 * * * ~/.openclaw/skills/context-manager-v2/scripts/error-stats.sh cleanup

# 周报告（每周一上午9点）
0 9 * * 1 ~/.openclaw/skills/context-manager-v2/scripts/error-stats.sh all
```

---

## 💡 最佳实践

### 1. 立即启用
```bash
# 测试增强版监控
bash ~/.openclaw/skills/context-manager-v2/scripts/context-monitor-enhanced.sh

# 更新crontab
crontab -e
# 将原版替换为增强版
```

---

### 2. 监控错误
```bash
# 查看实时错误日志
tail -f ~/.openclaw/workspace/logs/context-errors.log

# 查看统计报告
cat ~/.openclaw/workspace/logs/context-error-stats.txt
```

---

### 3. 调整阈值
```bash
# 编辑增强版脚本
nano ~/.openclaw/skills/context-manager-v2/scripts/context-monitor-enhanced.sh

# 修改阈值
ERROR_THRESHOLD=10  # 提高到10次/小时
MAX_RETRIES=5       # 增加重试到5次
TIMEOUT=60          # 增加超时到60秒
```

---

## 🔍 故障排查

### 问题1：仍然出现 "Request was aborted"

**原因**：可能网络持续不稳定

**解决**：
1. 增加重试次数：`MAX_RETRIES=5`
2. 增加超时时间：`TIMEOUT=60`
3. 增加重试延迟：`RETRY_DELAY=10`

---

### 问题2：频繁告警

**原因**：错误阈值太低

**解决**：
1. 提高阈值：`ERROR_THRESHOLD=10`
2. 检查网络稳定性
3. 查看错误统计报告

---

### 问题3：日志过大

**原因**：未定期清理

**解决**：
```bash
# 手动清理
bash ~/.openclaw/skills/context-manager-v2/scripts/error-stats.sh cleanup

# 或配置自动清理（已在crontab中）
```

---

## 📝 版本历史

### v2.2.3 (2026-03-14 18:05) ⭐⭐⭐⭐⭐
- ✅ 智能重试机制（解决"Request was aborted"）
- ✅ 错误统计与告警
- ✅ 完整的错误日志管理
- ✅ 自动清理机制

---

*Context Manager v2.2.3 - 生产就绪版*
*解决网络错误，提升稳定性*
