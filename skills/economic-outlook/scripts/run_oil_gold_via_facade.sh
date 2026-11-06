#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 通过经济分析门面调度器触发 oil_gold 微技能（统一平台推送）
# open_id 由 cron --command-env 注入，不进代码
set -u
WS="$HOME/.openclaw/workspace"
EO="$WS/skills/economic-outlook"
CLOG="$WS/logs/oil-gold-report-cron.log"
# 补全 report_text.py 子进程运行环境（等价老 run_report.sh）：PYTHONPATH site-packages + HOME
export HOME="${HOME:-$HOME}"
export PYTHONPATH="$HOME/.local/lib/python3.12/site-packages"
export OIL_GOLD_SKILL_DIR="$WS/skills/oil-gold-correlation"
cd "$EO"
export OIL_GOLD_BRIEF="1"  # 精简报告（OIL_GOLD_BRIEF=0 恢复完整版）
python3 - <<'PY' 1>"$HOME/.openclaw/workspace/logs/oil-gold-report-cron.log" 2>&1
import sys, os, logging, json, time
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
sys.path.insert(0, os.getcwd()); sys.path.insert(0, 'shared')
from orchestrator.registry import get_registry
reg = get_registry()
ctx = {'qq_target_user_id': os.environ.get('QQ_TARGET_USER_ID','')}
r = reg.get('oil_gold').execute(ctx)
# 静默：不向 QQ 输出技术状态；但把结果写进 cron 可见日志，漏推可查
if not r.success:
    log.error('oil_gold 失败: %s', r.error)
else:
    push = r.data.get('push', {})
    gen = r.data.get('report_generated', False)
    stale = r.data.get('report_stale', False)
    if push.get('sent'):
        log.info('oil_gold 门面调度完成, 报告%s%s, 推送成功', '新' if gen else '旧', '(陈旧)' if stale else '')
    else:
        log.error('oil_gold 漏推: 推送未成功, 原因=%s', push.get('note','未知'))
PY
