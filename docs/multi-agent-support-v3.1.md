# Session-Memory Enhanced v3.1.0 - 多代理支持

**发布时间**：2026-03-07 22:06
**版本**：v3.1.0
**作者**：小米辣

---

## 🎯 核心改进（v3.1.0）

### ⭐ 多代理隔离 ⭐⭐⭐⭐⭐

**目录结构**：
```
memory/
├── agents/                    # 多代理目录
│   ├── main/                 # main 代理
│   │   ├── part001.json      # 固化分片
│   │   ├── part002.json
│   │   └── .tail.tmp.json    # 临时暂存
│   ├── research/             # research 代理
│   │   ├── part001.json
│   │   └── .tail.tmp.json
│   └── trial/                # trial 代理
│       ├── part001.json
│       └── .tail.tmp.json
├── shared/                    # 共享文档库
│   ├── knowledge-base.md
│   └── project-docs/
└── [其他现有文件]             # 保持兼容性
```

### ⭐ 检索权限控制 ⭐⭐⭐⭐

**配置文件**：`config/agents.json`

```json
{
  "agents": {
    "main": {
      "searchableStores": ["self", "shared", "research"]
    },
    "research": {
      "searchableStores": ["self", "shared"]
    },
    "trial": {
      "searchableStores": ["self"]
    }
  }
}
```

**权限说明**：
- `self`：只检索自己的记忆
- `shared`：检索共享文档库
- `agent_name`：检索指定代理的记忆（需授权）

### ⭐ 使用方式 ⭐⭐⭐⭐

**方式1：环境变量**
```bash
# main 代理（默认）
bash session-memory-enhanced-v3.1.sh

# research 代理
AGENT_NAME=research bash session-memory-enhanced-v3.1.sh

# trial 代理
AGENT_NAME=trial bash session-memory-enhanced-v3.1.sh
```

**方式2：OpenClaw 配置**
```json
{
  "agents": {
    "main": {
      "env": {
        "AGENT_NAME": "main"
      }
    },
    "research": {
      "env": {
        "AGENT_NAME": "research"
      }
    }
  }
}
```

---

## 📊 v3.0.0 vs v3.1.0

| 特性 | v3.0.0 | v3.1.0 | 提升 |
|------|--------|--------|------|
| 代理隔离 | ❌ | ✅ | 完全隔离 |
| 共享文档 | ❌ | ✅ | 统一管理 |
| 检索权限 | ❌ | ✅ | 精确控制 |
| 配置文件 | ❌ | ✅ | agents.json |
| 向后兼容 | ✅ | ✅ | 100%兼容 |

---

## 🚀 使用场景

### 场景1：主代理 + 研究代理
```
main 代理：
- 日常对话
- 任务管理
- 检索：self + shared + research

research 代理：
- 深度研究
- 知识整理
- 检索：self + shared
```

### 场景2：测试代理隔离
```
trial 代理：
- 新功能测试
- 实验性对话
- 检索：self（完全隔离）
```

### 场景3：共享知识库
```
shared 目录：
- 项目文档
- 知识库
- 模板文件

所有代理都可以访问（根据权限）
```

---

## 💡 技术亮点

### 1. 完全隔离
- 每个代理独立的 memory 目录
- 独立的 partNNN.json 文件
- 独立的 .tail.tmp.json

### 2. 灵活权限
- 支持跨代理检索（需授权）
- 共享文档库统一管理
- 可配置检索范围

### 3. 向后兼容
- 不影响现有功能
- 默认使用 main 代理
- 配置文件可选

---

## 📝 配置说明

### agents.json 配置

```json
{
  "agents": {
    "main": {
      "description": "主代理",
      "memoryEnabled": true,
      "searchEnabled": true,
      "searchableStores": ["self", "shared", "research"]
    },
    "research": {
      "description": "研究代理",
      "memoryEnabled": true,
      "searchEnabled": true,
      "searchableStores": ["self", "shared"]
    },
    "trial": {
      "description": "测试代理",
      "memoryEnabled": true,
      "searchEnabled": true,
      "searchableStores": ["self"]
    }
  },
  "shared": {
    "path": "memory/shared",
    "description": "共享文档库",
    "readableBy": ["main", "research", "trial"]
  },
  "defaults": {
    "memoryEnabled": true,
    "searchEnabled": true,
    "searchableStores": ["self"]
  }
}
```

### 配置字段说明

- `memoryEnabled`：是否启用记忆功能
- `searchEnabled`：是否启用搜索功能
- `searchableStores`：可检索的存储列表
  - `self`：自己的记忆
  - `shared`：共享文档库
  - `agent_name`：其他代理的记忆

---

## 🎯 未来优化

### v3.2.0
- [ ] AI 智能摘要
- [ ] 自动分类记忆
- [ ] 跨代理知识迁移

### v3.3.0
- [ ] 实时文件监控（inotify）
- [ ] 自动推送远程 Git
- [ ] 智能压缩历史提交

---

**版本历史**：
- v3.1.0 (2026-03-07)：多代理支持 ⭐⭐⭐⭐⭐
- v3.0.0 (2026-03-07)：不可变分片 + 会话清洗
- v2.1.0 (2026-03-07)：向量生成
- v2.0.0 (2026-03-07)：三位一体
- v1.0.0 (2026-03-07)：基础功能

---

**测试状态**：✅ **测试通过**

**核心功能**：
- ✅ 多代理隔离
- ✅ 共享文档库
- ✅ 检索权限控制
- ✅ 配置文件支持
- ✅ 向后兼容

**下一步**：发布到 ClawHub
