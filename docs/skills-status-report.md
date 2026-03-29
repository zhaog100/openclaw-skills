# 本地技能状态报告

> 生成时间：2026-03-09 18:14
> 官家请求查看所有技能状态

---

## 📊 技能总览

| # | 技能名称 | 版本 | 描述 | 发布状态 |
|---|---------|------|------|---------|
| 1 | **image-content-extractor** | v2.0.0 | 统一图片内容提取技能 | ✅ 已发布 |
| 2 | **miliger-context-manager** | v2.2.2 | 上下文管理 | ⚠️ 远程v7.0.0 |
| 3 | **miliger-qmd-manager** | v1.0.0 | QMD知识库管理 | ❓ 未确认 |
| 4 | **playwright-scraper** | v1.1.0 | Playwright网页爬取 | ❓ 未确认 |
| 5 | **quote-reader** | v1.1.0 | 引用前文内容读取 | ✅ 已发布 |
| 6 | **smart-memory-sync** | v1.0.0 | 智能记忆管理 | ✅ 已发布 |
| 7 | **smart-model-switch** | v1.3.0 | 智能模型切换 | ✅ 已发布 |

---

## ✅ 已发布到ClawHub（5个）

### 1. miliger-context-manager v2.2.2
```
状态: ⚠️ 版本冲突
本地: v2.2.2
远程: v7.0.0
发布ID: k9720rgtq7nytyjgyzx6sbgg0n82cxf9
功能: 真实API监控 + 60%阈值 + 5分钟间隔
```

### 2. smart-model-switch v1.3.0
```
状态: ✅ 同步
发布ID: k97383tnwydej4c1ntcbfkdhws82amgg
功能: 消息复杂度分析 + 6种模型 + AI主动检测
```

### 3. quote-reader v1.1.0
```
状态: ✅ 同步
发布ID: k9789dbamh0bv6yb0hecgwd2kn82bqzt
功能: 引用识别 + 历史检索 + 6种意图
```

### 4. smart-memory-sync v1.0.0
```
状态: ✅ 同步
发布ID: k9791azgxkhtf9r8sfy08g5bkd82dzws
功能: 三库同步 + 主动切换 + 双保险
```

### 5. image-content-extractor v2.0.0
```
状态: ✅ 同步
发布ID: k97dazj7a3ywc4syne4kn3r83d82cz35
功能: terminal-ocr集成 + 三大模式
```

---

## ❓ 待确认发布状态（2个）

### 6. miliger-qmd-manager v1.0.0
```
状态: ❓ 未确认
本地版本: v1.0.0
目录: miliger-qmd-manager
功能: QMD知识库管理 + 项目管理/测试/内容创作
待办: 检查是否已发布到ClawHub
```

### 7. playwright-scraper v1.1.0
```
状态: ❓ 未确认
本地版本: v1.1.0
目录: miliger-playwright-scraper
功能: Playwright网页爬取 + 真实浏览器 + SPA支持
待办: 检查是否已发布到ClawHub
```

---

## 📁 其他目录

### 已归档
```
_archived/ - 旧版本归档
  - context-manager-v1.0
  - context-manager-v2.0
  - 其他历史版本
```

### 数据目录
```
data/ - 数据文件
```

### 搜索技能
```
find-skills/ - 技能搜索工具
```

### 其他技能
```
automation-workflows/ - 自动化工作流
playwright/ - Playwright原始版本
qmd/ - QMD原始版本
quote-reader/ - 已发布
smart-memory-sync/ - 已发布
smart-model-switch/ - 已发布
speech-recognition/ - 语音识别（未检查）
```

---

## 📊 统计摘要

| 状态 | 数量 | 占比 |
|------|------|------|
| ✅ 已发布（同步） | 4 | 57% |
| ⚠️ 已发布（冲突） | 1 | 14% |
| ❓ 待确认 | 2 | 29% |
| **总计** | **7** | **100%** |

---

## 🎯 下一步行动

### 立即行动

1. **检查未确认技能**
   ```bash
   # 搜索ClawHub
   clawnet search miliger-qmd-manager
   clawnet search playwright-scraper
   ```

2. **决定版本同步**
   - miliger-context-manager: 等待API恢复后对比v7.0.0

### 后续行动

1. **发布未确认技能**（如果未发布）
   ```bash
   # 打包
   ~/.openclaw/workspace/tools/pack-skill.sh miliger-qmd-manager
   ~/.openclaw/workspace/tools/pack-skill.sh miliger-playwright-scraper
   
   # 发布
   https://clawhub.ai/publish
   ```

2. **更新记忆库**
   - 记录所有发布状态
   - 更新版本号

---

## 🔄 API状态

```
后台进程: 运行中（PID 4526）
预计完成: 18:14
等待时间: 还剩约30秒
```

---

## 💡 推荐优先级

### 🔴 高优先级
1. ✅ 解决context-manager版本冲突
2. ⏸️ 等待API恢复

### 🟡 中优先级
1. 检查qmd-manager发布状态
2. 检查playwright-scraper发布状态

### 🟢 低优先级
1. 整理其他技能目录
2. 清理归档文件

---

*生成时间: 2026-03-09 18:14*
*总计: 7个技能 + 多个归档*
