# 微信公众号草稿创建工具

**版本**：v1.5.0
**版权**：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

---

## 功能

- 自动生成商贸主题封面图（Playwright，900×383像素）
- 上传封面图到微信素材库
- 创建公众号草稿
- **微信API错误码详细提示**（40+常见错误）
- **兼容 Node.js 14+**
- **API调用超时保护**

## 安装依赖

```bash
npm install
```

## 使用方式

```bash
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

## 内容填充

```javascript
const { CONTENT_TEMPLATE, publishBusinessDraft } = require('./wechat-draft.js');

CONTENT_TEMPLATE.cover.title = '我的标题';
CONTENT_TEMPLATE.article.title = '文章标题';
CONTENT_TEMPLATE.article.content = '<p>文章HTML内容...</p>';

publishBusinessDraft();
```

## 超时设置

| API | 超时 |
|-----|------|
| access_token | 10秒 |
| 封面上传 | 30秒 |
| 草稿创建 | 20秒 |

## 兼容性

| Node.js | fetch | FormData |
|---------|-------|----------|
| 18+ | 原生fetch | form-data |
| < 18 | node-fetch | form-data |

---

*此工具为个人使用。*
