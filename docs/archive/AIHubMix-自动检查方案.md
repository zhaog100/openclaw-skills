# AIHubMix模型自动检查方案

## 方案概述

由于技术限制，无法完全自动化检查AIHubMix官网，但可以采用**半自动方案**：

### 方案1: 定期提醒 + 手动检查（当前方案）
- ✅ 已配置：每周一10:00自动提醒
- 用户访问 https://aihubmix.com 手动检查
- 发现新模型后告知AI Agent自动添加

### 方案2: 脚本辅助检查
- 用户运行检查脚本
- 脚本自动爬取官网
- 对比现有配置，输出新模型列表

---

## 使用方式

### 方式1: 运行检查脚本

```bash
# 安装依赖（首次）
npm install playwright
npx playwright install chromium

# 运行检查
node scripts/check-aihubmix-models.js
```

**输出**:
- 截图: `aihubmix-screenshot.png`
- 页面文本: `aihubmix-page-text.txt`
- 对比报告: `aihubmix-models-report.json`

### 方式2: 手动检查

1. 访问 https://aihubmix.com
2. 查看免费模型列表
3. 对比以下已配置模型（14个）:

```
coding-glm-5-free
gemini-3.1-flash-image-preview-free
gemini-3-flash-preview-free
gpt-4.1-free
gpt-4.1-mini-free
gpt-4o-free
glm-4.7-flash-free
coding-glm-4.7-free
step-3.5-flash-free
coding-minimax-m2.1-free
coding-glm-4.6-free
coding-minimax-m2-free
kimi-for-coding-free
mimo-v2-flash-free
```

4. 发现新模型后告诉我

---

## 定时任务

### 当前任务（已配置）
- **时间**: 每周一 10:00
- **任务ID**: ac855289-aa3a-4dbc-9f33-9240b24d1f20
- **内容**: 提醒用户检查AIHubMix官网

### 任务消息
```
喏，官家！每周AIHubMix模型检查提醒：

## 📊 当前配置
- AIHubMix模型：14个
- 最后更新：2026-02-27

## 🎯 检查任务
请访问 https://aihubmix.com 检查：
1. 是否有新增免费模型
2. 是否有模型更新
3. 是否有模型下线

## 📝 如发现新模型
请提供模型信息：
- 模型ID（例如：new-model-free）
- 模型名称
- 特性描述

我将自动添加到配置中。
```

---

## 快速添加新模型

如果发现新模型，请提供以下信息：

### 最小信息
```
官家，发现新模型：
- 模型ID: new-model-free
- 模型名称: New Model Free
```

### 完整信息（推荐）
```
官家，发现新模型：
- 模型ID: new-model-free
- 模型名称: New Model Free
- 推理能力: 是/否
- 上下文窗口: 128000
- 最大输出: 4096
- 限制: 无限制/XXX次/天
```

我会立即添加到配置！

---

## 技术限制说明

### 为什么不能完全自动化？

1. **网站需要JavaScript渲染**
   - web_fetch工具只能获取静态HTML
   - 动态内容需要真实浏览器

2. **browser工具需要Chrome扩展**
   - 当前Chrome扩展未连接
   - 需要手动点击扩展图标

3. **可能有反爬机制**
   - 频繁访问可能被限制
   - 需要模拟真实用户行为

4. **页面结构可能变化**
   - 选择器需要维护
   - 脚本可能失效

---

## 最佳实践

### 推荐流程

1. **每周一10:00** - 收到自动提醒
2. **访问官网** - 浏览AIHubMix网站
3. **对比模型** - 检查是否有新增
4. **告知AI** - 提供新模型信息
5. **自动更新** - AI添加到配置

### 替代方案

如果需要更频繁的检查：
- 每天运行检查脚本
- 或调整定时任务频率（例如每天）

---

## 当前配置状态

### AIHubMix模型（14个）

**GLM系列**（4个）:
1. coding-glm-5-free
2. glm-4.7-flash-free
3. coding-glm-4.7-free
4. coding-glm-4.6-free

**GPT系列**（3个）:
5. gpt-4.1-free
6. gpt-4.1-mini-free
7. gpt-4o-free

**Gemini系列**（2个）:
8. gemini-3.1-flash-image-preview-free
9. gemini-3-flash-preview-free

**MiniMax系列**（2个）:
10. coding-minimax-m2.1-free
11. coding-minimax-m2-free

**其他**（3个）:
12. step-3.5-flash-free
13. kimi-for-coding-free
14. mimo-v2-flash-free

### 最后更新
- **日期**: 2026-02-27
- **来源**: 用户提供
- **状态**: 完整配置

---

**创建时间**: 2026-02-27 19:15
**维护者**: 小米辣（AI Agent）
