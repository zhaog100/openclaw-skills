# RAKE 关键词提取 API 调研报告 - 竞品关键词挖掘

**调研时间**: 2026-04-11 15:40
**API名称**: RAKE (Rapid Automatic Keyword Extraction)
**GitHub**: https://github.com/csurfer/rake-nltk
**文档**: https://csurfer.github.io/rake-nltk/_build/html/index.html
**PyPI**: https://pypi.org/project/rake-nltk/
**维护**: 小米椒 🌶️‍🔥

---

## 📊 基本信息

| 项目 | 信息 |
|------|------|
| 核心功能 | 快速自动关键词提取 |
| 算法类型 | RAKE (Rapid Automatic Keyword Extraction) |
| 语言支持 | 多语言（依赖NLTK分词） |
| 输出格式 | 关键词列表+评分 |
| 集成方式 | Python库 |
| 费用 | 完全免费（MIT License） |

---

## 🎯 核心功能

### 1. 领域无关算法
- **RAKE特点**: 领域无关关键词提取
- **工作原理**: 分析词频和共现频率
- **优势**: 不需要领域特定训练数据

### 2. 自动识别关键短语
- **短语提取**: 识别多词关键词短语
- **评分机制**: 根据词频和度评分
- **排序输出**: 按重要性降序排列

### 3. 高效处理
- **快速**: 线性时间复杂度
- **简单**: 极简API接口
- **可扩展**: 支持批量文本处理

---

## 💰 定价方案

| 计划 | 费用 |
|------|--------|
| Free | 完全免费（MIT License） |

---

## 🧧 API使用方法

### 1. 安装
```bash
pip install rake-nltk
```

### 2. Python基础使用
```python
from rake_nltk import Rake

# 创建RAKE实例
r = Rake()

# 提取关键词
text = "The steam eye mask is perfect for office workers. It helps relieve eye strain during breaks."
r.extract_keywords_from_text(text)

# 获取关键词（带评分）
keywords_with_scores = r.get_ranked_phrases_with_scores()
print(keywords_with_scores)
# 输出: [('steam eye mask', 9.0), ('relieve eye strain', 8.0), ('office workers', 6.0)]

# 获取关键词（无评分）
keywords = r.get_ranked_phrases()
print(keywords)
# 输出: ['steam eye mask', 'relieve eye strain', 'office workers']
```

### 3. 批量处理
```python
from rake_nltk import Rake

r = Rake()

# 批量提取关键词
texts = [
    "The steam eye mask helps relieve eye fatigue during office breaks.",
    "Cervical massage device reduces neck pain for computer users.",
    "Scented tea promotes relaxation and better sleep quality."
]

for text in texts:
    r.extract_keywords_from_text(text)
    keywords = r.get_ranked_phrases()[:5]  # 取前5个

    print(f"文本: {text}")
    print(f"关键词: {', '.join(keywords)}\n")
```

---

## ⚙️ 参数说明

| 参数 | 类型 | 说明 |
|------|--------|------|
| min_length | integer | 最小关键词长度（默认：1） |
| max_length | integer | 最大关键词长度（默认：100000） |
| include_repeated_phrases | boolean | 是否包含重复短语（默认：False） |

---

## 📊 响应格式

### Python输出示例（带评分）
```python
[
    ('steam eye mask', 9.0),
    ('relieve eye strain', 8.0),
    ('office workers', 6.0)
]
```

### Python输出示例（无评分）
```python
[
    'steam eye mask',
    'relieve eye strain',
    'office workers'
]
```

---

## 🚀 集成建议

### 场景1：竞品关键词挖掘
- **输入**: 竞品商品标题/描述/评论区
- **处理**: 调用RAKE提取关键词
- **输出**: 竞品关键词列表（按重要性排序）
- **应用**:
  - 分析竞品标题关键词
  - 优化自身商品标题
  - 找出热门关键词

### 场景2：小红书关键词优化
- **输入**: 小红书笔记标题+正文
- **处理**: 调用RAKE提取关键词
- **输出**: 关键词列表
- **应用**:
  - 生成标签
  - 优化标题
  - 埋词策略

### 场景3：用户反馈关键词分析
- **输入**: 用户评论/私信
- **处理**: 调用RAKE提取关键词
- **输出**: 用户关注点关键词
- **应用**:
  - 识别用户痛点
  - 优化产品文案
  - 改进产品功能

---

## ⚠️ 注意事项

### 语言支持
- **多语言**: 支持多语言（依赖NLTK分词）
- **中文支持**: 需要配置中文分词器（如Jieba）

### 准确性
- **短语提取**: 能够识别多词短语（比单词更有价值）
- **评分机制**: 根据词频和度评分（相对客观）

### 性能
- **速度**: 本地运行，无API延迟
- **批量处理**: 适合批量分析大量文本

---

## 📋 集成清单

### 第1步：安装RAKE
- [ ] 安装rake-nltk库
- [ ] 测试基础功能

### 第2步：编写提取脚本
- [ ] 编写关键词提取函数
- [ ] 编写批量提取脚本
- [ ] 测试准确性

### 第3步：集成到工作流
- [ ] 集成到竞品分析流程
- [ ] 集成到小红书优化流程
- [ ] 测试准确性

---

## ✅ 已完成

- [x] API文档调研
- [x] 使用方法整理
- [x] 集成场景设计
- [x] 集成清单编写

---

## ⏳ 待完成

- [ ] 安装rake-nltk库
- [ ] 编写测试脚本
- [ ] 执行测试验证
- [ ] 集成到工作流

---

## 📚 相关资源

- **GitHub**: https://github.com/csurfer/rake-nltk
- **文档**: https://csurfer.github.io/rake-nltk/_build/html/index.html
- **PyPI**: https://pypi.org/project/rake-nltk/
- **NLTK**: https://www.nltk.org/

---

*小米椒 🌶️‍🔥 | 2026-04-11*
