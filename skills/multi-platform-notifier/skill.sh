#!/bin/bash
# multi-platform-notifier - 多平台通知集成
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# GitHub: https://github.com/zhaog100/xiaomili-skills

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORMS_DIR="$SCRIPT_DIR/platforms"
CONFIG_FILE="$SCRIPT_DIR/config/platforms.conf"
LOG_FILE="$SCRIPT_DIR/logs/send.log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $*"
  echo -e "${GREEN}[INFO]${NC} $*"
  echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
}

log_error() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $*"
  echo -e "${RED}[ERROR]${NC} $*" >&2
  echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
}

log_warn() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] $*"
  echo -e "${YELLOW}[WARN]${NC} $*"
  echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
}

# 显示帮助
show_help() {
  cat << EOF
${BLUE}╔════════════════════════════════════════════════════════╗${NC}
${BLUE}║${NC}     multi-platform-notifier - 多平台通知集成          ${BLUE}║${NC}
${BLUE}╚════════════════════════════════════════════════════════╝${NC}

${YELLOW}用法:${NC}
  ./skill.sh <command> [options]

${YELLOW}命令:${NC}
  ${GREEN}send${NC}      发送通知消息
  ${GREEN}config${NC}    管理平台配置
  ${GREEN}test${NC}      测试平台连接
  ${GREEN}history${NC}   查看发送历史
  ${GREEN}help${NC}      显示此帮助信息

${YELLOW}发送命令:${NC}
  ./skill.sh send --platform <平台> --content <内容> [选项]
  
  选项:
    --platform, -p    目标平台 (wecom|dingtalk|feishu|all)
    --content, -c     消息内容
    --type, -t        消息类型 (text|markdown|card, 默认:text)
    --template, -T    使用模板 (alert|success|reminder)

  示例:
    ./skill.sh send -p wecom -c "系统告警：CPU 使用率 95%"
    ./skill.sh send -p all -c "重要通知"
    ./skill.sh send -p dingtalk -T alert --level 紧急 --message 服务器宕机

${YELLOW}配置命令:${NC}
  ./skill.sh config --list                  # 列出所有配置
  ./skill.sh config --add <平台> <webhook>  # 添加平台
  ./skill.sh config --remove <平台>         # 删除平台
  ./skill.sh config --test <平台>           # 测试连接

${YELLOW}历史命令:${NC}
  ./skill.sh history --limit 10             # 查看最近 10 条
  ./skill.sh history --status failed        # 查看失败记录
  ./skill.sh history --platform wecom       # 查看指定平台

${YELLOW}示例:${NC}
  # 发送文本消息到企业微信
  ./skill.sh send -p wecom -c "Hello World"
  
  # 发送到所有平台
  ./skill.sh send -p all -c "重要通知"
  
  # 使用告警模板
  ./skill.sh send -p wecom -T alert --level 紧急 --message 数据库连接失败

${BLUE}支持的平台:${NC}
  - 企业微信 (wecom)
  - 钉钉 (dingtalk)
  - 飞书 (feishu)

EOF
}

# 发送命令
cmd_send() {
  local platform=""
  local content=""
  local msg_type="text"
  local template=""
  local template_vars=()
  
  # 解析参数
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -p|--platform)
        platform="$2"
        shift 2
        ;;
      -c|--content)
        content="$2"
        shift 2
        ;;
      -t|--type)
        msg_type="$2"
        shift 2
        ;;
      -T|--template)
        template="$2"
        shift 2
        ;;
      --*)
        template_vars+=("$1=$2")
        shift 2
        ;;
      *)
        shift
        ;;
    esac
  done
  
  # 验证参数
  if [ -z "$platform" ]; then
    log_error "请指定平台 (--platform)"
    exit 1
  fi
  
  if [ -z "$content" ] && [ -z "$template" ]; then
    log_error "请指定内容 (--content) 或模板 (--template)"
    exit 1
  fi
  
  # 处理模板
  if [ -n "$template" ]; then
    content=$(render_template "$template" "${template_vars[@]}")
  fi
  
  # 发送到指定平台
  if [ "$platform" = "all" ]; then
    send_to_all "$content" "$msg_type"
  else
    send_to_platform "$platform" "$content" "$msg_type"
  fi
}

