# APITube News API 调研报告 - 热点采集扩展

**调研时间**: 2026-04-11 14:50
**API名称**: APITube News API
**官网**: https://apitube.io/
**GitHub**: 待确认
**维护**: 小米椒 🌶️‍🔥

---

## 📊 基本信息

| 项目 | 信息 |
|------|------|
| 核心功能 | 全球新闻实时采集与NLP分析 |
| 新闻源数量 | 500,000+ |
| 支持语言 | 60种 |
| 响应时间 | 发布到API<1分钟（最快） |
| 历史数据 | 12个月 |
| 集成方式 | REST API + SDK（30+语言） |
| 认证方式 | API Key |

---

## 🎯 核心特性

### 1. 实时监控
- **500,000+新闻源**: RSS feeds + Sitemaps + 爬虫
- **持续监控**: 自动发现新文章
- **Google News集成**: 整合Google News数据
- **过滤系统**: 65+过滤器

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
- **发布者排名**: 优先权威来源
- **内容验证**: 多层验证机制

### 4. 数据导出
- **实时导出**: JSON/JSONL/XML/CSV
- **批量导出**: RSS/XLSX/Parquet
- **SSE流**: 实时Server-Sent Events流
- **Webhook**: 实时推送通知

### 5. 高级功能
- **故事聚类**: 自动聚合相关文章
- **故事演变**: 跟踪事件发展
- **来源偏移检测**: 识别新闻源偏见
- **MCP Server**: AI助手协议支持

---

## 💰 定价计划

| 计划 | 月费 | 月请求 | 每请求文章数 | 速率限制 |
|------|------|--------|--------|--------|--------|
| Basic | $99 | 20,000 | 200 | 50/分钟 |
| Professional | $199 | 50,000 | 200 | 50/分钟 |
| Corporate | $599 | 300,000 | 500 | 200/分钟 |

### 免费层
- **Basic计划**: $99/月，包含：
  - 情感分析 ✅
  - 实体提取 ✅
  - 主题分类 ✅
  - 可读性评分 ✅
  - 基础过滤器
- **免费额度**: 200积分/天

### 付费层优势
- **Professional**: 更高速率（200/分钟），完整历史数据
- **Corporate**: 最大速率（300,000/月），专属支持

### 附加功能
- **Pay-as-You-Go**: 变量计费（$0.01/请求），灵活用量
- **自动升级**: 余额不足时自动升级
- **积分滚动**: 未用积分滚转到下月

---

## 🧧 API使用方法

### 1. 注册和获取API Key
```bash
# 访问 https://apitube.io
# 注册账户
# 获取API Key（以sk_开头）

# 免费层开始（200积分/天）
```

### 2. 基础查询（GET方式）
```bash
# 获取最新新闻（默认10条）
curl "https://api.apitube.io/v1/news" \
  -H "X-Api-Key: sk_YOUR_API_KEY" \
  -G

# 带参数查询
curl "https://api.apitube.io/v1/news?language=en&category=technology&sort=date" \
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
npm install apitube

// 使用
import { APITube } from 'apitube';

const client = new APITube({ apiKey: 'sk_YOUR_API_KEY' });

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

### 5. 完整参数列表
```javascript
// 搜索参数
{
  language: 'en',           // 语言代码（50+语言）
  category: 'technology',     // 分类：business/sports/technology等
  topic: 'AI',              // 主题关键词
  country: 'US',            // 国家代码
  source: 'bbc',            // 新闻源ID
  dateFrom: '2024-01-01',  // 开始日期
  dateTo: '2024-01-31',    // 结束日期
  sentiment: 'positive',      // 情感：positive/negative/neutral
  hasImage: true,           // 包含图片
  limit: 20,                // 每页结果数（默认10，最大100）
  page: 1,                  // 页码
  sort: 'date'                // 排序：date/relevance/important
}
```

---

## 🚀 集成建议

### 场景1：扩展热点采集来源
- **当前系统**: 百度热搜（scripts/hotspot-collector.sh）
- **集成目标**: 添加APITube News作为第二数据源
- **优势**: 500,000+源 vs 百度单一源
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

---

## 📋 集成清单

### 第1步：注册和获取API Key
- [ ] 注册APITube账户
- [ ] 获取API Key（sk_开头）
- [ ] 配置到环境变量

### 第2步：测试API连接
- [ ] 测试基础查询（GET）
- [ ] 验证响应格式
- [ ] 测试过滤参数
- [ ] 验证速率限制

### 第3步：扩展热点采集脚本
- [ ] 扩展scripts/hotspot-collector.sh
- [ ] 新增APITube查询函数
- [ ] 整合数据输出
- [ ] 测试自动化流程

### 第4步：情感分析集成
- [ ] 编写情感分析函数
- [ ] 集成到热点数据复盘
- [ ] 测试准确性

---

## ⚠️ 注意事项

### 免费层限制
- **请求限制**: 20,000请求/月（Basic）
- **免费积分**: 200积分/天（约6666积分/月）
- **历史访问**: 12个月数据仅Professional以上
- **高级功能**: 付费层专属（完整历史、MCP等）

### 速率限制
- **Basic层**: 50请求/分钟
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

---

## ✅ 已完成

- [x] API文档调研
- [x] 定价方案整理
- [x] 使用方法编写（cURL/Python/JS）
- [x] 集成场景设计

---

## ⏳ 待完成

- [ ] 获取API Key
- [ ] 编写测试脚本
- [ ] 执行测试验证
- [ ] 集成到热点采集脚本

---

*小米椒 🌶️‍🔥 | 2026-04-11*
