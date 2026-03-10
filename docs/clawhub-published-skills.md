# ClawHub 已发布技能列表

> 从 MEMORY.md 和本地技能目录提取

---

## 📊 你在 ClawHub 上发布的技能

### 1. **miliger-context-manager**
- **版本**: v2.2.2
- **发布ID**: k9720rgtq7nytyjgyzx6sbgg0n82cxf9
- **发布日期**: 2026-03-06
- **描述**: 真实API监控 + 启动优化 + 无感会话切换
- **功能**:
  - 调用OpenClaw API获取准确上下文
  - 60%阈值+5分钟间隔
  - 飞书通知
  - 分层读取（核心<5KB + 摘要<10KB）

---

### 2. **smart-model-switch**
- **版本**: v1.3.0
- **发布ID**: k97383tnwydej4c1ntcbfkdhws82amgg
- **发布日期**: 2026-03-05
- **描述**: 智能模型自动切换技能
- **功能**:
  - 消息复杂度分析（4维度评分）
  - 智能模型选择（6种模型）
  - 上下文监控切换
  - AI主动检测机制

---

### 3. **smart-memory-sync**
- **版本**: v1.0.0
- **发布ID**: k9791azgxkhtf9r8sfy08g5bkd82dzws
- **发布日期**: 2026-03-06
- **描述**: 主动智能记忆管理技能
- **功能**:
  - 实时分析聊天
  - 三库同步（MEMORY+QMD+Git）
  - 主动切换
  - 预防性保护

---

### 4. **quote-reader**
- **版本**: v1.1.0
- **发布ID**: k9789dbamh0bv6yb0hecgwd2kn82bqzt
- **发布日期**: 2026-03-05
- **描述**: 引用前文内容读取技能
- **功能**:
  - 智能引用识别
  - 历史检索
  - 智能理解（6种引用意图）
  - AI集成（静默模式）

---

### 5. **image-content-extractor**
- **版本**: v2.0.0
- **发布ID**: k97dazj7a3ywc4syne4kn3r83d82cz35
- **发布日期**: 2026-03-06
- **描述**: 统一图片内容提取技能
- **功能**:
  - 集成terminal-ocr
  - 三大模式（终端/文档/通用）
  - 智能检测
  - 自动提取内容生成Markdown

---

## 📊 统计

| 指标 | 数值 |
|------|------|
| **已发布技能数** | 5个 |
| **最新版本** | v2.2.2 (context-manager) |
| **首次发布** | 2026-03-05 |
| **最近发布** | 2026-03-06 |
| **发布平台** | clawhub.ai |

---

## 📋 本地待发布技能

以下技能存在于本地，但可能未发布到 ClawHub：

1. **miliger-qmd-manager** v1.0.0
2. **playwright-scraper** v1.1.0
3. **speech-recognition** (版本未知)
4. **automation-workflows**
5. **find-skills**

---

## 🚀 下一步

**发布新技能：**
```bash
# 打包技能
~/.openclaw/workspace/tools/pack-skill.sh <skill-name>

# 访问发布页面
https://clawhub.ai/publish

# 上传 .tar.gz 文件
```

**更新现有技能：**
1. 修改版本号（package.json）
2. 重新打包
3. 上传新版本

---

## ⚠️ 注意事项

- **文件大小限制**: 20MB
- **命名规范**: 使用 `miliger-` 前缀
- **版本格式**: x.y.z
- **必需文件**: SKILL.md, package.json

---

*最后更新: 2026-03-09*
*总计: 5个已发布技能*
