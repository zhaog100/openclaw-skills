---
name: multi-article-scraper
description: 多平台文章爬取技能 - 支持微信/小红书/抖音/知乎等平台
author: 小米辣 (PM + Dev)
version: 2.0.0
---

# 多平台文章爬取技能

## 🎯 功能

- ✅ 支持多平台爬取（微信/小红书/抖音/知乎/简书/Dev.to/Hacker News）
- ✅ 使用 Playwright 浏览器自动化
- ✅ 支持 Cookie 登录验证
- ✅ 提取标题、作者、内容、发布时间
- ✅ 保存为 Markdown/JSON/CSV 格式
- ✅ 绕过反爬虫机制
- ✅ 批量爬取（URL 列表）
- ✅ 定时自动爬取

## 📋 使用方法

### 方法 1: 单篇文章爬取
```bash
python3 scripts/multi_scraper.py "https://mp.weixin.qq.com/s/xxx"
```

### 方法 2: 批量爬取
```bash
python3 scripts/multi_scraper.py --batch urls.txt --output articles/
```

### 方法 3: 指定平台
```bash
python3 scripts/multi_scraper.py --platform xiaohongshu "https://www.xiaohongshu.com/xxx"
```

### 方法 4: 定时爬取
```bash
python3 scripts/multi_scraper.py --schedule "0 6 * * *" --urls urls.txt
```

## 🌐 支持平台

| 平台 | 状态 | 需要登录 | 说明 |
|------|------|---------|------|
| **微信公众号** | ✅ 已支持 | 可选 | 文章爬取 |
| **小红书** | ⏳ 待实现 | 必需 | 笔记爬取 |
| **抖音** | ⏳ 待实现 | 可选 | 视频文案爬取 |
| **知乎** | ⏳ 待实现 | 可选 | 回答/文章爬取 |
| **简书** | ⏳ 待实现 | 否 | 文章爬取 |

## 🔧 技术实现

### 1. Playwright 浏览器自动化
- 真实浏览器模式（非 headless）
- 模拟真实用户行为
- 处理 JavaScript 渲染内容

### 2. 反爬虫绕过
- 随机 User-Agent 轮换
- 模拟鼠标移动
- 随机延迟（2-5 秒）
- 代理 IP 池（可选）
- 浏览器指纹处理

### 3. 登录验证
- Cookie 导入/导出
- Session 持久化
- 二维码登录（可选）
- 登录失效自动提醒

### 4. 数据持久化
- 增量爬取（避免重复）
- 导出多种格式（Markdown/JSON/CSV）
- 自动备份到本地
- PDF/EPUB 导出（可选）

## 📝 输出格式

### Markdown
```markdown
# 文章标题

**作者**: 作者名  
**发布时间**: 2026-03-21  
**平台**: 微信公众号  
**原文链接**: https://...

---

文章内容...
```

### JSON
```json
{
  "title": "文章标题",
  "author": "作者名",
  "publish_date": "2026-03-21",
  "platform": "wechat",
  "url": "https://...",
  "content": "文章内容..."
}
```

### CSV
```csv
title,author,publish_date,platform,url,content
文章标题，作者名，2026-03-21,wechat,https://...,文章内容...
```

## ⚠️ 注意事项

1. **遵守 robots.txt** - 尊重网站爬取规则
2. **频率限制** - 建议间隔 2-5 秒
3. **登录 Cookie** - 定期更新，避免失效
4. **内容版权** - 仅用于个人学习
5. **每日限制** - 默认每日最多 100 篇

## 📄 许可证

MIT License - 免费使用、修改和重新分发

**出处**:
- GitHub: https://github.com/zhaog100/openclaw-skills
- 创建者：小米辣 (PM + Dev)

**版权**: MIT License | Copyright (c) 2026 小米辣 (PM + Dev)

**商业使用授权**:
- 个人/开源：免费
- 小微企业：¥999/年
- 中型企业：¥4,999/年
- 大型企业：¥19,999/年
- 源码买断：¥99,999 一次性

详情请查看：[LICENSE](../../LICENSE)

## 🌐 论坛支持

| 论坛 | 状态 | 需要登录 | 说明 |
|------|------|---------|------|
| **Dev.to** | ✅ 已支持 | 否 | AI 教程和技术文章 |
| **Hacker News** | ✅ 已支持 | 否 | AI 和技术讨论 |

