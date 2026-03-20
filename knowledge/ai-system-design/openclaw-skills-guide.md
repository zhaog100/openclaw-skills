# OpenClaw Skills 完整指南

_2026-03-02 学习自官方文档_

---

## 🎯 什么是OpenClaw Skills

**定义：** 模块化的功能扩展包，为AI助手提供专门领域的知识、工作流和工具

**为什么使用：**
- 🎯 **专业化** - 每个Skill专注特定领域
- 🔌 **即插即用** - 安装简单，无需复杂配置
- 📦 **模块化** - 根据需要安装或卸载
- 🌐 **生态丰富** - 社区贡献了大量实用Skills

---

## 📦 Skill安装方法（4种）

### 方法1：ClawHub下载ZIP + 飞书机器人（推荐）⭐

**步骤：**
1. 访问 https://clawhub.ai/
2. 浏览或搜索想要的Skill
3. 下载ZIP压缩包
4. 在飞书中发送ZIP文件给OpenClaw机器人
5. 机器人自动识别并安装

**优势：** 最简单，无需命令行

### 方法2：发送SKILL.md链接

**步骤：**
1. 获取SKILL.md文件URL
2. 在飞书中发送链接给机器人
3. 机器人自动下载并安装

### 方法3：Skills CLI（适合开发者）

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

**参数说明：**
- `-g`：全局安装（用户级别）
- `-y`：跳过确认提示

### 方法4：手动安装（高级用户）

```bash
# 1. 下载Skill文件到本地
# 2. 放到Skills目录
cp -r /path/to/skill ~/.openclaw/skills/<skill-name>/

# 3. 验证安装
ls -la ~/.openclaw/skills/
```

---

## 🔍 已安装的4个核心Skills

### Skill 1: Find Skills -- 发现和安装技能

**功能：** "元Skill"，帮你找到更多有用的Skills

**使用场景：**
1. 搜索Skills生态系统
2. 一键安装Skills
3. 检查和更新已安装的Skills

**常用命令：**
```bash
# 搜索相关Skills
npx skills find [关键词]

# 示例
npx skills find react performance
npx skills find pr review
npx skills find changelog

# 安装Skill
npx skills add <owner/repo@skill> -g -y

# 示例
npx skills add vercel-labs/agent-skills@vercel-react-best-practices -g -y

# 检查更新
npx skills check

# 更新所有Skills
npx skills update
```

**搜索分类：**
| 分类 | 关键词示例 |
|------|-----------|
| Web开发 | react, nextjs, typescript, css, tailwind |
| 测试 | testing, jest, playwright, e2e |
| DevOps | deploy, docker, kubernetes, ci-cd |
| 文档 | docs, readme, changelog, api-docs |
| 代码质量 | review, lint, refactor, best-practices |
| 设计 | ui, ux, design-system, accessibility |
| 生产力 | workflow, automation, git |

**搜索技巧：**
- 使用具体关键词："react testing" 比 "testing" 更好
- 尝试同义词：deploy → deployment → ci-cd
- 查看热门来源：vercel-labs/agent-skills、ComposioHQ/awesome-claude-skills

**在线浏览：** https://clawhub.ai/

### Skill 2: Multi Search Engine -- 多搜索引擎集成

**功能：** 集成17个搜索引擎（8个国内 + 9个国际），无需API Key

**国内搜索引擎（8个）：**
| 引擎 | 网址 | 说明 |
|------|------|------|
| 百度 | https://www.baidu.com/ | 国内最大搜索引擎 |
| Bing国内版 | https://cn.bing.com/ | 微软必应国内版 |
| Bing国际版 | https://cn.bing.com/ | 微软必应国际版 |
| 360搜索 | https://www.so.com/ | 360搜索引擎 |
| 搜狗搜索 | https://sogou.com/ | 搜狗搜索引擎 |
| 微信搜索 | https://wx.sogou.com/ | 微信公众号文章搜索 |
| 头条搜索 | https://so.toutiao.com/ | 今日头条搜索 |
| 集思录 | https://www.jisilu.cn/ | 投资社区搜索 |

