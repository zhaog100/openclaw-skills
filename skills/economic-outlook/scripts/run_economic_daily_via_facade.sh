#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 通过经济分析门面调度器触发 economic_daily 微技能（统一平台推送）
# open_id 由 cron --command-env 注入, 不进代码 (跟 run_oil_gold_via_facade.sh 同构)
# 官家11-21: 经济形势日报是门面之后开发的, 之前没接进来, 现在补上
set -u
WS="$HOME/.openclaw/workspace"
EO="$WS/skills/economic-outlook"
CLOG="$WS/logs/economic-daily-report-cron.log"
export HOME="${HOME:-$HOME}"
export PYTHONPATH="$HOME/.local/lib/python3.12/site-packages"
cd "$EO" || exit 1

log(){ echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$CLOG"; }
mkdir -p "$(dirname "$CLOG")"

log "=== 门面调度: economic_daily (经济形势日报) ==="
python3 - <<'PYEOF' >> "$CLOG" 2>&1
import sys, os, json, logging
sys.path.insert(0, ".")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger('facade')
try:
    from orchestrator.registry import get_registry
    ctx = {}
    if os.environ.get("QQ_TARGET_USER_ID"):
        ctx["qq_target_user_id"] = os.environ["QQ_TARGET_USER_ID"]
    reg = get_registry()
    r = reg.get('economic_daily').execute(ctx)
    if not r.success:
        log.error('economic_daily 失败: %s', r.error)
        sys.exit(0)
    out = r.data if hasattr(r, 'data') and r.data else {}
    push = out.get('push', {})
    if push.get('sent'):
        log.info('economic_daily 门面调度完成, 报告已生成(%s 字), 推送成功', out.get('report_len'))
    else:
        log.warning('economic_daily 门面调度完成, 报告已生成(%s 字), 推送未成功: %s', out.get('report_len'), push.get('note','未知'))
except Exception as e:
    log.error('门面调度异常: %s', e)
    sys.exit(0)
PYEOF

log "=== economic_daily 门面调度结束 ==="
exit 0
