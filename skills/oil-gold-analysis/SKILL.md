---
name: "oil-gold-analysis"
description: "石油黄金分析：运行analysis.py+report_text.py生成报告，send_qq.sh推送QQ。触发：用户询问或cron定时。"
---

# 石油黄金分析技能

## 触发条件
- 用户询问黄金/石油价格或分析
- cron定时任务执行（每日4次）

## 核心路径

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
输出保存到: `skills/oil-gold-correlation/reports/report_text_latest.txt`

### 3. 发送QQ通知
**注意**：qqbot 插件 preload.cjs 有 bug，CLI 不支持 qqbot 频道。必须使用 Gateway REST API 发送：

```bash
# 方法1：通过 Gateway REST API（推荐）
python3 skills/oil-gold-correlation/scripts/send_qq_gw.py

# 方法2：通过 cron wrapper（已集成）
bash skills/oil-gold-correlation/scripts/run_report.sh
```

send_qq.sh 已失效（CLI 报 `Unknown channel "qqbot"`），改用 send_qq_gw.py

**send_qq_gw.py 修复记录 (2026-09-08 21:30)**：
- 问题：QQ_TARGET_USER_ID 环境变量未设置，导致 target 为空
- 修复：第26行硬编码默认 target `${QQ_OPEN_ID:-unset}`
- 同时修复 target 格式：从 `qqbot:c2c:{target}` 改为直接使用 `{target}`（open_id）
- Gateway 要求 target 格式为 open_id，不要加 `qqbot:c2c:` 前缀

## 正确Cron配置
```
0 10 * * * /bin/bash /home/ubuntu/.openclaw/workspace/skills/oil-gold-correlation/scripts/run_report.sh >> /home/ubuntu/.openclaw/workspace/logs/oil-gold-report-cron.log 2>&1
30 15 * * * /bin/bash /home/ubuntu/.openclaw/workspace/skills/oil-gold-correlation/scripts/run_report.sh >> /home/ubuntu/.openclaw/workspace/logs/oil-gold-report-cron.log 2>&1
0 23 * * * /bin/bash /home/ubuntu/.openclaw/workspace/skills/oil-gold-correlation/scripts/run_report.sh >> /home/ubuntu/.openclaw/workspace/logs/oil-gold-report-cron.log 2>&1
```

## 定时任务时间说明
- 早间报告：10:00
- 午间报告：15:30
- 晚间报告：23:00（用户期望22:30，需确认是否调整）

## 关键路径
- 数据脚本: `skills/oil-gold-correlation/scripts/analysis.py`
- 报告生成: `skills/oil-gold-correlation/scripts/report_text.py`
- 发送脚本: `skills/oil-gold-correlation/scripts/send_qq.sh`
- 报告目录: `skills/oil-gold-correlation/reports/`
- 日志目录: `logs/oil-gold-*.log`

## 环境变量
```bash
export PYTHONPATH="/home/ubuntu/.local/lib/python3.12/site-packages"
```

## 故障排查
1. 日志为空 → 检查cron是否执行，查看 `/var/log/syslog`
2. 报告未生成 → 确认 report_text.py 能独立运行
3. QQ发送失败 → openclaw message send CLI 不支持 qqbot 通道，需改用 send_qq_ws.py 或手动推送
4. Gateway WebSocket 认证 → client.mode 必须为 "operator" 或 "backend"，需携带 device 信息

## 数据源受限环境（腾讯云）排障（2026-09-29）
官方数据源（NBS/海关/央行/东财行情/新浪 retail）在本机多为"接口本身被墙/风控"而非代码 bug，按此顺序判别，避免空盯或误改代码：
1. 先分层探活：主站可通（`curl -o /dev/null -w '%{http_code}'` 得 200）但数据子域返回 `HTTP 000`/412/RemoteDisconnected，即该子域被限，**不是断网**——其它 akshare 源（如 macro_usa_pmi）能拉通即可佐证。
2. 官方源拉不到时**一律走降级**：宏观 21 个 akshare 源兜底、出口品类/国内品类/招聘走占位+总额兜底、信号层捕获异常降级 neutral，主流程不崩、周报照常出。
3. 别为此改代码或加代理硬拉：换国内网络/代理后官方源自动生效，代码零改动。排障结论按此记录即可。
4. 测试/全链路验证被官方源超时时，用 mock 信号（不联网）快速验逻辑不崩，再跑全量测试；别因超时误判为逻辑错。

