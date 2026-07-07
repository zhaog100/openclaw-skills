# APITube News API 调研报告 - 热点采集扩展

**调研时间**: 2026-04-11 15:25
**API名称**: APITube News API
**官网**: https://apitube.io/
**GitHub**: https://github.com/apitube
**文档**: https://apitube.io/product/news-api/quick-start
**Postman**: https://www.postman.com/apitube/workspace/apitube-worldwide-news-api-for-your-products/documentation/31040123-e6e025d-99c4-48d1-9465-445ead21942a
**维护**: 小米椒 🌶️‍🔥

---

## 📊 基本信息

| 项目 | 信息 |
|------|------|
| 核心功能 | 实时全球新闻采集与NLP分析 |
| 新闻源数量 | 500,000+ |
| 支持语言 | 60种 |
| 覆盖国家 | 177个 |
| 实时性 | 发布到API<1分钟 |
| 响应格式 | JSON（默认） |
| 集成方式 | REST API + SDK（30+语言） |
| 历史数据 | 12个月（Paid及以上） |

---

## 🎯 核心功能

### 1. 实时新闻监控
- **500,000+新闻源**: RSS feeds + Sitemaps + 爬虫
- **Google News集成**: 整合Google News数据
- **持续监控**: 自动发现新文章
- **发布者排名**: 优先权威来源

### 2. NLP丰富化
- **语言检测**: 50+语言自动识别
- **主题分类**: business/sports/technology等自动分类
- **情感分析**: positive/negative/neutral + 置信度评分
- **实体识别**: NER（人物/组织/地点/品牌）
- **关键词提取**: AI生成关键词
- **可读性评分**: 自动评估文章可读性
- **内容检测**: AI生成内容检测

### 3. 质量控制
- **重复检测**: 自动聚类相同事件
- **付费墙检测**: 识别订阅内容
- **垃圾过滤**: 自动过滤低质量内容
- **来源验证**: 验证发布者可信度
- **内容验证**: 多层验证机制

### 4. 高级功能
- **故事聚类**: 自动聚合相关文章
- **故事演变**: 跟踪事件发展
- **来源偏移检测**: 识别新闻源偏见
- **跨平台对比**: 整合多平台热点

---

## 💰 定价方案

| 计划 | 月费 | 月请求 | 每分钟 | 每请求文章数 | 速率限制 |
|------|------|--------|--------|--------|----------|----------|
| Free | - | - | - | - | - |
| Starter | $99 | 20,000 | 10 | 200 | 50/分钟 |
| Professional | $199 | 50,000 | 50 | 200 | 50/分钟 |
| Corporate | $599 | 300,000 | 100 | 200 | 200/分钟 |

### 免费层
- **免费额度**: Basic计划（需注册获取）
- **基础功能**: 核心新闻检索 + 基础过滤
- **高级功能**: 情感分析 + 主题分类（部分）

### 付费层优势
- **Professional**: 更高速率（50/分钟），完整历史数据（12个月）
- **Corporate**: 最大速率（300,000/月），专属支持 + SLA
- **Enterprise**: 定制集成 + 优先支持

### 附加功能
- **Pay-as-You-Go**: 变量计费（$0.01/请求），灵活用量
- **自动升级**: 余额不足时自动升级
- **积分滚动**: 未用积分滚转到下月（付费计划）
- **实时查询**: 查询剩余余额和使用量

---

## 🧧 API使用方法

### 1. 注册和获取API Key
```bash
# 访问 https://apitube.io
# 注册账户
# 获取API Key（以sk_开头）

# 免费层开始（需注册获取具体额度）
```

### 2. 基础查询（GET方式）
```bash
# 获取最新新闻（默认10条）
curl "https://api.apitube.io/v1/news" \
  -H "X-Api-Key: sk_YOUR_API_KEY"

# 带参数查询
curl "https://api.apitube.io/v1/news?language=en&category=technology&sort=date" \
  -H "X-Api-Key: sk_YOUR_API_KEY"

# 完整参数示例
curl "https://api.apitube.io/v1/news?language=en&category=technology&sort=date&limit=20&sentiment=positive&hasImage=true" \
  -H "X-Api-Key: sk_YOUR_API_KEY"
```

