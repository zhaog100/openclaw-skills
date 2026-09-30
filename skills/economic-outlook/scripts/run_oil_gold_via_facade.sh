#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 通过经济分析门面调度器触发 oil_gold 微技能（统一平台推送）
# open_id 由 cron --command-env 注入，不进代码
set -u
WS="$HOME/.openclaw/workspace"
EO="$WS/skills/economic-outlook"
export PYTHONPATH="$WS/skills/economic-outlook/shared:$WS/skills/economic-outlook/signals:$WS/skills/economic-outlook/outcomes"
cd "$EO"
python3 -c "
import sys, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, 'shared')
from orchestrator.registry import get_registry
reg = get_registry()
ctx = {'qq_target_user_id': os.environ.get('QQ_TARGET_USER_ID','')}
r = reg.get('oil_gold').execute(ctx)
print('门面调度 oil_gold:', 'OK' if r.success else r.error)
import json; print(json.dumps(r.data.get('push',{}), ensure_ascii=False))
"
