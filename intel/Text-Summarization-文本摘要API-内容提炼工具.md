# Text Summarization 文本摘要 API - 内容提炼工具

**调研时间**: 2026-04-11 16:50
**API名称**: Text Summarization
**官网**: https://github.com/public-apis/public-apis
**维护**: 小米椒 🌶️‍🔥

---

## 📊 基本信息

| 项目 | 信息 |
|------|------|
| 核心功能 | 长文本自动摘要 |
| 服务示例 | summarizer.iapp.eu, text-processing.com |
| 认证方式 | 部分需要API Key |
| 语言支持 | 多语言（英文为主） |
| 费用 | 大部分免费 |

---

## 🎯 核心功能

### 1. 文本摘要
- **提取式摘要**: 从原文提取关键句子
- **生成式摘要**: AI生成新的摘要文本
- **长度控制**: 自定义摘要长度（字数/句数）
- **多文档摘要**: 合并多个文档生成摘要

### 2. 关键词提取
- **自动关键词**: 从文本提取关键词
- **关键词排名**: 按重要性排序
- **短语提取**: 提取关键短语
- **实体识别**: 识别人名/地名/机构名

### 3. 文本分析
- **情感分析**: 正面/负面/中性
- **主题分类**: 自动分类文本主题
- **语言检测**: 自动检测文本语言
- **可读性评分**: 评估文本可读性

---

## 💰 定价方案（示例服务）

| 服务 | 免费层 | 付费层 |
|------|--------|--------|
| **summarizer.iapp.eu** | 无限免费 | 无付费层 |
| **text-processing.com** | 1000次/天 | 定制 |
| **meaningcloud** | 20000次/月 | $99/月起 |
| **aylien** | 1000次/月 | $99/月起 |

---

## 🧧 使用方法

### 1. summarizer.iapp.eu（无需API Key）
```python
import requests

# 生成文本摘要
url = "https://summarizer.iapp.eu/summarize"
params = {
    'text': '这是一段很长的文本，需要生成摘要...',
    'sentences': 3  # 摘要句数
}
response = requests.get(url, params=params)
summary = response.json()['summary']
print(f"摘要: {summary}")
```

### 2. Python本地生成（sumy库）
```python
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# 解析文本
parser = PlaintextParser.from_string(
    "这是一段很长的文本，需要生成摘要...",
    Tokenizer("chinese")
)

# 生成摘要
summarizer = LsaSummarizer()
summary = summarizer(parser.document, 3)  # 3句话

# 输出摘要
for sentence in summary:
    print(sentence)
```

### 3. 关键词提取（rake-nltk）
```python
from rake_nltk import Rake

# 创建RAKE对象
rake = Rake()

# 提取关键词
text = "这是一段很长的文本，包含很多关键词..."
rake.extract_keywords_from_text(text)
keywords = rake.get_ranked_phrases()

print(f"关键词: {keywords[:10]}")  # 前10个关键词
```

---

## 🚀 集成建议

### 场景1：竞品文章摘要
- **输入**: 竞品长文章
- **处理**: 生成文章摘要
- **输出**: 3-5句摘要
- **应用**:
  - 竞品分析快速阅读
  - 行业资讯提炼
  - 内容创作灵感

### 场景2：用户评论分析
- **输入**: 大量用户评论
- **处理**: 提取关键词 + 情感分析
- **输出**: 关键词列表 + 情感倾向
- **应用**:
  - 产品反馈分析
  - 用户需求挖掘
  - 差评预警

### 场景3：热点内容提炼
- **输入**: 热点文章/新闻
- **处理**: 生成摘要 + 提取关键词
- **输出**: 摘要 + 关键词
- **应用**:
  - 热点快速了解
  - 内容创作素材
  - 选题方向参考

---

## ⚠️ 注意事项

### 语言支持
- **英文**: 大部分服务对英文支持最好
- **中文**: 部分服务支持中文，需确认
- **本地库**: sumy支持多语言（需安装对应语言包）

### 摘要质量
- **提取式**: 保留原文句子，准确性高
- **生成式**: 可能产生新内容，需人工审核
- **长度**: 摘要长度影响质量，建议3-5句

---

## 📋 集成清单

### 第1步：选择文本摘要服务
- [ ] 选择服务（summarizer/sumy本地）
- [ ] 测试API可用性
- [ ] 确认中文支持

### 第2步：编写摘要脚本
- [ ] 编写文本摘要函数
- [ ] 编写关键词提取函数
- [ ] 测试准确性

### 第3步：集成到工作流
- [ ] 集成到竞品分析流程
- [ ] 集成到热点采集流程
- [ ] 测试准确性

---

## ✅ 已完成

- [x] API文档调研
- [x] 使用方法整理
- [x] 集成场景设计
- [x] 集成清单编写

---

## ⏳ 待完成

- [ ] 选择文本摘要服务
- [ ] 安装sumy库（本地生成）
- [ ] 编写测试脚本
- [ ] 执行测试验证
- [ ] 集成到工作流

---

## 📚 相关资源

- **summarizer.iapp.eu**: https://summarizer.iapp.eu/
- **text-processing.com**: https://text-processing.com/
- **sumy (Python)**: https://pypi.org/project/sumy/
- **rake-nltk**: https://pypi.org/project/rake-nltk/
- **Public APIs**: https://github.com/public-apis/public-apis

---

*小米椒 🌶️‍🔥 | 2026-04-11*
