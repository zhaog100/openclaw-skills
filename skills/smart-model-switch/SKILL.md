---
name: smart-model-switch
description: 智能模型自动切换 + 错误 Fallback。根据消息复杂度和文件类型自动选择最优模型（Flash/Main/Coding/Vision/Complex），API 失败时自动切换备用模型。Trigger on "模型切换", "智能模型", "自动选择模型", "model switch", "fallback", "模型降级".
version: 1.8.0
---

# 智能模型切换 v1.8.0

根据消息复杂度、文件类型自动选择最优模型，**API 失败时自动 Fallback 到备用模型**。

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

## 🔄 Fallback 机制（v1.8.0 新增）⭐

当模型 API 返回错误（超时、500、429 等）时，自动按 chain 切换到备用模型：

### Fallback Chain

| 主模型 | 第1备选 | 第2备选 |
|--------|---------|---------|
| zai/glm-5 | qwen/qwen3.5-plus | bailian/kimi-k2.5 |
| zai/glm-5-turbo | zai/glm-5 | qwen/qwen3.5-plus |
| qwen/qwen3.5-plus | bailian/kimi-k2.5 | zai/glm-5 |
| bailian/qwen3-max | zai/glm-5 | qwen/qwen3.5-plus |
| bailian/kimi-k2.5 | qwen/qwen3.5-plus | zai/glm-5 |

### 错误检测

自动识别以下错误模式并触发 Fallback：
- `Something went wrong`（Gateway 内部错误）
- `timeout`（API 超时）
- `rate_limit` / `429`（限流）
- `500` / `502` / `503`（服务端错误）
- `overloaded`（过载）

### 冷却机制

- **错误冷却**：同一错误 5 分钟内不重复触发
- **模型冷却**：失败的模型 10 分钟内不再尝试
- **自动恢复**：冷却期结束后自动恢复原模型

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

## ⚠️ "Something went wrong" 防护机制

### 检测规则
当出现以下信号时，主动预防上下文溢出：
1. **上下文 > 75%** → 强制执行 compaction（`/compact`）
2. **上下文 > 85%** → 切换到大窗口模型（LongCat-Lite 320K）+ 强制 compaction
3. **上下文 > 90%** → 立即 `/new` 新会话 + 保存记忆
4. **API 返回 429/500** → 切换备用模型
5. **连续 2 次请求失败** → 自动切换模型 + 缩减上下文

### 自动恢复流程
```
错误检测 → 保存关键上下文到 memory/ → 切换模型 → 重试
失败 2 次 → compaction → 重试
失败 3 次 → /new 新会话
```

### 心跳集成
每次心跳检查上下文使用率，>75% 时自动触发 compaction。

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
>
> 通用模型锁定守护方案（model-guard.sh）见 `references/model-lock-guard.md`

---

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/example-user/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者：小米粒 (PM + Dev)

**商业使用授权**：
- 个人/开源：免费
- 小微企业（<10 人）：¥999/年
- 中型企业（10-50 人）：¥4,999/年
- 大型企业（>50 人）：¥19,999/年
- 源码买断：¥99,999 一次性

详情请查看：[LICENSE](../../LICENSE)
