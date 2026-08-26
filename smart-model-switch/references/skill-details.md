# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License

# 智能模型切换 - 详细使用指南

_日期：2026-05-10 | 版本：v2.0.0_

> MIT License · Copyright (c) 2026 思捷娅科技 (SJYKJ) · 创建者：小米粒 (PM + Dev)

---

## 📋 目录

1. [完整文件类型映射](#1-完整文件类型映射)
2. [模型配置详解](#2-模型配置详解)
3. [复杂度评分算法](#3-复杂度评分算法)
4. [使用示例](#4-使用示例)
5. [子代理模型选择配置](#5-子代理模型选择配置)
6. [故障排查](#6-故障排查)
7. [最佳实践](#7-最佳实践)

---

## 1. 完整文件类型映射

### 1.1 文件类型 → 模型映射表

| 文件类型 | 扩展名列表 | 专用模型 | 评分 | 说明 |
|----------|-----------|---------|------|------|
| **Vision (多模态)** | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`, `.tiff`, `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm` | `agnes/agnes-2.0-flash` (多模态备用) | - | 图片/视频识别 |
| **Coding (代码)** | `.js`, `.jsx`, `.ts`, `.tsx`, `.py`, `.java`, `.cpp`, `.c`, `.html`, `.css`, `.json`, `.xml`, `.yaml`, `.yml` | `agnes-2.0-flash` | - | 代码分析/生成 |
| **Complex (文档)** | `.pdf`, `.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx` | `agnes-2.0-flash` | - | 文档解析/深度分析 |
| **Main (常规)** | `.txt`, `.md`, `.csv` | `agnes-2.0-flash` | - | 普通文本处理 |

### 1.2 优先级规则

```
文件类型检测 > 消息特征检测 > 复杂度评分 > 默认模型
```

**示例**:
- 发送 `report.pdf` + "简单总结" → **Complex 模型** (文件类型优先)
- 发送 `script.py` + "这是什么" → **Coding 模型** (即使问题简单)
- 发送纯文本 "分析这个系统架构" → **Complex 模型** (关键词触发)

---


> **⚠️ 2026-06-10 清理**: 移除所有 glm-5, glm-5-turbo, zai/glm-5 引用。统一使用 agnes-2.0-flash + agnes/agnes-2.0-flash

## 2. 模型配置详解

### 2.1 完整模型列表

| 模型角色 | 模型 ID | 供应商 | 免费额度 | 适用场景 |
|---------|--------|--------|---------|---------|
| **Primary** | `agnes-2.0-flash` | Agnes AI | 付费 | 主力模型、代码/推理 |
| **Long-Context** | `agnes/agnes-2.0-flash` | Agnes AI | 免费 | 大上下文任务、备用模型 |

**Removed (2026-06-10)**: agnes-1.5-flash (Key无效), agnes-2.0-flash, agnes-2.0-flash, agnes-2.0-flash, agnes-2.0-flash, 智谱/GLM, MiniMax, OpenRouter |

### 2.2 自定义模型配置

编辑 `config/model-rules.json`：

```json
{
  "models": {
    "flash": {
      "id": "your-flash-model-id",
      "description": "简单任务专用"
    },
    "main": {
      "id": "your-main-model-id",
      "description": "常规对话"
    },
    // ... 其他模型
  }
}
```

**注意**: 修改配置后需要重启 OpenClaw 或重新加载技能。

---

## 3. 复杂度评分算法

### 3.1 评分维度

| 维度 | 权重 | 评分标准 |
|------|------|---------|
| **长度** | 30% | <50 字=1 分, 50-200 字=2 分, >200 字=3 分 |
| **关键词** | 40% | 1 个关键词=1 分, 2 个=2 分, 3 个+=3 分 |
| **代码** | 20% | 检测到代码=3 分, 无代码=0 分 |
| **视觉** | 10% | 检测到视觉关键词=3 分, 无=0 分 |

### 3.2 计算公式

```
总分 = 长度评分×0.3 + 关键词评分×0.4 + 代码评分×0.2 + 视觉评分×0.1
```

**示例计算**:
```
消息："请帮我分析这个架构图，并设计一个系统方案"

长度：20 字 → 1 分
关键词："分析"、"设计"、"系统"、"方案" → 4 个 → 3 分
代码：无 → 0 分
视觉："架构" → 1 个 → 1 分

总分 = 1×0.3 + 3×0.4 + 0×0.2 + 1×0.1 = 0.3 + 1.2 + 0 + 0.1 = 1.6 分
→ 选择 Flash 模型
```

### 3.3 关键词库

**复杂任务关键词** (编辑 `config/model-rules.json` → `complex_keywords`):

```json
[
  "分析", "设计", "架构", "深度", "详细", "全面", "系统", 
  "方案", "策略", "优化", "研究", "探讨", "文档", "PDF", "报告"
]
```

**视觉关键词** (`vision_keywords`):

```json
[
  "图片", "截图", "照片", "图像", "视频", "frame", "visual", 
  "image", "screenshot", "photo", "media", "attachment"
]
```

**代码模式** (`code_patterns`):

```json
[
  "function", "class", "def", "import", "export", "const", 
  "let", "var", "if", "for", "while", "return"
]
```

---

## 4. 使用示例

### 4.1 命令行测试

```bash
# 测试复杂度分析
cd skills/smart-model-switch/scripts
node analyze-complexity.js "请帮我分析这个系统架构"

# 输出示例:
{
  "message": "请帮我分析这个系统架构",
  "analysis": {
    "length": 12,
    "score": 1.6,
    "features": {
      "hasCode": false,
      "hasVision": false,
      "complexity": "simple",
      "keywords": ["分析", "架构", "系统"]
    },
    "breakdown": {
      "lengthScore": 1,
      "keywordScore": 3,
      "codeScore": 0,
      "visionScore": 1
    }
  },
  "selectedModel": "agnes/agnes-2.0-flash",
  "timestamp": "2026-05-10T00:46:38.123Z"
}
```

### 4.2 增强切换脚本

```bash
# 带文件测试
./smart-switch-enhanced.sh "分析这个视频内容" "/path/to/video.mp4"

# 输出:
# [INFO] 检测到视频文件 → Vision 模型
# [INFO] 关键词 "分析" → +1 分
# [RESULT] 最终选择：agnes/agnes-2.0-flash
```

### 4.3 日常使用场景

| 场景 | 消息示例 | 选择模型 | 原因 |
|------|---------|---------|------|
| 简单问答 | "今天天气怎么样" | Flash | 长度<50, 无关键词 |
| 常规分析 | "总结这篇文章的主要内容" | Main | 长度 50-200, 1 个关键词 |
| 代码审查 | "这段代码有 bug 吗？function test() {...}" | Coding | 检测到代码模式 |
| 图片识别 | "这张截图里显示什么？" + [图片] | Vision | 视觉关键词 + 图片文件 |
| 架构设计 | "设计一个高可用系统方案" | Complex | 3 个+ 复杂关键词 |

---

## 5. 子代理模型选择配置

### 5.1 任务类型 → 模型映射

编辑 `scripts/integrate-check.sh` 或配置 `config.json`:

```json
{
  "subagent": {
    "labelDetection": {
      "turbo": ["scan", "search", "monitor", "list", "check", "query"],
      "coding": ["develop", "coding", "fix", "debug", "refactor"],
      "complex": ["architecture", "design", "plan", "strategy"]
    },
    "defaultModel": "agnes-2.0-flash"
  }
}
```

### 5.2 sessions_spawn 使用示例

```bash
# 扫描任务 → 用 turbo (省钱)
sessions_spawn --model agnes-2.0-flash --task "scan 所有日志文件"

# 编码任务 → 用 agnes-2.0-flash
sessions_spawn --model agnes-2.0-flash --task "develop 一个 API 接口"

# 架构设计 → 用 agnes-2.0-flash + thinking
sessions_spawn --model agnes-2.0-flash --thinking --task "design 系统架构"
```

### 5.3 省钱策略

| 任务类型 | 推荐模型 | 成本 | 理由 |
|---------|---------|------|------|
| 扫描/搜索 | `agnes-2.0-flash` | 低 | 快速完成 |
| 简单 Review | `agnes-2.0-flash` | 低 | 够用就好 |
| 编码/修复 | `agnes-2.0-flash` | 中 | 减少 bug，避免返工 |
| 架构设计 | `agnes-2.0-flash + thinking` | 高 | 深度思考，质量优先 |

**原则**: 默认用 turbo，只在需要时升级。

---

## 6. 故障排查

### 6.1 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 模型选择错误 | 关键词库不完整 | 编辑 `model-rules.json` 添加关键词 |
| Fallback 不触发 | 错误模式未匹配 | 检查错误信息是否包含 `timeout`/`500`/`429` |
| 上下文溢出 | compaction 未触发 | 手动运行 `/compact` 或检查 75% 阈值 |
| 模型锁定 | sessions.json 有 override | 运行 `model-guard.sh` 清理 |

### 6.2 日志查看

```bash
# 查看技能日志
tail -f ~/.openclaw/data/smart-model-switch/*.log

# 查看 Fallback 记录
grep "fallback" ~/.openclaw/data/smart-model-switch/*.log
```

### 6.3 手动测试 Fallback

```bash
# 模拟 API 错误
export MOCK_API_ERROR=true
node analyze-complexity.js "测试消息"

# 应该输出 Fallback 链
```

---

## 7. 最佳实践

### 7.1 配置优化

1. **定期 review 关键词库**
   ```bash
   # 每周检查一次，根据实际使用添加关键词
   # 如果某个任务经常被误判，添加相关关键词
   ```

2. **监控成本节省**
   ```bash
   # 记录每天的 token 使用量
   # 对比使用技能前后的成本
   ```

3. **自定义 Fallback Chain**
   ```json
   // 根据自己可用的模型调整
   {
     "fallbackChain": {
     // 根据自己可用的模型调整
     {
       "fallbackChain": {
         "agnes-2.0-flash": ["agnes/agnes-2.0-flash"],
         "agnes/agnes-2.0-flash": ["agnes-2.0-flash"]
       }
     }
     }
   }
   ```

### 7.2 性能优化

1. **冷却时间调整**
   - 默认 5 分钟错误冷却 → 可根据实际情况调整为 2-10 分钟
   - 默认 10 分钟模型冷却 → 高频错误可延长到 15 分钟

2. **上下文阈值调整**
   ```json
   {
     "context_thresholds": {
       "compaction": 70,    // 降低到 70% 更早触发
       "model_switch": 80,  // 降低到 80% 更早切换
       "new_session": 90
     }
   }
   ```

### 7.3 集成建议

1. **心跳集成**
   ```bash
   # 在 HEARTBEAT.md 中添加
   - 检查上下文使用率，>75% 触发 compaction
   - 检查 Fallback 日志，发现异常
   ```

2. **自动化测试**
   ```bash
   # 每周运行一次测试脚本
   ./scripts/test-all-models.sh
   ```

---

## 📞 技术支持

- GitHub Issues: https://github.com/zhaog100/openclaw-skills/issues
- ClawHub: https://clawhub.com
- 创建者：小米粒 (PM + Dev)

---

**最后更新**: 2026-05-10  
**文档版本**: v2.0.0
