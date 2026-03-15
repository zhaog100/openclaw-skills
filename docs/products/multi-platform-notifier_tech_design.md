# 技术设计 - multi-platform-notifier

**版本**: v1.0  
**设计者**: 小米辣 (PM + Dev)  
**设计时间**: 2026-03-16 07:52  
**基于 PRD**: 2026-03-16_multi-platform-notifier_PRD.md

---

## 🏗️ 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户命令层                            │
│  ./skill.sh send|config|test|history [options]          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   主入口 (notifier.sh)                  │
│  - 参数解析  - 命令路由  - 错误处理  - 日志记录          │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼───────┐ ┌─▼─────────┐ ┌─▼──────────┐
│   wecom.sh    │ │dingtalk.sh│ │  feishu.sh │
│  (企业微信)   │ │  (钉钉)   │ │   (飞书)   │
└───────┬───────┘ └─────┬─────┘ └─────┬──────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
            ┌───────────▼───────────┐
            │      HTTP 请求         │
            │   (curl + jq)         │
            └───────────────────────┘
```

---

## 📁 文件结构

```
multi-platform-notifier/
├── skill.sh              # 主入口 (150 行)
├── platforms/            # 平台适配器目录
│   ├── base.sh          # 基础类 (50 行)
│   ├── wecom.sh         # 企业微信 (80 行)
│   ├── dingtalk.sh      # 钉钉 (80 行)
│   └── feishu.sh        # 飞书 (80 行)
├── templates/            # 消息模板
│   ├── alert.json       # 告警模板
│   ├── success.json     # 成功模板
│   └── reminder.json    # 提醒模板
├── config/
│   └── platforms.conf   # 平台配置
├── logs/
│   └── send.log         # 发送日志
├── SKILL.md             # 技能说明
├── README.md            # 使用文档
├── test.sh              # 测试脚本
└── package.json         # 包信息
```

---

## 🔧 核心实现

### 1. 主入口 (skill.sh)

```bash
#!/bin/bash
# multi-platform-notifier - 多平台通知集成
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/platforms/base.sh"

# 命令处理
case "$1" in
  send)
    cmd_send "${@:2}"
    ;;
  config)
    cmd_config "${@:2}"
    ;;
  test)
    cmd_test "${@:2}"
    ;;
  history)
    cmd_history "${@:2}"
    ;;
  *)
    show_help
    ;;
esac
```

### 2. 平台适配器基类 (platforms/base.sh)

```bash
#!/bin/bash

# 平台适配器基类
# 所有平台适配器必须继承此类

CONFIG_FILE="$SCRIPT_DIR/config/platforms.conf"
LOG_FILE="$SCRIPT_DIR/logs/send.log"

# 发送消息（抽象方法，子类必须实现）
send_message() {
  local platform="$1"
  local content="$2"
  local msg_type="${3:-text}"
  
  log_info "Sending $msg_type message to $platform"
}

# 记录日志
log_info() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $*" >> "$LOG_FILE"
}

log_error() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $*" >> "$LOG_FILE"
}

# 读取配置
get_webhook() {
  local platform="$1"
  grep "^${platform}=" "$CONFIG_FILE" | cut -d'=' -f2
}
```

### 3. 企业微信适配器 (platforms/wecom.sh)

```bash
#!/bin/bash

# 企业微信机器人适配器

send_wecom_message() {
  local webhook="$1"
  local content="$2"
  local msg_type="${3:-text}"
  
  local payload
  if [ "$msg_type" = "text" ]; then
    payload=$(cat <<EOF
{
  "msgtype": "text",
  "text": {
    "content": "$content"
  }
}
EOF
)
  fi
  
  local response
  response=$(curl -s -X POST "$webhook" \
    -H "Content-Type: application/json" \
    -d "$payload")
  
  local errcode
  errcode=$(echo "$response" | jq -r '.errcode')
  
  if [ "$errcode" = "0" ]; then
    log_info "WeCom message sent successfully"
    return 0
  else
    log_error "WeCom send failed: $response"
    return 1
  fi
}
```

### 4. 钉钉适配器 (platforms/dingtalk.sh)

```bash
#!/bin/bash