# 渲染模板
render_template() {
  local template_name="$1"
  shift
  local template_vars=("$@")
  
  local template_file="$SCRIPT_DIR/templates/${template_name}.json"
  
  if [ ! -f "$template_file" ]; then
    log_error "模板不存在：$template_name"
    exit 1
  fi
  
  # 读取模板
  local template_text
  template_text=$(jq -r '.template' "$template_file")
  
  # 替换变量
  local result="$template_text"
  for var in "${template_vars[@]}"; do
    local key="${var%%=*}"
    local value="${var#*=}"
    result="${result//\{\{${key}\}\}/$value}"
  done
  
  # 添加时间
  result="${result//\{\{time\}\}/$(date '+%Y-%m-%d %H:%M:%S')}"
  
  echo "$result"
}

# 发送到所有平台
send_to_all() {
  local content="$1"
  local msg_type="$2"
  
  local platforms=("wecom" "dingtalk" "feishu")
  local success_count=0
  local fail_count=0
  
  for platform in "${platforms[@]}"; do
    if send_to_platform "$platform" "$content" "$msg_type"; then
      ((success_count++))
    else
      ((fail_count++))
    fi
  done
  
  log_info "发送完成：成功 $success_count 个，失败 $fail_count 个"
  
  if [ $fail_count -gt 0 ]; then
    exit 1
  fi
}

# 发送到指定平台
send_to_platform() {
  local platform="$1"
  local content="$2"
  local msg_type="$3"
  
  # 获取 webhook
  local webhook
  webhook=$(get_webhook "$platform")
  
  if [ -z "$webhook" ]; then
    log_error "平台未配置：$platform"
    log_warn "使用 ./skill.sh config --add $platform <webhook> 添加配置"
    return 1
  fi
  
  log_info "正在发送消息到 $platform"
  
  # 加载平台适配器
  local adapter="$PLATFORMS_DIR/${platform}.sh"
  if [ ! -f "$adapter" ]; then
    log_error "平台适配器不存在：$adapter"
    return 1
  fi
  
  source "$adapter"
  
  # 调用发送函数
  local func_name="send_${platform}_message"
  if declare -f "$func_name" > /dev/null; then
    if $func_name "$webhook" "$content" "$msg_type"; then
      log_info "消息发送成功"
      return 0
    else
      log_error "消息发送失败"
      return 1
    fi
  else
    log_error "发送函数不存在：$func_name"
    return 1
  fi
}

# 获取 webhook
get_webhook() {
  local platform="$1"
  if [ -f "$CONFIG_FILE" ]; then
    grep "^${platform}=" "$CONFIG_FILE" 2>/dev/null | cut -d'=' -f2-
  fi
}

# 配置命令
cmd_config() {
  local action=""
  local platform=""
  local webhook=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --list|-l)
        action="list"
        shift
        ;;
      --add|-a)
        action="add"
        platform="$2"
        webhook="$3"
        shift 3
        ;;
      --remove|-r)
        action="remove"
        platform="$2"
        shift 2
        ;;
      --test|-t)
        action="test"
        platform="$2"
        shift 2
        ;;
      *)
        shift
        ;;
    esac
  done
  
  case "$action" in
    list)
      list_config
      ;;
    add)
      add_config "$platform" "$webhook"
      ;;
    remove)
      remove_config "$platform"
      ;;
    test)
      test_config "$platform"
      ;;
    *)
      echo "请指定操作：--list, --add, --remove, --test"
      exit 1
      ;;
  esac
}

