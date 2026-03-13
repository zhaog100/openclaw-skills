# Session-Memory Enhanced v3.3.0 - 实时监控版

**发布时间**：2026-03-07 22:14
**版本**：v3.3.0
**作者**：小米辣

---

## 🎯 核心功能（v3.3.0）

### ⭐ 实时监控 ⭐⭐⭐⭐⭐

**功能**：
1. 使用 inotify 监听文件变化
2. 实时触发记忆固化
3. 不再依赖 crontab

**优势**：
- ⚡ **更及时**：文件变化立即响应
- 🎯 **更精准**：只在需要时触发
- 💾 **更省资源**：不浪费 CPU 轮询

---

## 🚀 使用方式

### 方式1：前台运行（测试）

```bash
# main 代理
bash memory-watcher.sh

# research 代理
AGENT_NAME=research bash memory-watcher.sh
```

### 方式2：后台运行

```bash
# main 代理
nohup bash memory-watcher.sh > /dev/null 2>&1 &

# research 代理
AGENT_NAME=research nohup bash memory-watcher.sh > /dev/null 2>&1 &
```

### 方式3：systemd 服务（推荐）

```bash
# 1. 复制服务文件
sudo cp config/systemd/memory-watcher@.service /etc/systemd/system/

# 2. 重载 systemd
sudo systemctl daemon-reload

# 3. 启动服务（main 代理）
sudo systemctl start memory-watcher@main

# 4. 设置开机自启
sudo systemctl enable memory-watcher@main

# 5. 查看状态
sudo systemctl status memory-watcher@main

# 6. 查看日志
sudo journalctl -u memory-watcher@main -f
```

---

## 📊 双模式支持

### 模式1：inotify 监控（推荐）

**特点**：
- ✅ 实时响应（文件变化立即触发）
- ✅ 资源占用低
- ✅ 精准触发

**依赖**：
- inotify-tools

### 模式2：轮询模式（备用）

**特点**：
- ✅ 无需额外依赖
- ⏱️ 每5分钟检查一次
- ⚠️ 资源占用稍高

**触发条件**：
- inotify-tools 未安装时自动切换

---

## 📁 文件结构

```
/root/.openclaw/workspace/
├── skills/session-memory-enhanced/
│   └── scripts/
│       ├── memory-watcher.sh          # ⭐ 实时监控脚本
│       ├── session-memory-enhanced-v3.2.sh
│       └── ...
├── config/systemd/
│   └── memory-watcher@.service        # ⭐ systemd 服务
└── logs/
    └── memory-watcher.log             # ⭐ 监控日志
```

---

## 🔍 监控逻辑

```
启动监控
    ↓
检查 inotify-tools
    ├─ 已安装 → inotify 模式 ⭐
    └─ 未安装 → 轮询模式
    ↓
监听文件变化
    ↓
检测到变化 → 检查固化条件
    ├─ 消息数 >= 60 → 触发固化
    └─ 闲置时间 >= 30分钟 → 触发固化
    ↓
调用 session-memory-enhanced
    ↓
完成更新
```

---

## 💡 技术亮点

### 1. 自动降级
- inotify-tools 未安装 → 自动切换到轮询模式
- 无需手动干预

### 2. 多代理支持
- 每个代理独立监控
- 互不干扰

### 3. 日志记录
- 详细记录所有操作
- 便于调试和监控

---

## 📊 对比 crontab

| 特性 | crontab | 实时监控（v3.3.0）|
|------|---------|-----------------|
| 响应速度 | 1小时 | 实时 ⭐ |
| 精准度 | 固定时间 | 按需触发 ⭐ |
| 资源占用 | 低 | 极低 ⭐ |
| 依赖 | 无 | inotify-tools（可选）|

---

## 🎯 测试步骤

### 测试1：检查 inotify-tools

```bash
# 检查是否安装
command -v inotifywait && echo "已安装" || echo "未安装"

# 安装（如果需要）
yum install -y inotify-tools  # CentOS/RHEL
apt-get install -y inotify-tools  # Ubuntu/Debian
```

### 测试2：启动监控

```bash
# 前台运行（查看日志输出）
bash memory-watcher.sh

# 在另一个终端创建测试文件
echo '{"messages":[]}' > /root/.openclaw/workspace/memory/agents/main/.tail.tmp.json

# 观察监控日志
tail -f /root/.openclaw/workspace/logs/memory-watcher.log
```

### 测试3：触发固化

```bash
# 创建超过60条消息的测试文件
# （略）

# 观察是否触发固化
```

---

## 🚀 未来优化

### v3.3.1
- [ ] 多文件同时监控
- [ ] 智能休眠（低活跃时降低检查频率）
- [ ] 自动重启（异常退出时）

### v3.4.0
- [ ] 自动推送远程 Git
- [ ] 智能压缩历史提交
- [ ] 跨代理知识迁移

---

**版本历史**：
- v3.3.0 (2026-03-07)：实时监控（inotify）⭐⭐⭐⭐⭐
- v3.2.0 (2026-03-07)：AI 摘要系统
- v3.1.0 (2026-03-07)：多代理支持
- v3.0.0 (2026-03-07)：不可变分片 + 会话清洗
- v2.1.0 (2026-03-07)：向量生成
- v2.0.0 (2026-03-07)：三位一体
- v1.0.0 (2026-03-07)：基础功能

---

**测试状态**：✅ **脚本已创建**

**核心功能**：
- ✅ inotify 实时监控
- ✅ 轮询模式（备用）
- ✅ 多代理支持
- ✅ systemd 服务

**下一步**：测试实时监控功能
