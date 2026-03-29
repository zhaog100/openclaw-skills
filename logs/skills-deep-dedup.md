# 技能深度去重分析报告

生成时间：2026-03-06 19:00:17

## 📊 技能总览

**总技能数**：13

## 🔍 功能分析

### agent-browser
**描述**：description: A fast Rust-based headless browser automation CLI with Node.js fallback that enables AI agents to navigate, click, type, and snapshot pages via structured commands. 

**工具**：description: A fast Rust-based headless browser automation CLI with Node.js fallback that enables AI agents to navigate, click, type, and snapshot pages via structured commands. allowed-tools: Bash(agent-browser:*) ```bash ```bash ```bash 

**依赖**：metadata: {"clawdbot":{"emoji":"🌐","requires":{"bins":["node","npm"]}}} ## Installation npm install -g agent-browser agent-browser install agent-browser install --with-deps 

---

### find-skills
**描述**：description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill. 

**工具**：description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill. - Wants to search for tools, templates, or workflows The Skills CLI (`npx skills`) is the package manager for the open agent skills ecosystem. Skills are modular packages that extend agent capabilities with specialized knowledge, workflows, and tools. **Key commands:** Run the find command with a relevant query: 

**依赖**：description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill. This skill helps you discover and install skills from the open agent skills ecosystem. - `npx skills add <package>` - Install a skill from GitHub or other sources - `npx skills update` - Update all installed skills Install with npx skills add <owner/repo@skill> 

---

### github
**描述**：description: "Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api` for issues, PRs, CI runs, and advanced queries." 

**工具**：description: "Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api` for issues, PRs, CI runs, and advanced queries." ```bash ```bash ```bash ```bash 

**依赖**：

---

### miliger-context-manager
**描述**：description: Auto context management with seamless session switching. Monitors usage, triggers at 85% threshold, automatically creates new session with loaded memory. Zero user intervention required. Trigger on "context", "memory", "session management", "context limit", "memory transfer". ### ⭐ 启动优化（v2.1新功能）⭐⭐⭐⭐⭐ ### ⭐ 无感自动切换（v2.0功能） ### 📊 智能监控（v2.2新功能）⭐⭐⭐⭐⭐ - ✅ 手动提醒功能 

**工具**：description: Auto context management with seamless session switching. Monitors usage, triggers at 85% threshold, automatically creates new session with loaded memory. Zero user intervention required. Trigger on "context", "memory", "session management", "context limit", "memory transfer". ```bash bash install.sh ```bash */10 * * * * ~/.openclaw/skills/context-manager/scripts/seamless-switch.sh 

**依赖**：description: Auto context management with seamless session switching. Monitors usage, triggers at 85% threshold, automatically creates new session with loaded memory. Zero user intervention required. Trigger on "context", "memory", "session management", "context limit", "memory transfer". clawhub install miliger-context-manager bash install.sh 

---

### notion
**描述**：description: Notion API for creating and managing pages, databases, and blocks. 

**工具**：description: Notion API for creating and managing pages, databases, and blocks. ```bash ```bash ```bash ```bash 

**依赖**：> **Note:** The `Notion-Version` header is required. This skill uses `2025-09-03` (latest). In this version, databases are called "data sources" in the API. 

---

### obsidian
**描述**：description: Work with Obsidian vaults (plain Markdown notes) and automate via obsidian-cli. 

**工具**：description: Work with Obsidian vaults (plain Markdown notes) and automate via obsidian-cli. - Config: `.obsidian/` (workspace + plugin settings; usually don’t touch from scripts) - Avoid writing hardcoded vault paths into scripts; prefer reading the config or using `print-default`. 

**依赖**：metadata: {"clawdbot":{"emoji":"💎","requires":{"bins":["obsidian-cli"]},"install":[{"id":"brew","kind":"brew","formula":"yakitrak/yakitrak/obsidian-cli","bins":["obsidian-cli"],"label":"Install obsidian-cli (brew)"}]}} - Requires Obsidian URI handler (`obsidian://…`) working (Obsidian installed). 

---

### playwright-scraper
**描述**：description: Playwright网页爬取技能。使用真实浏览器操作（点击、滚动、等待JS渲染）来爬取复杂动态网页。支持多Tab、懒加载、SPA单页应用。适用于会议议程、展会信息等公开信息型网站。 ## 功能概述 ### 核心能力 

