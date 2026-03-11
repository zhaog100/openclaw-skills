# OpenClaw Skills 安装与使用完整指南

_2026-02-28 学习记录_

---

## 📚 什么是OpenClaw Skills

### 核心概念
**Skills** = 模块化功能扩展包
- 为AI助手提供专门领域的知识、工作流和工具
- 像给机器人安装不同的"大脑模块"
- 让AI能够完成更专业的任务

### 为什么使用Skills
- 🎯 **专业化** - 每个Skill专注特定领域
- 🔌 **即插即用** - 安装简单，无需复杂配置
- 📦 **模块化** - 可根据需要安装或卸载
- 🌐 **生态丰富** - 社区贡献大量实用Skills

---

## 🔧 Skill安装方法（4种）

### 方法1: ClawHub下载ZIP + 飞书机器人（推荐）⭐

**步骤**：
1. 访问 https://clawhub.ai/
2. 浏览或搜索想要的Skill
3. 点击下载ZIP压缩包
4. 打开飞书，找到OpenClaw机器人
5. 把ZIP文件直接发送给机器人
6. 机器人自动识别并安装

**优势**：
- ✅ 最简单方便
- ✅ 无需命令行
- ✅ 自动处理依赖

### 方法2: 发送SKILL.md链接

**步骤**：
1. 从ClawHub或GitHub找到SKILL.md文件URL
2. 发送链接给飞书机器人
3. 机器人自动下载并安装

### 方法3: Skills CLI（开发者）

**命令**：
```bash
# 搜索Skills
npx skills find [关键词]

# 安装Skill
npx skills add <owner/repo@skill> -g -y

# 检查更新
npx skills check

# 更新所有Skills
npx skills update
```

**参数说明**：
- `-g`: 全局安装（用户级别）
- `-y`: 跳过确认提示

### 方法4: 手动安装（高级用户）

**步骤**：
```bash
# 1. 下载Skill文件到本地
# 2. 放到Skills目录
cp -r /path/to/skill ~/.openclaw/skills/<skill-name>/

# 3. 验证安装
ls -la ~/.openclaw/skills/
```

---

## 🎯 4个核心Skills详解

### Skill 1: Find Skills -- 发现和安装技能

**功能**：
- 🔍 搜索Skills生态系统
- 📦 一键安装Skills
- 📋 检查和更新已安装的Skills

**使用场景**：
```
场景1: 想找某个功能的Skill
"如何做X" 或 "有没有能做X的Skill"

场景2: 浏览可用的Skills
访问 https://clawhub.ai/

场景3: 安装找到的Skill
npx skills add <owner/repo@skill> -g -y

场景4: 检查和更新
npx skills check
npx skills update
```

**搜索技巧**：
- 使用具体关键词："react testing" 比 "testing" 更好
- 尝试同义词："deploy" → "deployment" 或 "ci-cd"
- 查看热门来源：vercel-labs/agent-skills, ComposioHQ/awesome-claude-skills

**常见分类**：
| 分类 | 关键词示例 |
|------|-----------|
| Web开发 | react, nextjs, typescript, css, tailwind |
| 测试 | testing, jest, playwright, e2e |
| DevOps | deploy, docker, kubernetes, ci-cd |
| 文档 | docs, readme, changelog, api-docs |
| 代码质量 | review, lint, refactor, best-practices |
| 设计 | ui, ux, design-system, accessibility |
| 生产力 | workflow, automation, git |

---

### Skill 2: Multi Search Engine -- 多搜索引擎集成

**功能**：
- 集成17个搜索引擎（8个国内 + 9个国际）
- 一个地方搜索全网内容
- **不需要任何API Key！**

**国内搜索引擎（8个）**：
1. 百度 - https://www.baidu.com/
2. Bing国内版 - https://cn.bing.com/
3. Bing国际版 - https://cn.bing.com/
4. 360搜索 - https://www.so.com/
5. 搜狗搜索 - https://sogou.com/
6. 微信搜索 - https://wx.sogou.com/
7. 头条搜索 - https://so.toutiao.com/
8. 集思录 - https://www.jisilu.cn/

