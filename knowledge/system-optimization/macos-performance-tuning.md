# macOS 系统性能调优指南

_最后更新: 2026-03-30_

---

## 📋 概述

本指南记录了 macOS 系统性能优化的实用技巧，特别是针对内存受限（8GB）的老旧 MacBook Air。

---

## 🔧 内存优化

### 1. 小部件管理

**问题**: macOS 通知中心的小部件会自动重启，消耗内存

**小部件内存占用**:
- 股票小部件（StocksWidget）: ~55MB
- 天气小部件（WeatherWidget）: ~50MB
- 时钟小部件（WorldClockWidget）: ~45MB
- **总计**: ~150MB

**解决方案**:

```bash
# 方法1: 禁用通知中心小部件（命令行）
defaults write com.apple.notificationcenterui TodayViewShowOnLockScreen -bool false
defaults write com.apple.notificationcenterui TodayViewShowInNotificationCenter -bool false

# 重启通知中心使配置生效
killall NotificationCenter

# 方法2: 手动移除小部件
# 打开通知中心 → 编辑 → 移除所有小部件
```

**效果**: 释放 ~150MB 内存，防止自动重启

### 2. 媒体分析服务

**问题**: `mediaanalysisd` 进程会消耗大量 CPU 和内存（173MB + 28.8% CPU）

**解决方案**:

```bash
# 临时停止（下次启动会重新运行）
killall mediaanalysisd

# 永久禁用（不推荐，影响照片分析）
sudo launchctl bootout system/com.apple.mediaanalysisd
```

**效果**: 释放 173MB 内存，降低 CPU 使用率

**注意**: 媒体分析服务会在系统空闲时自动重启，这是正常行为

### 3. Safari 缓存清理

**问题**: Safari 缓存会占用磁盘空间

**解决方案**:

```bash
# 清理 Safari WebKit 缓存
rm -rf ~/Library/Caches/com.apple.Safari/Webkit
rm -rf ~/Library/Caches/com.apple.helpd
rm -rf ~/Library/Caches/com.apple.nsurlsessiond
```

**效果**: 释放磁盘空间，不影响浏览历史

---

## 💾 缓存清理

### 用户缓存目录

```bash
# 查看缓存大小
du -sh ~/Library/Caches

# 安全清理的缓存（不影响系统运行）
rm -rf ~/Library/Caches/com.apple.Safari/Webkit      # Safari 浏览器缓存
rm -rf ~/Library/Caches/com.apple.helpd              # 帮助文档缓存
rm -rf ~/Library/Caches/com.apple.nsurlsessiond      # URL Session 缓存
rm -rf ~/Library/Caches/com.apple.photolibraryd      # 照片库缓存
rm -rf ~/Library/Caches/com.apple.Dock.agent         # Dock 缓存
rm -rf ~/Library/Caches/pip                          # pip 包管理缓存
rm -rf ~/Library/Caches/yarn                         # yarn 包管理缓存
rm -rf ~/Library/Caches/Homebrew                     # Homebrew 缓存

# 清理临时文件
rm -rf /tmp/*                                        # 系统临时文件
rm -rf ~/Library/Logs/*                              # 用户日志

# ⚠️ 注意：不要删除整个 ~/Library/Caches 目录
# 某些应用缓存是必需的，删除后会影响应用启动速度
```

**清理效果**: 可释放 1-3GB 磁盘空间

### 系统缓存清理

```bash
# 清理系统日志（需要管理员权限）
sudo rm -rf /Library/Logs/*

# 清理系统临时文件
sudo rm -rf /private/var/folders/*
```

---

## 🔄 进程管理

### 识别高内存占用进程

```bash
# 按内存排序显示 TOP 10
ps aux | sort -nrk 4,4 | head -11

# 按实际内存（RSS）排序
ps aux | sort -nrk 6,6 | head -11 | awk '{printf "%-10s %-6s %6s %s\n", $1, $2, $6/1024"M", $11}'
```

### 识别高 CPU 占用进程

```bash
# 按 CPU 排序显示 TOP 10
ps aux | sort -nrk 3,3 | head -11

# 实时监控
top -o cpu
```