## 定时推送与门面集成（2026-09-30）

- **每日 4 次推送时间不变**：早盘 10:00 / 日盘 15:00 / 晚盘 21:00 / 美盘 22:00，各自是一个 openclaw cron 任务（名字 `oil-gold-morning/daily/evening/us`，实际路径 `skills/oil-gold-correlation/scripts/run_report.sh`，非系统 crontab）。改动前先 `openclaw cron list` 核对这 4 个任务。
- **推送目标必须固定**：delivery 的 channel 用 `qqbot`、to 用 `qqbot:c2c:C099848DC9A60BF60A7BE31626822790`。若任务是 `channel=last`，`openclaw cron list` 会显示 `will fail-closed`（静默失败、用户收不到）；用 `openclaw cron edit <id> --channel qqbot --to qqbot:c2c:<open_id>` 修复。修完以 list 不再出现 fail-closed 为准。
- **门面集成**：本 skill 已作为 economic-outlook 门面平台的微技能 `skills/oil_gold`（第 19 个）挂入，`orchestrator/registry.py` 自动发现；配置登记在 `skills/economic-outlook/config/schedules.yaml` 的 `oil_gold_push`。推送时间调整只改 openclaw cron，保持 schedules.yaml 与实际 cron 一致。
- **脱敏去硬编码后必须同步注入环境变量（2026-09-30 教训）**：`run_report.sh`/`send_qq_gw.py` 的 open_id 已去硬编码，改为"读 `QQ_TARGET_USER_ID` 环境变量，缺失则拒绝推送并 exit 1"。因此 4 个 openclaw cron 任务（oil-gold-morning/daily/evening/us）必须带 `--command-env QQ_TARGET_USER_ID=<open_id>`，否则 cron 触发时脚本直接 exit 1、报告静默不推（症状：automation `lastRunStatus=error`，diagnostics 报"QQ_TARGET_USER_ID 未设置"）。**规则：任何把硬编码凭证改成环境变量/config 读取的脱敏改动，落地时必须同步给每个调用方（cron/CI/上游脚本）注入该变量，并以"手动带 env 跑一次该脚本全链路成功"为完成标准，再验证下一次 cron 触发。**
- **门面调度入口的运行时环境 = 老 cron 链路环境（2026-10-04 教训）**：把 cron payload 从独立脚本（`run_report.sh`）切到门面调度入口（`run_oil_gold_via_facade.sh` → `skills/oil_gold` 微技能）时，老 wrapper 里的运行时环境（`PYTHONPATH=site-packages`、`HOME`、正确的 `cwd`、`OIL_GOLD_SKILL_DIR`）不会自动迁移——微技能里"调 `report_text.py` 生成报告"若只做 import 调 `main()` 或子进程但环境不全，会静默拉不到数据、报告不更新（文件 mtime 停留旧值），推送又因"报告未生成/旧"被跳过 → 连续多天全静默漏推而 cron 仍显示 `status=ok`。**规则：切调度链路时必须核对新入口带全老链路的环境变量（对照老 `run_report.sh` 的 export 段逐项）；"报告生成"用子进程独立跑 `report_text.py`（等价老 cron，真自拉数据落盘）；完成标准 = 跑一次后报告文件 mtime 真更新 + 推送成功；并给入口加"漏推/报告旧 → 写 ERROR 进 cron 可见日志"告警，且别把 stdout 清空清掉可观测信号——静默化的是刷到聊天窗口的技术状态，不是日志。** 验证命令：`stat -c %Y reports/report_text_latest.txt` 前后对比确认 mtime 更新。