**国际搜索引擎（9个）**：
1. Google - https://www.google.com/
2. Google香港 - https://www.google.com.hk/
3. DuckDuckGo - https://duckduckgo.com/
4. Yahoo - https://search.yahoo.com/
5. Startpage - https://www.startpage.com/
6. Brave - https://search.brave.com/
7. Ecosia - https://www.ecosia.org/
8. Qwant - https://www.qwant.com/
9. WolframAlpha - https://www.wolframalpha.com/

**高级搜索技巧**：

1. **站内搜索（site:）**
```bash
# 只在GitHub上搜索
web_fetch({"url": "https://www.google.com/search?q=site:github.com+react"})
```

2. **文件类型搜索（filetype:）**
```bash
# 搜索PDF文档
web_fetch({"url": "https://www.google.com/search?q=machine+learning+filetype:pdf"})
```

3. **精确匹配（""）**
```bash
# 精确匹配短语
web_fetch({"url": "https://www.google.com/search?q=\"machine+learning\""})
```

4. **时间过滤**
```bash
# 过去1小时
web_fetch({"url": "https://www.google.com/search?q=ai+news&tbs=qdr:h"})

# 过去1天
web_fetch({"url": "https://www.google.com/search?q=ai+news&tbs=qdr:d"})
```

**DuckDuckGo Bangs（快捷指令）**：
```bash
# !g - 跳转到Google
web_fetch({"url": "https://duckduckgo.com/html/?q=!g+tensorflow"})

# !gh - 跳转到GitHub
web_fetch({"url": "https://duckduckgo.com/html/?q=!gh+tensorflow"})

# !so - 跳转到Stack Overflow
web_fetch({"url": "https://duckduckgo.com/html/?q=!so+python+error"})
```

---

### Skill 3: Tavily Search -- AI优化搜索

**功能**：
- 🤖 AI优化的网页搜索
- 📝 返回简洁相关的结果
- 🔍 支持深度研究模式
- 📰 专门的新闻搜索

**配置**：
1. 访问 https://tavily.com 获取API Key
2. 设置环境变量：
```bash
export TAVILY_API_KEY="你的API密钥"
```

**使用方法**：
```bash
# 基本搜索
node scripts/search.mjs "OpenClaw 安装教程"

# 自定义结果数量
node scripts/search.mjs "Python 最佳实践" -n 15

# 深度搜索
node scripts/search.mjs "人工智能发展历史" --deep

# 新闻搜索
node scripts/search.mjs "科技新闻" --topic news

# 提取网页内容
node scripts/extract.mjs "https://docs.openclaw.ai/"
```

**什么时候用Tavily vs Multi Search Engine**：

| 场景 | 推荐 | 原因 |
|------|------|------|
| 快速获取相关信息 | Tavily | AI优化，结果更相关 |
| 需要多种来源对比 | Multi Search Engine | 17个引擎，覆盖全面 |
| 深度研究复杂问题 | Tavily (--deep) | 深度搜索模式 |
| 搜索最新新闻 | Tavily (--topic news) | 专门的新闻主题 |
| 需要隐私保护 | Multi Search Engine (DuckDuckGo) | 隐私搜索引擎 |
| 需要知识计算 | Multi Search Engine (WolframAlpha) | 知识计算引擎 |

---

### Skill 4: EvoMap -- AI协作进化市场

**核心概念**：
- **Gene（基因）**: 可重用的策略模板（修复/优化/创新）
- **Capsule（胶囊）**: 应用Gene产生的经过验证的修复或优化
- **EvolutionEvent（进化事件）**: 进化过程的审计记录
- **Hub（中心）**: 存储、评分、推广和分发资产的中央注册表

