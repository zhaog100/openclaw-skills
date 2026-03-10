# OpenClaw 技能开发标准化文档

**版本**：v1.0.0  
**创建日期**：2026-03-10  
**参考**：社区最佳实践 + 自有技能经验

---

## 📋 目录

1. [技能模板结构](#1-技能模板结构)
2. [命名规范](#2-命名规范)
3. [SKILL.md 规范](#3-skillmd-规范)
4. [代码规范](#4-代码规范)
5. [测试规范](#5-测试规范)
6. [发布流程](#6-发布流程)
7. [版本管理](#7-版本管理)
8. [文档规范](#8-文档规范)

---

## 1. 技能模板结构

### 标准目录结构

```
<skill-name>/
├── SKILL.md                    # 必需：技能说明（元数据 + 使用指南）
├── README.md                   # 必需：详细说明
├── package.json                # 必需：依赖管理
├── install.sh                  # 推荐：安装脚本
├── .clawhubignore              # 推荐：ClawHub 忽略文件
├── _meta.json                  # 可选：元数据
│
├── scripts/                    # 推荐：执行脚本
│   ├── main.sh                 # 主脚本
│   ├── helper.sh               # 辅助脚本
│   └── setup.sh                # 配置脚本
│
├── config/                     # 推荐：配置文件
│   ├── default.json            # 默认配置
│   └── example.json            # 配置示例
│
├── src/                        # 可选：源代码
│   ├── index.js                # 入口文件
│   └── utils.js                # 工具函数
│
├── docs/                       # 可选：文档
│   ├── USAGE.md                # 使用指南
│   └── API.md                  # API 文档
│
├── tests/                      # 推荐：测试用例
│   ├── test-main.sh            # 主测试
│   └── fixtures/               # 测试数据
│
└── logs/                       # 可选：日志目录
    └── .gitignore              # 忽略日志文件
```

---

### 最小可行结构

```
<skill-name>/
├── SKILL.md          # 必需
├── README.md         # 必需
└── scripts/
    └── main.sh       # 至少一个执行脚本
```

---

## 2. 命名规范

### 技能命名

**格式**：`kebab-case`（短横线分隔）

**示例**：
```
✅ smart-model-switch      # 清晰描述功能
✅ image-content-extractor # 清晰描述功能
✅ quote-reader            # 简洁明了
❌ SmartModelSwitch        # 不要用驼峰
❌ skill_v1                # 不要带版本号
❌ my-awesome-skill        # 不要用个人前缀
```

---

### 文件命名

| 文件 | **命名** | **说明** |
|------|---------|---------|
| 技能说明 | `SKILL.md` | 全大写 |
| 说明文档 | `README.md` | 全大写 |
| 使用指南 | `USAGE.md` | 全大写 |
| 变更日志 | `CHANGELOG.md` | 全大写 |
| 脚本文件 | `*.sh` | 小写 + 短横线 |
| 配置文件 | `*.json` | 小写 + 短横线 |

---

### 函数命名

**Shell 脚本**：
```bash
# 使用小写 + 下划线
✅ check_dependencies()
✅ install_skill()
✅ cleanup_temp()
❌ CheckDependencies()    # 不要用大驼峰
❌ check-dependencies()   # 不要用短横线
```

**JavaScript**：
```javascript
// 使用小驼峰
✅ checkDependencies()
✅ installSkill()
❌ check_dependencies()   # 不要用下划线
❌ CheckDependencies()    # 不要用大驼峰
```

---

## 3. SKILL.md 规范

### 元数据格式

```markdown
---
name: <skill-name>                      # 必需：技能名称（kebab-case）
description: <简短描述>                  # 必需：50 字以内
version: <版本号>                        # 推荐：语义化版本
author: <作者>                           # 推荐：作者名
homepage: <主页链接>                     # 可选：GitHub/文档
metadata:                                # 可选：元数据
  clawdbot:
    emoji: "🔍"                         # 技能图标
    os: ["darwin", "linux"]             # 支持系统
    requires:
      bins: ["bun", "qmd"]              # 依赖命令
    install:
      - id: bun-qmd
        kind: shell
        command: "bun install -g https://github.com/tobi/qmd"
        bins: ["qmd"]
        label: "Install qmd via Bun"
---
```

---

### 内容结构

```markdown
# <技能名称>

_简短描述（50 字以内）_

## 🎯 核心功能

- ✅ 功能 1
- ✅ 功能 2
- ✅ 功能 3

## 🚀 使用方式

### 方法 1：命令行

```bash
<command>
```

### 方法 2：配置文件

```json
{
  "key": "value"
}
```

## 📋 配置说明

| 配置项 | **类型** | **默认值** | **说明** |
|--------|---------|-----------|---------|
| key1 | string | "default" | 说明 1 |
| key2 | number | 100 | 说明 2 |

## 📁 文件结构

```
<skill-name>/
├── scripts/
├── config/
└── ...
```

## 🧪 测试方法

```bash
# 运行测试
./scripts/test.sh
```

## 📝 变更日志

- v1.0.0 (2026-03-10) - 初始版本
```

---

## 4. 代码规范

### Shell 脚本规范

**头部注释**：
```bash
#!/bin/bash
# 技能名称：<skill-name>
# 功能描述：<简短描述>
# 作者：<作者>
# 版本：<版本号>
# 创建日期：<日期>
```

**变量命名**：
```bash
# 使用大写表示常量
readonly SKILL_NAME="my-skill"
readonly VERSION="1.0.0"

# 使用小写表示变量
local temp_file="/tmp/temp"
local retry_count=3
```

**错误处理**：
```bash
# 使用 set 增强错误处理
set -e          # 遇到错误立即退出
set -u          # 使用未定义变量时报错
set -o pipefail # 管道中任何命令失败则整个管道失败

# 错误处理函数
handle_error() {
    echo "❌ 错误：$1" >&2
    exit 1
}

# 使用示例
command || handle_error "命令执行失败"
```

---

### JavaScript 规范

**ES6+ 特性**：
```javascript
// 使用 const/let 代替 var
const SKILL_NAME = 'my-skill';
let retryCount = 3;

// 使用箭头函数
const processData = (data) => {
    return data.map(item => item.value);
};

// 使用模板字符串
const message = `技能 ${SKILL_NAME} 启动成功`;
```

**错误处理**：
```javascript
// 使用 try-catch
try {
    await processData();
} catch (error) {
    console.error('❌ 错误:', error.message);
    process.exit(1);
}

// 使用 async/await
async function main() {
    const result = await fetchData();
    return result;
}
```

---

## 5. 测试规范

### 测试文件结构

```
tests/
├── test-main.sh          # 主测试文件
├── test-config.sh        # 配置测试
├── test-scripts.sh       # 脚本测试
└── fixtures/             # 测试数据
    ├── input.json
    └── expected.json
```

---

### 测试用例模板

```bash
#!/bin/bash
# 测试文件：test-main.sh

# 引入测试框架
source ./test-framework.sh

# 测试用例：功能测试
test_feature_1() {
    local result=$(./scripts/main.sh --test)
    assert_equal "$result" "expected" "功能 1 测试"
}

test_feature_2() {
    local result=$(./scripts/main.sh --feature2)
    assert_contains "$result" "keyword" "功能 2 测试"
}

# 运行所有测试
run_tests
```

---

### 测试覆盖率

**目标**：
- ✅ 核心功能：100% 覆盖
- ✅ 主要功能：≥80% 覆盖
- ✅ 边缘功能：≥50% 覆盖

**检查命令**：
```bash
# 运行测试
npm test

# 检查覆盖率
npm run coverage
```

---

## 6. 发布流程

### 发布前检查清单

- [ ] SKILL.md 元数据完整
- [ ] README.md 文档完整
- [ ] 代码通过测试
- [ ] 版本号已更新
- [ ] CHANGELOG.md 已更新
- [ ] .clawhubignore 已配置
- [ ] 无敏感信息（API Key 等）

---

### ClawHub 发布步骤

**1. 准备发布文件**：
```bash
# 创建发布目录
mkdir -p dist/<skill-name>

# 复制必要文件
cp -r SKILL.md README.md package.json scripts/ config/ dist/<skill-name>/

# 排除不必要文件
echo "node_modules/" >> .clawhubignore
echo "logs/" >> .clawhubignore
echo "tests/" >> .clawhubignore
```

---

**2. 打包技能**：
```bash
# 进入发布目录
cd dist/<skill-name>

# 打包
tar -czf ../<skill-name>-v1.0.0.tar.gz .

# 返回上级
cd ..
```

---

**3. 发布到 ClawHub**：
```bash
# 使用 ClawHub CLI
clawhub publish <skill-name>-v1.0.0.tar.gz

# 或者手动上传
# 访问 https://clawhub.com/publish
# 上传 tar.gz 文件
# 填写发布信息
# 提交审核
```

---

**4. 验证发布**：
```bash
# 搜索技能
clawhub search <skill-name>

# 安装技能
clawhub install <skill-name>

# 验证功能
<skill-command> --test
```

---

## 7. 版本管理

### 语义化版本

**格式**：`MAJOR.MINOR.PATCH`

**规则**：
- **MAJOR**：不兼容的 API 变更
- **MINOR**：向后兼容的功能新增
- **PATCH**：向后兼容的问题修复

**示例**：
```
v1.0.0  - 初始发布
v1.0.1  - Bug 修复
v1.1.0  - 新增功能
v2.0.0  - 不兼容变更
```

---

### 变更日志格式

```markdown
# 变更日志

## [1.1.0] - 2026-03-10

### Added
- 新增功能 1
- 新增功能 2

### Changed
- 优化功能 3

### Fixed
- 修复 Bug 1
- 修复 Bug 2

### Removed
- 移除废弃功能

## [1.0.0] - 2026-03-01

### Added
- 初始版本
```

---

## 8. 文档规范

### README.md 结构

```markdown
# <技能名称>

_简短描述_

## ✨ 特性

- 特性 1
- 特性 2

## 🚀 快速开始

### 安装

```bash
clawhub install <skill-name>
```

### 配置

```json
{
  "key": "value"
}
```

### 使用

```bash
<command>
```

## 📋 详细说明

（详细功能说明）

## 🧪 测试

```bash
npm test
```

## 📝 变更日志

（版本历史）

## 🤝 贡献

（贡献指南）

## 📄 许可证

（许可证信息）
```

---

## 🎯 最佳实践总结

### 技能开发 Checklist

**开发前**：
- [ ] 明确技能功能定位
- [ ] 检查是否有重复技能
- [ ] 设计技能接口

**开发中**：
- [ ] 遵循命名规范
- [ ] 编写单元测试
- [ ] 完善文档注释

**发布前**：
- [ ] 通过所有测试
- [ ] 更新版本文档
- [ ] 清理临时文件

**发布后**：
- [ ] 监控使用情况
- [ ] 响应用户反馈
- [ ] 定期维护更新

---

**文档维护者**：米粒儿 🌾  
**最后更新**：2026-03-10  
**参考技能**：smart-model-switch/context-manager/quote-reader 等

---

*🌾 标准化开发，高质量技能*
