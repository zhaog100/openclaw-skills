---
name: error-handler
description: 通用错误处理库。为所有技能提供统一的错误处理、告警过滤、日志记录。支持 GraphQL 警告过滤、Python 安全调用、API 重试、Git 安全操作。推荐搭配 session-memory-enhanced 和 context-manager-v2 使用。
---

# Error Handler Library - 通用错误处理库

**版本**: v1.2  
**创建者**: 思捷娅科技 (SJYKJ)  
**更新时间**: 2026-03-16 14:10  
**用途**: 为所有技能提供统一的错误处理和告警过滤

---

## 💡 推荐依赖

为了获得最佳效果，推荐安装以下技能：

### 1. session-memory-enhanced
- **功能**: 长上下文记忆管理
- **作用**: 自动保存和检索记忆，支持向量检索
- **路径**: `skills/session-memory-enhanced/`
- **安装**: `source skills/session-memory-enhanced/install.sh`

### 2. context-manager-v2
- **功能**: 会话切换管理
- **作用**: 自动监控上下文使用率，达到阈值自动切换
- **路径**: `skills/context-manager-v2/`
- **安装**: `source skills/context-manager-v2/install.sh`

**一起使用效果更佳**：
- Error Handler Library 处理错误和日志
- session-memory-enhanced 管理记忆保存
- context-manager-v2 管理会话切换
- 三者协同工作，提供完整的错误处理和记忆管理能力

---

## 🎯 核心功能

### 1. 统一日志系统
- ✅ `log_info()` - 信息日志
- ✅ `log_warn()` - 警告日志
- ✅ `log_error()` - 错误日志
- ✅ `log_debug()` - 调试日志（可选）

### 2. 错误处理
- ✅ `handle_error()` - 统一错误处理（降级运行）
- ✅ 不中断流程
- ✅ 完整日志记录

### 3. 告警过滤
- ✅ GraphQL 弃用警告过滤
- ✅ Projects (classic) 警告过滤
- ✅ Python Warning/Deprecation 过滤
- ✅ Git hint 提示过滤

### 4. 安全执行
- ✅ `safe_exec()` - 安全执行任意命令
- ✅ `safe_python()` - Python 脚本安全调用
- ✅ `safe_curl()` - API 请求（自动重试 3 次）
- ✅ `safe_git_push()` - Git 安全推送
- ✅ `safe_gh()` - GitHub CLI 安全调用
- ✅ `safe_issue_comment()` - Issue 评论安全发布

---

## 📁 文件结构

```
utils/
├── error-handler.sh       # 核心库（250 行）
├── SKILL.md               # 本文档
├── package.json           # ClawHub 配置
├── examples/
│   └── usage-example.sh   # 使用示例
└── tests/
    └── test-error-handler.sh   # 单元测试（13 个）
```

---

## 🚀 使用方法

### 1. 加载库

```bash
source /home/zhaog/.openclaw/workspace/skills/utils/error-handler.sh
```

### 2. 使用日志函数

```bash
log_info "操作成功"
log_warn "缺少依赖，降级运行"
log_error "严重错误，已记录"
log_debug "调试信息"  # 需要设置 ERROR_HANDLER_DEBUG=true
```

### 3. 安全执行命令

```bash
# 过滤 GraphQL 警告
safe_exec "git push origin master" "log_warn '推送失败，本地已保存'"

# Python 脚本
safe_python "/path/to/script.py" "--arg value" "log_warn '使用降级方案'"

# API 请求（自动重试 3 次）
response=$(safe_curl "https://api.github.com/..." "{}")

# Git 推送
safe_git_push "chore: auto save" "/path/to/workspace"

# GitHub CLI
safe_gh "issue comment 16 --repo zhaog100/openclaw-skills --body '内容'"

# Issue 评论
safe_issue_comment "zhaog100/openclaw-skills" "16" "评论内容"
```

---

## 🔧 集成到其他技能

### 快速集成（3 步）

```bash
# 1. 在技能脚本开头加载库
source /home/zhaog/.openclaw/workspace/skills/utils/error-handler.sh

# 2. 替换原有日志函数
# 原来：log() { echo "$1" >> "$LOG_FILE"; }
# 现在：log_info "$1"

# 3. 替换命令执行
# 原来：git push origin master
# 现在：safe_git_push "chore: update"
```

### 示例：session-memory-enhanced

```bash
#!/bin/bash
# 加载错误处理库
ERROR_HANDLER_LOG="$LOG_FILE"  # 使用技能的日志文件
source /home/zhaog/.openclaw/workspace/skills/utils/error-handler.sh

# 使用安全函数
safe_python "$EXTRACTOR" "$part_file" "log_warn '降级运行'"
safe_git_push "chore: memory auto-save" "$WORKSPACE"
```

### 示例：context-manager-v2

```bash
#!/bin/bash
# 加载错误处理库
source /home/zhaog/.openclaw/workspace/skills/utils/error-handler.sh

# 使用安全函数
response=$(safe_curl "http://localhost:18789/sessions" "{}")
safe_gh "issue comment 16 --repo zhaog100/openclaw-skills --body '内容'"
```

### 迁移清单

| 旧代码 | 新代码 |
|--------|--------|
| `log "msg"` | `log_info "msg"` |
| `echo "warn" >&2` | `log_warn "warn"` |
| `command 2>&1 \| grep -v GraphQL` | `safe_exec "command"` |
| `python3 script.py 2>&1 \| grep -v Warning` | `safe_python "script.py"` |
| `git push 2>&1 \| grep -v hint` | `safe_git_push` |
| `curl -s $url` | `safe_curl "$url" "{}"` |

---

## 📋 配置说明

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ERROR_HANDLER_LOG` | `/tmp/error-handler.log` | 日志文件路径 |
| `ERROR_HANDLER_DEBUG` | `false` | 启用调试日志 |

### 错误降级策略

| 错误类型 | 处理方式 |
|---------|---------|
| GraphQL 警告 | 静默过滤 |
| Python 依赖缺失 | 跳过功能，继续运行 |
| API 调用失败 | 重试 3 次，返回默认值 |
| Git 推送失败 | 本地保存，下次重试 |
| 权限错误 | 记录日志，不中断 |

---

## 📊 测试

### 运行测试

```bash
cd /home/zhaog/.openclaw/workspace/skills/utils/tests
bash test-error-handler.sh
```

### 测试结果

```
总测试数：13
通过：13 ✅
失败：0
```

### 测试覆盖

- ✅ 日志函数（4 个）
- ✅ 错误处理（2 个）
- ✅ 安全执行（4 个）
- ✅ API 重试（2 个）
- ✅ Git 操作（1 个）

---

## 🎯 最佳实践

### 1. 始终使用安全函数

```bash
# ❌ 错误写法
git push origin master
python3 script.py
curl $url

# ✅ 正确写法
safe_git_push "chore: update"
safe_python "script.py"
safe_curl "$url" "{}"
```

### 2. 提供降级方案

```bash
# 始终提供 fallback
safe_exec "命令" "log_warn '失败，使用默认值'"
safe_curl "$url" "{}"  # 返回空 JSON
```

### 3. 记录完整日志

```bash
# 所有错误都会记录到日志文件
# 用户可以查看 /tmp/error-handler.log 排查问题
```

---

## 📝 许可证

MIT License  
Copyright (c) 2026 思捷娅科技 (SJYKJ)

---

*版本：v1.1*  
*最后更新：2026-03-16 13:28*  
*创建者：思捷娅科技 (SJYKJ)*
