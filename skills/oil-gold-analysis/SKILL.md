---
name: "oil-gold-analysis"
description: "石油黄金分析：analysis.py + report_text.py 生成报告，Gateway 推送 QQ；数据源降级链与口径纪律。"
---

# 石油黄金分析

## 触发
- 用户询问黄金/石油价格或分析
- cron 定时任务（4 个 openclaw cron：oil-gold-morning/daily/evening/us）

## 核心流程

### 1. 数据获取与分析
```bash
cd /home/ubuntu/.openclaw/workspace && \
PYTHONPATH=/home/ubuntu/.local/lib/python3.12/site-packages \
python3 skills/oil-gold-correlation/scripts/analysis.py \
  --period {1d,7d,30d,1y} \
  --method {pearson,spearman,granger,cointegration,all} \
  >> logs/oil-gold-{morning,day,evening,us}.log 2>&1
```

### 2. 生成格式化报告（必须执行）
```bash
cd /home/ubuntu/.openclaw/workspace && \
PYTHONPATH=/home/ubuntu/.local/lib/python3.12/site-packages \
python3 skills/oil-gold-correlation/scripts/report_text.py
```
输出：`skills/oil-gold-correlation/reports/report_text_latest.txt`，完成后 `stat -c %Y` 核对 mtime 真更新。

### 3. 发送 QQ 通知
qqbot 插件 preload.cjs 有 bug，CLI 不支持 qqbot 频道。必须使用 Gateway REST API：

```bash
# 方法 1（推荐）
python3 skills/oil-gold-correlation/scripts/send_qq_gw.py

# 方法 2（cron wrapper，已集成）
bash skills/oil-gold-correlation/scripts/run_report.sh
```

send_qq.sh 已失效（CLI 报 `Unknown channel "qqbot"`），不要再用。

## 关键路径

- 数据脚本：`skills/oil-gold-correlation/scripts/analysis.py`
- 报告生成：`skills/oil-gold-correlation/scripts/report_text.py`
- 推送：`skills/oil-gold-correlation/scripts/send_qq_gw.py` / `run_report.sh`
- 报告目录：`skills/oil-gold-correlation/reports/`
- 日志：`logs/oil-gold-*.log`

环境变量：`export PYTHONPATH="/home/ubuntu/.local/lib/python3.12/site-packages"`；`QQ_TARGET_USER_ID` 缺失则拒绝推送并 exit 1（已脱敏去硬编码）。

## cron 配置

- 4 个任务：`oil-gold-morning` 10:00、`oil-gold-daily` 15:30、`oil-gold-evening` 23:00、`oil-gold-us`（美盘）
- 每个任务必须 `--command-env QQ_TARGET_USER_ID=<open_id>`，否则触发时静默 exit 1
- 改动前先 `openclaw cron list` 核对 4 个任务存在；投递目标 `--channel qqbot --to <open_id> --announce`（不走 `last`，会 fail-closed）
- 一次性任务：`openclaw cron add --name "xxx" --at "<ISO 带时区>" --delete-after-run --agent main --channel qqbot --to <open_id> --announce --message "拉取…出报告推给官家"`（无 `--once` 选项；payload 四选一：`--system-event`/`--message`/`--command`/`--script`）

## 推送脚本静默规则

推送类脚本 logger 必须静默：`logger.setLevel(CRITICAL)` + `logger.addHandler(NullHandler())` + `logger.propagate = False`，绝不打 stdout/stderr；诊断信息只写文件日志。修完模拟跑一遍确认 stdout/stderr 零输出。进推送文案的状态字段值必须中文化，改值时同步改 signal 层赋值与 outcome 层比较字面量两处，验证 = 跑一遍 outcome 输出 `json.dumps` 后正则扫 `[A-Za-z]{6,}` 无残留英文串。

## 数据源降级链（盯价用）

- 盯价沪金现货基准 = 东财 `118.AU9999`（上金所 Au9999 现货，贴官家网页口径）；`113.AUM` 是上期所期货主力，只作档位/参考，**不是现货基准**
- 海外服务器（新加坡等）访问东财全线 502/被风控：这是 IP 问题不是接口坏，别反复重拉。备用通道优先级：CF Worker 中转（`worker.js` 已入库，CF 网页可能建不出纯 Worker、"Workers for Platforms" 是付费 $25/月，建前先确认）→ 国内小主机 `gold_proxy.py` 转发（8899 端口）→ 官家网页报数。CF/国内机均未就绪前，东财 502 = 静默，不拿 T+D/纸黄金/JO_71/昨收/折算冒充
- `f43` 是 ×100 放大的整数（862.58 → 86258），取价 `/100.0`
- 降级（官家 2026-11-01 拍板最终版）：东财 502 → Tmini `tmini.net/api/gold-price` 无 key 准实时（`黄金_9999` 取 `today_price`，1 分钟级，海外机稳拉通；限流 5 次/分，拉空再退下一层）→ 金投网 jijinhao `JO_71` [黄金9999]（海外机能拉，时通时抖，只兜底）→ 全拉空静默。
- 金投网 `JO_71` 取价字段（官家 2026-11-01 14:00 拍板）：取 `q5`（最新成交现价），拉不到退 `q4`/`q63`；`q2`/`q64` 是昨收/结算（854.76 一类），绝不当现价基准。东财侧 `f43`/`f19`/`f45` 三字段同指现价可互证，`f60` 是昨收弃用。
- 报告（`report_text.py`）取价链（官家 2026-11-02 16:40 A+B 版）：东财 AUM/AGM 实时 → 东财 502 时退盯价主链（复用 `economic-outlook` 的 `_fetch_au0_realtime`，动态解析 workspace 根加进 `sys.path` 后 import，不许写死绝对路径——pre-push 关卡拦硬编码路径）→ 仍拉空才退 akshare 日线，且口径标签必须带日期 `[日线·YYYY-MM-DD收盘]`，防隔日旧价冒充最新（旧版东财 502 直接退隔日日线，报过 855 vs 实盘 835 的旧价坑）。改后单跑 `_fetch_live_price` 验证：gold 应出 `实时(Tmini·黄金_9999)`，退日线品种应见 `日线·…收盘` 标签。上金所官方 `sge.com.cn/graph/Dailyhq` 无实时 API，返日终/静态快照且海外机常超时，不进链；弃 T+D/纸黄金/金条/877 折算/861 期货/昨收 `f60`/`q2`。原 `JO_283972`（银行纸黄金，虚高冒充现货）已弃用
- 国际金实时 `PAXG` Binance / `api.gold-api.com/price/XAU` 只作盘中参考，**不进买卖判定**
- 沪银：东财 `113.AGM` → 金投网 jijinhao → akshare `futures_main_sina("AG0")` 日线兜底