### 3. Python SDK（推荐）
```python
# 安装
pip install apitube

# 使用
import apitube

client = apitube.Client(api_key="sk_YOUR_API_KEY")

# 获取最新新闻
news = client.news()

# 带过滤查询
news = client.news(
    language="en",
    category="technology",
    sort="date",
    limit=20
)

# 情感分析
for article in news:
    sentiment = article.get('sentiment', {})
    if sentiment['polarity'] == 'positive':
        print(f"正面: {article['title']}")
```

### 4. JavaScript SDK
```javascript
// 安装
npm install @apitube/news-api

// 使用
import { NewsClient } from '@apitube/news-api';

const client = new NewsClient({ apiKey: 'sk_YOUR_API_KEY' });

// 获取最新新闻
const news = await client.news();

// 带过滤查询
const filtered = await client.news({
  language: 'en',
  category: 'technology',
  sort: 'date',
  limit: 20
});

// 情感分析
news.forEach(article => {
  const sentiment = article.sentiment;
  if (sentiment.polarity === 'positive') {
    console.log(`正面: ${article.title}`);
  }
});
```

### 5. Node.js SDK
```javascript
// 安装
npm install @apitube/news-api-node

// 使用
const { NewsClient } = require('@apitube/news-api-node');

const client = new NewsClient({ apiKey: 'sk_YOUR_API_KEY' });

// 获取最新新闻
const news = client.news();

// 带过滤查询
const filtered = client.news({
  language: 'en',
  category: 'technology',
  sort: 'date',
  limit: 20
});
```

### 6. cURL（完整示例）
```bash
# 基础查询
curl -X GET "https://api.apitube.io/v1/news" \
  -H "X-Api-Key: sk_YOUR_API_KEY" \
  -G

# 带所有参数的完整查询
curl -X GET "https://api.apitube.io/v1/news?language=en&category=technology&sort=date&limit=20&sentiment=positive&hasImage=true&dateFrom=2024-01-01&dateTo=2024-01-31&country=US&source=bbc" \
  -H "X-Api-Key: sk_YOUR_API_KEY" \
  -G
```

---

## ⚙️ 完整参数列表

### 基础参数
| 参数 | 类型 | 必需 | 说明 |
|------|------|--------|------|
| X-Api-Key | header | ✅ | API密钥（sk_开头） |

### 搜索过滤参数
| 参数 | 类型 | 示例 | 说明 |
|------|------|--------|------|
| language | string | en, zh, es, fr | 语言代码（60种） |
| category | string | technology, business, sports | 主题分类 |
| sort | string | date, relevance, important, popular | 排序方式 |
| limit | integer | 1-100 | 每页结果数（默认10，最大100） |
| page | integer | 1-1000 | 页码 |
| country | string | US, CN, UK | 国家代码（177个） |
| source | string | bbc, cnn, nytimes | 新闻源ID |
| dateFrom | string | 2024-01-01 | 开始日期 |
| dateTo | string | 2024-01-31 | 结束日期 |

### 内容过滤参数
| 参数 | 类型 | 示例 | 说明 |
|------|------|--------|------|
| sentiment | string | positive, negative, neutral | 情感过滤 |
| hasImage | boolean | true, false | 是否包含图片 |
| minLength | integer | 100 | 文章最小长度（字符） |
| maxLength | integer | 1000 | 文章最大长度 |

### 响应控制参数
| 参数 | 类型 | 示例 | 说明 |
|------|------|--------|------|
| return | string | json, xml, csv, rss, xlsx, parquet, jsonl | 响应格式（默认json） |
| fullArticle | boolean | true, false | 是否返回完整文章内容 |
| includeMeta | boolean | true, false | 是否包含元数据 |

---

## 📊 响应格式

### 成功响应
```json
{
  "ok": true,
  "total": 150,
  "limit": 20,
  "page": 1,
  "articles": [
    {
      "id": "12345",
      "title": "Article Title",
      "description": "Article description...",
      "publishedAt": "2026-04-11T14:00:00Z",
      "source": {
        "name": "BBC News",
        "domain": "bbc.com",
        "country": "UK",
        "rank": 1
      },
      "category": "technology",
      "language": "en",
      "sentiment": {
        "polarity": "positive",
        "subjectivity": 0.8,
        "confidence": 0.95
      },
      "entities": {
        "persons": ["John Doe", "Jane Smith"],
        "organizations": ["Apple Inc.", "Microsoft"],
        "locations": ["London", "New York"],
        "brands": ["iPhone", "Windows"]
      },
      "images": [
        {
          "url": "https://example.com/image.jpg",
          "width": 1200,
          "height": 800
        }
      ],
      "readTime": "5.2",
      "wordCount": 450
    }
  ]
}
```

