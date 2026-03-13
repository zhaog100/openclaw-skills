# Google Antigravity 配置指南

**版本**：v1.0.0  
**创建日期**：2026-03-10  
**目标**：配置 Google Antigravity 免费额度 + Skill 支持

---

## 🎯 Google Antigravity 简介

**什么是 Google Antigravity**：
- Google 推出的免费 AI 平台
- 集成 Gemini 系列、Claude Sonnet 4.5、Opus 4.5
- 提供免费算力额度（网友称"大慈善家"）
- 最近支持 Agent Skills（类似 OpenClaw 技能系统）

---

## 📋 配置步骤

### 步骤 1：安装 Gemini CLI

**官方安装方式**：
```bash
# 使用 npm 安装
npm install -g @google/gemini-cli

# 或者使用 pnpm
pnpm add -g @google/gemini-cli
```

**验证安装**：
```bash
gemini --version
```

---

### 步骤 2：配置 Google 账号

**登录 Google 账号**：
```bash
gemini auth login
```

**验证登录状态**：
```bash
gemini auth status
```

---

### 步骤 3：安装 Antigravity

**安装命令**：
```bash
npm install -g @google/antigravity
```

**验证安装**：
```bash
antigravity --version
```

---

### 步骤 4：配置 Skills 目录

**创建全局 Skills 目录**：
```bash
mkdir -p ~/.gemini/antigravity/skills/
```

**创建项目 Skills 目录**（可选）：
```bash
cd /home/zhaog/.openclaw/workspace
mkdir -p .agent/skills/
```

---

### 步骤 5：测试 Skill 功能

**创建测试 Skill**：
```bash
cat > ~/.gemini/antigravity/skills/test-skill.md << 'EOF'
# Test Skill

## Description
A simple test skill for Google Antigravity

## Usage
```
/test hello
```

## Response
Hello from Antigravity Skill!
EOF
```

**测试 Skill**：
```bash
antigravity run /test hello
```

---

## 🔗 与 OpenClaw 集成

### 方案 1：作为备用模型源 ⭐⭐⭐⭐

**配置思路**：
- OpenClaw 为主系统
- Antigravity 作为备用模型源
- 通过 exec 调用 Gemini CLI

**配置方法**：
```bash
# 创建 OpenClaw 技能
cat > /home/zhaog/.openclaw/workspace/skills/gemini-antigravity/SKILL.md << 'EOF'
---
name: gemini-antigravity
description: 使用 Google Antigravity 免费额度进行 AI 对话
---

# Gemini Antigravity 技能

使用 Google Antigravity 的免费额度进行 AI 对话。

## 使用方法

```bash
antigravity ask "你的问题"
```

## 适用场景

- 简单问答
- 代码生成
- 文本处理

## 注意事项

- 需要 Google 账号
- 有免费额度限制
EOF
```

---

### 方案 2：Skill 互认 ⭐⭐⭐⭐⭐

**配置思路**：
- OpenClaw 技能可以在 Antigravity 中使用
- Antigravity Skill 可以在 OpenClaw 中调用
- 共享技能生态

**实现方式**：
```bash
# 复制 OpenClaw 技能到 Antigravity
cp -r /home/zhaog/.openclaw/workspace/skills/smart-model-switch/* \
      ~/.gemini/antigravity/skills/

# 或者创建软链接
ln -s /home/zhaog/.openclaw/workspace/skills/smart-model-switch \
      ~/.gemini/antigravity/skills/smart-model-switch
```

---

### 方案 3：额度互补 ⭐⭐⭐⭐⭐

**配置思路**：
- OpenClaw 使用百炼/智谱（主力）
- Antigravity 使用 Google 免费额度（备用）
- 智能模型切换自动选择

**配置智能切换**：
```json
{
  "models": {
    "flash": {
      "id": "zai/glm-4.7-flash",
      "description": "快速响应"
    },
    "main": {
      "id": "zai/glm-5",
      "description": "主力模型"
    },
    "gemini": {
      "id": "antigravity/gemini-pro",
      "description": "Google 免费额度",
      "command": "antigravity ask"
    }
  }
}
```

