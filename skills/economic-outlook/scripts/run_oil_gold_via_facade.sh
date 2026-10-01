#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 通过经济分析门面调度器触发 oil_gold 微技能（统一平台推送）
# open_id 由 cron --command-env 注入，不进代码
set -u
WS="$HOME/.openclaw/workspace"
EO="$WS/skills/economic-outlook"
export PYTHONPATH="$WS/skills/economic-outlook/shared:$WS/skills/economic-outlook/signals:$WS/skills/economic-outlook/outcomes"
cd "$EO"
python3 - <<'PY' 2>/dev/null
import sys, os, logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
sys.path.insert(0, os.getcwd()); sys.path.insert(0, 'shared')
from orchestrator.registry import get_registry
reg = get_registry()
ctx = {'qq_target_user_id': os.environ.get('QQ_TARGET_USER_ID','')}
r = reg.get('oil_gold').execute(ctx)
# 只记日志，不向 stdout 输出技术状态（避免刷到 QQ 提醒）
if not r.success:
    log.error('oil_gold 失败: %s', r.error)
else:
    log.info('oil_gold 门面调度完成, push=%s', r.data.get('push', {}))
PY
