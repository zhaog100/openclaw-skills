# Obsidian Vault 使用指南

## ✅ 安装状态

**Vault 路径**：`/root/.openclaw/workspace/obsidian-vault/`
**CLI 工具**：obsidian-cli（已安装）
**集成状态**：✅ 与 QMD 自动集成
**文件数量**：1 个（README.md）

---

## 🎯 Obsidian 本质

**Obsidian vault = 普通的 Markdown 文件夹**

- ✅ 纯文本格式（`.md` 文件）
- ✅ 支持双向链接 `[[note-name]]`
- ✅ 支持标签 `#tag`
- ✅ 支持附件和图片
- ✅ 跨平台兼容

---

## 🚀 使用方式

### **1. 添加笔记**

```bash
# 方式1：直接创建 Markdown 文件
cat > /root/.openclaw/workspace/obsidian-vault/new-note.md << 'EOF'
# 新笔记

这是笔记内容。

## 关联
- [[README]]
- #标签

## 参考
- 来源：网页链接
EOF

# 方式2：使用 OpenClaw 自动创建
# Session-Memory Enhanced 会自动保存会话记忆到 vault
```

### **2. 检索笔记**

```bash
# 使用 QMD 检索（推荐）
qmd search "关键词" -c memory

# 示例
qmd search "项目管理" -c memory
qmd search "PMP" -c memory
```

### **3. 编辑笔记**

```bash
# 使用任何文本编辑器
nano /root/.openclaw/workspace/obsidian-vault/note.md
vim /root/.openclaw/workspace/obsidian-vault/note.md
code /root/.openclaw/workspace/obsidian-vault/  # VS Code
```

### **4. 组织笔记**

```bash
# 创建文件夹
mkdir /root/.openclaw/workspace/obsidian-vault/projects
mkdir /root/.openclaw/workspace/obsidian-vault/knowledge

# 移动笔记
mv note.md projects/
```

---

## 📚 与 OpenClaw 集成

### **1. Session-Memory Enhanced**

**自动保存会话记忆**：
- 每小时自动运行
- 保存重要对话到 vault
- 自动生成关键词和摘要

**配置文件**：`/root/.openclaw/workspace/skills/session-memory-enhanced/config/unified.json`

**vault 路径**：`memory/agents/main/`（已集成）

### **2. QMD Manager**

**自动索引和检索**：
- 每小时更新索引
- 每天 23:55 生成向量
- 支持语义搜索

**当前状态**：
- 已索引：95 个文件
- 已嵌入：256 个向量
- 待嵌入：8 个文件

### **3. Playwright Scraper**

**从网页导入笔记**：

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("https://example.com/article")

    # 提取内容
    title = page.title()
    content = page.locator("article").text_content()

    # 保存到 vault
    with open("/root/.openclaw/workspace/obsidian-vault/article.md", "w") as f:
        f.write(f"# {title}\n\n{content}")

    browser.close()
```

---

## 🎯 实际用例

### **用例1：项目管理笔记**

```bash
cat > /root/.openclaw/workspace/obsidian-vault/projects/pmp-study.md << 'EOF'
# PMP 学习笔记

## 知识领域
1. 整合管理
2. 范围管理
3. 进度管理
4. 成本管理
5. 质量管理
6. 资源管理
7. 沟通管理
8. 风险管理
9. 采购管理
10. 相关方管理

## 参考
- [[项目管理流程]]
- #PMP #项目管理
EOF
```

### **用例2：会议记录**

```bash
cat > /root/.openclaw/workspace/obsidian-vault/meetings/2026-03-09.md << 'EOF'
# 会议记录 - 2026-03-09

## 参与者
- 官家（南仲）
- 米粒儿

## 讨论内容
1. Session-Memory Enhanced v4.0.0 开发
2. 技能环境检查
3. Playwright 网页爬取安装

## 决策
- ✅ 吸收 memu-engine 核心功能
- ✅ 每天自动运行 qmd embed
- ✅ 安装 Playwright 网页爬取

## 待办
- [ ] 明天提供 OpenAI API Key
- [ ] Moltbook API 配置

## 标签
#会议 #2026-03
EOF
```

### **用例3：知识卡片**

```bash
cat > /root/.openclaw/workspace/obsidian-vault/knowledge/token-optimization.md << 'EOF'
# Token 优化策略

## 核心洞察
- **传统方式**：读取整个文件（2000 tokens）
- **QMD 方式**：精准回忆（150 tokens）
- **节省**：90%+

## 技术实现
1. QMD 精准检索
2. 向量搜索
3. 混合检索（精度 93%）

## 来源
- Hazel_OC: "I traced every token I generated for 7 days"
- opencode-moltu-1: "Tiered Context Bucketing"

## 关联
- [[Session-Memory Enhanced]]
- #Token优化 #知识管理
EOF
```

---

## 🔧 高级功能

### **1. 双向链接**

```markdown
# 笔记A

关联到 [[笔记B]]

---

# 笔记B

反向链接会自动出现在 Obsidian 中
```

### **2. 标签系统**

```markdown
# 项目管理

#PMP #项目管理 #学习
```

### **3. 图谱视图**

Obsidian Desktop 提供：
- 本地图谱（Local Graph）
- 全局图谱（Global Graph）
- 反向链接面板

---

## 📋 Vault 结构建议

```
obsidian-vault/
├── .obsidian/          # Obsidian 配置
├── projects/           # 项目笔记
├── meetings/           # 会议记录
├── knowledge/          # 知识卡片
├── daily/              # 每日笔记
├── templates/          # 模板
├── attachments/        # 附件
└── README.md           # 说明文档
```

---

## 🎯 与其他工具对比

| 工具 | 优势 | 劣势 |
|------|------|------|
| **Obsidian** | 本地优先、双向链接、插件丰富 | 需要桌面应用 |
| **Notion** | 在线协作、数据库功能 | 需要网络、隐私问题 |
| **Logseq** | 大纲式、本地优先 | 学习曲线陡峭 |
| **Roam Research** | 双向链接先驱 | 昂贵、需要网络 |

---

## ⚠️ 注意事项

1. **服务器环境**：
   - 没有桌面 GUI，无法使用 Obsidian Desktop
   - 使用文本编辑器直接编辑 `.md` 文件
   - 通过 QMD 实现检索功能

2. **同步问题**：
   - 建议使用 Git 版本控制
   - 或使用 Obsidian Sync（需要订阅）
   - 或使用第三方同步工具（Syncthing、Dropbox）

3. **备份建议**：
   ```bash
   # 定期备份 vault
   tar -czf obsidian-backup-$(date +%Y%m%d).tar.gz obsidian-vault/
   ```

---

## 🚀 快速开始

```bash
# 1. 查看当前 vault
ls /root/.openclaw/workspace/obsidian-vault/

# 2. 创建新笔记
cat > /root/.openclaw/workspace/obsidian-vault/my-first-note.md << 'EOF'
# 我的第一篇笔记

这是内容。

## 标签
#笔记 #入门
EOF

# 3. 检索笔记
qmd search "第一篇" -c memory

# 4. 查看所有笔记
find /root/.openclaw/workspace/obsidian-vault -name "*.md"
```

---

**官家，Obsidian vault 已配置完成！** 🌾

**可以开始使用了！** ✅
