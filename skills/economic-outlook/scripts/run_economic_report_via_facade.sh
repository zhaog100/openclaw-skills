#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 经济形势日报 — 走 orchestrator 门面调度(官家11-21 统一: 跟油金/彩票同构)
# orchestrator.registry → weekly_report skill(生成经济报告) → 统一推送
# open_id 由 cron --command-env 注入, 不进代码
set -u
WS="$HOME/.openclaw/workspace"
EO="$WS/skills/economic-outlook"
CLOG="$WS/logs/economic-report-cron.log"
export HOME="${HOME:-$HOME}"
export PYTHONPATH="$HOME/.local/lib/python3.12/site-packages"
cd "$EO"

python3 - <<'PY' 1>"$HOME/.openclaw/workspace/logs/economic-report-cron.log" 2>&1
import sys, os, logging, time
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
sys.path.insert(0, os.getcwd()); sys.path.insert(0, 'shared')
from orchestrator.registry import get_registry

reg = get_registry()
ctx = {'qq_target_user_id': os.environ.get('QQ_TARGET_USER_ID', '')}

# 经济日报 = 综合经济报告, 走 weekly_report skill(汇总信号+出口+历史类比+触发器)
# 若 weekly_report 不可用, 明标不静默降级
sk = reg.get('weekly_report')
if sk is None:
    log.error('weekly_report skill 未注册, 经济日报本轮跳过')
    sys.exit(1)

r = sk.execute(ctx)
if not r.success:
    log.error('weekly_report 生成失败: %s', r.error)
    sys.exit(1)

text = r.data.get('text', '')
if not text:
    log.error('weekly_report 返回空文本, 跳过推送')
    sys.exit(1)

# 报告落盘(供推送 + 补推)
import os as _os
report_path = os.path.join(os.path.dirname(os.path.abspath('entry.py')), 'cache', 'economic_report_latest.txt')
_os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(text + "\n\n⚠️ 仅供参考, 不构成投资建议")
log.info('经济报告已落盘: %s (%d 字符)', report_path, len(text))

# 统一推送: 走 send_qq_gw.py 门面(与油金/彩票同通道)
target = ctx.get('qq_target_user_id', '')
if not target:
    log.warning('无 QQ_TARGET_USER_ID, 跳过推送(不硬编码 open_id)')
    sys.exit(0)

# 定位 send_qq_gw.py(全候选扫描, 找不到明标不静默)
base = _os.path.dirname(_os.path.dirname(_os.path.abspath('entry.py')))
cands = []
for n in range(1, 6):
    parent = base
    for _ in range(n - 1):
        parent = _os.path.dirname(parent)
    for c in (_os.path.join(parent, 'oil-gold-correlation', 'scripts', 'send_qq_gw.py'),
              _os.path.join(parent, 'skills', 'oil-gold-correlation', 'scripts', 'send_qq_gw.py')):
        cands.append(c)
gw = next((c for c in cands if _os.path.isfile(c)), '')
if not gw:
    log.error('找不到 send_qq_gw.py, 经济日报推送跳过(明标不静默)')
    sys.exit(1)

import subprocess
env = dict(_os.environ)
env['QQ_TARGET_USER_ID'] = target
rr = subprocess.run(['python3', gw, report_path], env=env, timeout=120, capture_output=True, text=True)
if rr.returncode == 0:
    log.info('经济日报门面推送成功 (orchestrator → weekly_report → send_qq_gw)')
else:
    log.error('经济日报推送失败: %s', (rr.stderr or rr.stdout)[:80])
    sys.exit(1)
PY
echo "[$(date '+%F %T')] 经济日报门面调度完成 rc=$?" >> "$CLOG" 2>&1 || true
