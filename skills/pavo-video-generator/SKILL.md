---
name: "pavo-video-generator"
description: "Pavo大赛视频提示词生成技能，严格参照案例格式，确保东方神话风格"
---

# 🎬 Pavo大赛视频提示词生成技能

> 用于生成符合Pavo大赛规范的东方神话风格AI视频提示词

---

## 📋 触发条件

当用户需要：
- 生成Pavo大赛视频提示词
- 创作东方神话风格AI视频
- 需要参照案例格式编写提示词

---

## 🎯 核心流程

### 1. 读取案例参考
必须读取已有的成功案例文件，理解格式规范：
- 案例文件位置：`projects/Pavo大赛/提示词_场景*_全新版.md`
- 重点关注：提示词公式、关键词详解、风格前缀

### 2. 确定提示词公式
```
[风格] + [环境] + [主体元素] + [动态细节] + [光影氛围] + [镜头]
```

### 3. 编写提示词
**必须包含的风格前缀**：
```
Chinese ink painting style, ink wash technique,
```

**东方神话专用术语**：
- `xianxia` - 仙侠
- `immortal cultivator` - 仙人
- `Taoist robe` - 道袍
- `flying sword` - 飞剑
- `qi` / `energy` - 气/能量
- 特定名称：`Tongtian Jiazhu`, `Wanxian Array`, `Jiejiao`

**禁止使用的西方元素**：
- ❌ Western dragon → ✅ Chinese dragon / 龙
- ❌ Medieval castle → ✅ Ancient Chinese palace
- ❌ European knight → ✅ Chinese immortal cultivator
- ❌ Gothic atmosphere → ✅ Chinese mystical atmosphere

### 4. 生成中英对照版
- 英文提示词用于视频生成
- 中文翻译用于文档存档
- 包含人物设定、台词、音效设计

### 5. 统计检查
- 总时长 ≤ 84秒（7片段×12秒）
- 每个片段 ≤ 12秒
- 词数 30-55词
- 东方元素 100%符合

### 6. 西方词汇扫描替换（文化一致性）
当需要替换西方末日/废土词汇为东方神话概念时：
```bash
# 扫描所有文件中的西方词汇
grep -rn "末日\|荒原\|post-apocalyptic\|wasteland\|apocalypse" projects/Pavo大赛/
```
**必须替换的词汇对照**：
| 西方词汇 | 东方替换 |
|---------|---------|
| 末日 / 焦土末日 | 天崩地裂 / 封神劫 |
| 荒原 / wasteland | 焦土 / scorched earth |
| post-apocalyptic | post-calamity / Heavenly Tribulation |
| apocalyptic | Heavenly Tribulation aftermath |
**执行步骤**：
1. 先用grep扫描所有受影响文件
2. 逐个文件edit，每次替换后验证
3. 最后再次grep确认无遗漏

---

## 📝 输出格式

### 提示词文件结构
```markdown
# 🎬 《作品名》第X集 - 优化版提示词

> 集数、总时长、风格、制作规范

## 📝 片段详情
### 片段N：标题（时间）
**视频提示词**：[英文提示词]
**人物设定**：[角色描述]
**台词**：[中文台词]
**音效设计**：[音效描述]

## 🎨 东方风格规范
[关键词表、禁止元素表]

## 📊 统计
[时长、片段数、词数等]
```

---

## ⚠️ 注意事项

1. **必须先读案例**：不允许凭空创作，必须参照已有成功案例
2. **风格前缀必须**：每个提示词必须以 `Chinese ink painting style, ink wash technique` 开头
3. **禁止西方元素**：严格排除 dragon, castle, knight, Gothic 等词汇
4. **镜头明确**：使用 `epic wide shot`, `macro close-up`, `medium shot` 等专业术语
5. **时长控制**：每个片段≤12秒，总时长≤84秒

---

## 📂 相关文件

- 案例文件：`projects/Pavo大赛/提示词_场景*_全新版.md`
- 规则详解：`projects/Pavo大赛/提示词规则详解.md`
- 输出文件：`projects/Pavo大赛/提示词_第X集_优化版_vN.md`

---

*MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)*
