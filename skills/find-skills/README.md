# Find Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensourc.org/licenses/MIT)

> 帮助用户发现并安装Agent技能 - 当用户问"如何做X"、"找到X的技能"、"是否有技能可以..."时使用

## 🎯 简介

Find Skills 是一个技能发现工具，帮助用户在开放Agent技能生态系统中找到并安装合适的技能。

### 使用场景

当用户：
- 问 "如何做 X"（X可能是某个常见任务）
- 说 "找到 X 的技能" 或 "是否有 X 的技能"
- 问 "你能做 X 吗"（X是某种专门能力）
- 想扩展Agent能力
- 想搜索工具、模板或工作流
- 提到希望在某领域得到帮助（设计、测试、部署等）

## 📚 技能CLI

### 安装

```bash
# 全局安装
npm install -g skills

# 或使用npx（推荐）
npx skills [command]
```

### 核心命令

```bash
# 搜索技能
npx skills find [query]

# 安装技能
npx skills add <package>

# 检查更新
npx skills check

# 更新所有技能
npx skills update
```

**浏览技能**：https://skills.sh/

## 🚀 快速开始

### 步骤1：了解需求

识别用户需求：
1. **领域**：React, 测试, 设计, 部署等
2. **具体任务**：写测试、创建动画、审查PR
3. **常见性**：是否足够常见，很可能有现有技能

### 步骤2：搜索技能

```bash
npx skills find [query]
```

**示例**：

| 用户问题 | 搜索命令 |
|---------|---------|
| "如何让React应用更快？" | `npx skills find react performance` |
| "能帮我审查PR吗？" | `npx skills find pr review` |
| "我需要创建变更日志" | `npx skills find changelog` |

### 步骤3：展示结果

**搜索结果示例**：
```
Install with npx skills add <owner/repo@skill>

vercel-labs/agent-skills@vercel-react-best-practices
└ https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

**展示格式**：
```
我找到了一个相关技能！"vercel-react-best-practices"
提供来自Vercel Engineering的React和Next.js性能优化指南。

安装命令：
npx skills add vercel-labs/agent-skills@vercel-react-best-practices

了解更多：https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### 步骤4：安装技能

```bash
# 安装技能（全局 + 自动确认）
npx skills add <owner/repo@skill> -g -y
```

**参数说明**：
- `-g` - 全局安装（用户级别）
- `-y` - 跳过确认提示

## 📊 常见技能类别

| 类别 | 搜索关键词 |
|------|-----------|
| **Web开发** | react, nextjs, typescript, css, tailwind |
| **测试** | testing, jest, playwright, e2e |
| **DevOps** | deploy, docker, kubernetes, ci-cd |
| **文档** | docs, readme, changelog, api-docs |
| **代码质量** | review, lint, refactor, best-practices |
| **设计** | ui, ux, design-system, accessibility |
| **生产力** | workflow, automation, git |

## 💡 搜索技巧

### 1. 使用具体关键词
```bash
# ❌ 太泛
npx skills find testing

# ✅ 具体
npx skills find react testing
```

### 2. 尝试同义词
```bash
# 如果 "deploy" 没结果，尝试：
npx skills find deployment
npx skills find ci-cd
```

### 3. 检查热门来源
- `vercel-labs/agent-skills`
- `ComposioHQ/awesome-claude-skills`

## 🎯 最佳实践

### 1. 多个关键词组合
```bash
npx skills find react testing best-practices
```

### 2. 按需安装
```bash
# 预览模式（不安装）
npx skills find [query]

# 确认后再安装
npx skills add <skill>
```

### 3. 查看技能详情
```bash
# 访问详情页
open https://skills.sh/<owner>/<repo>/<skill>
```

## 🚨 没找到技能？

### 告知用户
```
我搜索了与"xyz"相关的技能，但没有找到匹配项。

我仍然可以直接帮助您完成这个任务！要继续吗？

如果这是您经常做的事，可以创建自己的技能：
npx skills init my-xyz-skill
```

## 📖 详细文档

- **SKILL.md** - 详细使用指南
- **官方文档**：https://skills.sh/docs

## 📞 技术支持

- **技能浏览器**：https://skills.sh/
- **GitHub**：https://github.com/nicholasoxford/skills
- **文档**：`SKILL.md`

## 📄 许可证

MIT License

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 米粒儿 (miliger)

详见 [LICENSE](../../LICENSE) 文件。

---

*最后更新：2026-03-14*