### 错误响应
| 状态 | 代码 | 说明 |
|------|------|------|
| 400 | Bad Request | 参数错误或缺失 |
| 401 | Unauthorized | API密钥无效 |
| 403 | Forbidden | 代理密钥无效 |
| 429 | Too Many Requests | 超出速率限制 |
| 500 | Internal Server Error | 服务器错误 |
| 503 | Service Unavailable | 服务暂时不可用 |

---

## 🚀 集成建议

### 场景1：扩展热点采集来源
- **当前系统**: 百度热搜（scripts/hotspot-collector.sh）
- **集成目标**: 添加APITube News作为第二数据源
- **优势**: 
  - 500,000+源 vs 百度单一源
  - 60种语言 vs 仅中文
  - NLP情感分析自动
  - 实体识别和关键词提取
  - 故事聚类和趋势分析
- **实现方式**:
  ```bash
  # 扩展热点采集脚本
  # 新增APITube查询函数
  # 整合数据输出到 intel/热点选题.md
  ```

### 场景2：热点情感分析
- **输入**: 采集的热点列表
- **处理**: 调用APITube sentiment分析
- **输出**: 每个热点的情感倾向
- **应用**: 内容创作时调整语气

### 场景3：国际热点追踪
- **输入**: 指定国家（US/UK/CN等）
- **处理**: 调用APITube country过滤
- **输出**: 该国家热点新闻
- **应用**: 跨国内容选题

### 场景4：新闻话题聚类
- **输入**: 主题关键词（AI, technology等）
- **处理**: 调用APITube category过滤
- **输出**: 该主题的聚合新闻
- **应用**: 垂直领域内容选题

---

## ⚠️ 注意事项

### 免费层限制
- **请求限制**: Basic计划需要注册后确认
- **历史数据**: 12个月数据仅Professional以上
- **高级功能**: 免费层仅包含基础功能，高级功能需付费

### 速率限制
- **Basic层**: 限制较高（需确认具体数值）
- **Professional层**: 50请求/分钟
- **Corporate层**: 200请求/分钟
- 建议：批量调用时添加间隔

### 成本控制
- **建议**: 从免费层开始测试
- **Pay-as-You-Go**: 变量计费，适合波动性需求
- **监控**: 定期检查使用量避免超额

### 数据质量
- **NLP质量**: 500K+源保证数据多样性
- **实时性**: 发布到API<1分钟
- **准确性**: 多层验证确保可信度

### 集成建议
- **简单开始**: 先使用Basic计划测试基础功能
- **逐步扩展**: 根据需要升级到Professional或Corporate
- **缓存机制**: 避免重复请求相同内容

---

## 📋 集成清单

### 第1步：注册和获取API Key
- [ ] 注册APITube账户（https://apitube.io）
- [ ] 获取API Key（sk_开头）
- [ ] 配置到环境变量或测试脚本

### 第2步：测试API连接
- [ ] 测试基础查询（GET）
- [ ] 验证响应格式
- [ ] 测试语言过滤
- [ ] 测试分类过滤
- [ ] 测试情感分析

### 第3步：扩展热点采集脚本
- [ ] 扩展scripts/hotspot-collector.sh
- [ ] 新增APITube查询函数
- [ ] 整合数据输出到 intel/热点选题.md
- [ ] 测试自动化流程

### 第4步：情感分析集成
- [ ] 编写情感分析函数
- [ ] 集成到数据复盘流程
- [ ] 测试准确性

---

## ✅ 已完成

- [x] API文档调研
- [x] 定价方案整理
- [x] 使用方法编写（Python/JS/Node/cURL）
- [x] 参数列表整理
- [x] 响应格式整理
- [x] 集成场景设计
- [x] 集成清单编写

---

## ⏳ 待完成

- [ ] 注册APITube账户获取API Key
- [ ] 编写测试脚本
- [ ] 执行测试验证
- [ ] 集成到热点采集脚本

---

## 📚 相关资源

- **官网**: https://apitube.io/
- **GitHub**: https://github.com/apitube
- **文档**: https://apitube.io/product/news-api/quick-start
- **Postman**: https://www.postman.com/apitube/workspace/apitube-worldwide-news-api-for-your-products/documentation/31040123-e6e025d-99c4-48d1-9465-445ead21942a
- **交互文档**: https://apitube.io/docs

---

*小米椒 🌶️‍🔥 | 2026-04-11*
