# 定时任务通知配置说明

## 📋 已切换到飞书通知

**切换时间：** 2026-03-05 11:41

**修改内容：**
- ✅ context-monitor.sh（每10分钟检查）
- ✅ smart-context-check.sh（AI主动检查）

**通知渠道：** QQ → 飞书

**飞书账户：** main
**通知目标：** user:ou_64e8948aedd09549e512218c96702830

---

## 🔧 配置详情

### 1. context-monitor.sh（定时任务）

**执行频率：** 每10分钟
**触发条件：** 最近1小时修改文件数 > 10
**通知内容：**
- 检测到活跃对话
- 建议检查上下文或发送/new

**命令格式：**
```bash
openclaw message send \
  --channel feishu \
  --account main \
  --target "user:ou_64e8948aedd09549e512218c96702830" \
  --message "通知内容"
```

### 2. smart-context-check.sh（AI主动）

**调用时机：** AI每次回复前
**触发条件：**
- 上下文 ≥ 85%：预警提醒
- 上下文 ≥ 95%：严重告警

**通知内容：**
- 当前上下文使用率
- 建议操作（继续对话或发送/new）

---

## ⏰ Crontab配置

```bash
# 每周日凌晨2点备份
0 2 * * 0 /home/zhaog/.openclaw/workspace/tools/backup-workspace.sh >> /home/zhaog/.openclaw/workspace/logs/backup-cron.log 2>&1

# 每10分钟检查上下文
*/10 * * * * /home/zhaog/.openclaw/workspace/tools/context-monitor.sh >> /home/zhaog/.openclaw/workspace/logs/context-monitor-cron.log 2>&1
```

---

## ✅ 测试结果

**测试时间：** 2026-03-05 11:41
**测试命令：**
```bash
openclaw message send --channel feishu --account main \
  --target "user:ou_64e8948aedd09549e512218c96702830" \
  --message "✅ 定时任务通知已切换到飞书"
```

**测试结果：** ✅ 成功
**消息ID：** om_x100b55bbf568a8a4c4494e387f6c917

---

## 📝 重要说明

1. **必须指定--account main**
   - 不指定account会报错：`Feishu account "default" not configured`
   - 正确的account是"main"（从gateway配置中获取）

2. **target格式**
   - 用户：`user:ou_xxx`
   - 群组：`chat:xxx`

3. **通知策略**
   - 定时任务：每10分钟检查，活跃时提醒
   - AI主动：每次回复前检查，超过阈值提醒

---

*配置完成时间：2026-03-05 11:41*
*通知渠道：飞书（main账户）*
