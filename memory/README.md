<<<<<<< HEAD
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
=======
# 记忆系统说明

_2026-03-07 重构完成_

---

## 📂 系统结构

```
memory/
├── MEMORY.md              # 核心记忆（205行，8KB）
│   ├── 关于用户
│   ├── 关键决策
│   ├── 核心教训
│   ├── 核心洞察
│   └── 记忆系统结构
│
├── INDEX.md               # 快速导航（98行）
│   ├── 结构说明
│   ├── 快速查找（按主题/时间/关键词）
│   ├── 检索方法
│   └── 统计信息
│
├── milestones/            # 里程碑记录（6个文件，666行）
│   ├── system.md          # 系统配置（83行）
│   ├── skills.md          # 技能开发（80行）
│   ├── wool-gathering.md  # 薅羊毛系统（185行）
│   ├── context-monitor.md # 上下文监控（150行）
│   ├── moltbook.md        # Moltbook（94行）
│   └── tools.md           # 工具配置（74行）
│
├── episodic/              # 会话记忆（短期）
├── semantic/              # 语义记忆（QMD向量）
└── heartbeat-state.json   # 心跳状态
```

---

## 🎯 重构效果

| 指标 | 重构前 | 重构后 | 改善 |
|------|--------|--------|------|
| **MEMORY.md** | 1031行, 48KB | 205行, 8KB | **-83%** |
| **文件数量** | 1个 | 8个（含索引） | +700% |
| **主题分类** | 混合 | 6个明确分类 | ✅ |
| **检索效率** | 全量读取 | 按需读取 | **+90%** |
| **维护难度** | 高（大文件） | 低（模块化） | ✅ |

---

## 🔍 使用方法

### 1. 快速导航（推荐）

```bash
# 查看索引
read memory/INDEX.md

# 按主题查找
read memory/milestones/wool-gathering.md
```

### 2. QMD精准检索

```bash
# 搜索关键词
qmd search "京东" -c knowledge-base

# 混合搜索
qmd search "Token优化" --hybrid
```

### 3. Memory搜索

```bash
# 搜索MEMORY.md
memory_search "CPU模式"

# 获取片段
memory_get memory/milestones/system.md --from 10 --lines 20
```

---

## 📊 主题分布

- **系统相关**：83行（12.5%）
- **技能开发**：80行（12.0%）
- **薅羊毛**：185行（27.8%）
- **上下文监控**：150行（22.5%）
- **Moltbook**：94行（14.1%）
- **工具配置**：74行（11.1%）

---

## 🚀 下一步优化

1. ✅ **重构完成**（2026-03-07）
2. ⏳ **整合优化策略**：
   - Tiered Context Bucketing
   - Hazel_OC Token追踪
   - 结构化输出模板
3. ⏳ **实现Token追踪**
4. ⏳ **优化工具调用缓存**

---

*最后更新：2026-03-07*
>>>>>>> 4c8083cdd342607c75894cbd7c4bbc132b36e911