## 金投网 jijinhao 正确参数

- 批量接口 `quoteCenter/realTime.htm` 参数名必须是**复数 `codes=`**（单数 `code=` 报错）
- 值用页面里真实 `JO_xxxxx` 完整 code，**不猜短名**
- 用法：HTTP 拉 `https://m.cngold.org/quote/gjs/` → 正则挖全部 `JO_\d{4,6}` → `codes=` 逗号批量拉

## 现货基准静默规则

- 盯价基准只认真实现货实时价，绝不退 au0 期货日线或国际金 XAU 折算价当现货基准
- 现货 K 线拉空只影响动态档位计算，不影响基准
- 两条现货实时源全拉空 → `success=False`，静默不推送、不触发申购，绝不顶脏缓存值
- `boc_spot` 字段存旧值视为脏数据，禁用；`boc_spot=None` 走静默
- 金投网 code 必须逐个核 `showName` 定品种（8xx 区间多为银行纸黄金/金条，非上金所现货），接前实拉打印 `showName` 核对含"上金所/Au9999"字样

## 报价口径纪律

1. 截图只作"值"的证据，绝不作实时基准/对齐目标；实时基准只认自动源拉到的数
2. 三口径严格区分不混用：① 上金所现货 `Au99.99`（东财 `118.AU9999`）② 上期所期货主力（东财 `113.AUM`）③ 具体远月合约；官家没指定前默认锚①现货
3. 单位跟上期所官方口径：沪金=元/克（8xx）；沪银=元/千克（1xxxx）；报完先看量级对不对
4. 同一份报告内所有引用同一品种的段落必须同口径同单位同数值来源，生成后 grep 关键价核对再推

## 死源清单（别再试）

- 东财 SGE 现货 `113.AU9999`/`113.AU9995`/`113.SHGM`/`8.AUxxxx` → 502 / data=null
- 中财网 `gold.10jqka.com.cn` → DNS 解析失败；`stock.10jqka.com.cn/gold/` → 404
- TickDB / 探数 / QOS / adona → 全要 key 或本地部署，等官家申请 `TICKDB_KEY` 后填入降级链

## 拉不到实时价时

明标"⚠️数据源不可用，以下为旧数据"，绝不静默回退缓存推给官家（官家 2026-10-23 起反复强调）。

## 故障排查

- 盯价壳脚本（`gold_watch.sh` 等 `bash` 包 python heredoc 的）：定时任务状态 error 但实跑时好时坏、退出码 1 无日志 → 先抓真实 Traceback 再修，别只信 cron 状态；已知坑=未触发分支引用未定义变量（`alert` 应为 `out`）NameError，且 heredoc `1>"$STATE"` 会把异常栈写进 state.json 混脏数据。修法定式：取价段套 try/except 走门面降级链、全源拉空 `print SKIP_UNAVAILABLE; sys.exit(0)` 静默不裸退 1、state 只写纯 JSON、修后连跑 3 次全 exit 0 才收口（2026-11-05 双副本/双 error task 实修）。

1. 日志为空 → 检查 cron 是否执行，查看 `/var/log/syslog`
2. 报告未生成 → 确认 `report_text.py` 能独立运行，`stat -c %Y` 核对 mtime
3. QQ 发送失败 → openclaw CLI 不支持 qqbot 通道，改用 `send_qq_gw.py` 或手动推送
4. Gateway 认证 → `client.mode` 必须为 `operator` 或 `backend`，需携带 device 信息
5. 门面调度器接管定时任务 → 微技能里"调 `report_text.py`"用子进程独立执行并落盘，不得依赖旧产物文件作旁路；切换后首个触发点前手动带 env 实跑一次并确认产物 mtime 推进

## 脱敏改动同步调用方

去硬编码 open_id/secret 是"代码侧去硬编码 + 调用方注入替代值"两件事，只做一半即线上故障：
1. 代码改成读环境变量后，立即给每个调用方（cron/CI/上游脚本）注入该变量
2. 注入后手动带 env 跑一次全链路确认 `exit=0`，再算脱敏完成
3. 每次排查"没收到推送"先查报告产物文件 mtime 与脚本日志是否当日更新，而非只看 cron 状态
