# QMD快速使用指南

## 🔍 搜索命令

### 日常记忆搜索
```bash
# 搜索今天的内容
qmd search "2026-02-26" -c daily-logs

# 搜索项目相关
qmd search "项目" -c daily-logs

# 搜索学习笔记
qmd search "学习" -c daily-logs
```

### 专业知识搜索
```bash
# 搜索PMP相关
qmd search "PMP" -c knowledge-base

# 搜索测试相关
qmd search "测试" -c knowledge-base

# 搜索敏捷方法
qmd search "敏捷" -c knowledge-base
```

### 全局搜索
```bash
# 搜索所有collections
qmd search "关键词"

# 限制结果数量
qmd search "项目管理" -n 3
```

## 📂 查看文件

### 列出collections
```bash
qmd collection list
```

### 列出文件
```bash
# 日常记忆
qmd ls daily-logs

# 专业知识库
qmd ls knowledge-base
```

### 查看文档
```bash
# 查看具体文档
qmd get qmd://daily-logs/2026-02-26.md

# 查看部分内容
qmd get qmd://knowledge-base/test-document.md:1-20
```

## 🛠️ 维护命令

### 更新索引
```bash
# 更新所有collections
qmd update

# 更新特定collection
qmd update -c daily-logs
```

### 生成向量
```bash
# 首次生成（需要15-20分钟）
qmd embed

# 强制更新
qmd embed -f
```

### 系统状态
```bash
# 查看状态
qmd status

# 清理缓存
qmd cleanup
```

## 💡 使用技巧

### 搜索技巧
1. **精确匹配**: 使用引号 `"项目管理"`
2. **排除词**: 使用减号 `测试 -单元`
3. **多词搜索**: 用空格分隔 `PMP 认证`

### 文件命名
- 日常记忆: `YYYY-MM-DD.md`
- 主题文档: `topic-name.md`
- 任务记录: `task-name.md`

### 内容组织
- 使用清晰的标题
- 添加emoji标记
- 使用标签分类

## ⚡ 快速参考

### 最常用命令
```bash
# 1. 搜索知识
qmd search "关键词" -c knowledge-base

# 2. 查看日常记忆
qmd ls daily-logs

# 3. 更新索引
qmd update

# 4. 查看状态
qmd status
```

### 本地搜索工具
```bash
# 使用PowerShell脚本
.\search-knowledge.ps1 "关键词"
```

## 🎯 典型场景

### 场景1: 查找PMP相关信息
```bash
# 搜索PMP相关内容
qmd search "PMP" -c knowledge-base -n 5
```

### 场景2: 回忆昨天的工作
```bash
# 查看昨天的记忆
qmd get qmd://daily-logs/2026-02-25.md
```

### 场景3: 学习测试工具
```bash
# 搜索测试工具相关
qmd search "测试工具" -c knowledge-base
```

## 📞 获取帮助

### QMD帮助
```bash
# 查看帮助
qmd --help

# 查看命令帮助
qmd search --help
```

### 在线文档
- QMD GitHub: https://github.com/tobi/qmd
- pi-qmd: https://www.npmjs.com/package/pi-qmd

---

**提示**: 收藏此文件，随时查阅！

*创建时间：2026年2月26日*