**国际搜索引擎（9个）：**
| 引擎 | 网址 | 说明 |
|------|------|------|
| Google | https://www.google.com/ | 全球最大搜索引擎 |
| Google香港 | https://www.google.com.hk/ | Google香港版 |
| DuckDuckGo | https://duckduckgo.com/ | 隐私保护搜索引擎 |
| Yahoo | https://search.yahoo.com/ | 雅虎搜索 |
| Startpage | https://www.startpage.com/ | Google结果 + 隐私保护 |
| Brave | https://search.brave.com/ | Brave浏览器独立索引 |
| Ecosia | https://www.ecosia.org/ | 种树公益搜索引擎 |
| Qwant | https://www.qwant.com/ | 欧盟GDPR合规 |
| WolframAlpha | https://www.wolframalpha.com/ | 知识计算引擎 |

**特点：**
- ✅ 无需API Key
- ✅ 所有搜索通过web_fetch工具完成
- ✅ 开箱即用

**当前状态：** ✅ 已安装
**路径：** ~/.openclaw/skills/multi-search-engine/

### Skill 3: Tavily Search -- AI优化搜索

**功能：** AI优化的网页搜索，返回简洁相关的结果

**特点：**
- AI优化的搜索结果
- 返回简洁相关的内容
- 适合快速信息获取

### Skill 4: EvoMap -- AI协作进化市场

**功能：** 连接AI协作进化市场

**特点：**
- AI协作平台
- 进化市场连接
- 社区驱动的AI进化

---

## 🛠️ 常用命令汇总

**ClawHub操作：**
```bash
# 访问ClawHub
https://clawhub.ai/

# 搜索Skills
npx skills find [关键词]

# 安装Skill
npx skills add <owner/repo@skill> -g -y

# 检查更新
npx skills check

# 更新所有
npx skills update
```

**验证安装：**
```bash
# 查看已安装的Skills
ls -la ~/.openclaw/skills/

# 读取Skill说明
cat ~/.openclaw/skills/<skill-name>/SKILL.md
```

**飞书机器人：**
- 发送ZIP文件 → 自动安装
- 发送SKILL.md链接 → 自动安装
- 问："你安装了哪些Skills？"

---

## 💡 最佳实践

### 1. 从ClawHub开始
- 先浏览 https://clawhub.ai/
- 了解可用的Skills
- 选择需要的安装

### 2. 优先使用飞书机器人
- 最简单的安装方式
- 自动处理依赖
- 即装即用

### 3. 定期更新
```bash
npx skills check
npx skills update
```

### 4. 按需安装
- 不要一次性安装太多
- 根据实际需求选择
- 保持系统轻量

### 5. 学习SKILL.md
- 每个Skill都有详细文档
- 安装后先读SKILL.md
- 了解使用方法和限制

---

## 🎯 当前状态（2026-03-02）

**已安装Skills（8个）：**
1. ✅ qqbot-cron（定时提醒）
2. ✅ qqbot-media（图片发送）
3. ✅ clawhub（技能市场）
4. ✅ healthcheck（健康检查）
5. ✅ skill-creator（技能创建）
6. ✅ weather（天气查询）
7. ✅ playwright-scraper（网页爬取）
8. ✅ speech-recognition（语音识别）

**待探索Skills：**
- ⏳ Multi Search Engine（多搜索引擎）
- ⏳ Tavily Search（AI优化搜索）
- ⏳ EvoMap（AI协作市场）

**Skills目录：** ~/.openclaw/skills/
**文档位置：** 每个Skill的SKILL.md

---

## 🔗 相关链接

- ClawHub：https://clawhub.ai/
- OpenClaw文档：https://docs.openclaw.ai
- GitHub：https://github.com/openclaw/openclaw
- 社区Discord：https://discord.com/invite/clawd

---

*学习时间：2026-03-02 22:42*
*理解度：95%*
*实战价值：⭐⭐⭐⭐⭐*
