#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 技能: economic-outlook/scripts/run_macro_policy_via_facade.sh
# 经济面(宏观政策)报告一键门面调度: 生成完整经济面报告 → 走门面 send_qq_gw.py(双路互备) 推 QQ
# 用法: 由 OpenClaw cron / crontab 定时调用; open_id 由 --command-env / QQ_TARGET_USER_ID 注入, 不进代码
set -u
WS="$HOME/.openclaw/workspace"
EO="$WS/skills/economic-outlook"
CLOG="$WS/logs/macro-policy-report-cron.log"

# 补全 report_text.py 子进程运行环境(等价老 run_report.sh)
export HOME="${HOME:-$HOME}"
export PYTHONPATH="$HOME/.local/lib/python3.12/site-packages"
export OIL_GOLD_SKILL_DIR="$WS/skills/oil-gold-correlation"   # send_qq_gw.py 复用油金目录那份(已双路)
# source 油金 .env（QQ 推送配置: QQ_TARGET_USER_ID / APPID 等），经济面 facade 复用油金 send_qq_gw.py
[ -f "$OIL_GOLD_SKILL_DIR/.env" ] && source "$OIL_GOLD_SKILL_DIR/.env"
cd "$EO"
export OIL_GOLD_BRIEF="0"   # 经济面报告走完整版, 非精简

# ============ 1. 生成经济面全报告(report_text.py: 宏观状态+信号+出口+历史类比+触发器) ============
REGEN_OK=0
for ATTEMPT in 1 2 3; do
  echo "[regen] 第 ${ATTEMPT}/3 次生成经济面报告 ..." >> "$CLOG" 2>&1 || true
  if ( cd "$EO" && python3 scripts/report_text.py ) >> "$CLOG" 2>&1; then
    REGEN_OK=1
    break
  fi
  [ "$ATTEMPT" -lt 3 ] && sleep 15
done

REPORT="$EO/cache/report_text.txt"
if [ "$REGEN_OK" != "1" ] || [ ! -f "$REPORT" ]; then
  echo "[error] 报告生成失败或落盘不存在: $REPORT, 详见 $CLOG" >&2
  exit 1
fi
if [ ! -s "$REPORT" ]; then
  echo "[error] 报告内容为空: $REPORT" >&2
  exit 1
fi

# ============ 2. 门面统一推送(双路: QQ 开放平台直发 + Gateway 降级) ============
echo "[push] 经济面报告生成成功, 走 send_qq_gw.py 推送 ($(wc -c < "$REPORT") 字节) ..." >> "$CLOG"
if python3 "$OIL_GOLD_SKILL_DIR/scripts/send_qq_gw.py" "$REPORT"; then
  echo "[push] 经济面(宏观政策)报告推送成功: $(date '+%Y-%m-%d %H:%M:%S')" >> "$CLOG"
  exit 0
else
  echo "[push] 经济面(宏观政策)报告推送失败, 双路全挂: $(date '+%Y-%m-%d %H:%M:%S')" >> "$CLOG"
  exit 1
fi
