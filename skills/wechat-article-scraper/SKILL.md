---
name: wechat-article-scraper
description: 爬取微信公众号文章内容，支持反爬虫绕过和登录验证
author: 小米辣 (PM + Dev)
version: 1.0.0
---

# 微信文章爬取技能

## 🎯 功能

- ✅ 爬取微信公众号文章内容
- ✅ 绕过反爬虫机制
- ✅ 支持登录验证（Cookie/Session）
- ✅ 提取标题、内容、作者、发布时间
- ✅ 保存为 Markdown 格式

## 📋 使用方法

### 方法 1: 直接爬取（无需登录）
```bash
python3 scripts/wechat_scraper.py "https://mp.weixin.qq.com/s/xxx"
```

### 方法 2: 使用 Cookie 爬取（需要登录）
```bash
python3 scripts/wechat_scraper.py "https://mp.weixin.qq.com/s/xxx" --cookie "your_cookie"
```

### 方法 3: 批量爬取
```bash
python3 scripts/wechat_scraper.py --batch urls.txt --output articles/
```

## 🔧 技术实现

### 1. Playwright 浏览器自动化
- 启动真实浏览器（非 headless）
- 模拟真实用户行为
- 处理 JavaScript 渲染内容

### 2. 反爬虫绕过
- 随机 User-Agent
- 模拟鼠标移动
- 随机延迟
- 代理 IP 池（可选）

### 3. 登录验证
- Cookie 导入
- Session 持久化
- 二维码登录（可选）

## 📝 输出格式

```markdown
# 文章标题

**作者**: 作者名  
**发布时间**: 2026-03-21  
**原文链接**: https://...

---

文章内容...
```

## ⚠️ 注意事项

1. **遵守 robots.txt** - 尊重网站爬取规则
2. **频率限制** - 建议间隔 2-5 秒
3. **登录 Cookie** - 定期更新，避免失效
4. **内容版权** - 仅用于个人学习

## 📄 许可证

MIT License - 免费使用、修改和重新分发

**出处**:
- GitHub: https://github.com/zhaog100/openclaw-skills
- 创建者：小米辣 (PM + Dev)

**版权**: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
