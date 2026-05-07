# 微信公众号草稿创建工具

**版权**：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

---

## 功能

- 自动生成商贸主题封面图
- 上传封面图到微信素材库
- 创建公众号草稿

## 使用方式

```bash
# 安装依赖
npm install playwright

# 运行脚本
node wechat-draft.js [credentials_path] [output_dir]

# 示例
node wechat-draft.js ./secrets/wechat-mp-credentials.json ./output
```

## 配置

创建 `secrets/wechat-mp-credentials.json`：

```json
{
  "account": {
    "appId": "your_app_id",
    "appSecret": "your_app_secret"
  }
}
```

## 依赖

- Node.js 18+
- Playwright
- 微信公众平台账号

---

*此工具为个人使用，不适合共享发布。*
