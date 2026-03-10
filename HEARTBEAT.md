# 心跳清单（主动巡检模板）

## 定期检查（每次心跳轮换 1-2 项）

- [ ] **邮件**：有紧急未读消息吗？
- [ ] **日历**：未来 24-48 小时有什么事件？
- [ ] **社交**：Twitter/微信/社交通知？
- [ ] **天气**：如果人类可能外出，天气如何？
- [ ] **项目**：git status，有未处理的 PR 或 issue 吗？
- [ ] **Moltbook**：检查 /api/v1/home，回复评论，参与互动
- [ ] **Hacker News**：检查 AI 相关热门故事（使用 get-ai-stories.sh）
- [ ] **Dev.to**：检查 AI 教程和技术文章（使用 get-ai-tutorials.sh）

## 记忆维护（每隔几天做一次）

- [ ] 回顾最近的 `memory/YYYY-MM-DD.md`
- [ ] 将值得保留的内容更新到 `MEMORY.md`
- [ ] 从 `MEMORY.md` 移除过时信息

## 提醒/待办

### ✅ Moltbook认领（已完成）
- [x] 访问认领链接：https://www.moltbook.com/claim/moltbook_claim_89erW7Yi62z7Z4BwIF1a8yoPjXUaWR-U
- [x] 验证邮箱：zhaog100@gmail.com
- [x] 发布验证推文：`I'm claiming my AI agent "miliger" on @moltbook 🦞 Verification: deep-RHD4`
- [x] 确认认领完成
- [x] 官家已回复"已认领"（2026-02-28）

### ClawTasks充值（官家暂缓）
- ⏸️ **暂缓决定**：等待需要时再充值（2026-02-28）
- [ ] 充值Base L2 USDC
- [ ] 充值Base L2 ETH（gas费，0.001 ETH）
- [ ] 充值链接：https://clawtasks.com/fund/0x3840298Bd84AC98C24E5f4347f9CAe6f99302178
- [ ] 完成后回复"已充值"

### 向量生成（已完成）
- ✅ **向量生成完成**（2026-02-28 13:52）
- ✅ **110个向量**（31个文档，11分44秒）
- ✅ **双模式检索**：向量搜索 + 关键词搜索
- ⚠️ **CPU模式**：无GPU加速，速度较慢但功能完整

### Moltbook 互动（已完成 ✅）
- ✅ **认证完成**：2026-03-05
- ✅ **首发帖子**：Token优化经验分享
- ✅ **关注3个作者**：Hazel_OC、GanglionMinion、trader_anya
- 📊 **定期检查**：每周查看feed、回复评论、参与讨论
- 🔗 **帖子链接**：https://www.moltbook.com/post/2fa7bd5d-d41a-4962-aff9-f94f8fb99c14

### ✅ Moltbook API配置（已完成）
- [x] 获取API Key：https://www.moltbook.com
- [x] 配置路径：`~/.config/moltbook/credentials.json`
- [x] 格式：`{"api_key": "moltbook_sk_rP_W3tvDtGw0dKsmzJ7A4VBhErXFQTnf"}`
- [x] 完成时间：2026-03-09 22:49

### ⏰ 提供 OpenAI API Key（今天上午 9:00）
- [ ] 时间：2026-03-10 上午 9:00（还有约2小时）
- [ ] 用途：启用 Session-Memory Enhanced v4.0.0 高级功能
- [ ] 操作：`export OPENAI_API_KEY="sk-..."`
- [ ] 启用功能：结构化提取 + 向量检索
- ⏰ **已提醒**：7:09 AM（提前2小时通知）

### ⏸️ ClawHub 发布问题（等待修复）
- ✅ **问题已记录**：`acceptLicenseTerms: invalid value`
- ✅ **Issue 已准备**：`/tmp/clawhub-issue.md`
- [ ] **提交 issue**：https://github.com/openclaw/clawhub/issues/new
- [ ] **等待修复**：ClawHub 团队处理
- [ ] **重新发布**：v4.0.0（修复后）
- 📊 **影响范围**：14个技能更新 + Session-Memory Enhanced v4.0.0

### ✅ Session-Memory Enhanced v4.0.0（已完成）
- ✅ **开发完成**：2026-03-09 19:52
- ✅ **吸收 memu-engine 核心功能**（结构化提取 + 向量检索）
- ✅ **保留 session-memory 优势**（不可变分片 + 三位一体）
- ✅ **本地配置完成**（定时任务：每小时自动运行）
- ✅ **Python 组件测试通过**（规则提取无需 API）
- ❌ **ClawHub 发布失败**（CLI 技术问题，待解决）
- 📁 **技能目录**：`/root/.openclaw/workspace/skills/session-memory-enhanced/`

---

**注意**：保持精简。每项检查都消耗 token。
