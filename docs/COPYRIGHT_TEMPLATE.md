# 技能版权声明模板

**创建时间**：2026-03-12 11:55
**创建者**：小米辣
**用途**：所有技能发布/更新时必须包含此版权声明

---

## 📋 标准版权声明

### 简短版（用于SKILL.md末尾）

```markdown
## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技/米粒儿

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com/skills/<技能名>
- 创建者: 小米辣/米粒儿
```

### 完整版（用于README.md末尾）

```markdown
## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技/米粒儿

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

### ⚠️ 重要声明

**免费使用、修改和重新分发时，需注明出处。**

**出处信息**：
- **GitHub仓库**：https://github.com/zhaog100/openclaw-skills
- **ClawHub页面**：https://clawhub.com/skills/<技能名>
- **创建者**：小米辣/米粒儿
- **联系方式**：GitHub Issues

**引用格式**：
```
来源：小米辣/米粒儿 - OpenClaw技能库
GitHub：https://github.com/zhaog100/openclaw-skills
许可证：MIT License
```

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🎯 适用范围

### 必须包含版权声明的文件

1. ✅ **SKILL.md** - 技能说明（必须包含简短版）
2. ✅ **README.md** - 详细文档（必须包含完整版）
3. ✅ **package.json** - 元信息（license字段）
4. ✅ **主脚本** - 代码文件头部注释

---

## 📝 版权声明位置

### 1. SKILL.md

**位置**：文件末尾

**示例**：
```markdown
## 📞 联系方式

- **GitHub Issue**：https://github.com/zhaog100/openclaw-skills/issues/2
- **创建者**：小米辣

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com/skills/demo-skill
- 创建者: 小米辣
```

### 2. README.md

**位置**：文件末尾（许可证章节）

**示例**：见上方完整版

### 3. package.json

**位置**：license字段

```json
{
  "name": "demo-skill",
  "license": "MIT",
  "copyright": "Copyright (c) 2026 思捷娅科技 - 免费使用、修改和重新分发时，需注明出处"
}
```

### 4. 主脚本（demo-skill.sh）

**位置**：文件头部注释

```bash
#!/bin/bash
# demo-skill - 双米粒协作系统演示技能
# 版本：v1.0.0
# 创建者：小米辣
# 创建时间：2026-03-12
#
# 版权声明：
# MIT License
# Copyright (c) 2026 思捷娅科技
# 免费使用、修改和重新分发时，需注明出处。
# GitHub: https://github.com/zhaog100/openclaw-skills
```

---

## 🔄 发布/更新检查清单

发布或更新技能时，必须检查：

- [ ] SKILL.md包含简短版权声明
- [ ] README.md包含完整版权声明
- [ ] package.json包含license字段
- [ ] 主脚本包含版权注释
- [ ] 注明出处：GitHub + ClawHub + 创建者

---

## 📊 版权模板变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `<年份>` | 发布年份 | 2026 |
| `<创建者>` | 创建者名称 | 小米辣/米粒儿 |
| `<技能名>` | 技能名称 | demo-skill |
| `<GitHub URL>` | GitHub仓库 | https://github.com/zhaog100/openclaw-skills |
| `<ClawHub URL>` | ClawHub页面 | https://clawhub.com/skills/demo-skill |

---

## 💡 注意事项

1. **所有新技能**：必须包含版权声明
2. **更新技能**：检查版权声明是否完整
3. **ClawHub发布**：在描述中包含版权声明
4. **Git提交**：在commit message中提及版权

---

*创建时间：2026-03-12 11:55*
*创建者：小米辣*
*用途：所有技能的版权声明标准*
