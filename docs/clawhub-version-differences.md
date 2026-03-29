# ClawHub 技能版本差异对比报告

> 生成时间：2026-03-09 18:02
> 对比范围：本地技能 vs ClawHub远程版本

---

## 📊 本地技能清单

| # | 技能名称 | 本地版本 | 本地目录 | 状态 |
|---|---------|---------|---------|------|
| 1 | image-content-extractor | v2.0.0 | image-content-extractor | ✅ |
| 2 | miliger-context-manager | v2.2.2 | context-manager-v2 | ⚠️ |
| 3 | miliger-qmd-manager | v1.0.0 | miliger-qmd-manager | ❓ |
| 4 | playwright-scraper | v1.1.0 | miliger-playwright-scraper | ❓ |
| 5 | quote-reader | v1.1.0 | quote-reader | ✅ |
| 6 | smart-memory-sync | v1.0.0 | smart-memory-sync | ✅ |
| 7 | smart-model-switch | v1.3.0 | smart-model-switch | ✅ |

**总计：7个本地技能**

---

## 🔍 已确认的版本差异

### ⚠️ 1. miliger-context-manager

| 项目 | 本地 | 远程 | 差异 |
|------|------|------|------|
| **版本** | v2.2.2 | **v7.0.0** | ⚠️ **相差4.7个版本！** |
| **所有者** | - | zhaog100 | ✅ 你的账号 |
| **平台** | 本地 | clawhub.ai | - |
| **URL** | - | https://clawhub.ai/zhaog100/miliger-context-manager | ✅ |

**状态：** 🔴 **重大差异 - 需要立即处理**

**可能原因：**
- 你在其他设备上发布了v3.0-v7.0版本
- 版本管理不一致
- 存在未同步的更新

**建议行动：**
1. 访问远程页面查看v7.0.0详情
2. 决定同步方向（下载远程/上传本地）
3. 避免版本冲突

---

### ✅ 2. quote-reader

| 项目 | 本地 | 远程（记忆） | 状态 |
|------|------|------------|------|
| **版本** | v1.1.0 | v1.1.0 | ✅ **一致** |
| **发布ID** | - | k9789dbamh0bv6yb0hecgwd2kn82bqzt | ✅ |
| **发布日期** | - | 2026-03-05 | ✅ |

**状态：** ✅ **无差异 - 版本同步**

---

### ✅ 3. smart-memory-sync

| 项目 | 本地 | 远程（记忆） | 状态 |
|------|------|------------|------|
| **版本** | v1.0.0 | v1.0.0 | ✅ **一致** |
| **发布ID** | - | k9791azgxkhtf9r8sfy08g5bkd82dzws | ✅ |
| **发布日期** | - | 2026-03-06 | ✅ |

**状态：** ✅ **无差异 - 版本同步**

---

### ✅ 4. smart-model-switch

| 项目 | 本地 | 远程（记忆） | 状态 |
|------|------|------------|------|
| **版本** | v1.3.0 | v1.3.0 | ✅ **一致** |
| **发布ID** | - | k97383tnwydej4c1ntcbfkdhws82amgg | ✅ |
| **发布日期** | - | 2026-03-05 | ✅ |

**状态：** ✅ **无差异 - 版本同步**

---

### ✅ 5. image-content-extractor

| 项目 | 本地 | 远程（记忆） | 状态 |
|------|------|------------|------|
| **版本** | v2.0.0 | v2.0.0 | ✅ **一致** |
| **发布ID** | - | k97dazj7a3ywc4syne4kn3r83d82cz35 | ✅ |
| **发布日期** | - | 2026-03-06 | ✅ |

**状态：** ✅ **无差异 - 版本同步**

---

## ❓ 待检查的技能

以下技能存在于本地，但无法确认远程状态：

### 6. miliger-qmd-manager

- **本地版本：** v1.0.0
- **远程状态：** ❓ 未知（未在记忆中找到发布记录）
- **可能状态：** 未发布 或 使用不同名称

### 7. playwright-scraper

- **本地版本：** v1.1.0
- **远程状态：** ❓ 未知
- **可能状态：** 未发布 或 使用不同名称

---

## 📊 版本差异统计

| 状态 | 数量 | 技能 |
|------|------|------|
| 🔴 **重大差异** | 1 | miliger-context-manager (2.2.2 → 7.0.0) |
| ✅ **版本同步** | 4 | quote-reader, smart-memory-sync, smart-model-switch, image-content-extractor |
| ❓ **待检查** | 2 | miliger-qmd-manager, playwright-scraper |

---

## 🚨 需要立即处理

### 🔴 miliger-context-manager

**优先级：** 🔥🔥🔥 **最高**

**行动清单：**
1. [ ] 访问 https://clawhub.ai/zhaog100/miliger-context-manager
2. [ ] 查看v7.0.0更新日志
3. [ ] 决定同步策略：
   - **方案A：** 下载远程v7.0.0替换本地
   - **方案B：** 发布本地v2.2.2为v7.0.1（需先合并远程更新）
   - **方案C：** 发布本地v2.2.2为v8.0.0（跳过v7.x）

---

## 📋 待办事项

### 立即行动

- [ ] **检查远程版本** - 访问ClawHub查看详情
- [ ] **同步版本** - 解决miliger-context-manager版本冲突
- [ ] **更新文档** - 记录最终版本状态

### 后续行动

- [ ] **检查未发布技能** - 确认qmd-manager和playwright-scraper状态
- [ ] **建立版本管理规范** - 避免未来版本冲突
- [ ] **定期同步** - 建立本地-远程同步机制

---

## 🔧 快速命令

### 查看本地版本
```bash
cd ~/.openclaw/workspace/skills/context-manager-v2
cat package.json | grep version
```

### 打包本地版本
```bash
~/.openclaw/workspace/tools/pack-skill.sh context-manager-v2
```

### 访问远程版本
```
https://clawhub.ai/zhaog100/miliger-context-manager
```

---

## 📝 版本历史参考

### Context Manager 版本演进（推测）

```
v1.0.0  → 手动切换
v2.0.0  → 自动切换
v2.1.0  → 启动优化
v2.2.0  → 真实API监控
v2.2.1  → Cron环境修复
v2.2.2  → 阈值优化（60%）[本地版本]
???     → v3.0-v6.0 未知更新
v7.0.0  → 最新版本 [远程版本]
```

---

## ⚠️ 重要提醒

**版本冲突风险：**
- 如果直接发布本地v2.2.2，可能覆盖远程v7.0.0
- 建议先查看远程版本再决定
- 确保不会丢失重要更新

**API限流：**
- ClawHub API当前处于限流状态
- 需要等待约1分钟后重试
- 或使用网站手动查看

---

*报告生成时间: 2026-03-09 18:02*
*总计: 7个本地技能*
*差异: 1个重大差异 + 2个待检查*
