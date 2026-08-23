# 📱 小红书运营技能索引

**位置**: `skills/xiaohongshu-ops-skill/`
**版本**: v1.0
**最后更新**: 2026-08-23

---

## 🎯 技能目标

构建可复用的"小红书运营"流程，覆盖账号定位、选题研究、内容生产、发布执行与复盘修复。

---

## 📁 技能目录结构

```
xiaohongshu-ops-skill/
├── SKILL.md                     # 技能主文件（通用流程）
├── persona.md                   # 平台人设规范（虾薯）
├── README.md                    # 技能说明
├── assets/                      # 图片资源
│   ├── 小红书账号.jpg
│   └── xiaohongshu-ops-poster.jpg
├── examples/                    # 案例模板
│   └── commerce/                # 商贸模式模板
│       ├── product-promo-template.md
│       ├── cross-platform-scripts.md
│       └── xianyu-listing-template.md
├── knowledge-base/              # 知识库
│   ├── README.md
│   ├── accounts/                # 账号分析
│   ├── topics/                  # 选题记录
│   ├── patterns/                # 爆款模式
│   ├── actions/                 # 动作记录
│   └── reviews/                 # 复盘记录
├── references/                  # 引用文档
│   ├── xhs-runtime-rules.md     # 运行规则
│   ├── xhs-account-analysis.md  # 账号分析
│   ├── xhs-home-feed-analysis.md # 首页分析
│   ├── xhs-topic-ideation.md    # 选题灵感
│   ├── xhs-viral-copy-flow.md   # Viral Copy流程
│   ├── xhs-publish-flows.md     # 发布流程
│   ├── xhs-comment-ops.md       # 评论操作
│   └── xhs-eval-patterns.md     # 提取模式
└── scripts/                     # 脚本（待开发）
```

---

## 🚀 核心流程

### 0) 启动与环境校验
- 固定使用内置浏览器 `profile=openclaw`
- 先读 `persona.md` 了解人设规范
- 先读 `knowledge-base/README.md` 查看已有记录

### 1) 账号定位（4变量）
- 目标用户：年龄/场景/痛点
- 内容价值主张：每篇给用户什么
- 差异化角度：同类不做什么，你做什么
- 风格规范：语气、长度、冲突边界

### 2) 选题流程
1. 平台侧抓取（首页推荐流分析）
2. 需求侧补充（评论区观点分歧）
3. 形成选题清单（≥3条）

### 3) 内容模板（5元组）
- 标题（≤20字，争议/立场/反问）
- 开头钩子（1-2句）
- 正文（3段：观点→证据→反方）
- 互动提问（1句）
- 话题（5-8个）

### 4) 发布链路
- 登录创作后台
- 明确发布类型（视频/图文/长文）
- 封面+标题+正文三要素
- **到发布按钮可见处停手**

### 5) 评论与回复
- 优先走通知页
- 遵循 `persona.md` 语气规范
- one-send-per-turn（无明确要求不连发）

---

## 📝 触发词索引

| 触发词 | 执行动作 | 输出文件 |
|--------|----------|----------|
| `选题灵感` | 生成3-5条选题 | knowledge-base/topics/ |
| `账号分析` | 体检账号5维度 | knowledge-base/accounts/ |
| `Viral Copy` | URL→新笔记 | 直接输出 |
| `发布笔记` | 执行发布流程 | actions/记录 |
| `复盘` | 数据复盘分析 | reviews/ |

---

## ⚠️ 注意事项

1. **所有浏览器操作走 `profile=openclaw`**
2. **发布前必须确认，不自动点击发布**
3. **关键步骤前保留快照**
4. **失败后保留已获结果，改道稳健路径**

---

*小米椒🌶️🔥 | v1.0 | 2026-08-23*
