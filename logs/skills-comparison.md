# 技能对比分析报告

生成时间：2026-03-06 15:08:00

## agent-browser

### 元数据
```
name: Agent Browser
description: A fast Rust-based headless browser automation CLI with Node.js fallback that enables AI agents to navigate, click, type, and snapshot pages via structured commands.
```

### 功能描述（前10行）
```
  - Automating web interactions
  - Extracting structured data from pages
  - Filling forms programmatically
  - Testing web UIs
metadata: {"clawdbot":{"emoji":"🌐","requires":{"bins":["node","npm"]}}}
allowed-tools: Bash(agent-browser:*)
---

# Browser Automation with agent-browser

```

---

## find-skills

### 元数据
```
name: find-skills
description: Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill.
```

### 功能描述（前10行）
```

# Find Skills

This skill helps you discover and install skills from the open agent skills ecosystem.

## When to Use This Skill

Use this skill when the user:

- Asks "how do I do X" where X might be a common task with an existing skill
```

---

## github

### 元数据
```
name: github
description: "Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api` for issues, PRs, CI runs, and advanced queries."
```

### 功能描述（前10行）
```

# GitHub Skill

Use the `gh` CLI to interact with GitHub. Always specify `--repo owner/repo` when not in a git directory, or use URLs directly.

## Pull Requests

Check CI status on a PR:
```bash
gh pr checks 55 --repo owner/repo
```

---

## miliger-context-manager

### 元数据
```
name: context-manager
description: Auto context management with seamless session switching. Monitors usage, triggers at 85% threshold, automatically creates new session with loaded memory. Zero user intervention required. Trigger on "context", "memory", "session management", "context limit", "memory transfer".
```

### 功能描述（前10行）
```

# Context Manager - 无感会话切换版

智能上下文管理技能，自动监控上下文使用率，达到阈值时自动保存记忆并创建新会话，用户完全无感知。

## 🎯 核心特性

### ⭐ 启动优化（v2.1新功能）⭐⭐⭐⭐⭐
- ✅ **分层读取**：核心层<5KB + 摘要层<10KB + 详情QMD检索
- ✅ **启动占用**：从40%+降低到<10%（节省75%空间）
```

---

## notion

### 元数据
```
name: notion
description: Notion API for creating and managing pages, databases, and blocks.
```

### 功能描述（前10行）
```
metadata: {"clawdbot":{"emoji":"📝"}}
---

# notion

Use the Notion API to create/read/update pages, data sources (databases), and blocks.

## Setup

1. Create an integration at https://notion.so/my-integrations
```

---

## obsidian

### 元数据
```
name: obsidian
description: Work with Obsidian vaults (plain Markdown notes) and automate via obsidian-cli.
```

### 功能描述（前10行）
```
metadata: {"clawdbot":{"emoji":"💎","requires":{"bins":["obsidian-cli"]},"install":[{"id":"brew","kind":"brew","formula":"yakitrak/yakitrak/obsidian-cli","bins":["obsidian-cli"],"label":"Install obsidian-cli (brew)"}]}}
---

# Obsidian

Obsidian vault = a normal folder on disk.

Vault structure (typical)
- Notes: `*.md` (plain text Markdown; edit with any editor)
- Config: `.obsidian/` (workspace + plugin settings; usually don’t touch from scripts)
```

---

## playwright-scraper

### 元数据
```
name: playwright-scraper
description: Playwright网页爬取技能。使用真实浏览器操作（点击、滚动、等待JS渲染）来爬取复杂动态网页。支持多Tab、懒加载、SPA单页应用。适用于会议议程、展会信息等公开信息型网站。
```

### 功能描述（前10行）
```

# Playwright 网页爬取技能

## 功能概述

使用Playwright进行真实浏览器操作，爬取复杂动态网页。

### 核心能力
- ✅ **真实浏览器操作** - 点击、滚动、输入、等待
- ✅ **处理复杂SPA** - 单页应用、多Tab、懒加载
```

---

## qmd-manager

### 元数据
```
```

### 功能描述（前10行）
```

## 🎯 主要功能
- **项目管理知识搜索** - 搜索项目管理文档、最佳实践
- **软件测试知识搜索** - 搜索测试方法论、工具使用
- **内容创作知识管理** - 管理公众号、视频号内容
- **本地语义搜索** - 使用 BM25 和向量搜索
- **文档预览和获取** - 查看和加载文档内容

## 🔧 可用工具
- **qmd_search** - 快速关键词搜索
```

---

## summarize

### 元数据
```
name: summarize
description: Summarize URLs or files with the summarize CLI (web, PDFs, images, audio, YouTube).
```

### 功能描述（前10行）
```
metadata: {"clawdbot":{"emoji":"🧾","requires":{"bins":["summarize"]},"install":[{"id":"brew","kind":"brew","formula":"steipete/tap/summarize","bins":["summarize"],"label":"Install summarize (brew)"}]}}
---

# Summarize

Fast CLI to summarize URLs, local files, and YouTube links.

## Quick start

```bash
```

---

## tavily-search

### 元数据
```
name: tavily
description: AI-optimized web search via Tavily API. Returns concise, relevant results for AI agents.
```

### 功能描述（前10行）
```
metadata: {"clawdbot":{"emoji":"🔍","requires":{"bins":["node"],"env":["TAVILY_API_KEY"]},"primaryEnv":"TAVILY_API_KEY"}}
---

# Tavily Search

AI-optimized web search using Tavily API. Designed for AI agents - returns clean, relevant content.

## Search

```bash
```

---

## tencentcloud-lighthouse-skill

### 元数据
```
name: tencentcloud-lighthouse-skill
description: Manage Tencent Cloud Lighthouse (轻量应用服务器) — auto-setup mcporter + MCP, query instances, monitoring & alerting, self-diagnostics, firewall, snapshots, remote command execution (TAT). Use when user asks about Lighthouse or 轻量应用服务器. NOT for CVM or other cloud server types.
```

### 功能描述（前10行）
```
  {
    "openclaw":
      {
        "emoji": "☁️",
        "requires": {},
        "install":
          [
            {
              "id": "node-mcporter",
              "kind": "node",
```

---

## weather

### 元数据
```
name: weather
description: Get current weather and forecasts (no API key required).
```

### 功能描述（前10行）
```
metadata: {"clawdbot":{"emoji":"🌤️","requires":{"bins":["curl"]}}}
---

# Weather

Two free services, no API keys needed.

## wttr.in (primary)

Quick one-liner:
```

---

## wool-gathering

### 元数据
```
name: wool-gathering
description: "薅羊毛综合技能 - 自动签到、价格监控、优惠券推送。支持阿里云盘、百度网盘、B站、爱奇艺、京东等平台。包括青龙面板部署、dailycheckin配置、价格爬虫开发。当用户提到：薅羊毛、自动签到、价格监控、京东京豆、淘宝淘金币、优惠券推送、青龙面板、dailycheckin时使用此技能。"
```

### 功能描述（前10行）
```

# 薅羊毛综合技能

自动化省钱赚钱工具集，包括自动签到、价格监控、优惠券推送等功能。

---

## 🎯 核心功能

### 1. **京东薅羊毛系统**（✅ 已上线，v2.3.0）
```

---

