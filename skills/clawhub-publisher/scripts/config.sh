#!/bin/bash
# config.sh - 共享配置加载器
# 环境变量优先，其次 config.json，最后默认值

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="$SKILL_DIR/config.json"

# 从config.json加载（如果存在）
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        CLAWHUB_USER="${CLAWHUB_USER:-$(grep -oP '"clawhub_user"\s*:\s*"\K[^"]+' "$CONFIG_FILE")}"
        PUBLISH_JS_PATH="${PUBLISH_JS_PATH:-$(grep -oP '"publish_js_path"\s*:\s*"\K[^"]+' "$CONFIG_FILE")}"
        CLAWHUB_TEMP_BASE="${CLAWHUB_TEMP_BASE:-$(grep -oP '"temp_base"\s*:\s*"\K[^"]+' "$CONFIG_FILE")}"
        GITHUB_ORG="${GITHUB_ORG:-$(grep -oP '"github_org"\s*:\s*"\K[^"]+' "$CONFIG_FILE")}"
    fi

    # 默认值
    CLAWHUB_USER="${CLAWHUB_USER:-${USER}}"
    PUBLISH_JS_PATH="${PUBLISH_JS_PATH:-/usr/lib/node_modules/clawhub/dist/cli/commands/publish.js}"
    CLAWHUB_TEMP_BASE="${CLAWHUB_TEMP_BASE:-/tmp/clawhub}"
    GITHUB_ORG="${GITHUB_ORG:-openclaw}"
}
