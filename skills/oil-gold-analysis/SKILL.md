---
name: "oil-gold-analysis"
description: "石油黄金分析：运行analysis.py+report_text.py生成报告，send_qq.sh推送QQ。触发：用户询问或cron定时。"
version: 1.1.0

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
- 修复：第26行硬编码默认 target `C099848DC9A60BF60A7BE31626822790`
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
