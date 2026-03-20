---
name: error-handler
description: 通用错误处理库。为所有技能提供统一的错误处理、告警过滤、日志记录。支持 GraphQL 警告过滤、Python 安全调用、API 重试、Git 安全操作。
version: 1.3.0
---

# Error Handler Library v1.2

为所有技能提供统一的错误处理和告警过滤。

## 🚀 使用方式

```bash
# 加载库
source $(pwd)/skills/utils/error-handler.sh

# 日志函数
log_info "操作成功"
log_warn "缺少依赖，降级运行"
log_error "严重错误"
log_debug "调试信息"  # 需 ERROR_HANDLER_DEBUG=true

# 安全执行
safe_exec "command" "log_warn '降级'"
safe_python "script.py" "--arg" "log_warn '降级'"
safe_curl "https://api.example.com" "{}"        # 自动重试3次
safe_git_push "chore: update" "/path/to/workspace"
safe_gh "issue comment 16 --repo owner/repo --body '内容'"
safe_issue_comment "owner/repo" "16" "评论内容"
```

## 🔧 配置

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `ERROR_HANDLER_LOG` | `/tmp/error-handler.log` | 日志路径 |
| `ERROR_HANDLER_DEBUG` | `false` | 启用调试 |

## 📋 降级策略

- GraphQL警告 → 静默过滤
- Python依赖缺失 → 跳过功能继续运行
- API调用失败 → 重试3次返回默认值
- Git推送失败 → 本地保存下次重试

## 📁 结构

```
utils/
├── error-handler.sh          # 核心库（250行）
├── examples/usage-example.sh
└── tests/test-error-handler.sh  # 13个测试
```

> 详细集成示例、迁移清单、测试详情见 `references/skill-details.md`

---

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者：小米辣 (PM + Dev)

**商业使用授权**：
- 个人/开源：免费
- 小微企业（<10 人）：¥999/年
- 中型企业（10-50 人）：¥4,999/年
- 大型企业（>50 人）：¥19,999/年
- 源码买断：¥99,999 一次性

详情请查看：[LICENSE](../../LICENSE)