**为什么使用EvoMap**：
- 🧠 **集体智慧**: 每个经过验证的修复都对所有连接的AI可用
- ✅ **质量保证**: 所有资产都经过内容可寻址验证、验证共识和GDI评分
- 💰 **收益分成**: 当你发布的Capsule被重用时，你可以获得积分
- 🎯 **悬赏任务**: 用户发布真实问题和悬赏，AI可以认领任务、发布解决方案并获得报酬
- 🐝 **群体分解**: 大型任务可以拆分给多个AI并行工作

**使用Evolver客户端**：
```bash
# 克隆仓库
git clone https://github.com/autogame-17/evolver.git
cd evolver
npm install

# 设置Hub URL
export A2A_HUB_URL=https://evomap.ai

# 单次运行
node index.js

# 循环模式（每4小时）
node index.js --loop
```

**4个Level使用指南**：

**Level 1: 连接和观察**
- 注册节点
- 获取已推广的资产
- 研究3-5个Capsule

**Level 2: 发布第一个Bundle**
- 准备资产（Gene + Capsule + EvolutionEvent）
- 计算asset_id（sha256）
- 发布Bundle

**Level 3: 通过悬赏任务获得积分**
- 获取任务
- 认领任务
- 解决问题并发布
- 完成任务

**Level 4: 持续改进**
- 提高GDI评分
- 建立声誉
- 使用webhooks
- 探索Swarm

**常见错误**：
- ❌ 只发送payload没有信封
- ❌ 使用payload.asset（单数）
- ❌ 包含Gene + Capsule省略EvolutionEvent
- ❌ 硬编码message_id/timestamp
- ❌ 忘记保存sender_id

---

## 📝 常用命令汇总

### Find Skills
```bash
npx skills find [query]          # 搜索Skills
npx skills add <package>         # 安装Skill
npx skills check                 # 检查更新
npx skills update                # 更新所有Skills
```

### Multi Search Engine
使用web_fetch工具，构造不同的搜索引擎URL

### Tavily Search
```bash
node scripts/search.mjs "query"              # 基本搜索
node scripts/search.mjs "query" -n 10        # 指定结果数量
node scripts/search.mjs "query" --deep       # 深度搜索
node scripts/search.mjs "query" --topic news # 新闻搜索
node scripts/extract.mjs "url"               # 提取网页内容
```

### EvoMap
```bash
node index.js          # 单次运行Evolver
node index.js --loop   # 循环模式（每4小时）
```

---

## 💡 最佳实践

### 1. 合理组合使用Skills
- **日常搜索**: 先用Tavily，结果不够再用Multi Search Engine
- **寻找工具**: 用Find Skills搜索是否有现成的Skill
- **贡献社区**: 如果你解决了有价值的问题，考虑通过EvoMap分享

### 2. 保持Skills更新
```bash
npx skills check
npx skills update
```

### 3. 管理API Keys
- 把API Keys保存在 ~/.zshrc 或 ~/.bashrc 中
- 不要把API Keys提交到代码仓库
- 定期轮换API Keys

### 4. 探索更多Skills
访问 https://clawhub.ai/ 发现更多有用的Skills！

---

## 🎓 学习价值

### 核心收获
1. ✅ **Skills机制** - 理解模块化扩展原理
2. ✅ **安装方法** - 掌握4种安装方式
3. ✅ **4个核心Skills** - Find、Multi Search、Tavily、EvoMap
4. ✅ **最佳实践** - 合理组合使用

### 实践意义
- 📈 **扩展性** - 随时添加新能力
- 🎯 **专业性** - 每个Skill专注领域
- 🔄 **灵活性** - 可随时调整配置
- 🌐 **生态化** - 参与社区协作

---

**学习时间**: 2026-02-28 09:10
**文章来源**: Z:\OpenClaw\OpenClaw Skills.txt
**价值评估**: ⭐⭐⭐⭐⭐（OpenClaw生态核心知识）
**待实现**: 评估是否需要安装文章提到的4个Skills
