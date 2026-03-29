# AIHubMix 免费模型接入指南

_2026-03-02 学习自废囧囧文章_

---

## 🎯 平台简介

**AIHubMix** - 提供免费AI模型API接口
- 网址：https://aihubmix.com/
- 支持模型：GPT-4.1、GLM 5、MiniMax M2.5、Gemini 3 Flash等
- 完全免费，无需付费

---

## 📝 注册流程

**步骤1：注册账号**
1. 访问：https://aihubmix.com/
2. 点击 "sign up"
3. 使用邮箱或GitHub/Google账号注册

**步骤2：获取API Key**
- 注册成功后自动下发token
- 点击Key进行复制
- 格式：`sk-xEAlqFr****2`

---

## 🔧 配置信息

**正确的配置：**
```
base_url: https://aihubmix.com/v1
api_key: 你的API Key
```

**⚠️ 重要更正：**
- ❌ 错误：`https://api.aihubmix.com/v1`
- ✅ 正确：`https://aihubmix.com/v1`

---

## 🎁 免费模型列表

**识别规则：**
- 所有带 `-free` 关键字的都是免费模型

**免费模型示例：**
- `coding-glm-5-free`
- `gpt-4.1-free`
- `gpt-4o-free`
- `gemini-3-flash-preview-free`
- `glm-4.7-flash-free`
- 等等...

---

## ⚡ 速率限制（RPM/RPD）

**GPT系列：**
- RPM（每分钟请求数）：无限制
- RPD（每日请求数）：无限制

**国产系列（GLM、MiniMax等）：**
- RPM：5次/分钟
- RPD：500次/天

**谷歌系列（Gemini）：**
- RPD：250次/天

---

## 🛠️ OpenClaw 配置示例

**配置文件：** `~/.openclaw/openclaw.json`

```json
{
  "models": {
    "providers": {
      "aihubmix": {
        "base_url": "https://aihubmix.com/v1",
        "api_key": "YOUR_API_KEY",
        "api": "openai-completions",
        "models": [
          {
            "id": "coding-glm-5-free",
            "name": "Coding GLM-5"
          },
          {
            "id": "gpt-4.1-free",
            "name": "GPT-4.1"
          },
          {
            "id": "gpt-4o-free",
            "name": "GPT-4o"
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "coding-glm-5-free"
      }
    }
  }
}
```

**重启服务：**
```bash
openclaw onboard --install-daemon
```

---

## 💡 使用建议

**模型选择：**
- **编程任务** → `coding-glm-5-free`
- **日常对话** → `gpt-4.1-mini-free`
- **复杂推理** → `gpt-4.1-free` 或 `gpt-4o-free`
- **图像理解** → `gemini-3.1-flash-image-preview-free`
- **长文本** → `kimi-for-coding-free`

**注意限制：**
- 国产模型：5 RPM / 500 RPD（注意控制频率）
- Gemini：250 RPD（每天250次）
- GPT系列：无限制（优先使用）

---

## 📊 当前配置状态

**已配置（2026-03-02）：**
- ✅ Provider：aihubmix
- ❌ base_url：错误（需更新）
- ⏳ API Key：待官家获取

**待更新：**
1. 修改 `openclaw.json` 中的 `base_url`
2. 添加官家的API Key
3. 重启Gateway服务

---

## 🔗 相关链接

- 官网：https://aihubmix.com/
- 文档：https://docs.aihubmix.com/en/quick-start
- 原文：废囧囧《免费gpt-4.1、glm 5、MiniMax m2.5以及Gemini 3 flash等》

---

*学习时间：2026-03-02 22:00*
*来源：废囧囧公众号文章*
