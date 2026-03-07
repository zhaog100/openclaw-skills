# Memory Lite

_精简启动版 · 2-3KB · 快速加载_

---

## 👤 Quick Start

**官家（南仲）** | PMP认证 | 务实、高效

**米粒儿** | 精灵 | 🌾 | 16岁

**问候**：问"在？"→ "官家，我在这儿，随时待命！"

---

## 🎯 核心策略

### Token优化（92.5%节省）
```
1. memory_search() - 个人记忆
2. qmd search - 知识库
3. 只读必要的行 - 其他
```

### 模型优先级
```
1. zai/glm-5（官方，稳定）
2. deepseek/deepseek-chat（官方）
3. AIHubMix（免费，限流风险）
```

### 上下文预算（50k阈值）
```
5k - 指令目标
20k - 当前工作
10k - 最近历史
15k - 弹性空间
```

---

## 📊 Memory系统

### 结构
```
memory/
├── episodic/（原始经历）
│   └── YYYY-MM-DD.md
├── semantic/（提炼知识）
│   ├── decisions.md
│   ├── lessons.md
│   └── knowledge.md
└── MEMORY-LITE.md（本文件）
```

### 检索
```bash
# 搜索daily logs
qmd search "关键词" -c daily-logs

# 搜索知识库（混合模式）
qmd search "关键词" -c knowledge-base --hybrid

# 读取片段
qmd get qmd://path/to/file.md --from 10 --lines 20
```

---

## ⚙️ 系统配置

**软件安装**：D:\Program Files (x86)\

**输出目录**：Z:\OpenClaw\

**QMD**：CPU模式（QMD_FORCE_CPU=1）

**Context Monitor**：v5.0（智能分层，每5分钟）

---

## 🌾 薅羊毛

**青龙面板**：http://43.133.55.138:5700

**京东账号**：双账号（月收益70-170元）

**总收益**：100-270元/月

---

## 📚 快速参考

**MEMORY.md** → 长期记忆索引

**semantic/decisions.md** → 核心决策

**semantic/lessons.md** → 核心教训

**semantic/knowledge.md** → 通用知识

**episodic/YYYY-MM-DD.md** → 原始记录

---

*精简高效 · 快速启动 · 按需展开*
