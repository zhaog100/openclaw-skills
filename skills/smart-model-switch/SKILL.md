---
name: smart-model-switch
description: 智能模型自动切换。根据消息复杂度和文件类型自动选择最优模型（Flash/Main/Coding/Vision/Complex），提升响应质量和效率。Trigger on "模型切换", "智能模型", "自动选择模型", "model switch".
---

# 智能模型切换 v1.3

根据消息复杂度、文件类型自动选择最优模型。

## 🎯 选择规则

| 评分 | 模型 | 适用 |
|------|------|------|
| 0-3 | Flash | 简单问答、快速查询 |
| 4-6 | Main | 常规对话、分析任务 |
| - | Coding | 代码文件（.js/.py/.java等） |
| - | Vision | 图片/视频（.jpg/.png/.mp4等） |
| - | Complex | 文档（.pdf/.docx等） |
| 8-10 | Complex | 深度分析、架构设计 |
| 85%+ | Long-Context | 超长上下文（256k窗口） |

**优先级**：文件类型 > 消息特征 > 复杂度评分 > 默认模型

## 🚀 使用方式

```bash
# 安装
cd skills/smart-model-switch && bash install.sh

# 增强分析
./scripts/smart-switch-enhanced.sh "分析视频" "/path/to/video.mp4"

# AI集成（每次回复前自动执行）
scripts/integrate-check.sh
```

## 📁 文件结构

```
smart-model-switch/
├── scripts/
│   ├── analyze-complexity.js    # 消息复杂度分析
│   ├── analyze-file-type.js     # 文件类型分析
│   ├── smart-switch-enhanced.sh # 增强切换
│   └── integrate-check.sh       # AI集成
└── config/model-rules.json      # 模型规则配置
```

## ⚠️ 注意

- 上下文连续2次超85% → 自动提醒切换
- 切换后10分钟冷却期
- 评分维度：长度(30%) + 关键词(40%) + 代码(20%) + 视觉(10%)

## 🤖 子代理模型选择（Subagent Model Selection）

子代理默认用 `glm-5-turbo`，但应根据任务类型自动选模型：

### 任务类型 → 模型映射

| 任务类型 | 模型 | Thinking | 说明 |
|----------|------|----------|------|
| 扫描/搜索/监控 | `glm-5-turbo` | ❌ | 便宜快速，高吞吐 |
| Review/简单分析 | `glm-5-turbo` | ❌ | 够用就好 |
| 开发/编码/修复 | `glm-5` | ❌ | 质量优先，减少bug |
| 架构设计/重构 | `glm-5` | ✅ | 深度思考，复杂推理 |

### sessions_spawn 建议

spawn 子代理时，根据任务标签自动选模型：

```
标签含 scan/search/monitor → --model zai/glm-5-turbo
标签含 develop/coding/fix  → --model zai/glm-5
标签含 architecture/design → --model zai/glm-5 --thinking
无明确标签                → 默认 zai/glm-5-turbo（省钱）
```

**检测关键词**：配置见 `config.json` → `subagent.labelDetection`

### 省钱原则
- ✅ 简单任务用 turbo，省钱省时间
- ✅ 编码质量用 glm-5，避免返工浪费更多
- ✅ 默认 turbo，只在需要时升级
- ❌ 不要所有任务都用 glm-5

> 详细文件类型映射、模型配置、使用示例见 `references/skill-details.md`
