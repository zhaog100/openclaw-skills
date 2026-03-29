# 技能合并方案

生成时间：2026-03-06 19:01

## 🔍 深度对比分析

### 1. 浏览器自动化类（3个技能）

#### agent-browser
- **版本**：0.2.1
- **技术**：Rust + Node.js
- **核心功能**：
  - 通用浏览器自动化
  - 点击、输入、截图
  - DOM快照和元素引用
- **适用场景**：简单网页操作、自动化测试
- **优势**：性能优秀，简单易用

#### playwright-scraper
- **版本**：1.0.1
- **技术**：Playwright
- **核心功能**：
  - 专注网页爬取
  - AI自动生成脚本
  - 支持复杂SPA、多Tab、懒加载
  - 数据结构化输出
- **适用场景**：复杂动态网页爬取
- **优势**：功能丰富，AI辅助，中文文档

#### wool-gathering（包含爬虫功能）
- **版本**：1.0.0
- **技术**：Python + Playwright/Puppeteer
- **核心功能**：
  - 价格监控（爬虫）
  - 优惠券获取（爬虫）
  - 签到自动化
- **适用场景**：薅羊毛专用
- **优势**：专业化，收益明确

**重复度分析**：
- ⭐⭐⭐⭐ **高度重复**（agent-browser vs playwright-scraper）
- ⭐⭐ **中度重复**（wool-gathering的爬虫功能 vs playwright-scraper）

**合并建议**：
1. **agent-browser + playwright-scraper**
   - 保留：**playwright-scraper**（功能更强）
   - 原因：
     - playwright-scraper功能完全覆盖agent-browser
     - 支持AI辅助脚本生成
     - 中文文档更适合官家
   - 操作：删除agent-browser

2. **wool-gathering的爬虫部分**
   - 保留：独立技能（专业化）
   - 原因：
     - 薅羊毛场景特殊
     - 已有完整生态（青龙面板）
     - 与通用爬虫需求不同
   - 操作：保持独立

---

### 2. 搜索类（3个技能）

#### qmd-manager
- **核心功能**：本地知识库搜索
- **技术**：QMD（BM25 + 向量）
- **适用场景**：项目管理、软件测试知识

#### find-skills
- **核心功能**：在线技能发现和安装
- **技术**：Skills CLI
- **适用场景**：扩展功能

#### tavily-search
- **核心功能**：AI优化的网页搜索
- **技术**：Tavily API
- **适用场景**：实时信息查询

**重复度分析**：
- ⭐ **无重复**（完全不同的搜索领域）

**合并建议**：
- ✅ **全部保留**（功能互补）

---

### 3. 云服务类（1个技能）

#### tencentcloud-lighthouse-skill
- **核心功能**：腾讯云Lighthouse管理
- **技术**：mcporter + MCP
- **适用场景**：云服务器管理

**重复度分析**：
- ⭐ **无重复**（唯一云服务技能）

**合并建议**：
- ✅ **保留**

---

## 📋 最终合并方案

### ✅ 需要合并（1对）

**agent-browser → playwright-scraper**

**合并原因**：
1. 功能高度重复（都是浏览器自动化）
2. playwright-scraper功能更强
3. 有AI辅助脚本生成
4. 中文文档

**合并步骤**：
1. 确认playwright-scraper功能完整性
2. 备份agent-browser配置（如有）
3. 删除agent-browser技能
4. 测试playwright-scraper是否满足所有需求

**命令**：
```bash
# 删除agent-browser
rm -rf /root/.openclaw/workspace/skills/agent-browser

# 提交到Git
cd /root/.openclaw/workspace
git add -A
git commit -m "合并agent-browser到playwright-scraper（功能重复）"
```

---

### ✅ 保留技能（12个）

1. playwright-scraper（浏览器自动化+爬取）
2. qmd-manager（本地知识搜索）
3. find-skills（在线技能发现）
4. tavily-search（网页搜索）
5. github（GitHub交互）
6. notion（Notion API）
7. obsidian（Obsidian笔记）
8. summarize（摘要工具）
9. tencentcloud-lighthouse-skill（腾讯云管理）
10. weather（天气查询）
11. miliger-context-manager（上下文管理）
12. wool-gathering（薅羊毛系统）

---

## 📊 合并效果

**合并前**：13个技能
**合并后**：12个技能
**减少**：1个技能（-7.7%）

**优势**：
1. ✅ 减少功能重复
2. ✅ 简化技能选择
3. ✅ 降低维护成本
4. ✅ 保持功能完整性

---

## ⚠️ 注意事项

1. **测试playwright-scraper**：
   - 确认能完成所有agent-browser的功能
   - 测试简单网页操作
   - 测试DOM快照

2. **备份**：
   - 如有agent-browser的自定义配置，先备份
   - 确保可以恢复

3. **文档更新**：
   - 更新技能使用指南
   - 更新MEMORY.md

---

## 🎯 执行建议

**立即执行**：
1. 删除agent-browser
2. 提交到Git
3. 更新文档

**可选执行**：
- 创建技能使用指南（明确每个技能的最佳场景）

---

*生成时间：2026-03-06 19:01*