# 列出配置
list_config() {
  echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║${NC}       平台配置列表                  ${BLUE}║${NC}"
  echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
  echo
  
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "配置文件不存在"
    return
  fi
  
  while IFS='=' read -r platform webhook; do
    [[ -z "$platform" || "$platform" =~ ^# ]] && continue
    
    # 脱敏显示
    local masked_webhook="${webhook:0:30}..."
    echo -e "${GREEN}$platform${NC}: $masked_webhook"
  done < "$CONFIG_FILE"
}

# 添加配置
add_config() {
  local platform="$1"
  local webhook="$2"
  
  if [ -z "$platform" ] || [ -z "$webhook" ]; then
    log_error "请指定平台和 webhook"
    exit 1
  fi
  
  # 创建配置目录
  mkdir -p "$(dirname "$CONFIG_FILE")"
  
  # 检查是否已存在
  if grep -q "^${platform}=" "$CONFIG_FILE" 2>/dev/null; then
    # 更新现有配置
    sed -i "s|^${platform}=.*|${platform}=${webhook}|" "$CONFIG_FILE"
    log_info "已更新配置：$platform"
  else
    # 添加新配置
    echo "${platform}=${webhook}" >> "$CONFIG_FILE"
    log_info "已添加配置：$platform"
  fi
  
  # 设置权限
  chmod 600 "$CONFIG_FILE"
}

# 删除配置
remove_config() {
  local platform="$1"
  
  if [ -z "$platform" ]; then
    log_error "请指定平台"
    exit 1
  fi
  
  if [ ! -f "$CONFIG_FILE" ]; then
    log_error "配置文件不存在"
    exit 1
  fi
  
  if grep -q "^${platform}=" "$CONFIG_FILE"; then
    sed -i "/^${platform}=/d" "$CONFIG_FILE"
    log_info "已删除配置：$platform"
  else
    log_warn "配置不存在：$platform"
  fi
}

# 测试配置
test_config() {
  local platform="$1"
  
  if [ -z "$platform" ]; then
    log_error "请指定平台"
    exit 1
  fi
  
  local webhook
  webhook=$(get_webhook "$platform")
  
  if [ -z "$webhook" ]; then
    log_error "平台未配置：$platform"
    exit 1
  fi
  
  log_info "测试连接到 $platform"
  
  # 发送测试消息
  local test_content="【连接测试】$(date '+%Y-%m-%d %H:%M:%S') - multi-platform-notifier"
  
  if send_to_platform "$platform" "$test_content" "text"; then
    echo -e "${GREEN}✓ 连接成功${NC}"
  else
    echo -e "${RED}✗ 连接失败${NC}"
    exit 1
  fi
}

# 历史命令
cmd_history() {
  local limit=20
  local status=""
  local platform=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --limit|-l)
        limit="$2"
        shift 2
        ;;
      --status|-s)
        status="$2"
        shift 2
        ;;
      --platform|-p)
        platform="$2"
        shift 2
        ;;
      *)
        shift
        ;;
    esac
  done
  
  if [ ! -f "$LOG_FILE" ]; then
    echo "暂无历史记录"
    return
  fi
  
  echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║${NC}       发送历史记录                  ${BLUE}║${NC}"
  echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
  echo
  
  local grep_pattern=""
  if [ -n "$status" ]; then
    grep_pattern="[$status]"
  fi
  
  if [ -n "$platform" ]; then
    grep_pattern="$grep_pattern $platform"
  fi
  
  if [ -n "$grep_pattern" ]; then
    grep "$grep_pattern" "$LOG_FILE" | tail -n "$limit"
  else
    tail -n "$limit" "$LOG_FILE"
  fi
}

# 主入口
case "${1:-help}" in
  send)
    cmd_send "${@:2}"
    ;;
  config)
    cmd_config "${@:2}"
    ;;
  test)
    cmd_config --test "${@:2}"
    ;;
  history)
    cmd_history "${@:2}"
    ;;
  help|--help|-h)
    show_help
    ;;
  *)
    log_error "未知命令：$1"
    show_help
    exit 1
    ;;
esac
