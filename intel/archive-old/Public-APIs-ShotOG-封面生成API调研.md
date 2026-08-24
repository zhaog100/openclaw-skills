# ShotOG API 调研报告 - 封面生成

**调研时间**: 2026-04-11 14:25
**API名称**: ShotOG - Open Source OG Image Generation
**官网**: https://shotog.2214962083.workers.dev/
**GitHub**: https://github.com/nicepkg/shotog
**License**: MIT
**维护**: 小米椒 🌶️‍🔥

---

## 📊 基本信息

| 项目 | 信息 |
|------|------|
| 核心功能 | Open Graph图片生成（社交媒体分享封面） |
| 运行环境 | Cloudflare Workers（边缘计算，~17ms冷启动） |
| 模板数量 | 8个（basic/blog/product/social/event/changelog/testimonial/announcement） |
| 批量支持 | ✅ 最多20张/请求 |
| 输出格式 | PNG（默认）或SVG |
| API端点 | `https://shotog.2214962083.workers.dev/v1/og` |
| 批量端点 | `https://shotog.2214962083.workers.dev/v1/og/batch` |
| API Key创建 | `https://shotog.2214962083.workers.dev/v1/keys` |
| 使用查询 | `https://shotog.2214962083.workers.dev/v1/keys/usage` |

---

## 🎯 核心特性

### 1. 一键生成
- 单一URL调用
- 无需设计工具（Figma等）
- 无需无头浏览器
- ~50ms边缘响应

### 2. 8个专业模板
| Template | 最佳用途 | 预览 |
|----------|----------|------|
| basic | 通用页面、社交分享 | - |
| blog | 博客文章、长文 | ✅ |
| product | SaaS产品、发布 | ✅ |
| social | 社交媒体帖子 | ✅ |
| event | 活动、网络研讨会 | ✅ |
| changelog | 发布说明 | ✅ |
| testimonial | 客户引用 | ✅ |
| announcement | 重大更新、公告 | ✅ |

### 3. 自定义选项
- **字体**: 支持自定义TTF/OTF字体（最大5MB，缓存1h）
- **颜色**: 背景色、文本色、强调色
- **尺寸**: 宽度200-2400，高度200-1260（默认1200x630）
- **图片**: Avatar头像、Logo图标

### 4. 批量生成
- 最多20张/请求
- 并行渲染（Promise.allSettled）
- 配额预检查（不足时返回429）
- 仅成功渲染计入使用量

---

## 🧧 API使用方法

### GET方式（简单URL）
```bash
# 基础使用
curl "https://shotog.2214962083.workers.dev/v1/og?title=Hello&template=basic" -o og.png

# 带模板
curl "https://shotog.2214962083.workers.dev/v1/og?title=How+We+Scaled&template=blog&author=John" -o og.png

# 带副标题
curl "https://shotog.2214962083.workers.dev/v1/og?title=Product+Launch&template=product&subtitle=Built+with+ShotOG" -o og.png
```

### POST方式（JSON Body）
```bash
curl -X POST https://shotog.2214962083.workers.dev/v1/og \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Hello World",
    "template":"product",
    "subtitle":"Built with ShotOG"
  }' \
  -o og.png
```

### 批量生成
```bash
curl -X POST https://shotog.2214962083.workers.dev/v1/og/batch \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: sk_YOUR_API_KEY" \
  -d '{
    "images": [
      {"id": "hero", "title": "My Product", "template": "product"},
      {"id": "blog-1", "title": "First Post", "template": "blog", "author": "Alice"},
      {"id": "blog-2", "title": "Second Post", "template": "blog", "author": "Bob"}
    ],
    "defaults": {
      "format": "png",
      "width": 1200,
      "domain": "example.com"
    }
  }'
```

### SDK方式（JavaScript/TypeScript）
```bash
# 安装
npm install shotog

# 使用
import { ShotOG } from "shotog";

// 初始化（可选API Key，提高速率限制）
const og = new ShotOG({ apiKey: "sk_..." });

// 生成URL（无网络请求）
const imageUrl = og.url({
  title: "How We Scaled to 1M Users",
  subtitle: "A deep dive into our infrastructure",
  template: "blog",
  author: "Jane Smith"
});
// → https://shotog.2214962083.workers.dev/v1/og?title=How+We+Scaled...

// 直接生成图片二进制
const imageBuffer = await og.generate({
  title: "Product Launch",
  template: "announcement"
});
await fs.writeFile("output.png", imageBuffer);

// 列出模板
await og.templates();

// 检查使用量
await og.usage();

// 创建新API Key（静态方法）
await ShotOG.createKey("email@example.com");
```

