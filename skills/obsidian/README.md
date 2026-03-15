# Obsidian Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Work with Obsidian vaults (plain Markdown notes) and automate via obsidian-cli. 💎

## 🎯 简介

Obsidian 技能提供完整的 Obsidian 笔记库自动化能力，支持：
- ✅ **笔记管理** - 读取、创建、编辑 Markdown 笔记
- ✅ **库操作** - 多库管理、默认库设置
- ✅ **自动化** - 通过 obsidian-cli 自动化常见操作

## 🚀 快速开始

### 1. 安装 obsidian-cli

```bash
# macOS (via Homebrew)
brew install yakitrak/yakitrak/obsidian-cli

# 验证安装
obsidian-cli --version
```

### 2. 查找活跃的库

Obsidian 桌面版跟踪库的位置：
```
~/Library/Application Support/obsidian/obsidian.json
```

**快速查询**：
```bash
# 如果已设置默认库
obsidian-cli print-default --path-only

# 否则，读取配置文件
cat ~/Library/Application Support/obsidian/obsidian.json | jq '.vaults[] | select(.open == true)'
```

### 3. 基本操作

#### 读取笔记
```bash
# 读取笔记内容
obsidian-cli read "Daily Notes/2026-03-14.md"
```

#### 创建笔记
```bash
# 创建新笔记
obsidian-cli new "Projects/New Project.md" --content "# New Project\n\nCreated on $(date +%Y-%m-%d)"
```

## 📚 核心功能

### 1. 库管理

#### 查找所有库
```bash
# 列出所有库
obsidian-cli list-vaults

# 查看当前活跃库
cat ~/Library/Application Support/obsidian/obsidian.json | jq -r '.vaults[] | select(.open == true) | .path'
```

#### 设置默认库
```bash
# 设置默认库
obsidian-cli set-default "My Vault"

# 验证默认库
obsidian-cli print-default --path-only
```

### 2. 笔记操作

#### 创建笔记
```bash
# 创建简单笔记
obsidian-cli new "Notes/Meeting Notes.md"

# 创建带模板的笔记
obsidian-cli new "Daily/$(date +%Y-%m-%d).md" --template "Templates/Daily Note.md"
```

#### 读取笔记
```bash
# 读取笔记内容
obsidian-cli read "Notes/Meeting Notes.md"

# 搜索笔记
obsidian-cli search "project"
```

#### 编辑笔记
```bash
# 追加内容
obsidian-cli append "Notes/Meeting Notes.md" --content "\n## Action Items\n- [ ] Task 1\n- [ ] Task 2"

# 前置内容
obsidian-cli prepend "Notes/Meeting Notes.md" --content "# Updated Title\n\n"
```

### 3. 高级操作

#### 批量操作
```bash
# 批量添加标签
for file in Notes/*.md; do
  obsidian-cli append "$file" --content "\n#tag"
done
```

#### 模板应用
```bash
# 应用模板
obsidian-cli new "Projects/New Project.md" --template "Templates/Project Template.md"
```

## 💡 最佳实践

### 1. 库结构

典型的 Obsidian 库结构：
```
My Vault/
├── Notes/           # 笔记
├── Daily/           # 日报
├── Projects/        # 项目
├── Templates/       # 模板
├── .obsidian/       # 配置（不要手动修改）
└── Attachments/     # 附件
```

### 2. 自动化工作流

#### 每日创建日报
```bash
#!/bin/bash
# 每日创建日报笔记

today=$(date +%Y-%m-%d)
note_path="Daily/$today.md"

# 检查是否已存在
if [ ! -f "$note_path" ]; then
  obsidian-cli new "$note_path" --template "Templates/Daily Note.md"
  echo "✅ 创建日报: $note_path"
else
  echo "⚠️ 日报已存在: $note_path"
fi
```

#### 自动添加创建时间
```bash
#!/bin/bash
# 为笔记添加创建时间

note="$1"
created=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$note")

obsidian-cli prepend "$note" --content "---\ncreated: $created\n---\n\n"
```

### 3. 多库管理

```bash
# 工作库
WORK_VAULT="$HOME/Documents/Work Vault"

# 个人库
PERSONAL_VAULT="$HOME/Documents/Personal Vault"

# 根据需要切换
obsidian-cli set-default "Work Vault"
```

## 🎯 常见用途

### 1. 自动化会议记录
```bash
# 创建会议笔记
meeting_title="Weekly Standup"
date=$(date +%Y-%m-%d)
note_path="Meetings/${date} - ${meeting_title}.md"

obsidian-cli new "$note_path" --content "# ${meeting_title}\n\n**Date**: ${date}\n\n## Attendees\n- \n\n## Agenda\n- \n\n## Notes\n\n## Action Items\n- [ ] "
```

### 2. 项目跟踪
```bash
# 创建项目笔记
project_name="New Feature"
note_path="Projects/${project_name}.md"

obsidian-cli new "$note_path" --template "Templates/Project Template.md"
```

### 3. 知识库管理
```bash
# 批量添加标签
topic="AI"
for file in Notes/*${topic}*.md; do
  obsidian-cli append "$file" --content "\n#${topic}"
done
```

## ⚠️ 注意事项

1. **配置文件** - `.obsidian/` 目录由 Obsidian 管理，不要手动修改
2. **多库管理** - 使用配置文件查找活跃库，不要猜测路径
3. **路径格式** - 使用相对路径（相对于库根目录）
4. **备份** - 定期备份整个库目录

## 📖 详细文档

- **SKILL.md** - 完整使用指南
- **Obsidian 帮助**：https://help.obsidian.md
- **obsidian-cli**：https://github.com/yakitrak/obsidian-cli

## 📞 技术支持

- **Obsidian 社区**：https://forum.obsidian.md
- **GitHub**：https://github.com/zhaog100/openclaw-skills

## 📄 许可证

MIT License

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 思捷娅科技 (SJYKJ)

详见 [LICENSE](../../LICENSE) 文件。

---

*最后更新：2026-03-14*
