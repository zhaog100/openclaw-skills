# 微信文章爬取技能 (WeChat Article Scraper)

🕷️ 使用 Playwright 浏览器自动化爬取微信公众号文章

## 🎯 功能

- ✅ 爬取微信公众号文章内容
- ✅ 绕过反爬虫机制
- ✅ 支持 Cookie 登录验证
- ✅ 提取标题、作者、内容、发布时间
- ✅ 保存为 Markdown 格式

## 🚀 快速开始

### 安装依赖

```bash
pip install playwright
playwright install chromium
```

### 使用方法

#### 1. 简单爬取（无需登录）

```bash
python3 scripts/wechat_scraper.py "https://mp.weixin.qq.com/s/xxx"
```

#### 2. 使用 Cookie 爬取（推荐）

```bash
python3 scripts/wechat_scraper.py "https://mp.weixin.qq.com/s/xxx" --cookie "your_wx_cookie"
```

#### 3. 指定输出目录

```bash
python3 scripts/wechat_scraper.py "https://mp.weixin.qq.com/s/xxx" --output /path/to/output/
```

## 📝 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `<URL>` | 文章 URL（必需） | `https://mp.weixin.qq.com/s/xxx` |
| `--cookie` | 登录 Cookie（可选） | `--cookie "wx_cookie=..."` |
| `--output` | 输出目录（可选） | `--output ./articles/` |

## 📋 输出格式

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

## 🔧 技术实现

- **Playwright** - 浏览器自动化
- **真实浏览器模式** - 避免被检测（非 headless）
- **随机延迟** - 模拟真实用户行为
- **Cookie 支持** - 登录验证

## 📄 许可证

MIT License - 免费使用、修改和重新分发

**出处**:
- GitHub: https://github.com/zhaog100/openclaw-skills
- 创建者：小米辣 (PM + Dev)

**版权**: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

**商业使用授权**:
- 个人/开源：免费
- 小微企业：¥999/年
- 中型企业：¥4,999/年
- 大型企业：¥19,999/年

详情请查看：[LICENSE](../../LICENSE)
