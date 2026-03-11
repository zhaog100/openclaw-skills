# Playwright 长图截图功能

## ✅ 已安装技能

**技能名称**：Playwright Scraper v1.0.0
**安装状态**：✅ 完全就绪
**支持功能**：✅ 长图截图（full_page=True）

---

## 🎯 长图截图功能

### **核心参数**

```python
page.screenshot(path="screenshot.png", full_page=True)
```

**参数说明**：
- `path`: 截图保存路径
- `full_page=True`: **启用长图模式**（截取整个页面，包括滚动区域）

---

## 🚀 使用方式

### **方式1：基础长图截图**

```python
from playwright.sync_api import sync_playwright

# 激活虚拟环境
source /tmp/playwright-venv/bin/activate

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 访问页面
    page.goto("https://example.com", wait_until="networkidle")
    
    # 截取长图
    page.screenshot(path="long-screenshot.png", full_page=True)
    
    print("✅ 长图已保存: long-screenshot.png")
    
    browser.close()
```

### **方式2：自定义视口长图**

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    # 自定义视口大小
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    
    page.goto("https://example.com")
    
    # 等待页面完全加载
    page.wait_for_load_state("networkidle")
    
    # 截取长图
    page.screenshot(
        path="custom-screenshot.png",
        full_page=True,
        animations="disabled"  # 禁用动画，加快截图
    )
    
    browser.close()
```

### **方式3：延迟加载内容长图**

```python
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    page.goto("https://example.com")
    
    # 滚动到底部，触发延迟加载
    for i in range(5):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
    
    # 滚动回顶部
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(1)
    
    # 截取长图
    page.screenshot(path="lazy-load-screenshot.png", full_page=True)
    
    browser.close()
```

---

## 🎯 实际用例

### **用例1：截取微信公众号文章**

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 访问微信文章
    page.goto("https://mp.weixin.qq.com/s/xxxxx")
    
    # 等待图片加载
    page.wait_for_load_state("networkidle")
    time.sleep(3)  # 额外等待图片
    
    # 截取长图
    page.screenshot(
        path="wechat-article.png",
        full_page=True,
        type="png",
        animations="disabled"
    )
    
    print("✅ 微信文章长图已保存")
    
    browser.close()
```

### **用例2：截取长网页**

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    
    page.goto("https://example.com/long-page")
    page.wait_for_load_state("networkidle")
    
    # 截取长图
    page.screenshot(
        path="long-page.png",
        full_page=True,
        type="jpeg",  # JPEG 格式，文件更小
        quality=80     # 质量 80%
    )
    
    browser.close()
```

### **用例3：批量截取多个页面**

```python
from playwright.sync_api import sync_playwright

urls = [
    ("https://example1.com", "screenshot1.png"),
    ("https://example2.com", "screenshot2.png"),
    ("https://example3.com", "screenshot3.png"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    for url, filename in urls:
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        
        # 截取长图
        page.screenshot(path=filename, full_page=True)
        print(f"✅ {filename} 已保存")
        
        page.close()
    
    browser.close()
```

---

## 📋 高级参数

### **screenshot() 完整参数**

```python
page.screenshot(
    path="screenshot.png",        # 保存路径
    full_page=True,               # 长图模式
    type="png",                   # 格式：png/jpeg
    quality=80,                   # JPEG 质量（0-100）
    omit_background=False,        # 是否透明背景
    animations="disabled",        # 禁用动画：disabled/allow
    clip={                        # 裁剪区域（可选）
        "x": 0,
        "y": 0,
        "width": 1920,
        "height": 1080
    },
    mask=[page.locator(".ads")]   # 遮挡元素（可选）
)
```

---

## 🔧 常用配置

### **1. 移动端长图**

```python
page = browser.new_page(
    viewport={"width": 375, "height": 812},
    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
)
page.goto("https://example.com")
page.screenshot(path="mobile.png", full_page=True)
```

### **2. 高清长图**

```python
page = browser.new_page(
    viewport={"width": 1920, "height": 1080},
    device_scale_factor=2  # 2倍分辨率
)
page.goto("https://example.com")
page.screenshot(path="hd.png", full_page=True)
```

### **3. 去广告长图**

```python
page = browser.new_page()
page.goto("https://example.com")

# 隐藏广告元素
page.evaluate("""
    document.querySelectorAll('.ads, .advertisement, .banner').forEach(el => {
        el.style.display = 'none';
    });
""")

page.screenshot(path="clean.png", full_page=True)
```

---

## ⚠️ 注意事项

1. **页面加载**：
   - 使用 `wait_until="networkidle"` 等待页面完全加载
   - 对于延迟加载内容，需要手动滚动触发

2. **内存占用**：
   - 长图会占用较多内存（~500MB-1GB）
   - 建议分批处理大量截图

3. **文件大小**：
   - PNG 格式：无损，文件大
   - JPEG 格式：有损，文件小（推荐用于长图）

4. **超时问题**：
   - 设置合理的超时时间
   - 使用 `page.set_default_timeout(60000)`（60秒）

---

## 🚀 快速测试

```bash
# 激活虚拟环境
source /tmp/playwright-venv/bin/activate

# 运行截图脚本
python3 << 'EOF'
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    page.goto("https://example.com", wait_until="networkidle")
    page.screenshot(path="/tmp/test-long-screenshot.png", full_page=True)
    
    print("✅ 长图已保存: /tmp/test-long-screenshot.png")
    
    browser.close()
EOF

# 查看文件大小
ls -lh /tmp/test-long-screenshot.png
```

---

## 📊 性能对比

| 截图类型 | 文件大小 | 截图时间 | 内存占用 |
|---------|---------|---------|---------|
| **普通截图** | ~100KB | <1秒 | ~100MB |
| **长图（PNG）** | ~2MB | 2-3秒 | ~500MB |
| **长图（JPEG）** | ~500KB | 2-3秒 | ~500MB |
| **高清长图** | ~5MB | 3-5秒 | ~1GB |

---

**官家，Playwright Scraper 已支持长图截图功能！** 🌾

**使用参数**：`page.screenshot(path="xxx.png", full_page=True)`
