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
# ============ 推送前重新生成报告（堵"推旧版"洞）============
# 策略: 重试 3 次(间隔 20s), 成功即停; 全失败仍推现有落盘(标记陈旧, 不阻塞)
# 生成后校验: 时间戳必须 < 15min(防旧缓存顶替), 否则标 stale 让 skill.py 推旧报告
if [ -d "$WS/skills/oil-gold-correlation" ] && [ -f "$WS/skills/oil-gold-correlation/scripts/report_text.py" ]; then
  # 官家11-09: 重试 3 次→1 次。网络断时 3×(SIGALRM 120s)+2×20s 会超 cron 600s 被 SIGTERM;
  # 改 1 次后最坏 ~140s, 留足 460s 给推送+补推排程; 失败仍走"推现有落盘标陈旧"不阻塞
  REGEN_OK=0
  for ATTEMPT in 1; do
    echo "[regen] 第 ${ATTEMPT}/1 次重新生成 report_text_latest.txt ..." >> "$CLOG" 2>&1 || true
    if ( cd "$WS/skills/oil-gold-correlation" && python3 scripts/report_text.py ) >> "$CLOG" 2>&1; then
      REGEN_OK=1
      break
    fi
  done
  if [ "$REGEN_OK" = "1" ]; then
    # 校验时间戳: 防"生成成功但落盘还是旧文件"(report_text.py 异常没写盘)
    RECENT=$(find "$WS/skills/oil-gold-correlation/reports/report_text_latest.txt" -mmin -15 2>/dev/null | head -1)
    if [ -n "$RECENT" ]; then
      echo "[regen] 生成成功, 时间戳新鲜(15min 内), 走新报告" >> "$CLOG" 2>&1 || true
    else
      echo "[regen] 生成成功但落盘时间戳过旧(>15min), 视为陈旧, skill.py 会标 stale 推旧报告" >> "$CLOG" 2>&1 || true
      # 不阻塞: 让 skill.py 的 stale 逻辑接管(它读 report_text_path 存在就推, 加"陈旧"标记)
    fi
  else
    echo "[regen] 重新生成失败, 推现有落盘(陈旧), 日志见上" >> "$CLOG" 2>&1 || true
  fi
fi
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
        # 推送成功: 清除历史漏推待办标记(若有)
        try:
            import pathlib
            p = pathlib.Path(os.path.expanduser('~/.openclaw/workspace/intel/待办_油金漏推.md'))
            if p.exists(): p.unlink()
        except Exception:
            pass
    else:
        reason = push.get('note','未知')
        log.error('oil_gold 漏推: 推送未成功, 原因=%s', reason)
        # ============ 加固: 双路全失败时, 写醒目标记 + 隔 25min 自动补推 ============
        try:
            import pathlib
            todo = pathlib.Path(os.path.expanduser('~/.openclaw/workspace/intel/待办_油金漏推.md'))
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            old = todo.read_text() if todo.exists() else ''
            body = (f'# 油金漏推待办 (双路推送全失败)\n\n'
                    f'- 漏推时间: {now}\n'
                    f'- 原因: {reason}\n'
                    f'- 处理: 已排程 25min 后自动补推一次(读最新落盘报告, 双路互备); 人工可立即推 send_qq_gw.py\n')
            # 只保留最新一条标记(去重: 丢掉旧标记块), 追加本次
            todo.write_text(body + ('\n--- 历史 ---\n' + old if old else ''))
            log.warning('oil_gold 漏推待办标记已写: %s', todo)
        except Exception as e:
            log.warning('漏推待办标记写入异常(不影响主流程): %s', e)
        # 隔 25min 自动补推: 报告已落盘, 只重推 send_qq_gw.py(双路互备), 不重生成
        try:
            import subprocess
            subprocess.Popen(
                ['nohup','sh','-c',f'sleep 1500; python3 {os.environ.get("OIL_GOLD_SKILL_DIR", os.getcwd())}/scripts/send_qq_gw.py {os.environ.get("OIL_GOLD_SKILL_DIR", os.getcwd())}/reports/report_text_latest.txt >> {os.path.expanduser("~/.openclaw/workspace/logs/oil-gold-report-cron.log")} 2>&1'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            log.warning('oil_gold 已排程: 25min 后自动补推一次(读最新落盘报告, 双路互备)')
        except Exception as e:
            log.warning('补推排程失败(需人工补推): %s', e)
PY
