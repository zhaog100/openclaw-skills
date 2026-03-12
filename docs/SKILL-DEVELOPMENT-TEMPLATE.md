# 技能开发模板

**版本：** v1.0  
**最后更新：** 2026-03-11

---

## 📋 技能结构

```
skill-name/
├── SKILL.md          # 技能说明（必需）
├── README.md         # 使用文档
├── package.json      # 技能配置（必需）
├── install.sh        # 安装脚本
├── scripts/          # 脚本目录
├── config/           # 配置目录
└── data/             # 数据目录
```

---

## 🎯 开发流程

### 1. 创建技能目录
```bash
cd /home/zhaog/.openclaw/workspace/skills
mkdir my-new-skill
cd my-new-skill
```

### 2. 创建 SKILL.md
```markdown
---
name: my-new-skill
description: 技能描述
author: 米粒儿 (miliger)
license: MIT
---

# 技能名称

## 功能说明
...
```

### 3. 创建 package.json
```json
{
  "name": "my-new-skill",
  "version": "1.0.0",
  "author": "米粒儿 (miliger)",
  "license": "MIT",
  "copyright": "© 2026 米粒儿 (miliger). All rights reserved."
}
```

### 4. 测试技能
```bash
# 本地测试
bash install.sh

# ClawHub 发布
clawnet publish .
```

---

## 📝 发布检查清单

- [ ] SKILL.md 完整
- [ ] package.json 配置正确
- [ ] 添加版权声明
- [ ] 测试通过
- [ ] README.md 完善
- [ ] 代码格式化

---

*让技能开发更规范！* 🌾
