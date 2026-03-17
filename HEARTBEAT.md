# 心跳清单（主动巡检模板）

_保持精简，每次轮换 1-2 项_

---

## 定期检查（每次轮换 1-2 项）

- [ ] **GitHub Issues**：检查最新回复（30秒检查机制）⭐⭐⭐⭐⭐
- [ ] **系统健康**：Gateway状态、内存、磁盘
- [ ] **项目**：git status，有未处理的 PR 或 issue 吗？
- [ ] **Hacker News**：检查 AI 相关热门故事
- [ ] **Dev.to**：检查 AI 教程和技术文章
- [ ] **知识库**：QMD索引状态

## 记忆维护（每隔几天做一次）

- [ ] 回顾最近的 `memory/YYYY-MM-DD.md`
- [ ] 将值得保留的内容更新到 `MEMORY.md`
- [ ] 从 `MEMORY.md` 移除过时信息

## ⚠️ 重要提醒

**主动联系：**
- 重要系统异常
- 发现有趣内容
- 距上次联系 >8 小时

**保持安静（HEARTBEAT_OK）：**
- 深夜（23:00-08:00），除非紧急
- 官家明显忙碌
- 无新消息
- 30分钟内刚检查过

---

## 📊 技能发布汇总

### 已完成（15个）
| 技能 | 版本 | ClawHub ID |
|------|------|------------|
| agent-collab-platform | v1.17.0 | k971vakr |
| auto-pipeline | v2.0.0 | k97e0z1h |
| project-progress-tracker | v1.0.2 | k972ffb4 |
| auto-document-generator | v1.1.0 | k97daj97 |
| test-case-generator | v1.0.0 | k974q100 |
| ai-deterministic-control | v1.1.3 | k971t5dm |
| cli-tool-generator | v1.2.1 | k979ejn7 |
| ai-efficiency-monitor | v1.2.1 | k97f9ajw |
| smart-model v2.0 | v2.0 | 已发布 |
| multi-platform-notifier | v1.0 | 已发布 |
| ai-code-reviewer | v2.0 | 已发布 |
| Error Handler | v1.2.0 | k976cvkq |
| demo-skill | v1.0 | 不发布 |
| agent-collaboration-platform | v1.0 | k976y9ma |
| daily-review-helper | v1.0 | ClawHub |

### 待开发（2个）
- meeting-minutes-generator
- knowledge-graph-builder

---

## ⏰ Crontab（4个活跃任务）

| 时间 | 脚本 | 用途 |
|------|------|------|
| 每小时 | error-stats.sh stats | 上下文错误统计 |
| 每天02:00 | error-stats.sh cleanup | 日志清理 |
| 每天22:00 | jd_task_checker.sh | 京东任务检查 |
| 每天23:50 | daily_review.sh | 每日回顾 |

---

*保持精简。每项检查都消耗 token。*
*最后更新：2026-03-17 12:38*
