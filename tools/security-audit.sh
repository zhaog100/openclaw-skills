#!/bin/bash
# 定期安全审计脚本
# 由 OpenClaw 定时任务调用

# 设置环境变量（cron需要）
export HOME="/home/zhaog"
export PATH="/home/zhaog/.npm-global/bin:/usr/local/bin:/usr/bin:/bin"

# 日志文件
LOG_DIR="$HOME/.openclaw/logs/security"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/audit-$(date +%Y%m%d-%H%M%S).log"

# 记录开始时间
echo "========================================" >> "$LOG_FILE"
echo "安全审计开始: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 1. OpenClaw安全审计
echo -e "\n[1] OpenClaw安全审计" >> "$LOG_FILE"
openclaw security audit --json >> "$LOG_FILE" 2>&1

# 2. 系统更新检查
echo -e "\n[2] 系统更新检查" >> "$LOG_FILE"
openclaw update status >> "$LOG_FILE" 2>&1

# 3. Gateway状态检查
echo -e "\n[3] Gateway状态检查" >> "$LOG_FILE"
openclaw gateway status >> "$LOG_FILE" 2>&1

# 4. UFW防火墙状态（如果有权限）
echo -e "\n[4] 防火墙状态" >> "$LOG_FILE"
if command -v ufw &> /dev/null; then
    sudo -n ufw status verbose >> "$LOG_FILE" 2>&1 || echo "UFW需要sudo权限" >> "$LOG_FILE"
else
    echo "UFW未安装" >> "$LOG_FILE"
fi

# 5. 系统资源检查
echo -e "\n[5] 系统资源" >> "$LOG_FILE"
echo "内存使用:" >> "$LOG_FILE"
free -h >> "$LOG_FILE"
echo -e "\n磁盘使用:" >> "$LOG_FILE"
df -h / >> "$LOG_FILE"

# 记录结束时间
echo -e "\n========================================" >> "$LOG_FILE"
echo "安全审计完成: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 保留最近30天的日志
find "$LOG_DIR" -name "*.log" -mtime +30 -delete

# 如果发现严重问题，发送通知（可选）
# 这里可以集成QQ/飞书通知
