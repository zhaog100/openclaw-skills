# CLI Tool Generator (cligen)

> 🚀 快速创建 CLI 工具模板 - Bash/Python 支持

**版本**: v1.0.0 | **创建者**: 思捷娅科技 (SJYKJ) | **日期**: 2026-03-16

## 📋 简介

cligen 是一个 CLI 工具脚手架生成器，帮助快速创建结构完整、功能规范的命令行工具。支持 Bash 和 Python 两种语言，内置参数解析、帮助文档、错误处理和 Shell 自动补全。

## ✨ 核心特性

- 🎯 **快速生成** - 一条命令创建完整 CLI 工具骨架
- 🔧 **多语言支持** - Bash / Python 可选
- 📦 **开箱即用** - 包含参数解析、帮助文档、错误处理
- 🧪 **测试模板** - 内置测试脚本模板
- 🎨 **Shell 补全** - 支持 Bash/Zsh 自动补全
- 📚 **文档完整** - SKILL.md + README.md + 使用示例

## 🚀 快速开始

### 创建 Bash CLI 工具

```bash
cd $(pwd)/skills/cli-tool-generator
./cligen create --name mytool --lang bash --commands "status,deploy,config" --desc "我的部署工具"
```

### 创建 Python CLI 工具

```bash
cd $(pwd)/skills/cli-tool-generator
./cligen create --name mytool --lang python --commands "build,test,run" --desc "构建工具"
```

### 验证生成的工具

```bash
./cligen validate ./mytool/
```

## 📖 CLI 命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `create` | 创建新的 CLI 工具 | `cligen create --name mytool --lang bash --commands "cmd1,cmd2"` |
| `validate` | 验证 CLI 工具结构 | `cligen validate ./mytool/` |
| `help` | 显示帮助信息 | `cligen help` |

## 📦 安装

```bash
# 克隆或复制到本地
cd $(pwd)/skills/cli-tool-generator

# 添加执行权限
chmod +x cligen

# 添加到 PATH（可选）
ln -s $(pwd)/cligen ~/.local/bin/cligen
```

## 🧪 测试

```bash
# 运行完整测试
cd tests/
bash test_all.sh
```

## 📁 项目结构

```
cli-tool-generator/
├── cligen              # 主脚本
├── package.json        # 包配置
├── SKILL.md           # 技能文档
├── README.md          # 使用说明
├── src/               # 源代码模板
│   ├── bash_template/
│   └── python_template/
└── tests/             # 测试
    └── test_all.sh
```

## 💡 使用示例

### 示例 1：创建部署工具

```bash
./cligen create \
  --name deploy-tool \
  --lang bash \
  --commands "status,deploy,rollback,logs" \
  --desc "服务器部署工具"
```

生成后：
```bash
cd deploy-tool
./deploy-tool --help
./deploy-tool status
./deploy-tool deploy --env production
```

### 示例 2：创建构建工具

```bash
./cligen create \
  --name build-tool \
  --lang python \
  --commands "build,test,clean,watch" \
  --desc "项目构建工具"
```

## 🎯 生成的工具特性

- ✅ **参数解析** - 支持 `--help`, `--version`, 位置参数
- ✅ **命令系统** - 多命令支持，每个命令独立帮助
- ✅ **错误处理** - 统一错误码，友好的错误提示
- ✅ **日志输出** - 支持 INFO/WARN/ERROR 级别
- ✅ **退出码** - 成功返回 0，失败返回非 0
- ✅ **Shell 补全** - 自动生成 Bash/Zsh 补全脚本

## 📄 许可证

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/xiaomila-skills
- ClawHub: https://clawhub.com
- 创建者：思捷娅科技 (SJYKJ)

**商业使用授权**：
- 小微企业（<10 人）：¥999/年
- 中型企业（10-50 人）：¥4,999/年
- 大型企业（>50 人）：¥19,999/年
- 企业定制版：¥99,999 一次性（源码买断）

详情请查看：[LICENSE](../../LICENSE)

---

*cligen - 让 CLI 工具开发更高效* 🚀
