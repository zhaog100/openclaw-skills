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
```bash
bash skills/oil-gold-correlation/scripts/send_qq.sh
```

## 正确Cron配置
```
0 10 * * * cd /home/ubuntu/.openclaw/workspace && PYTHONPATH=/home/ubuntu/.local/lib/python3.12/site-packages python3 skills/oil-gold-correlation/scripts/report_text.py >> logs/oil-gold-report.log 2>&1 && bash skills/oil-gold-correlation/scripts/send_qq.sh
```

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
3. QQ发送失败 → 检查 api.openclaw.ai:8080 连通性
