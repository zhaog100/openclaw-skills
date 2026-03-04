# Multi Search Engine 实现指南

_基于OpenClaw Skills知识学习_

---

## 🎯 核心理念

**Multi Search Engine不依赖外部Skill，直接使用web_fetch工具即可！**

---

## 🌐 17个搜索引擎集成

### 国内搜索引擎（8个）

#### 1. 百度
```bash
web_fetch({"url": "https://www.baidu.com/s?wd=OpenClaw+教程"})
```

#### 2. Bing国内版
```bash
web_fetch({"url": "https://cn.bing.com/search?q=OpenClaw+tutorial"})
```

#### 3. Bing国际版
```bash
web_fetch({"url": "https://cn.bing.com/search?q=OpenClaw+tutorial&ensearch=1"})
```

#### 4. 360搜索
```bash
web_fetch({"url": "https://www.so.com/s?q=OpenClaw"})
```

#### 5. 搜狗搜索
```bash
web_fetch({"url": "https://sogou.com/web?query=OpenClaw"})
```

#### 6. 微信搜索
```bash
web_fetch({"url": "https://wx.sogou.com/weixin?type=2&query=人工智能"})
```

#### 7. 头条搜索
```bash
web_fetch({"url": "https://so.toutiao.com/search?keyword=科技新闻"})
```

#### 8. 集思录
```bash
web_fetch({"url": "https://www.jisilu.cn/search/?q=投资策略"})
```

---

### 国际搜索引擎（9个）

#### 1. Google
```bash
web_fetch({"url": "https://www.google.com/search?q=OpenClaw+tutorial"})
```

#### 2. Google香港
```bash
web_fetch({"url": "https://www.google.com.hk/search?q=OpenClaw+tutorial"})
```

#### 3. DuckDuckGo（隐私保护）
```bash
web_fetch({"url": "https://duckduckgo.com/html/?q=privacy+tools"})
```

#### 4. Yahoo
```bash
web_fetch({"url": "https://search.yahoo.com/search?p=OpenClaw"})
```

#### 5. Startpage（Google结果+隐私）
```bash
web_fetch({"url": "https://www.startpage.com/sp/search?query=OpenClaw"})
```

#### 6. Brave（独立索引）
```bash
web_fetch({"url": "https://search.brave.com/search?q=OpenClaw"})
```

#### 7. Ecosia（种树公益）
```bash
web_fetch({"url": "https://www.ecosia.org/search?q=OpenClaw"})
```

#### 8. Qwant（欧盟GDPR合规）
```bash
web_fetch({"url": "https://www.qwant.com/?q=OpenClaw"})
```

#### 9. WolframAlpha（知识计算）
```bash
web_fetch({"url": "https://www.wolframalpha.com/input?i=100+USD+to+CNY"})
```

---

## 🔍 高级搜索技巧

### 1. 站内搜索（site:）
```bash
# 只在GitHub上搜索
web_fetch({"url": "https://www.google.com/search?q=site:github.com+react"})

# 只在知乎上搜索
web_fetch({"url": "https://www.baidu.com/s?wd=site:zhihu.com+人工智能"})
```

### 2. 文件类型搜索（filetype:）
```bash
# 搜索PDF文档
web_fetch({"url": "https://www.google.com/search?q=machine+learning+filetype:pdf"})

# 搜索PPT
web_fetch({"url": "https://www.google.com/search?q=openclaw+filetype:ppt"})
```

### 3. 精确匹配（""）
```bash
web_fetch({"url": "https://www.google.com/search?q=\"machine+learning\""})
```

### 4. 排除关键词（-）
```bash
web_fetch({"url": "https://www.google.com/search?q=python+-snake"})
```

### 5. 或搜索（OR）
```bash
web_fetch({"url": "https://www.google.com/search?q=cat+OR+dog"})
```

### 6. 时间过滤
```bash
# 过去1小时
web_fetch({"url": "https://www.google.com/search?q=ai+news&tbs=qdr:h"})

# 过去1天
web_fetch({"url": "https://www.google.com/search?q=ai+news&tbs=qdr:d"})

# 过去1周
web_fetch({"url": "https://www.google.com/search?q=ai+news&tbs=qdr:w"})

# 过去1月
web_fetch({"url": "https://www.google.com/search?q=ai+news&tbs=qdr:m"})

# 过去1年
web_fetch({"url": "https://www.google.com/search?q=ai+news&tbs=qdr:y"})
```

---

## 🎯 DuckDuckGo Bangs（快捷指令）

**非常实用的功能！直接跳转到特定网站搜索：**

