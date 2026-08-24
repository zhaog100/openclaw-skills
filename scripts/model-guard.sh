#!/bin/bash
# model-guard.sh - 防止 session override 锁死模型
# 每5分钟运行，清理所有 session 的 modelOverride + auth-state cooldown
# by 小米椒 🌶️‍🔥 2026-04-16

SESSIONS_FILE="/root/.openclaw/agents/main/sessions/sessions.json"
AUTH_STATE_FILE="/root/.openclaw/agents/main/agent/auth-state.json"
LOG_FILE="/root/.openclaw/workspace/logs/model-guard.log"

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 清理 sessions.json 中的 override
if [ -f "$SESSIONS_FILE" ]; then
    CLEANED=$(python3 -c "
import json, sys
with open('$SESSIONS_FILE') as f:
    data = json.load(f)
count = 0
override_keys = ['modelOverride', 'providerOverride', 'authProfileOverride', 
                 'authProfileOverrideSource', 'authProfileOverrideCompactionCount',
                 'modelOverrideSource', 'fallbackNoticeActiveModel', 
                 'fallbackNoticeReason', 'fallbackNoticeSelectedModel',
                 'model', 'modelProvider']
for k, v in data.items():
    if isinstance(v, dict):
        for ok in override_keys:
            if ok in v:
                del v[ok]
                count += 1
with open('$SESSIONS_FILE', 'w') as f:
    json.dump(data, f, indent=2)
print(count)
" 2>&1)
    if [ "$CLEANED" != "0" ] && [ -n "$CLEANED" ]; then
        log "Cleaned $CLEANED override fields from sessions.json"
    fi
fi

# 清理 auth-state cooldown
if [ -f "$AUTH_STATE_FILE" ]; then
    python3 -c "
import json
with open('$AUTH_STATE_FILE') as f:
    data = json.load(f)
for k in list(data.get('usageStats', {}).keys()):
    stats = data['usageStats'][k]
    for field in ['errorCount', 'failureCounts', 'lastFailureAt', 'cooldownUntil', 'cooldownReason']:
        if field in stats: del stats[field]
with open('$AUTH_STATE_FILE', 'w') as f:
    json.dump(data, f, indent=2)
" 2>&1
fi
