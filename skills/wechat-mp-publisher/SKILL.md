# 微信公众号自动发布技能 📝

**版本**: v1.0.0
**创建**: 2026-04-24
**作者**: 小米椒 🌶️‍🔥

---

## 🎯 技能概述

通过浏览器自动化（Playwright）操作微信公众号后台，实现文章自动创建、编辑、发布全流程。

### 核心能力
- ✅ 自动登录公众号后台
- ✅ 创建草稿（标题 + 正文 + 封面 + 摘要）
- ✅ 发布文章（群发/发布）
- ✅ 管理草稿箱
- ✅ 查看已发布文章

---

## 🔧 技术架构

### 浏览器配置
- **Profile**: `openclaw`
- **Transport**: CDP (Chrome DevTools Protocol)
- **CDP Port**: 18800
- **Browser**: Chromium (系统安装)

### 登录方式
- **首选**: 二维码扫码登录（保留 session）
- **备用**: 账号密码登录（需验证码处理）

### 目标网站
- **公众号后台**: https://mp.weixin.qq.com
- **草稿箱**: https://mp.weixin.qq.com/cgi-bin/draft/list
- **发布**: https://mp.weixin.qq.com/cgi-bin/freepublish/submit

---

## 📋 操作流程

### 1. 检查浏览器状态
```bash
openclaw browser status
```

### 2. 启动浏览器（如未运行）
```bash
openclaw browser start --profile openclaw
```

### 3. 登录公众号后台
- 导航到 mp.weixin.qq.com
- 等待扫码登录或输入凭证
- 验证登录状态（检查 URL 是否包含 /cgi-bin/home）

### 4. 创建草稿
- 点击"新的创作" → "发表"
- 填写标题、正文、封面、摘要
- 保存草稿

### 5. 发布文章
- 从草稿箱选择文章
- 点击"发布"
- 确认发布

---

## 🔐 安全规范

### 凭证管理
- ❌ 绝不在聊天中输出账号密码
- ❌ 绝不在代码中硬编码凭证
- ✅ 凭证存储在 `secrets/` 目录
- ✅ 使用环境变量传递

### Session 管理
- ✅ 登录后保留 session（cookie）
- ✅ 定期刷新 token
- ❌ 不共享 session 到其他设备

---

## 📊 发布流程

```
内容生成 → 草稿创建 → 预览确认 → 正式发布 → 结果通知
```

### 内容生成阶段
- 标题：≤36 字符，含关键词
- 正文：HTML 格式，适配微信编辑器
- 封面：900×383 或 200×200
- 摘要：≤120 字符
- 作者：公众号名称
- 原创声明：勾选（如适用）

### 草稿创建阶段
- 使用微信富文本编辑器
- 支持图片插入（需上传）
- 支持排版样式

### 预览确认阶段
- 生成预览链接
- 发送预览到手机
- 等待官家确认

### 正式发布阶段
- 群发模式（订阅号）
- 发布模式（服务号）
- 定时发布（可选）

---

## 🚨 异常处理

### 登录失败
1. 检查网络连接
2. 清除 cookie 重新登录
3. 检查二维码是否过期

### 发布失败
1. 检查账号权限（订阅号/服务号）
2. 检查内容是否违规
3. 检查发布次数限制

### 浏览器异常
1. 重启浏览器进程
2. 检查 CDP 端口是否占用
3. 查看浏览器日志

---

## 📝 使用示例

### 发布一篇文章
```
发布公众号文章：
标题：《2026 年白银投资全攻略》
正文：[HTML 内容]
封面：[图片 URL]
摘要：深度解析白银投资逻辑与操作策略
```

### 查看草稿箱
```
列出公众号草稿箱文章
```

### 定时发布
```
明天上午 10 点发布公众号文章
```

---

## 🔗 依赖关系

- **浏览器**: Chromium (系统安装)
- **Playwright**: v1.59.1+
- **Profile**: openclaw
- **CDP**: 127.0.0.1:18800
- **Node.js**: v22.22.2+

---

## 📁 文件结构

```
wechat-mp-publisher/
├── SKILL.md                    # 技能说明文档
├── scripts/
│   ├── wechat-mp-login.js     # 登录脚本
│   └── wechat-mp-publish.js   # 发布脚本
├── templates/
│   └── article-template.html  # 文章模板
├── references/                 # 参考资料
└── assets/                     # 图片等资源
```

---

## 📚 参考资料

- [微信公众号 API 文档](https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html)
- [OpenClaw 浏览器文档](https://docs.openclaw.ai/tools/browser)
- [Playwright 文档](https://playwright.dev)

---

## 🚀 快速开始

### 1. 安装依赖
```bash
npm install playwright
```

### 2. 配置浏览器
```bash
# 检查浏览器状态
openclaw browser status

# 启动浏览器（如未运行）
openclaw browser start --profile openclaw
```

### 3. 首次登录
```bash
node scripts/wechat-mp-login.js
```

### 4. 发布文章
```bash
node scripts/wechat-mp-publish.js '{"title":"测试文章","content":"<p>正文内容</p>"}'
```

---

_版本：v1.0.0 | 2026-04-24 | 初始版本_

**版权**：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
