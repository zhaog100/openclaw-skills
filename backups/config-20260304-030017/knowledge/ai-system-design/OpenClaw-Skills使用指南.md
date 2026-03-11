# OpenClaw Skills 安装与使用完整指南

_2026-02-27 学习记录_

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

**适用场景**：
- 知道具体的SKILL.md链接
- 快速安装单个Skill

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

**适用场景**：
- 开发者习惯命令行
- 批量管理Skills

### 方法4: 手动安装（高级用户）

**步骤**：
```bash
# 1. 下载Skill文件到本地
# 2. 放到Skills目录
cp -r /path/to/skill ~/.openclaw/skills/<skill-name>/

# 3. 验证安装
ls -la ~/.openclaw/skills/
```

**适用场景**：
- 高级用户
- 需要自定义修改

### 验证安装

**方法1: 命令行**
```bash
# 查看已安装的Skills
ls -la ~/.openclaw/skills/

# 读取Skill文档
cat ~/.openclaw/skills/<skill-name>/SKILL.md
```

**方法2: 飞书机器人**
```
你安装了哪些Skills？
```

---

## 🎯 4个已安装的Skills

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

**特点**：
- ✅ 无需API Key
- ✅ 通过web_fetch工具完成
- ✅ 开箱即用

---

### Skill 3: Tavily Search -- AI优化搜索

**功能**：
- AI优化的网页搜索
- 返回简洁相关的结果
- 专为AI Agent设计

**优势**：
- 🎯 结果精准，减少噪音
- 🤖 AI友好的输出格式
- ⚡ 快速响应

**使用场景**：
- 需要精准搜索结果
- AI自动化流程中的搜索
- 减少人工筛选时间

---

### Skill 4: EvoMap -- AI协作进化市场

**功能**：
- 连接AI协作进化市场
- 发现AI协作机会
- 参与AI生态建设

**价值**：
- 🌐 AI生态连接
- 🤝 协作机会发现
- 📈 能力进化提升

---

## 📝 常用命令汇总

### Skills管理
```bash
# 搜索Skills
npx skills find [关键词]

# 安装Skill
npx skills add <owner/repo@skill> -g -y

# 检查更新
npx skills check

# 更新所有Skills
npx skills update

# 查看已安装
ls -la ~/.openclaw/skills/
```

### ClawHub使用
```bash
# 访问ClawHub
https://clawhub.ai/

# 搜索功能
# 浏览分类
# 查看详情
# 下载ZIP
```

### 飞书机器人
```
# 查询已安装Skills
"你安装了哪些Skills？"

# 安装Skill
发送ZIP文件 或 SKILL.md链接

# 使用Skill
直接描述需求，机器人会自动调用
```

---

## 💡 最佳实践

### 1. Skill选择原则
- ✅ **按需安装** - 只安装真正需要的
- ✅ **优先热门** - 选择社区活跃的Skills
- ✅ **定期清理** - 删除不用的Skills
- ✅ **保持更新** - 定期检查更新

### 2. 安装策略
```
1. 先访问ClawHub浏览
2. 查看Skill详情和评价
3. 下载ZIP通过飞书安装
4. 验证安装成功
5. 阅读SKILL.md学习使用
```

### 3. 使用技巧
- 📖 **阅读文档** - 每个Skill都有SKILL.md
- 🔍 **关键词精准** - 搜索时使用具体关键词
- 🔄 **定期更新** - 每周检查一次更新
- 🗑️ **及时清理** - 删除不用的Skills

### 4. 常见问题

**Q: Skills安装失败怎么办？**
```
A: 检查以下几点：
1. ZIP文件是否完整
2. SKILL.md格式是否正确
3. 依赖是否满足
4. 权限是否足够
```

**Q: 如何卸载Skill？**
```bash
# 方法1: 删除目录
rm -rf ~/.openclaw/skills/<skill-name>

# 方法2: 移动到临时目录
mv ~/.openclaw/skills/<skill-name> /tmp/
```

**Q: Skill冲突怎么办？**
```
A: 解决方法：
1. 查看Skill依赖
2. 优先使用功能更强的Skill
3. 暂时禁用冲突的Skill
4. 联系Skill作者反馈
```

---

## 🎓 学习价值

### 对OpenClaw用户
- ✅ 扩展AI能力边界
- ✅ 专业化领域知识
- ✅ 提升工作效率
- ✅ 参与社区生态

### 对AI Agent
- ✅ 获得专业工具
- ✅ 提升服务质量
- ✅ 更精准的响应
- ✅ 更强的实用性

---

## 🔧 技术细节

### Skill结构
```
skill-name/
├── SKILL.md       # 必需：Skill说明文档
├── scripts/       # 可选：脚本文件
├── references/    # 可选：参考资料
└── assets/        # 可选：资源文件
```

### SKILL.md格式
```markdown
---
name: skill-name
description: Skill描述
---

# Skill标题

## 功能说明
...

## 使用方法
...
```

### 依赖管理
- Skills可以声明依赖
- 通过package.json管理
- 自动安装缺失依赖

---

## 📊 当前状态检查

### 已安装Skills（6个）
1. ✅ qqbot-cron
2. ✅ qqbot-media
3. ✅ clawhub
4. ✅ healthcheck
5. ✅ skill-creator
6. ✅ qmd

### 文章提到的Skills（4个）
1. ⏸️ Find Skills - 待检查
2. ⏸️ Multi Search Engine - 待检查
3. ⏸️ Tavily Search - 待安装
4. ⏸️ EvoMap - 待安装

---

## 🎯 下一步行动

### 立即可做
1. **检查已安装Skills** - 验证Find Skills和Multi Search Engine是否已存在
2. **安装新Skills** - 如果需要，安装Tavily Search和EvoMap
3. **学习使用** - 阅读每个Skill的SKILL.md

### 持续优化
1. **定期浏览ClawHub** - 发现新的有用Skills
2. **定期更新** - 每周检查一次更新
3. **按需安装** - 根据实际需求安装
4. **及时清理** - 删除不用的Skills

---

**学习时间**: 2026-02-27 19:20
**文章来源**: OpenClaw Skills安装与使用完整指南
**价值评估**: ⭐⭐⭐⭐⭐（扩展AI能力的关键知识）
**待实现**: 检查并安装文章提到的4个Skills
