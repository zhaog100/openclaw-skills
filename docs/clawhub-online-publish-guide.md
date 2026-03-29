# ClawHub 在线发布指南

> 官家已发布12个技能，熟悉此流程 ✅

---

## 🎯 快速发布流程

### 步骤1：准备技能包

```bash
# 进入技能目录
cd ~/.openclaw/workspace/skills/<skill-name>

# 打包技能（排除不必要文件）
tar -czf ../<skill-name>.tar.gz \
  --exclude='*.tar.gz' \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='*.log' \
  .

# 查看打包大小（限制20MB）
ls -lh ../<skill-name>.tar.gz
```

### 步骤2：在线发布

1. **访问网站**
   - 打开：https://clawhub.ai
   - 登录你的账号

2. **发布技能**
   - 点击右上角 "Publish Skill"
   - 或访问：https://clawhub.ai/publish

3. **填写信息**
   - 上传 `.tar.gz` 文件
   - 技能名称（slug）
   - 版本号
   - 描述
   - 标签（可选）

4. **确认发布**
   - 检查预览
   - 点击 "Publish"

---

## 📋 必需文件

技能包必须包含：

```
<skill-name>/
├── SKILL.md          # 必需：技能说明
├── package.json      # 必需：元数据
├── README.md         # 推荐：详细文档
├── install.sh        # 推荐：安装脚本
└── scripts/          # 可选：功能脚本
    ├── *.sh
    └── *.js
```

### package.json 示例

```json
{
  "name": "miliger-context-manager",
  "version": "2.2.2",
  "description": "真实API监控 + 启动优化 + 无感会话切换",
  "author": "miliger",
  "license": "MIT",
  "keywords": ["context", "monitoring", "auto-switch"],
  "main": "SKILL.md"
}
```

---

## 🏷️ 命名规范

### 官方技能
```
格式：<功能名>
示例：qmd, playwright-scraper
```

### 个人定制技能
```
格式：miliger-<功能名>
示例：miliger-context-manager, miliger-qmd-manager
```

**你的技能统一使用：** `miliger-` 前缀 ✅

---

## 📊 版本管理

### 版本号格式
```
主版本.次版本.修订号
x.y.z
```

### 更新规则

| 变更类型 | 版本变化 | 示例 |
|---------|---------|------|
| 新功能 | x.(y+1).0 | 1.0.0 → 1.1.0 |
| Bug修复 | x.y.(z+1) | 1.1.0 → 1.1.1 |
| 重大变更 | (x+1).0.0 | 1.5.2 → 2.0.0 |

---

## 🚀 快速打包脚本

### 单个技能打包

```bash
#!/bin/bash
# 打包单个技能

SKILL_NAME=$1

if [ -z "$SKILL_NAME" ]; then
    echo "用法: ./pack-skill.sh <skill-name>"
    exit 1
fi

cd ~/.openclaw/workspace/skills/$SKILL_NAME

# 检查必需文件
if [ ! -f "SKILL.md" ]; then
    echo "❌ 缺少 SKILL.md"
    exit 1
fi

if [ ! -f "package.json" ]; then
    echo "❌ 缺少 package.json"
    exit 1
fi

# 打包
tar -czf ../${SKILL_NAME}.tar.gz \
  --exclude='*.tar.gz' \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='*.log' \
  .

SIZE=$(ls -lh ../${SKILL_NAME}.tar.gz | awk '{print $5}')
echo "✅ 打包完成: ${SKILL_NAME}.tar.gz ($SIZE)"
echo ""
echo "下一步："
echo "  1. 访问 https://clawhub.ai/publish"
echo "  2. 上传文件: ~/.openclaw/workspace/skills/${SKILL_NAME}.tar.gz"
```

### 批量打包所有技能

```bash
#!/bin/bash
# 批量打包所有技能

cd ~/.openclaw/workspace/skills

for dir in */; do
    SKILL_NAME=${dir%/}

    echo "打包 $SKILL_NAME..."

    cd $dir

    # 检查必需文件
    if [ -f "SKILL.md" ] && [ -f "package.json" ]; then
        tar -czf ../${SKILL_NAME}.tar.gz \
          --exclude='*.tar.gz' \
          --exclude='node_modules' \
          --exclude='.git' \
          --exclude='*.log' \
          .

        SIZE=$(ls -lh ../${SKILL_NAME}.tar.gz | awk '{print $5}')
        echo "  ✅ $SIZE"
    else
        echo "  ⏭️  跳过（缺少必需文件）"
    fi

    cd ..
done

echo ""
echo "✅ 批量打包完成"
echo "文件位置: ~/.openclaw/workspace/skills/*.tar.gz"
```

---

## 📝 发布检查清单

发布前确认：

- [ ] **SKILL.md** 存在且内容完整
- [ ] **package.json** 版本号已更新
- [ ] **README.md** 文档已更新
- [ ] **文件大小** < 20MB
- [ ] **技能名称** 使用 `miliger-` 前缀
- [ ] **版本号** 符合规范（x.y.z）

---

## 🔍 发布后验证

```bash
# 访问技能页面
https://clawhub.ai/skill/<skill-name>

# 安装测试
clawhub install <skill-name>
```

---

## ⚠️ 常见问题

### Q: 文件太大（>20MB）？
A: 排除不必要文件
```bash
tar -czf skill.tar.gz \
  --exclude='node_modules' \
  --exclude='*.log' \
  --exclude='.git' \
  .
```

### Q: 发布失败？
A: 检查
- package.json 格式
- SKILL.md 是否存在
- 网络连接

### Q: 如何更新技能？
A: 
1. 修改版本号
2. 重新打包
3. 上传新版本

---

## 📊 你已发布的技能

| 技能名称 | 最新版本 | 发布ID | 发布日期 |
|---------|---------|--------|---------|
| miliger-context-manager | v2.2.2 | k9720rgt... | 2026-03-06 |
| smart-model-switch | v1.3.0 | k97383tn... | 2026-03-05 |
| smart-memory-sync | v1.0.0 | k9791azg... | 2026-03-06 |
| quote-reader | v1.1.0 | k9789dba... | 2026-03-05 |
| image-content-extractor | v2.0.0 | k97dazj7... | 2026-03-06 |

**总计：12个技能** ⭐⭐⭐⭐⭐

---

## 🎯 快速命令

```bash
# 打包单个技能
cd ~/.openclaw/workspace/skills/<skill-name>
tar -czf ../<skill-name>.tar.gz --exclude='*.tar.gz' --exclude='node_modules' .

# 查看大小
ls -lh ../<skill-name>.tar.gz

# 访问发布页面
# https://clawhub.ai/publish
```

---

*ClawHub 在线发布指南*
*版本：v1.0*
*适用于：clawhub.ai 平台*