---

## 💡 免费额度利用策略

### 策略 1：模型分流 ⭐⭐⭐⭐⭐

**简单任务** → Antigravity（Gemini）
- 快速问答
- 代码片段
- 文本处理

**复杂任务** → OpenClaw（百炼/智谱）
- 深度分析
- 长上下文
- 专业领域

---

### 策略 2：定时任务 ⭐⭐⭐⭐

**配置定时同步**：
```bash
# 每天凌晨 2 点，使用 Antigravity 整理记忆
0 2 * * * antigravity ask "整理今天的记忆" >> /tmp/antigravity-summary.md
```

---

### 策略 3：技能开发辅助 ⭐⭐⭐⭐⭐

**使用 Antigravity 开发技能**：
```bash
# 让 Antigravity 帮忙写技能代码
antigravity ask "帮我写一个 OpenClaw 技能，功能是..."

# 测试技能
antigravity ask "测试这个技能脚本..."
```

---

## 📊 额度对比

| 平台 | **免费额度** | **模型质量** | **适用场景** |
|------|------------|------------|-------------|
| **Google Antigravity** | 很多（网友评价） | ⭐⭐⭐⭐⭐ | 简单任务/代码生成 |
| **百炼 qwen3.5-plus** | 100 万上下文 | ⭐⭐⭐⭐⭐ | 主力模型/长上下文 |
| **智谱 glm-5** | 200K 上下文 | ⭐⭐⭐⭐⭐ | 主力模型/免费 |
| **AIHubMix** | 14 个免费模型 | ⭐⭐⭐⭐ | 备用模型 |

---

## 🚀 快速开始

### 一键配置脚本

```bash
#!/bin/bash
# setup-google-antigravity.sh

echo "=== 安装 Gemini CLI ==="
npm install -g @google/gemini-cli

echo "=== 安装 Antigravity ==="
npm install -g @google/antigravity

echo "=== 创建 Skills 目录 ==="
mkdir -p ~/.gemini/antigravity/skills/
mkdir -p .agent/skills/

echo "=== 登录 Google 账号 ==="
gemini auth login

echo "=== 配置完成 ==="
echo "使用方法：antigravity ask \"你的问题\""
```

---

## 📝 注意事项

### 1. 网络要求 ⚠️

**Google 服务需要代理**：
```bash
# 配置代理（如果需要）
export https_proxy="http://127.0.0.1:7890"
export http_proxy="http://127.0.0.1:7890"
```

---

### 2. 账号安全 ⚠️

**使用独立 Google 账号**：
- 建议使用专门的工作账号
- 不要使用个人主账号
- 定期备份重要数据

---

### 3. 额度限制 ⚠️

**虽然免费但有上限**：
- 每日请求次数限制
- 单次请求长度限制
- 建议合理分配使用

---

## 🎯 预期收益

**短期**（1 周）：
- ✅ 完成 Antigravity 配置
- ✅ 测试基本功能
- ✅ 开发 1-2 个测试技能

**中期**（1 个月）：
- ✅ 与 OpenClaw 集成
- ✅ 实现模型分流
- ✅ 节省 30%+ 主力模型额度

**长期**（3 个月）：
- ✅ 建立完整技能生态
- ✅ 充分利用免费额度
- ✅ 发布技能到社区

---

## 📚 参考资源

- **Gemini CLI 官方文档**：https://github.com/google-gemini/gemini-cli
- **Antigravity 官方文档**：https://github.com/google/antigravity
- **技能开发指南**：https://docs.google.com/antigravity/skills
- **社区讨论**：https://discord.gg/google-ai

---

**文档维护者**：小米辣 🌾  
**最后更新**：2026-03-10  
**下次审查**：2026-03-17

---

*🌾 充分利用免费额度，武装自己系统*