# 钉钉机器人适配器

send_dingtalk_message() {
  local webhook="$1"
  local content="$2"
  
  local payload
  payload=$(cat <<EOF
{
  "msgtype": "text",
  "text": {
    "content": "$content"
  }
}
EOF
)
  
  local response
  response=$(curl -s -X POST "$webhook" \
    -H "Content-Type: application/json" \
    -d "$payload")
  
  local errcode
  errcode=$(echo "$response" | jq -r '.errcode')
  
  if [ "$errcode" = "0" ]; then
    log_info "DingTalk message sent successfully"
    return 0
  else
    log_error "DingTalk send failed: $response"
    return 1
  fi
}
```

### 5. 飞书适配器 (platforms/feishu.sh)

```bash
#!/bin/bash

# 飞书机器人适配器

send_feishu_message() {
  local webhook="$1"
  local content="$2"
  
  local payload
  payload=$(cat <<EOF
{
  "msg_type": "text",
  "content": {
    "text": "$content"
  }
}
EOF
)
  
  local response
  response=$(curl -s -X POST "$webhook" \
    -H "Content-Type: application/json" \
    -d "$payload")
  
  local status
  status=$(echo "$response" | jq -r '.StatusCode')
  
  if [ "$status" = "0" ] || [ "$status" = "success" ]; then
    log_info "Feishu message sent successfully"
    return 0
  else
    log_error "Feishu send failed: $response"
    return 1
  fi
}
```

---

## 📊 数据库设计

### 配置文件格式 (platforms.conf)

```ini
# 平台 Webhook 配置
# 格式：platform=webhook_url

wecom=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
dingtalk=https://oapi.dingtalk.com/robot/send?access_token=xxx
feishu=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
```

### 日志格式 (send.log)

```
[2026-03-16 07:52:00] [INFO] Sending text message to wecom
[2026-03-16 07:52:01] [INFO] WeCom message sent successfully
[2026-03-16 07:52:05] [ERROR] DingTalk send failed: {"errcode":40001}
```

---

## 🎨 消息模板

### 告警模板 (templates/alert.json)

```json
{
  "name": "alert",
  "description": "系统告警通知",
  "template": "🚨【系统告警】\n时间：{{time}}\n级别：{{level}}\n内容：{{message}}",
  "variables": ["time", "level", "message"]
}
```

### 成功模板 (templates/success.json)

```json
{
  "name": "success",
  "description": "成功通知",
  "template": "✅【操作成功】\n时间：{{time}}\n内容：{{message}}",
  "variables": ["time", "message"]
}
```

---

## ✅ 测试计划

### 单元测试

```bash
# 测试企业微信发送
./test.sh --platform wecom --test send

# 测试钉钉发送
./test.sh --platform dingtalk --test send

# 测试飞书发送
./test.sh --platform feishu --test send
```

### 集成测试

```bash
# 测试全平台发送
./test.sh --platform all --test integration

# 测试配置管理
./test.sh --test config

# 测试模板渲染
./test.sh --test template
```

---

## 📦 依赖清单

| 依赖 | 版本 | 用途 |
|------|------|------|
| bash | 4.0+ | 脚本运行 |
| curl | 7.0+ | HTTP 请求 |
| jq | 1.5+ | JSON 处理 |

---

## 🔒 安全考虑

1. **Webhook 保护**: 配置文件权限设置为 600
2. **日志脱敏**: 不在日志中记录完整 Webhook URL
3. **错误处理**: 捕获所有 API 错误，避免泄露敏感信息

---

## 📈 扩展性设计

### 新增平台

1. 在 `platforms/` 目录创建新适配器
2. 实现 `send_<platform>_message()` 函数
3. 在 `skill.sh` 中添加路由

### 新增模板

1. 在 `templates/` 目录创建 JSON 文件
2. 定义模板内容和变量
3. 在发送命令中支持 `--template` 参数

---

*设计版本：v1.0*  
*最后更新：2026-03-16 07:52*  
*设计者：小米辣 (PM + Dev)*
