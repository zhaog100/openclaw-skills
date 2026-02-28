# OpenClaw Workspace - 米粒儿的工作空间

> 🌾 米粒儿（Mili）- 官家的AI助手精灵

---

## 📖 项目简介

这是OpenClaw AI助手"米粒儿"的工作空间，包含完整的知识库、配置文件和自动化任务系统。

---

## 🎯 核心功能

### 1. 智能知识库
- ✅ QMD精准检索（Token节省92.5%）
- ✅ 22个知识文件
- ✅ BM25关键词搜索（精度70%）

### 2. 多模型支持
- ✅ 27个可用模型
- ✅ DeepSeek系列（7个）
- ✅ AIHubMix系列（14个）
- ✅ 其他系列（6个）

### 3. 自动化任务
- ✅ AIHubMix模型检查（每周一10:00）
- ✅ Playwright安装提醒（每周一10:00）
- ✅ Moltbook互动检查（每周一10:00）
- ✅ 每日回顾与查漏补缺（每天23:50）

### 4. 多搜索引擎
- ✅ 17个搜索引擎集成
- ✅ 国内引擎（8个，100%可用）
- ✅ 国际引擎（9个，33%可用）

### 5. 网页爬取
- ✅ Puppeteer爬虫（替代Playwright）
- ✅ 微信公众号文章爬取
- ✅ JavaScript渲染支持

---

## 📂 目录结构

```
.
├── AGENTS.md              # AI助手配置和行为规范
├── SOUL.md                # 米粒儿的身份和个性
├── USER.md                # 用户信息
├── MEMORY.md              # 长期记忆（精华）
├── HEARTBEAT.md           # 心跳检查任务清单
├── TOOLS.md               # 环境特定配置
│
├── knowledge/             # 知识库（17个文档）
│   ├── project-management/
│   ├── software-testing/
│   ├── content-creation/
│   └── ai-system-design/
│
├── memory/                # 每日记忆
│   ├── 2025-11-19.md
│   ├── 2026-02-26.md
│   └── 2026-02-27.md
│
├── scripts/               # 自动化脚本
│   ├── daily-review.js
│   ├── check-moltbook.js
│   └── scrape-wechat-puppeteer.js
│
├── skills/                # 技能目录
│   └── playwright-scraper/
│
├── config/                # 配置文件
│   └── mcporter.json
│
├── .moltbook/             # Moltbook凭证
│   └── credentials.json
│
└── .clawtasks/            # ClawTasks凭证
    └── config.json
```

---

## 🚀 快速开始

### 1. 检查系统状态
```bash
openclaw status
```

### 2. 查看可用模型
```bash
# 查看配置文件
cat C:\Users\zhaog\.openclaw\openclaw.json
```

### 3. 搜索知识库
```bash
node scripts/check-moltbook.js
```

### 4. 爬取网页
```bash
node scripts/scrape-wechat-puppeteer.js <URL>
```

---

## 🎓 核心配置

### 主力模型
```
aihubmix/gpt-4.1-free（免费、无限制、128K上下文）
```

### DeepSeek系列（7个）
- `deepseek/deepseek-chat`（通用对话）
- `deepseek/deepseek-coder`（编程任务）⭐
- `deepseek/deepseek-reasoner`（复杂推理）⭐
- `qcloudlkeap/deepseek-v3.2`（200K上下文）⭐
- 其他3个

### 其他模型
- `zai/glm-5`（GLM，204K上下文）
- `hunyuan/hunyuan-turbos-latest`（腾讯云）
- 其他AIHubMix免费模型（14个）

---

## 📊 系统统计

- **知识库文件**: 22个
- **可用模型**: 27个
- **定时任务**: 4个
- **搜索引擎**: 17个
- **Token节省**: 92.5%

---

## 🔐 安全配置

- ✅ API Key本地加密存储
- ✅ 凭证文件本地保存
- ✅ 定期配置备份
- ✅ Git版本控制

---

## 📝 最近更新

### 2026-02-28
- ✅ 添加DeepSeek官方API（3个模型）
- ✅ 配置Moltbook自动检查
- ✅ 完成心跳检查系统
- ✅ 系统全面优化

### 2026-02-27
- ✅ Moltbook账户认领
- ✅ ClawTasks账户注册
- ✅ Playwright技能创建
- ✅ AIHubMix模型配置
- ✅ QMD知识库系统上线

---

## 🎯 待办任务

### 官家待办
- ⏳ ClawTasks充值（暂缓，等待需要时）

### 自动执行
- ⏰ AIHubMix检查（每周一10:00）
- ⏰ Playwright提醒（每周一10:00）
- ⏰ Moltbook检查（每周一10:00）
- ⏰ 每日回顾（每天23:50）

---

## 💡 使用建议

### 日常对话
```
aihubmix/gpt-4.1-free（免费）⭐
```

### 编程任务
```
deepseek/deepseek-coder（专业）⭐⭐⭐
```

### 复杂推理
```
deepseek/deepseek-reasoner（官方）⭐⭐⭐
```

### 长文本
```
qcloudlkeap/deepseek-v3.2（200K上下文）⭐⭐⭐
```

---

## 📞 联系方式

- **用户**: 官家（南仲）
- **邮箱**: zhaog100@gmail.com
- **Moltbook**: https://www.moltbook.com/u/miliger

---

## 📄 许可证

本项目为个人工作空间，仅供官家使用。

---

**创建时间**: 2026-02-28
**最后更新**: 2026-02-28
**维护者**: 米粒儿（Mili）🌾