**工具**：description: Playwright网页爬取技能。使用真实浏览器操作（点击、滚动、等待JS渲染）来爬取复杂动态网页。支持多Tab、懒加载、SPA单页应用。适用于会议议程、展会信息等公开信息型网站。 - ✅ **SPA单页应用** - JavaScript异步加载 ```javascript ```javascript ```javascript 

**依赖**：const { chromium } = require('playwright'); npm install playwright npx playwright install chromium 

---

### qmd-manager
**描述**：## 🎯 主要功能 ## 🎨 特色功能 

**工具**：```bash 

**依赖**：1. 安装 QMD 二进制文件：`brew install oven-sh/bun/bun && bun i -g https://github.com/tobi/qmd` 

---

### summarize
**描述**：description: Summarize URLs or files with the summarize CLI (web, PDFs, images, audio, YouTube). 

**工具**：description: Summarize URLs or files with the summarize CLI (web, PDFs, images, audio, YouTube). ```bash 

**依赖**：metadata: {"clawdbot":{"emoji":"🧾","requires":{"bins":["summarize"]},"install":[{"id":"brew","kind":"brew","formula":"steipete/tap/summarize","bins":["summarize"],"label":"Install summarize (brew)"}]}} 

---

### tavily-search
**描述**：description: AI-optimized web search via Tavily API. Returns concise, relevant results for AI agents. 

**工具**：description: AI-optimized web search via Tavily API. Returns concise, relevant results for AI agents. ```bash node {baseDir}/scripts/search.mjs "query" node {baseDir}/scripts/search.mjs "query" -n 10 node {baseDir}/scripts/search.mjs "query" --deep 

**依赖**：metadata: {"clawdbot":{"emoji":"🔍","requires":{"bins":["node"],"env":["TAVILY_API_KEY"]},"primaryEnv":"TAVILY_API_KEY"}} 

---

### tencentcloud-lighthouse-skill
**描述**：description: Manage Tencent Cloud Lighthouse (轻量应用服务器) — auto-setup mcporter + MCP, query instances, monitoring & alerting, self-diagnostics, firewall, snapshots, remote command execution (TAT). Use when user asks about Lighthouse or 轻量应用服务器. NOT for CVM or other cloud server types. 

**工具**：description: Manage Tencent Cloud Lighthouse (轻量应用服务器) — auto-setup mcporter + MCP, query instances, monitoring & alerting, self-diagnostics, firewall, snapshots, remote command execution (TAT). Use when user asks about Lighthouse or 轻量应用服务器. NOT for CVM or other cloud server types. ```bash {baseDir}/scripts/setup.sh --check-only ```bash {baseDir}/scripts/setup.sh --secret-id "<用户提供的SecretId>" --secret-key "<用户提供的SecretKey>" 

**依赖**：        "requires": {},         "install":               "label": "Install mcporter (MCP CLI)", 

---

### weather
**描述**：description: Get current weather and forecasts (no API key required). 

**工具**：description: Get current weather and forecasts (no API key required). ```bash ```bash ```bash ```bash 

**依赖**：description: Get current weather and forecasts (no API key required). metadata: {"clawdbot":{"emoji":"🌤️","requires":{"bins":["curl"]}}} 

---

### wool-gathering
**描述**：description: "薅羊毛综合技能 - 自动签到、价格监控、优惠券推送。支持阿里云盘、百度网盘、B站、爱奇艺、京东等平台。包括青龙面板部署、dailycheckin配置、价格爬虫开发。当用户提到：薅羊毛、自动签到、价格监控、京东京豆、淘宝淘金币、优惠券推送、青龙面板、dailycheckin时使用此技能。" 自动化省钱赚钱工具集，包括自动签到、价格监控、优惠券推送等功能。 ## 🎯 核心功能 | 平台 | 功能 | 状态 | 收益 | | 平台 | 功能 | 状态 | 风险 | 

