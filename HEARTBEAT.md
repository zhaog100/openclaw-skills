# HEARTBEAT.md（新媒体运营专家）

## 每次心跳必检
- [ ] 热点监控是否正常运行
- [ ] 当日运营待办是否完成
- [ ] 平台数据是否同步

## 需要监控的核心定时任务
- **每日热点策划**：上午9:00前完成各平台当日热点选题推荐，写入 `intel/热点选题.md`
- **内容初稿创作**：中午12:00前完成当日规划的内容初稿，写入 `intel/内容初稿.md`
- **每日数据复盘**：晚上8:30前完成当日各平台运营数据复盘，写入 `intel/数据复盘.md`
- **每周运营总结**：周日晚上10:00前完成本周运营总结与下周规划，写入 `intel/每周运营规划.md`
- **平台规则更新**：每周一上午11:00前抓取各平台最新规则/算法变化，写入 `intel/平台规则更新.md`

## 定时任务行为规范（AI打卡上班模式）

### 早班任务（08:30-09:00）
1. 读取 MEMORY.md，了解昨日未完成事项
2. 执行热点采集，写入 `intel/热点选题.md`
3. 检查运营待办状态，更新 `intel/运营待办.md`

### 午间任务（12:00-12:30）
1. 执行午间回顾
2. 更新当日 memory 文件
3. 检查待发布的內容初稿

### 晚班任务（20:30-21:00）
1. 执行每日数据复盘，写入 `intel/数据复盘.md`
2. 汇总今日完成事项，更新 memory
3. 生成明日待办建议

### 定时任务安全规则
- 定时任务中绝对不执行删除操作
- 对外发送必须是已提前确认过的固定模板
- 任何异常情况立即停止并发送告警

## 规则
- 23:00-08:00 安静，除非有紧急热点
- 内容数据异常 → 主动通知官家

## Self-Improving Check
- Read `./skills/self-improving/heartbeat-rules.md`
- Use `~/self-improving/heartbeat-state.md` for last-run markers and action notes
- If no file inside `~/self-improving/` changed since the last reviewed change, return `HEARTBEAT_OK`

## Proactivity Check
- Read ~/proactivity/heartbeat.md
- Re-check active blockers, promised follow-ups, stale work, and missing decisions
- Ask what useful check-in or next move would help right now
- Message the user only when something changed or needs a decision
- Update ~/proactivity/session-state.md after meaningful follow-through

_版本：v1.3 | 2026-04-02 | 新增定时任务行为规范（AI打卡上班模式）_


