---
name: "gmail-payment-monitor"
description: "Gmail IMAP付款监控配置 - 解决OR语法限制和密码安全问题"
---

# Gmail Payment Monitor

监控Gmail中的bounty付款通知邮件。

## 触发条件
- 用户询问付款状态
- 每小时定时任务执行
- 需要检查USDT/RTC到账通知

## 核心配置

### 凭据文件
路径: `~/.openclaw/secrets/gmail.env`
格式:
```
GMAIL_USER=your_email@gmail.com
GMAIL_PASS=your_app_password
```

### 脚本位置
- 主脚本: `~/.openclaw/workspace/scripts/check_gmail_payments.sh`
- 日志文件: `~/.openclaw/workspace/logs/gmail_payment_monitor.log`

## 关键实现细节

### Gmail IMAP搜索限制（重要！）
❌ 不支持复杂OR语法：
```python
# 这会导致 "Could not parse command" 错误
search_query = 'SUBJECT "payment" OR SUBJECT "paid"'
```

✅ 必须逐个关键词搜索：
```python
keywords = ['payment', 'paid', 'bounty', 'reward', 'payout', 'merged', 'algora', 'rtc', 'usdt']
for kw in keywords:
    status, messages = mail.search(None, f'SUBJECT "{kw}" SINCE {since_date}')
    # 合并结果并去重
```

### 密码安全
- 日志中不要输出完整密码，使用 `***` 遮蔽
- 凭据文件权限设为 600

## 定时任务配置
```bash
openclaw cron add --name "gmail-payment-check" --cron "0 * * * *" \
  --command "bash ~/.openclaw/workspace/scripts/check_gmail_payments.sh"
```

## 测试命令
```bash
bash ~/.openclaw/workspace/scripts/check_gmail_payments.sh
tail -f ~/.openclaw/workspace/logs/gmail_payment_monitor.log
```

## 维护要点
1. 每小时自动检查
2. 发现付款相关邮件立即推送
3. 支持环境变量覆盖凭据
4. 日志记录所有操作

## 故障排除
- 连接失败: 检查IMAP服务器地址和端口
- 认证失败: 确认使用应用专用密码（非登录密码）
- 搜索超时: 增加timeout参数或减少关键词数量