---

## ⚙️ 参数选项

### 基础参数
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| title | string | ✅ | 主标题文本 |
| template | string | ❌ | 模板名称（默认：basic） |

### 可选参数
| 参数 | 类型 | 说明 |
|------|------|------|
| subtitle | string | 副标题（辅助文本） |
| eyebrow | string | 小标题（类别、标签） |
| author | string | 作者名称 |
| avatar | string | 头像图片URL（blog/social/testimonial显示） |
| logo | string | Logo图片URL（basic/product显示） |
| fontUrl | string | 自定义字体URL（TTF/OTF，最大5MB） |
| domain | string | 域名水印 |
| bgColor | string | 背景色（hex，如1a1a2e） |
| textColor | string | 文本颜色（hex） |
| accentColor | string | 强调色（hex） |
| format | string | 输出格式：png（默认）或svg |
| width | number | 图片宽度200-2400（默认：1200） |
| height | number | 图片高度200-1260（默认：630） |
| api_key | string | API Key（Header: X-Api-Key） |

---

## 📊 API Key管理

### 创建API Key
```bash
curl -X POST https://shotog.2214962083.workers.dev/v1/keys \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com"}'
```

### 响应示例
```json
{
  "id": "key_abc123",
  "key": "sk_live_...",
  "tier": "free",
  "monthly_limit": 500,
  "message": "Store your API key safely — it cannot be retrieved later."
}
```

### 查询使用量
```bash
curl https://shotog.2214962083.workers.dev/v1/keys/usage \
  -H "X-Api-Key: sk_live_..."
```

---

## 💰 定价计划

| 计划 | 月费 | 月额度 | 速率限制 |
|------|------|--------|----------|
| Free | $0 | 10/天 | 10/分钟 |
| Free | $0 | 500/月 | 60/分钟 |
| Starter | $9/月 | 5,000/月 | 120/分钟 |
| Pro | $29/月 | 25,000/月 | 300/分钟 |
| Scale | $79/月 | 100,000/月 | 600/分钟 |

### 定价详情
- **官网**: https://shotog.2214962083.workers.dev/pricing

---

## 🚀 集成建议

### 场景1：闲鱼商品分享卡片
- **模板**: product
- **输入**: 商品标题 + 价格/卖点
- **参数**: title, subtitle（价格）, logo
- **输出**: 1200x630 PNG
- **适用**: 闲鱼商品分享、推广图

### 场景2：小红书笔记封面
- **模板**: blog
- **输入**: 笔记标题 + 副标题 + 作者
- **参数**: title, subtitle（钩子）, author, template=blog
- **输出**: 9:16竖版（width=1080, height=1920）
- **适用**: 笔记封面、合集封面

### 场景3：产品发布公告
- **模板**: announcement
- **输入**: 产品名称 + 发布时间 + 特色
- **参数**: title, subtitle（日期）, template=announcement
- **输出**: 1200x630
- **适用**: 产品发布、更新公告

### 场景4：批量生成封面
```javascript
import { ShotOG } from "shotog";

const og = new ShotOG({ apiKey: "sk_YOUR_API_KEY" });

const products = [
  { id: "p1", title: "蒸汽眼罩10片装", template: "product", subtitle: "¥15.9" },
  { id: "p2", title: "蒸汽眼罩20片装", template: "product", subtitle: "¥25.9" },
  { id: "p3", title: "蒸汽眼罩30片装", template: "product", subtitle: "¥35.9" }
];

const result = await fetch("https://shotog.2214962083.workers.dev/v1/og/batch", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-Api-Key": "sk_YOUR_API_KEY"
  },
  body: JSON.stringify({ images: products })
});

const data = await result.json();
console.log(`成功: ${data.summary.succeeded}/${data.summary.total}`);
```

---

## 🔒 安全注意事项

1. **API Key保密**:
   - 一旦创建无法找回，必须安全存储
   - 不提交到版本控制
   - 推荐：使用环境变量

2. **错误处理**:
   - 429: 配额不足
   - 仅成功渲染计入使用量

---

## ⏳ 待完成

- [x] API文档调研
- [x] 使用方法整理
- [x] 集成场景设计
- [ ] 编写测试脚本（需API Key）
- [ ] 执行测试验证

---

*小米椒 🌶️‍🔥 | 2026-04-11*
