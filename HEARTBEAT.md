# HEARTBEAT.md

## 每次心跳必检（≤1项，轮换）
- [ ] Bounty PR状态（review/合并）
- [ ] GitHub Issues最新回复
- [ ] 系统健康（Gateway/内存/磁盘）

## 每次心跳必检（核心基础设施，不轮换）
- [ ] **核心定时任务完整性** — 对照 MEMORY.md 定时任务表，逐项检查 crontab 是否存在：
  - `seamless-switch.sh` (*/5 * * * *)
  - `bounty_scanner` (*/30 * * * *)
  - `github-bounty-hunter.sh` (*/30 * * * *)
  - `monitor.py` (0 * * * *)
  - `qmd update` (0 6 * * *)
  - `daily-review 早/晚` (0 12 / 50 23)
  - 缺失→立即修复→记录到 MEMORY.md 并通知官家

## 几天一次
- [ ] 回顾memory/，提炼精华到MEMORY.md
- [ ] 清理过时内容

## 规则
- 合并优先 | rebase用--skip禁--strategy=ours
- 个人→xiaomili，公共→origin
- 版权：MIT | 思捷娅科技 (SJYKJ)
- 主动联系：系统异常/有新bounty
- 保持安静：23:00-08:00除非紧急

_版本：v6.0 | 2026-03-22_
