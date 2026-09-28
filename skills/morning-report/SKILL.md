---
name: "morning-report"
description: "生成每日早报（系统状态+PR清单+Bounty进度+邮件+待办），通过QQ推送。含grep -c bug修复经验。"
---

# 小米椒早报生成器

> 每日09:00自动推送系统状态、PR清单、Bounty进度、邮件摘要和今日待办

## 📋 早报内容

### 1. 🖥️ 系统运行状态
- 内存使用
- CPU负载
- 运行时间
- 磁盘空间
- 安全状态（ufw）
- 系统更新（apt）
- 其他软件更新（flatpak/snap）

### 2. 📋 PR清单维护
- GitHub Open PR列表
- PR标题和编号

### 3. 💰 PR催款进度
- 近期已合并的Bounty PR
- 待收款Open PR统计

### 4. 📧 邮件摘要
- 未读邮件预览
- 自动标记为已读

### 5. 📌 今日待办
- 待完成数量
- 已完成数量
- 待办事项列表

## 🔧 关键实现

### Bug修复：grep -c 返回值问题
❌ 错误写法：
```bash
PENDING=$(grep -c '^pattern' file || echo "0")
# 当匹配0个时，grep返回退出码1，触发echo "0"，输出变成"0\n0"
```

✅ 正确写法：
```bash
PENDING=$(grep '^pattern' file | wc -l | tr -d ' ')
[ -z "$PENDING" ] && PENDING=0
```

### Cron配置
```bash
0 9 * * * bash /path/to/morning-report.sh >> /path/to/logs/morning-report.log 2>&1
```

## 📁 文件位置
- 脚本：`skills/daily-review-assistant/scripts/morning-report.sh`
- 日志：`skills/daily-review-assistant/logs/morning-report-YYYY-MM-DD.txt`
- 配置：`skills/daily-review-assistant/.env`（邮箱凭据）

## 🐛 Bug修复记录

### Problem: email-reader.py 邮件读取失败
**Symptom:** 早报显示"⚠️ 邮件读取失败"，但脚本手动执行正常
**Root cause:** `email-reader.py` 用 `logging` 输出到 stderr，bash `$()` 只捕获 stdout，`2>/dev/null` 全部吞掉
**Fix:** 
```python
# ❌ 错误：logging默认到stderr，被$()吞掉
logger.info(f"**未读邮件**: {len(emails)} 封")

# ✅ 正确：print到stdout
print(f"**未读邮件**: {len(emails)} 封")

# 或者用双Handler分离日志
_logging_fh_stdout = logging.StreamHandler(sys.stdout)
_logging_fh_stderr = logging.StreamHandler(sys.stderr)
logger.addHandler(_logging_fh_stdout)
logger.addHandler(_logging_fh_stderr)
```

### Problem: send_qq_msg.py QQ推送失败
**Symptom:** `NameError: name 'logger' is not defined`
**Root cause:** 缺少 `import logging`
**Fix:**
```python
import logging  # 必须添加
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
```

## 🚀 使用方法
```bash
# 手动执行测试
bash skills/daily-review-assistant/scripts/morning-report.sh

# 查看日志
tail -f skills/daily-review-assistant/logs/morning-report-2026-09-04.log
```
