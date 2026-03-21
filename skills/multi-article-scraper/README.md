# 多平台文章爬取技能 (Multi-Article Scraper)

🕷️ 支持微信/小红书/抖音/知乎/简书等平台的文章爬取技能

## 🎯 功能

- ✅ 支持多平台爬取（微信/小红书/抖音/知乎/简书）
- ✅ 使用 Playwright 浏览器自动化
- ✅ 支持 Cookie 登录验证
- ✅ 提取标题、作者、内容、发布时间
- ✅ 保存为 Markdown/JSON/CSV 格式
- ✅ 绕过反爬虫机制
- ✅ 批量爬取（URL 列表）
- ✅ 定时自动爬取

## 🌐 支持平台

| 平台 | 状态 | 需要登录 | 说明 |
|------|------|---------|------|
| **微信公众号** | ✅ 已支持 | 可选 | 文章爬取 |
| **小红书** | ⏳ 开发中 | 必需 | 笔记爬取 |
| **抖音** | ⏳ 开发中 | 可选 | 视频文案爬取 |
| **知乎** | ⏳ 开发中 | 可选 | 回答/文章爬取 |
| **简书** | ⏳ 开发中 | 否 | 文章爬取 |

## 🚀 快速开始

### 安装依赖

```bash
pip install playwright
playwright install chromium
```

### 基础用法

#### 1. 单篇文章爬取

```bash
python3 scripts/multi_scraper.py "https://mp.weixin.qq.com/s/xxx"
```

#### 2. 指定平台

```bash
python3 scripts/multi_scraper.py --platform wechat "https://mp.weixin.qq.com/s/xxx"
```

#### 3. 使用 Cookie

```bash
python3 scripts/multi_scraper.py "https://mp.weixin.qq.com/s/xxx" --cookie "your_cookie"
```

#### 4. 指定输出格式

```bash
python3 scripts/multi_scraper.py "https://mp.weixin.qq.com/s/xxx" --format json
```

#### 5. 批量爬取

```bash
python3 scripts/multi_scraper.py --batch urls.txt --output articles/
```

## 📝 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `url` | 文章 URL（必需） | `https://mp.weixin.qq.com/s/xxx` |
| `--platform` | 平台名称（可选，自动检测） | `--platform wechat` |
| `--cookie` | 登录 Cookie（可选） | `--cookie "wx_cookie=..."` |
| `--output` | 输出目录（可选） | `--output ./articles/` |
| `--format` | 输出格式（可选） | `--format json` |
| `--batch` | 批量爬取（可选） | `--batch urls.txt` |
| `--delay` | 爬取间隔秒数（可选） | `--delay 3` |

## 📋 输出格式

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

## 🔧 技术实现

- **Playwright** - 浏览器自动化
- **真实浏览器模式** - 避免被检测（非 headless）
- **随机延迟** - 模拟真实用户行为
- **Cookie 支持** - 登录验证
- **多平台支持** - 自动检测平台

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