**工具**：description: "薅羊毛综合技能 - 自动签到、价格监控、优惠券推送。支持阿里云盘、百度网盘、B站、爱奇艺、京东等平台。包括青龙面板部署、dailycheckin配置、价格爬虫开发。当用户提到：薅羊毛、自动签到、价格监控、京东京豆、淘宝淘金币、优惠券推送、青龙面板、dailycheckin时使用此技能。" ├── scripts/ (可执行脚本) 1. 运行 `scripts/price_monitor.py` 2. 配置 `scripts/coupon_fetcher.py` ```bash 

**依赖**：

---

## 🔄 重复功能检测

### cloud 类功能

**匹配技能**（2个）： tencentcloud-lighthouse-skill wool-gathering

**tencentcloud-lighthouse-skill**：
description: Manage Tencent Cloud Lighthouse (轻量应用服务器) — auto-setup mcporter + MCP, query instances, monitoring & alerting, self-diagnostics, firewall, snapshots, remote command execution (TAT). Use when user asks about Lighthouse or 轻量应用服务器. NOT for CVM or other cloud server types.

**wool-gathering**：
description: "薅羊毛综合技能 - 自动签到、价格监控、优惠券推送。支持阿里云盘、百度网盘、B站、爱奇艺、京东等平台。包括青龙面板部署、dailycheckin配置、价格爬虫开发。当用户提到：薅羊毛、自动签到、价格监控、京东京豆、淘宝淘金币、优惠券推送、青龙面板、dailycheckin时使用此技能。"
## 🎯 核心功能

---

### github 类功能

**匹配技能**（4个）： github obsidian find-skills wool-gathering

**github**：
description: "Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api` for issues, PRs, CI runs, and advanced queries."

**obsidian**：
description: Work with Obsidian vaults (plain Markdown notes) and automate via obsidian-cli.

**find-skills**：
description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.

**wool-gathering**：
description: "薅羊毛综合技能 - 自动签到、价格监控、优惠券推送。支持阿里云盘、百度网盘、B站、爱奇艺、京东等平台。包括青龙面板部署、dailycheckin配置、价格爬虫开发。当用户提到：薅羊毛、自动签到、价格监控、京东京豆、淘宝淘金币、优惠券推送、青龙面板、dailycheckin时使用此技能。"
## 🎯 核心功能

---

### knowledge 类功能

**匹配技能**（2个）： find-skills miliger-context-manager

**find-skills**：
description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.

**miliger-context-manager**：
description: Auto context management with seamless session switching. Monitors usage, triggers at 85% threshold, automatically creates new session with loaded memory. Zero user intervention required. Trigger on "context", "memory", "session management", "context limit", "memory transfer".

---

### browser 类功能

**匹配技能**（3个）： agent-browser wool-gathering playwright-scraper

**agent-browser**：
description: A fast Rust-based headless browser automation CLI with Node.js fallback that enables AI agents to navigate, click, type, and snapshot pages via structured commands.

**wool-gathering**：
description: "薅羊毛综合技能 - 自动签到、价格监控、优惠券推送。支持阿里云盘、百度网盘、B站、爱奇艺、京东等平台。包括青龙面板部署、dailycheckin配置、价格爬虫开发。当用户提到：薅羊毛、自动签到、价格监控、京东京豆、淘宝淘金币、优惠券推送、青龙面板、dailycheckin时使用此技能。"
## 🎯 核心功能

**playwright-scraper**：
description: Playwright网页爬取技能。使用真实浏览器操作（点击、滚动、等待JS渲染）来爬取复杂动态网页。支持多Tab、懒加载、SPA单页应用。适用于会议议程、展会信息等公开信息型网站。
### 核心能力

---

### search 类功能

**匹配技能**（3个）： find-skills tencentcloud-lighthouse-skill tavily-search

**find-skills**：
description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.

**tencentcloud-lighthouse-skill**：
description: Manage Tencent Cloud Lighthouse (轻量应用服务器) — auto-setup mcporter + MCP, query instances, monitoring & alerting, self-diagnostics, firewall, snapshots, remote command execution (TAT). Use when user asks about Lighthouse or 轻量应用服务器. NOT for CVM or other cloud server types.

**tavily-search**：
description: AI-optimized web search via Tavily API. Returns concise, relevant results for AI agents.

---

### automation 类功能

**匹配技能**（3个）： agent-browser miliger-context-manager wool-gathering

**agent-browser**：
description: A fast Rust-based headless browser automation CLI with Node.js fallback that enables AI agents to navigate, click, type, and snapshot pages via structured commands.

**miliger-context-manager**：
description: Auto context management with seamless session switching. Monitors usage, triggers at 85% threshold, automatically creates new session with loaded memory. Zero user intervention required. Trigger on "context", "memory", "session management", "context limit", "memory transfer".

**wool-gathering**：
description: "薅羊毛综合技能 - 自动签到、价格监控、优惠券推送。支持阿里云盘、百度网盘、B站、爱奇艺、京东等平台。包括青龙面板部署、dailycheckin配置、价格爬虫开发。当用户提到：薅羊毛、自动签到、价格监控、京东京豆、淘宝淘金币、优惠券推送、青龙面板、dailycheckin时使用此技能。"
## 🎯 核心功能

---

## 💡 合并建议

## 📋 总结

**分析完成时间**：2026-03-06 19:00:17

**总技能数**：13

