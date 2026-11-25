#!/usr/bin/env bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 东财 AU9999 主源恢复探针 (纯脚本, 不依赖 AI/inference account)
# 官家11-24: 原 agentTurn 探针升级 11.7 后 "no recorded inference account" 10连失败被自动禁用
#   改成纯脚本: 拉 push2 看有没有价, 有=恢复推QQ+停探针, 无=静默
set -u
export PYTHONPATH="$HOME/.local/lib/python3.12/site-packages"
GW="$HOME/.openclaw/workspace/skills/oil-gold-correlation/scripts/send_qq_gw.py"
LOG="$HOME/.openclaw/workspace/logs/dongcai_probe.log"
mkdir -p "$(dirname "$LOG")"

log(){ echo "$(date '+%F %T') $*" >> "$LOG"; }

# 拉东财 118.AU9999 push2 实时价 (纯 python 请求, 不拉全量数据, 轻)
RESULT=$(python3 - <<'PY' 2>/dev/null
import json, urllib.request, ssl
try:
    url="https://push2.eastmoney.com/api/qt/stock/get?secid=118.AU9999&fields=f43,f171"
    req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Referer":"https://quote.eastmoney.com/"})
    ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    d=json.loads(urllib.request.urlopen(req,timeout=10,context=ctx).read().decode("utf-8","ignore"))
    data=d.get("data") or {}
    p=data.get("f43")
    if p:
        print(f"OK {p}")
    else:
        print("NO")
except Exception as e:
    print(f"ERR {str(e)[:60]}")
PY
)

case "$RESULT" in
  OK*)
    PRICE="${RESULT#OK }"
    log "✅ 东财 AU9999 恢复: $PRICE 元 → 切回实时主源, 停探针"
    # 推 QQ "东财已恢复"
    export QQ_TARGET_USER_ID="C099848DC9A60BF60A7BE31626822790"
    python3 - "$GW" "$PRICE" <<'PYPUSH' 2>/dev/null
import sys, os, subprocess
gw, price = sys.argv[1], sys.argv[2]
if os.path.isfile(gw):
    msg=f"🥇 东财 AU9999 主源已恢复! 实时价 {price} 元, 盯价切回东财实时口径, 降级标注可摘除"
    env=dict(os.environ); env["QQ_TARGET_USER_ID"]=os.environ.get("QQ_TARGET_USER_ID","")
    r=subprocess.run(["python3",gw,"-m",msg],env=env,timeout=60,capture_output=True,text=True)
    print("push:", "ok" if r.returncode==0 else f"fail:{r.stderr[:40]}")
PYPUSH
    # 恢复后停探针 (防反复推)
    openclaw automations disable fedec584-fc12-493b-878c-ab8417a1cea6 2>/dev/null || true
    log "探针已停用 (东财恢复)"
    ;;
  NO*)
    log "东财 AU9999 未恢复 (无价), 静默"
    ;;
  *)
    log "东财 AU9999 探测异常: $RESULT, 静默"
    ;;
esac
exit 0
