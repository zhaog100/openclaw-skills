# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/usr/bin/env bash
# _utils.sh - 跨平台兼容工具
# 每个 .sh 脚本开头执行: source "$(dirname "$0")/_utils.sh"
#
# 版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

# ── 操作系统检测 ────────────────────────────────────────────
detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux" ;;
        Darwin*)    echo "macos" ;;
        CYGWIN*)    echo "windows" ;;
        MINGW*)     echo "windows" ;;
        MSYS*)      echo "windows" ;;
        *)          echo "unknown" ;;
    esac
}

# ── 临时目录（跨平台）────────────────────────────────────────
get_temp_dir() {
    case "$(detect_os)" in
        windows)
            # Windows: 使用 TEMP 环境变量，fallback 到用户目录
            echo "${TEMP:-$USERPROFILE/AppData/Local/Temp}"
            ;;
        *)
            # Linux/macOS: /tmp
            echo "/tmp"
            ;;
    esac
}

# ── 状态文件路径（跨平台）────────────────────────────────────
# 用法: get_state_file "myapp-state.json" → /tmp/myapp-state.json (linux) 或 $TEMP/myapp-state.json (windows)
get_state_file() {
    local filename="$1"
    echo "$(get_temp_dir)/$filename"
}

# ── 锁文件路径（跨平台）──────────────────────────────────────
# 用法: get_lock_file "myapp.lock" → /tmp/myapp.lock (linux) 或 $TEMP/myapp.lock (windows)
get_lock_file() {
    local filename="$1"
    echo "$(get_temp_dir)/$filename"
}

# ── 日志目录（跨平台）────────────────────────────────────────
get_log_dir() {
    local log_name="${1:-bounty}"
    echo "$(get_temp_dir)/${log_name}-logs"
}

# ── 命令存在检测 ─────────────────────────────────────────────
has_command() {
    command -v "$1" >/dev/null 2>&1
}

# ── 确保临时目录存在 ─────────────────────────────────────────
ensure_temp_dir() {
    local td
    td="$(get_temp_dir)"
    if [ ! -d "$td" ]; then
        mkdir -p "$td" 2>/dev/null || true
    fi
}

# ── 原子写入锁（防并发）───────────────────────────────────────
# 用法: acquire_lock "myapp" && { ... ; release_lock "myapp"; } || echo "already running"
acquire_lock() {
    local lockfile
    lockfile="$(get_lock_file "$1.lock")"
    if [ -f "$lockfile" ]; then
        return 1  # 锁已存在
    fi
    echo "$$" > "$lockfile"
    return 0
}

release_lock() {
    local lockfile
    lockfile="$(get_lock_file "$1.lock")"
    rm -f "$lockfile"
}

# ── 调试模式 ─────────────────────────────────────────────────
# 用法: debug_echo "something" (仅 DEBUG=1 时输出)
debug_echo() {
    if [ "${DEBUG:-}" = "1" ]; then
        echo "[DEBUG] $*" >&2
    fi
}
