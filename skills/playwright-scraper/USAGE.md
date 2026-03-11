# Playwright 网页爬取使用示例

## ✅ 安装状态

**版本**：Playwright v1.58.0
**浏览器**：Chromium 145.0.7632.6
**安装位置**：`/tmp/playwright-venv/`
**测试结果**：✅ 通过（example.com 爬取成功）

---

## 🚀 使用方式

### **1. 激活虚拟环境**

```bash
source /tmp/playwright-venv/bin/activate
```

### **2. 基础爬取示例**

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 访问页面
    page.goto("https://example.com")
    
    # 获取标题
    title = page.title()
    print(f"标题: {title}")
    
    # 获取内容
    content = page.content()
    print(f"内容: {content}")
    
    # 截图
    page.screenshot(path="screenshot.png")
    
    browser.close()
```

### **3. 高级功能**

#### **等待元素加载**
```python
page.goto("https://example.com")
page.wait_for_selector("h1")  # 等待 h1 元素出现
title = page.locator("h1").text_content()
```

#### **提取多个元素**
```python
page.goto("https://example.com")
links = page.locator("a").all()
for link in links:
    print(link.get_attribute("href"))
```

#### **执行 JavaScript**
```python
page.goto("https://example.com")
result = page.evaluate("() => document.title")
print(result)
```

#### **处理动态内容**
```python
page.goto("https://example.com")
page.wait_for_load_state("networkidle")  # 等待网络空闲
content = page.content()
```

#### **模拟用户操作**
```python
page.goto("https://example.com")
page.fill("input[name='q']", "搜索内容")
page.click("button[type='submit']")
page.wait_for_load_state("networkidle")
```

---

## 🎯 实际用例

### **示例1：爬取新闻标题**
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    page.goto("https://news.ycombinator.com")
    page.wait_for_selector(".titleline")
    
    titles = page.locator(".titleline > a").all()
    for i, title in enumerate(titles[:10], 1):
        print(f"{i}. {title.text_content()}")
    
    browser.close()
```

### **示例2：保存完整网页**
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    page.goto("https://example.com", wait_until="networkidle")
    
    # 保存 HTML
    with open("page.html", "w") as f:
        f.write(page.content())
    
    # 保存截图
    page.screenshot(path="page.png", full_page=True)
    
    # 保存 PDF
    page.pdf(path="page.pdf")
    
    browser.close()
```

### **示例3：API 拦截（加速爬取）**
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 拦截图片和样式，加速爬取
    page.route("**/*.{png,jpg,jpeg,gif,svg,css}", lambda route: route.abort())
    
    page.goto("https://example.com")
    content = page.content()
    
    browser.close()
```

---

## 📋 注意事项

1. **虚拟环境**：每次使用前需要激活虚拟环境
   ```bash
   source /tmp/playwright-venv/bin/activate
   ```

2. **反爬虫**：部分网站可能有反爬虫机制，建议：
   - 添加随机延迟
   - 使用 stealth 插件
   - 模拟真实用户行为

3. **资源占用**：Playwright 会占用较多内存（~500MB）

4. **法律合规**：确保遵守网站的 robots.txt 和使用条款

---

## 🔧 常用命令

```bash
# 查看版本
playwright --version

# 安装其他浏览器
playwright install firefox
playwright install webkit

# 安装系统依赖
playwright install-deps

# 查看安装的浏览器
ls ~/.cache/ms-playwright/
```

---

**官家，网页爬取功能已完全就绪！** 🌾
