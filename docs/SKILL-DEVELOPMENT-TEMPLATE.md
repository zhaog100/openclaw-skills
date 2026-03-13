# 技能开发标准化模板

_适用于 OpenClaw 技能开发的标准结构和最佳实践_

---

## 📁 标准目录结构

```
skill-name/
├── SKILL.md                 # 必需 - 技能定义文件
├── package.json             # 必需 - 技能元数据
├── README.md                # 推荐 - 使用说明
├── .gitignore              # 推荐 - Git 忽略配置
├── install.sh              # 可选 - 安装脚本
├── test.sh                 # 可选 - 测试脚本
├── core/                   # 可选 - 核心逻辑
│   ├── __init__.py
│   └── main.py
├── scripts/                # 可选 - 辅助脚本
│   └── helper.sh
├── config/                 # 可选 - 配置文件
│   └── default.json
├── modes/                  # 可选 - 多模式支持
│   ├── basic.py
│   └── advanced.py
├── logs/                   # 自动 - 日志目录（.gitignore）
├── data/                   # 可选 - 数据文件
└── examples/               # 可选 - 示例代码
```

---

## 📄 核心文件模板

### 1. SKILL.md

```markdown
# 技能名称

技能简要描述（1-2 句话）

## 触发条件

当用户提到以下关键词时触发：
- 关键词 1
- 关键词 2
- 关键词 3

## 功能说明

- 功能点 1
- 功能点 2
- 功能点 3

## 使用方法

\`\`\`bash
# 示例命令
skill-command [options]
\`\`\`

## 配置说明

如需配置，请在 SKILL.md 中说明配置项。

## 依赖项

- 依赖 1
- 依赖 2

## 注意事项

- 注意 1
- 注意 2

---

*版本：v1.0.0*
*作者：开发者名称*
*最后更新：YYYY-MM-DD*
```

### 2. package.json

```json
{
  "name": "skill-name",
  "version": "1.0.0",
  "description": "技能简要描述",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "test": "bash test.sh",
    "dev": "nodemon index.js"
  },
  "keywords": [
    "openclaw",
    "skill",
    "automation"
  ],
  "author": "开发者名称",
  "license": "MIT",
  "dependencies": {
    "package-name": "^1.0.0"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  }
}
```

### 3. README.md

```markdown
# 技能名称

## 简介

技能的详细介绍，包括用途、特点等。

## 功能特性

- ✅ 功能 1
- ✅ 功能 2
- ✅ 功能 3

## 安装方法

\`\`\`bash
# 方法 1：通过 OpenClaw 技能市场安装
openclaw skill install skill-name

# 方法 2：手动安装
git clone <repo-url>
cd skill-name
bash install.sh
\`\`\`

## 使用方法

\`\`\`bash
# 基本用法
skill-command [options]

# 示例
skill-command --help
\`\`\`

## 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| API_KEY | API 密钥 | 无 |
| TIMEOUT | 超时时间 | 30s |

## 示例

\`\`\`bash
# 示例 1：基本使用
skill-command

# 示例 2：带参数
skill-command --param value
\`\`\`

## 常见问题

### Q1: 问题描述
A: 解答内容

### Q2: 问题描述
A: 解答内容

## 更新日志

### v1.0.0 (YYYY-MM-DD)
- ✨ 初始版本发布

## 开发者

- 开发者名称 - [GitHub](链接)

## 许可证

MIT License
```

### 4. .gitignore

```gitignore
# 依赖
node_modules/
__pycache__/
*.pyc
venv/

# 日志
logs/
*.log

# 数据
data/*.json
!data/.gitkeep

# 配置（敏感信息）
.env
.env.local
config/local.json

# 临时文件
*.tmp
*.bak
.DS_Store

# 构建输出
dist/
build/
*.tar.gz
```

### 5. install.sh

```bash
#!/bin/bash
# 技能安装脚本

set -e

echo "🚀 安装技能：skill-name"

# 检查依赖
echo "📋 检查依赖..."
# if ! command -v python3 &> /dev/null; then
#     echo "❌ 需要安装 Python 3"
#     exit 1
# fi

# 安装依赖
echo "📦 安装依赖..."
# pip install -r requirements.txt
# npm install

# 创建必要目录
echo "📁 创建目录..."
mkdir -p logs data config

# 复制配置文件
if [ ! -f config/config.json ]; then
    echo "⚙️  创建默认配置..."
    cp config/default.json config/config.json
fi

# 设置权限
echo "🔐 设置权限..."
chmod +x scripts/*.sh 2>/dev/null || true

echo "✅ 安装完成！"
echo ""
echo "📖 使用说明："
echo "   skill-command [options]"
echo ""
echo "⚙️  配置文件：config/config.json"
```

### 6. test.sh

```bash
#!/bin/bash
# 技能测试脚本

set -e

echo "🧪 运行技能测试..."

# 测试 1：基本功能
echo "测试 1: 基本功能..."
# python3 -m pytest tests/test_basic.py

# 测试 2：边界条件
echo "测试 2: 边界条件..."
# python3 -m pytest tests/test_edge_cases.py

# 测试 3：集成测试
echo "测试 3: 集成测试..."
# bash tests/integration.sh

echo ""
echo "✅ 所有测试通过！"
```

---

## 🎯 开发规范

### 命名规范

- **目录名**：小写，连字符分隔（如：`skill-name`）
- **文件名**：小写，下划线分隔（如：`helper_function.py`）
- **函数名**：小写，下划线分隔（如：`get_data()`）
- **类名**：大驼峰（如：`SkillManager`）
- **常量**：全大写，下划线分隔（如：`MAX_RETRIES`）

### 代码规范

- **Python**: 遵循 PEP 8
- **JavaScript**: 遵循 ESLint 标准
- **Shell**: 遵循 ShellCheck 建议
- **注释**: 中文注释，清晰简洁

### 版本控制

- **版本号**: 语义化版本（MAJOR.MINOR.PATCH）
- **提交信息**: 类型 + 描述（如：`feat: 添加新功能`）
- **分支管理**: 
  - `master` - 主分支
  - `feature/xxx` - 功能分支
  - `fix/xxx` - 修复分支

---

## 📋 发布前检查清单

### 必需项
- [ ] SKILL.md 完整且准确
- [ ] package.json 版本正确
- [ ] README.md 使用说明清晰
- [ ] .gitignore 配置正确
- [ ] 无敏感信息泄露

### 推荐项
- [ ] install.sh 可正常执行
- [ ] test.sh 测试通过
- [ ] 代码注释完整
- [ ] 示例代码可用
- [ ] 错误处理完善

### 可选项
- [ ] 单元测试覆盖
- [ ] 集成测试通过
- [ ] 性能测试通过
- [ ] 文档站点更新

---

## 🚀 发布流程

1. **本地测试**
   ```bash
   bash test.sh
   ```

2. **打包技能**
   ```bash
   tar -czf skill-name-v1.0.0.tar.gz \
       --exclude='node_modules' \
       --exclude='logs' \
       --exclude='.git' \
       skill-name/
   ```

3. **发布到 ClawHub**
   ```bash
   clawnet publish skill-name-v1.0.0.tar.gz
   ```

4. **更新文档**
   - 更新 README.md 版本号
   - 更新 CHANGELOG.md
   - 提交 Git 标签

---

## 📚 参考资源

- [OpenClaw 技能开发文档](https://docs.openclaw.ai)
- [ClawHub 发布指南](../CLAWHUB-PUBLISH-GUIDE.md)
- [技能审查模板](../.clawhub/review_template.md)

---

*模板版本：v1.0.0*
*最后更新：2026-03-12*
*维护者：小米辣*
