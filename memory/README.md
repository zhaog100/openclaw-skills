# 记忆系统结构说明

## 📚 Collections组织

### 1. daily-logs
- **路径**: memory/*.md
- **用途**: 日常记忆日志
- **文件**: 3个（2026-02-14.md, 2026-02-26.md, install-tasks.md）
- **更新**: 每日自动更新

### 2. knowledge-base
- **路径**: knowledge/**/*.md
- **用途**: 专业知识库
- **文件**: 12个
- **分类**:
  - 项目管理（PMP、敏捷、项目规划）
  - 软件测试（自动化、管理、工具）
  - 内容创作（公众号、视频、策略）

### 3. workspace
- **路径**: *.md
- **用途**: 工作空间根目录文件
- **文件**: 0个（暂无）

## 🔍 搜索策略

### 按类型搜索
```bash
# 搜索日常记忆
qmd search "关键词" -c daily-logs

# 搜索专业知识
qmd search "PMP" -c knowledge-base

# 搜索所有
qmd search "项目管理"
```

### 推荐使用场景
1. **回忆工作内容**: daily-logs
2. **查询专业知识**: knowledge-base
3. **快速定位**: 使用精确关键词

## 📝 维护建议

### 日常维护
1. 每日创建记忆文件：memory/YYYY-MM-DD.md
2. 定期更新知识库文档
3. 重要决策记录到MEMORY.md

### 定期优化
1. 每周运行：`qmd update`
2. 每月运行：`qmd embed`
3. 定期清理过期文件

## 🎯 最佳实践

### 文件命名
- 日常记忆：YYYY-MM-DD.md
- 任务记录：task-name.md
- 主题文档：topic-name.md

### 内容组织
- 使用清晰的标题层级
- 添加emoji标记重要内容
- 使用标签分类（如 #project, #testing）

### 搜索技巧
- 关键词搜索：适合精确查找
- 向量搜索：适合模糊查询（需要embeddings）
- 混合搜索：最佳质量（需要embeddings）

---

*创建时间：2026年2月26日*