### 常用Bangs
```bash
# !g - 跳转到Google
web_fetch({"url": "https://duckduckgo.com/html/?q=!g+tensorflow"})

# !gh - 跳转到GitHub
web_fetch({"url": "https://duckduckgo.com/html/?q=!gh+tensorflow"})

# !so - 跳转到Stack Overflow
web_fetch({"url": "https://duckduckgo.com/html/?q=!so+python+error"})

# !w - 跳转到Wikipedia
web_fetch({"url": "https://duckduckgo.com/html/?q=!w+artificial+intelligence"})

# !yt - 跳转到YouTube
web_fetch({"url": "https://duckduckgo.com/html/?q=!yt+openclaw+tutorial"})

# !r - 跳转到Reddit
web_fetch({"url": "https://duckduckgo.com/html/?q=!r+programming"})

# !npm - 跳转到npm
web_fetch({"url": "https://duckduckgo.com/html/?q=!npm+react"})
```

---

## 🧮 WolframAlpha知识计算

**不是普通搜索引擎，而是知识计算引擎！**

### 数学计算
```bash
# 积分计算
web_fetch({"url": "https://www.wolframalpha.com/input?i=integrate+x%5E2+dx"})

# 解方程
web_fetch({"url": "https://www.wolframalpha.com/input?i=solve+x%5E2+%2B+2x+%3D+0"})
```

### 单位转换
```bash
# 货币转换
web_fetch({"url": "https://www.wolframalpha.com/input?i=100+USD+to+CNY"})

# 长度转换
web_fetch({"url": "https://www.wolframalpha.com/input?i=100+miles+to+km"})
```

### 股票信息
```bash
web_fetch({"url": "https://www.wolframalpha.com/input?i=AAPL+stock"})
```

### 天气查询
```bash
web_fetch({"url": "https://www.wolframalpha.com/input?i=weather+in+Beijing"})
```

---

## 💡 实战应用场景

### 场景1: 快速获取技术文档
```bash
# 搜索React文档
web_fetch({"url": "https://duckduckgo.com/html/?q=!gh+react+documentation"})
```

### 场景2: 解决编程问题
```bash
# 搜索Stack Overflow
web_fetch({"url": "https://duckduckgo.com/html/?q=!so+python+list+comprehension"})
```

### 场景3: 查找学术资料
```bash
# 搜索PDF论文
web_fetch({"url": "https://www.google.com/search?q=machine+learning+survey+filetype:pdf"})
```

### 场景4: 实时新闻
```bash
# 头条搜索最新新闻
web_fetch({"url": "https://so.toutiao.com/search?keyword=AI最新动态"})
```

### 场景5: 微信公众号文章
```bash
# 搜狗微信搜索
web_fetch({"url": "https://wx.sogou.com/weixin?type=2&query=项目管理最佳实践"})
```

---

## 🎯 最佳实践

### 1. 优先使用隐私搜索引擎
- **DuckDuckGo** - 不追踪用户
- **Startpage** - Google结果+隐私保护
- **Brave** - 独立索引

### 2. 使用Bangs提升效率
- **!gh** - GitHub搜索
- **!so** - Stack Overflow搜索
- **!w** - Wikipedia查询

### 3. 组合使用高级技巧
```bash
# 站内搜索 + 文件类型
web_fetch({"url": "https://www.google.com/search?q=site:github.com+filetype:pdf+react"})
```

### 4. 根据需求选择引擎
- **快速搜索** → DuckDuckGo / Google
- **技术问题** → DuckDuckGo (!so)
- **学术资料** → Google (filetype:pdf)
- **国内内容** → 百度 / 微信搜索
- **实时新闻** → 头条搜索
- **知识计算** → WolframAlpha

---

## 📊 对比传统Skills

| 方面 | Multi Search Engine Skill | 直接使用web_fetch |
|------|--------------------------|------------------|
| **安装** | 需要安装 | ✅ 无需安装 |
| **配置** | 可能需要配置 | ✅ 开箱即用 |
| **灵活性** | Skill封装限制 | ✅ 完全灵活 |
| **更新** | 依赖Skill更新 | ✅ 始终最新 |
| **学习成本** | 需要学习Skill API | ✅ 标准web_fetch |

---

## 🎓 总结

**Multi Search Engine功能已经完全可用！**

✅ **无需安装额外Skill**
✅ **17个搜索引擎直接访问**
✅ **高级搜索技巧全支持**
✅ **隐私保护选择丰富**
✅ **知识计算能力强大**

---

**创建时间**: 2026-02-28 09:15
**实现方式**: 基于web_fetch工具
**状态**: ✅ 立即可用
