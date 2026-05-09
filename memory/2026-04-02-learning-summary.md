# 2026-04-02 学习总结

_生成时间: 2026-04-02 15:21 CST_

---

## 📚 今日学到的 3 个新知识点

### 1️⃣ **OpenClaw 配置结构 - exec 字段位置**

**问题**: 一开始把 `exec` 放在根级别导致配置错误
```json
❌ 错误: {"exec": {...}, "meta": {...}}
✅ 正确: {"meta": {...}, "tools": {"exec": {...}}}
```

**教训**:
- OpenClaw 配置有严格的结构要求
- `exec` 必须放在 `tools.exec` 下
- 配置错误会导致 Gateway 无法启动

**应用场景**: 以后修改配置时，先查看官方文档或现有配置结构

---

### 2️⃣ **防火墙规则优先级 - allow 在 deny 之前**

**配置顺序很重要**:
```bash
✅ 正确顺序:
1. ufw allow from 127.0.0.1 to any port 25
2. ufw deny 25

❌ 错误顺序（会导致完全拒绝）:
1. ufw deny 25
2. ufw allow from 127.0.0.1 to any port 25
```

**教训**:
- UFW 规则从上到下匹配，先匹配的生效
- allow 规则必须在 deny 之前
- 每次修改后要验证规则顺序

**应用场景**: 以后配置防火墙时，先添加 allow 规则，再添加 deny 规则

---

### 3️⃣ **Gateway 重启会触发 doctor - 配置可能被重置**

**发现**: Gateway 重启时运行了 `doctor` 命令，导致配置被重置

**现象**:
```
[restart] Running doctor...
Config warnings: ...
```

**教训**:
- Gateway 重启不是简单的重启
- `doctor` 会检查并可能修改配置
- 重要配置修改后要立即重启验证

**解决方案**:
- 修改配置后立即重启验证
- 如果配置被重置，重新添加配置并再次重启
- 第二次重启时 `doctor` 不会再运行

**应用场景**: 以后修改重要配置时，准备好两次重启的策略

---

## 🔧 今日掌握的技能

### 1. **多实例配置同步**

**流程**:
```bash
# 1. 修改本地配置
jq '.tools.exec = {...}' config.json > tmp.json

# 2. 同步到 Docker 容器
docker cp tmp.json container:/path/config.json

# 3. 验证配置
docker exec container cat config.json | jq '.tools.exec'

# 4. 重启容器
docker restart container
```

**注意事项**:
- 使用 `jq` 确保 JSON 格式正确
- 先验证再重启
- 重启后检查日志确认成功

---

### 2. **QQ Bot Token 更新流程**

**完整流程**:
```bash
# 1. 获取新 Token（用户在 QQ 开放平台申请）
# 2. 更新配置文件
jq '.channels.qqbot.clientSecret = "NEW_TOKEN"' config.json > tmp.json

# 3. 应用配置
mv tmp.json config.json

# 4. 重启服务
openclaw gateway restart

# 5. 验证连接
docker logs container --tail 20 | grep -i "qqbot.*ready"
```

**关键指标**:
- `Access token obtained successfully`
- `WebSocket connected`
- `Gateway ready`

---

## 📊 今日工作数据

| 指标 | 数值 |
|------|------|
| **工作时长** | 6 小时 |
| **Git 提交** | 5 次 |
| **配置修改** | 3 个文件 |
| **实例同步** | 2 个 |
| **QQ Bot 更新** | 2 个 |
| **防火墙规则** | 6 条 |
| **PR 监控** | 8 个 |

---

## 💡 明日改进方向

1. **早间学习**: 暂停 AI 资讯搜集（待第一桶金后配置 Perplexity）
2. **午间回顾**: 继续保持，添加 PR 状态检查
3. **晚间学习**: 总结知识点并更新长期记忆
4. **自动化**: Bounty 监控（每 30 分钟）+ 每日维护（凌晨 2:00）

---

_生成时间: 2026-04-02 15:21 CST_
