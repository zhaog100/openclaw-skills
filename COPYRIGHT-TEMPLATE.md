# 版权声明模板（技能发布专用）

---

## 📜 标准版权声明（推荐）

```markdown
## 📜 版权与许可

**许可证：** MIT License（个人免费）/ 商业授权（企业付费）

**使用条款：**
- ✅ 个人使用：完全免费
- ✅ 允许修改和重新分发
- ⚠️ 需注明出处：原作者 米粒儿 (miliger)
- ❌ 商业使用：需购买商业授权

**商业授权：**
- 小微企业：¥999/年
- 中型企业：¥4,999/年
- 大型企业：¥19,999/年
- 源码买断：¥99,999（一次性）

**版权所有：** © 2026 米粒儿 (miliger)  
**原文链接：** https://clawhub.ai/skill/技能名  
**授权查询：** miliger@example.com
```

---

## 📝 package.json 配置

```json
{
  "name": "技能名",
  "version": "1.0.0",
  "author": "米粒儿 (miliger)",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/miliger/技能名"
  },
  "homepage": "https://clawhub.ai/skill/技能名",
  "keywords": ["openclaw", "skill", "miliger"],
  "copyright": "© 2026 米粒儿 (miliger). All rights reserved.",
  "commercialUse": {
    "personal": "free",
    "business": "paid",
    "contact": "miliger@example.com"
  }
}
```

---

## 📄 SKILL.md 头部声明

```markdown
---
name: 技能名
version: 1.0.0
author: 米粒儿 (miliger)
license: MIT
copyright: © 2026 米粒儿 (miliger)
commercialUse: paid
contact: miliger@example.com
description: 技能描述
---

# 技能名

## 📜 版权说明

- **个人使用：** 免费（需注明出处）
- **商业使用：** 需购买授权（¥999 起/年）
- **版权所有：** © 2026 米粒儿 (miliger)
- **授权咨询：** miliger@example.com

---
```

---

## 📖 README.md 底部声明

```markdown
---

## 📜 版权信息

**License:** MIT (个人免费 / 企业付费)  
**Copyright:** © 2026 米粒儿 (miliger)  
**Author:** 米粒儿 (miliger)  
**Contact:** miliger@example.com

**商业授权：**
- 小微企业：¥999/年
- 中型企业：¥4,999/年
- 大型企业：¥19,999/年
- 源码买断：¥99,999（一次性）

[查看完整授权协议](../../LICENSE-COMMERCIAL.md)
```

---

## 🏷️ 技能包内声明文件

创建 `LICENSE` 文件：

```
MIT License

Copyright (c) 2026 米粒儿 (miliger)

个人使用免费，商业使用需授权。

详见：LICENSE-COMMERCIAL.md
```

创建 `COMMERCIAL-LICENSE.md` 文件：

```markdown
# 商业授权说明

本技能采用双重授权模式：

1. **个人使用：** MIT License（免费）
2. **商业使用：** 需购买商业授权

**授权费用：**
- 小微企业：¥999/年
- 中型企业：¥4,999/年
- 大型企业：¥19,999/年

**联系我们：** miliger@example.com
```

---

## ✅ 发布前检查清单

- [ ] package.json 添加 author/license/copyright
- [ ] SKILL.md 添加版权声明
- [ ] README.md 添加版权信息
- [ ] 创建 LICENSE 文件
- [ ] 创建 COMMERCIAL-LICENSE.md
- [ ] ClawHub 发布时填写正确许可证
- [ ] 添加联系方式

---

**模板版本：** v1.0  
**更新时间：** 2026-03-11  
**适用技能：** 米粒儿全部技能
