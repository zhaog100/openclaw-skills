# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/bin/bash
# model-guard.sh — 通用模型锁定守护
# 每5分钟由 crontab 调用，清理 sessions.json 和 auth-state.json 中的模型锁定状态
# 适用于所有模型厂商（Agnes AI 等）
#
# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
#
# 部署: crontab -e
#   */5 * * * * /path/to/skills/smart-model-switch/scripts/model-guard.sh >> /path/to/logs/model-guard.log 2>&1

set -euo pipefail

# ===== 配置 =====
OPENCLAW_HOME="${HOME}/.openclaw"
AGENT="main"
SESSIONS_FILE="${OPENCLAW_HOME}/agents/${AGENT}/sessions/sessions.json"
AUTH_STATE_FILE="${OPENCLAW_HOME}/agents/${AGENT}/agent/auth-state.json"
LOG_DIR="${OPENCLAW_HOME}/workspace/logs"
LOG_FILE="${LOG_DIR}/model-guard.log"

# 要从 sessions.json 各 session 清理的字段（11种）
SESSION_OVERRIDE_FIELDS=(
  "modelOverride"
  "providerOverride"
  "authProfileOverride"
  "authProfileOverrideSource"
  "authProfileOverrideCompactionCount"
  "modelOverrideSource"
  "fallbackNoticeActiveModel"
  "fallbackNoticeReason"
  "fallbackNoticeSelectedModel"
  "model"
  "modelProvider"
)

# 要从 auth-state.json 清理的字段
AUTH_STATE_FIELDS=(
  "errorCount"
  "failureCounts"
  "lastFailureAt"
  "cooldownUntil"
  "cooldownReason"
)

# ===== 日志 =====
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# ===== 主逻辑 =====
mkdir -p "$LOG_DIR"

# --- 1. 清理 sessions.json ---
cleaned_sessions=0
if [ -f "$SESSIONS_FILE" ]; then
  # 构建 jq 删除表达式
  del_expr=""
  for field in "${SESSION_OVERRIDE_FIELDS[@]}"; do
    del_expr+="del(.[] | select(type == \"object\") | .${field}) | "
  done
  # 去掉末尾的 " | "
  del_expr="${del_expr% | }"

  # 统计清理前的 override 数量
  FIELDS_CSV=$(IFS=,; echo "${SESSION_OVERRIDE_FIELDS[*]}")
  before_count=$(python3 -c "
import json,sys
fields = '$FIELDS_CSV'.split(',')
with open('$SESSIONS_FILE') as f:
    data = json.load(f)
count = 0
if isinstance(data, dict):
    for k, v in data.items():
        if isinstance(v, dict):
            for field in fields:
                if field in v:
                    count += 1
print(count)
" 2>/dev/null || echo "0")

  if [ "$before_count" -gt 0 ]; then
    # 备份
    cp "$SESSIONS_FILE" "${SESSIONS_FILE}.bak.$(date +%s)"

    FIELDS_CSV=$(IFS=,; echo "${SESSION_OVERRIDE_FIELDS[*]}")
    # 用 python3 清理（更可靠）
    python3 << PYEOF
import json

fields = "$FIELDS_CSV".split(',')
sessions_file = "$SESSIONS_FILE"
cleaned = 0

with open(sessions_file) as f:
    data = json.load(f)

if isinstance(data, dict):
    for k, v in data.items():
        if isinstance(v, dict):
            for field in fields:
                if field in v:
                    del v[field]
                    cleaned += 1

with open(sessions_file, 'w') as f:
    json.dump(data, f, indent=2)

print(cleaned)
PYEOF

    cleaned_sessions="$before_count"
    log "✅ sessions.json: 清理 ${cleaned_sessions} 个 override 字段"
  else
    log "ℹ️ sessions.json: 无需清理（0 个 override）"
  fi
else
  log "⚠️ sessions.json 不存在: $SESSIONS_FILE"
fi

# --- 2. 清理 auth-state.json ---
cleaned_auth=0
if [ -f "$AUTH_STATE_FILE" ]; then
  AUTH_FIELDS_CSV=$(IFS=,; echo "${AUTH_STATE_FIELDS[*]}")
  before_auth=$(python3 -c "
import json
with open('$AUTH_STATE_FILE') as f:
    data = json.load(f)
fields = '$AUTH_FIELDS_CSV'.split(',')
count = 0

def count_fields(obj, fields):
    c = 0
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in fields:
                c += 1
            c += count_fields(v, fields)
    return c

print(count_fields(data, fields))
" 2>/dev/null || echo "0")

  if [ "$before_auth" -gt 0 ]; then
    cp "$AUTH_STATE_FILE" "${AUTH_STATE_FILE}.bak.$(date +%s)"

    AUTH_FIELDS_CSV=$(IFS=,; echo "${AUTH_STATE_FIELDS[*]}")
    python3 << PYEOF
import json

fields = set("$AUTH_FIELDS_CSV".split(','))
auth_file = "$AUTH_STATE_FILE"
cleaned = 0

def clean_recursive(obj, fields):
    global cleaned
    if isinstance(obj, dict):
        for field in fields:
            if field in obj:
                del obj[field]
                cleaned += 1
        for k, v in list(obj.items()):
            clean_recursive(v, fields)
    elif isinstance(obj, list):
        for item in obj:
            clean_recursive(item, fields)

with open(auth_file) as f:
    data = json.load(f)

clean_recursive(data, fields)

with open(auth_file, 'w') as f:
    json.dump(data, f, indent=2)

print(cleaned)
PYEOF

    cleaned_auth="$before_auth"
    log "✅ auth-state.json: 清理 ${cleaned_auth} 个错误记录"
  else
    log "ℹ️ auth-state.json: 无需清理（0 个错误记录）"
  fi
else
  log "⚠️ auth-state.json 不存在: $AUTH_STATE_FILE"
fi

# --- 3. 汇总 ---
total=$((cleaned_sessions + cleaned_auth))
if [ "$total" -gt 0 ]; then
  log "🔄 总计清理 ${total} 个锁定字段（sessions: ${cleaned_sessions}, auth: ${cleaned_auth}）"
else
  log "✅ 所有模型状态正常，无需清理"
fi