### 关闭不必要进程

```bash
# 关闭特定应用
killall <应用名称>

# 强制关闭
killall -9 <应用名称>
```

---

## 📊 监控系统状态

### 实时监控命令

```bash
# 系统负载
uptime

# 内存使用
top -l 1 | grep PhysMem

# CPU 使用率
top -l 2 -n 10 -o cpu -s 2 | grep -E "^Processes|^CPU"

# 磁盘使用
df -h /

# 进程数
ps aux | wc -l
```

### 系统健康度评估

```bash
# 负载评估（假设 4 核 CPU）
# 负载 < 1.0  = 系统轻松
# 负载 1.0-2.0 = 系统正常
# 负载 2.0-4.0 = 系统繁忙
# 负载 > 4.0   = 系统过载

# 内存评估
# 可用内存 > 1GB  = 健康
# 可用内存 500MB-1GB = 正常
# 可用内存 < 500MB = 紧张
# 可用内存 < 100MB = 危险
```

---

## ⚡ 性能优化效果

### 实测案例（2026-03-30）

**优化前**:
- 系统负载: 4.44
- 内存使用: 7.97GB (97%)
- 可用内存: 222MB
- CPU 空闲: ~50%
- 缓存大小: 2.3GB

**优化后**:
- 系统负载: 0.67 (-85%)
- 内存使用: 7.22GB (88%)
- 可用内存: 969MB (+337%)
- CPU 空闲: 97.81% (+48%)
- 缓存大小: 726MB (-68%)

**优化措施**:
1. ✅ 停止 mediaanalysisd
2. ✅ 关闭小部件（股票/天气/时钟）
3. ✅ 清理缓存 1.6GB
4. ✅ 关闭 Safari 相关进程

---

## 🛡️ 预防措施

### 1. 定期清理（每周）

```bash
# 每周清理缓存
#!/bin/bash
echo "清理用户缓存..."
rm -rf ~/Library/Caches/com.apple.Safari/Webkit
rm -rf ~/Library/Caches/pip
rm -rf ~/Library/Caches/yarn
rm -rf ~/Library/Caches/Homebrew
rm -rf ~/Library/Logs/*
echo "清理完成"
```

### 2. 监控脚本

```bash
# 每日检查系统状态
#!/bin/bash
echo "=== 系统健康检查 $(date) ==="
uptime
top -l 1 | grep PhysMem
df -h / | grep -E "Filesystem|/$"
```

### 3. 自动化工具

- 使用 OpenClaw 的 `power-monitor.sh` 进行功耗和系统监控
- 设置 crontab 定期执行清理脚本

---

## 🚫 避免的操作

### 1. 危险的清理操作

```bash
# ❌ 不要删除以下目录
~/Library/Caches/              # 整个缓存目录
~/Library/Application Support/ # 应用支持文件
~/Library/Preferences/         # 应用偏好设置

# ❌ 不要强制清理系统进程
sudo killall -9 WindowServer   # 会导致重启
```

### 2. 不推荐的优化软件

- 避免使用"内存清理"软件（macOS 会自动管理内存）
- 避免使用"系统加速"软件（可能造成系统不稳定）

---

## 📚 相关资源

### macOS 系统文档
- [Activity Monitor User Guide](https://support.apple.com/guide/activity-monitor/welcome/mac)
- [macOS Memory Management](https://developer.apple.com/library/archive/documentation/Performance/Conceptual/ManagingMemory/)

### 命令参考
- `man ps` - 进程状态
- `man top` - 系统监控
- `man killall` - 进程管理
- `man du` - 磁盘使用

---

## 💡 最佳实践

### 1. 轻量化原则
- 使用轻量级应用替代重量级应用
- 关闭不必要的启动项
- 定期清理不用的应用

### 2. 监控优先
- 定期检查系统负载
- 关注内存使用趋势
- 及时处理异常进程

### 3. 预防为主
- 定期维护胜过紧急修复
- 建立自动化监控
- 保留系统日志用于分析

---

_创建时间: 2026-03-30_  
_适用版本: macOS Monterey (12.x)_  
_测试环境: MacBook Air (2017, 8GB RAM)_
