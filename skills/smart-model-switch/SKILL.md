name: smart-model-switch
description: 智能模型自动切换 + 错误 Fallback。根据消息复杂度和文件类型自动选择最优模型（Flash/Main/Coding/Vision/Complex），API 失败时自动切换备用模型。Trigger on "模型切换", "智能模型", "自动选择模型", "model switch", "fallback", "模型降级".
version: 1.9.0

# 智能模型切换 v1.9.0

根据消息复杂度、文件类型自动选择最优模型，**API 失败时自动 Fallback 到备用模型**。

## v1.9.0 优化

### 1. 增强关键词规则库
- `forceComplex`: 架构设计、微服务、分布式等 → complex 模型
- `forceFlash`: 简单问候语、问句 → flash 模型
- `forceCoding`: 代码关键词、帮我写 → coding 模型
- `forceVision`: 图片视频格式 → vision 模型

### 2. 用户反馈学习机制
```bash
# 记录模型选择是否正确
./scripts/feedback-log.sh coding glm-5 yes
./scripts/feedback-log.sh analysis glm-5 no
```

### 3. 动态权重调整
```bash
# 每周自动运行，根据反馈调整权重
node scripts/dynamic-weight-adjust.js
```

### 4. 手动覆盖机制
```bash
# 手动指定模型
./scripts/manual-override.sh --task "代码开发" --model glm-5 --force

# 清除覆盖
./scripts/manual-override.sh --clear

# 查看状态
./scripts/manual-override.sh --show
```

## 🎯 选择规则

| 类型 | 模型 | 触发条件 |
|------|------|----------|
| Flash | LongCat-Flash-Lite | 简单问答、"你好"/"谢谢"等 |
| Main | LongCat-Flash-Chat | 常规对话 |
| Coding | glm-5.1 | 代码文件、"帮我写"等 |
| Vision | LongCat-Flash-Omni-2603 | 图片/视频相关 |
| Complex | LongCat-Flash-Thinking-2601 | 架构设计、深度分析 |

**优先级**：forceRule > complexityScore > defaultModel

## 测试结果

```
简单问答: "你好，今天天气怎么样？" → flash ✅
代码开发: "帮我写一个Python函数" → coding ✅  
复杂架构: "请设计微服务架构" → complex ✅
```

## 📚 详细文档

完整使用指南见 `references/skill-details.md`，包含：
- 文件类型 → 模型映射表
- 复杂度评分算法详解
- 子代理模型选择配置
- 故障排查指南
- 最佳实践

---

Copyright (c) 2026 思捷娅科技 — MIT License
