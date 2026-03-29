# Playwright - Browser Automation & Web Scraping

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/)

> 浏览器自动化和网页爬取技能，支持表单、截图、数据提取，可独立使用或通过MCP集成

## 🎯 简介

Playwright 是一个强大的浏览器自动化和网页爬取工具，支持：
- ✅ **浏览器自动化** - 表单填充、登录、导航
- ✅ **网页爬取** - 静态或JavaScript渲染的页面
- ✅ **E2E测试** - 完整的测试框架
- ✅ **截图和PDF** - 页面捕获
- ✅ **MCP集成** - 与AI代理无缝集成

## 📊 使用场景选择

| 场景 | 推荐方法 | 速度 |
|------|---------|------|
| 静态HTML | `web_fetch` 工具 | ⚡ 最快 |
| JavaScript渲染 | Playwright直接使用 | 🚀 快 |
| AI代理自动化 | MCP服务器 | 🤖 集成 |
| E2E测试 | @playwright/test | ✅ 完整框架 |

## 📚 核心文档

### 1. E2E测试模式
- 文件：`testing.md`
- 内容：测试模式、最佳实践、常见问题

### 2. CI/CD集成
- 文件：`ci-cd.md`
- 内容：GitHub Actions、Jenkins等

### 3. 调试失败
- 文件：`debugging.md`
- 内容：错误诊断、调试技巧

### 4. 网页爬取
- 文件：`scraping.md`
- 内容：数据提取、反爬策略

### 5. 选择器策略
- 文件：`selectors.md`
- 内容：元素定位、最佳实践

## 🚀 快速开始

### 安装

```bash
npm install -D @playwright/test
npx playwright install
```

### 基础用法

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // 导航到页面
  await page.goto('https://example.com');

  // 提取数据
  const title = await page.title();
  console.log(title);

  await browser.close();
})();
```

## 🎯 核心规则

1. **永不使用 `waitForTimeout()`** - 总是等待特定条件
2. **总是关闭浏览器** - 调用 `browser.close()` 防止内存泄漏
3. **优先使用角色选择器** - `getByRole()` 更稳定
4. **处理动态内容** - 使用 `waitFor()` 等待元素
5. **持久化认证状态** - 使用 `storageState` 保存登录

## 💡 常见任务

### 1. 网页爬取
```javascript
// 提取数据
const data = await page.$$eval('.item', items =>
  items.map(item => ({
    title: item.querySelector('h2').textContent,
    price: item.querySelector('.price').textContent
  }))
);
```

### 2. 表单填充
```javascript
// 登录表单
await page.fill('input[name="username"]', 'user@example.com');
await page.fill('input[name="password"]', 'password');
await page.click('button[type="submit"]');
```

### 3. 截图
```javascript
// 截取整页
await page.screenshot({ path: 'screenshot.png', fullPage: true });
```

## 📖 详细文档

- **E2E测试**：`testing.md`
- **CI/CD集成**：`ci-cd.md`
- **调试指南**：`debugging.md`
- **爬取模式**：`scraping.md`
- **选择器策略**：`selectors.md`

## 🎯 最佳实践

### 1. 等待策略
```javascript
// ❌ 错误
await page.waitForTimeout(3000);

// ✅ 正确
await page.waitForSelector('.loaded');
await page.waitForLoadState('networkidle');
```

### 2. 选择器
```javascript
// ❌ 脆弱
await page.click('.btn-abc123');

// ✅ 稳定
await page.getByRole('button', { name: '提交' });
```

### 3. 错误处理
```javascript
try {
  await page.click('button', { timeout: 5000 });
} catch (error) {
  console.error('点击失败:', error.message);
}
```

## 📞 技术支持

- **文档**：`SKILL.md` + 5个详细文档
- **官方文档**：https://playwright.dev
- **GitHub**：https://github.com/microsoft/playwright

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 思捷娅科技 (SJYKJ)

详见 [LICENSE](../../LICENSE) 文件。

---

*最后更新：2026-03-14*
