#!/bin/bash
# 安全工具一键安装脚本
# 需要sudo权限

set -e

echo "========================================="
echo "安全工具安装脚本"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="

# 检查sudo权限
if [ "$EUID" -ne 0 ]; then
    echo "请使用sudo运行此脚本"
    exit 1
fi

# 1. 安装Fail2Ban
echo -e "\n[1/3] 安装Fail2Ban..."
apt-get update
apt-get install -y fail2ban

# 配置Fail2Ban
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
ignoreip = 127.0.0.1/8

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

[nginx-http-auth]
enabled = false

[nginx-limit-req]
enabled = false
EOF

# 启用Fail2Ban
systemctl enable fail2ban
systemctl start fail2ban

echo "Fail2Ban安装完成"

# 2. 安装Rootkit检测工具
echo -e "\n[2/3] 安装Rootkit检测工具..."
apt-get install -y rkhunter chkrootkit

# 更新rkhunter数据库
rkhunter --update
rkhunter --propupd

echo "Rootkit检测工具安装完成"

# 3. 安装文件完整性检查
echo -e "\n[3/3] 安装文件完整性检查..."
apt-get install -y aide

# 初始化AIDE数据库
aideinit
mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db

echo "文件完整性检查安装完成"

# 4. 创建定时任务（可选）
echo -e "\n[4/4] 配置定时检查..."
cat > /etc/cron.daily/security-check << 'EOF'
#!/bin/bash
# 每日安全检查

# Fail2Ban状态
systemctl is-active fail2ban > /dev/null 2>&1 || echo "Fail2Ban未运行"

# Rootkit检查（静默模式）
rkhunter --check --skip-keypress --report-warnings-only > /var/log/rkhunter-daily.log 2>&1

# 文件完整性检查
aide --check > /var/log/aide-daily.log 2>&1

# 发送通知（如果配置了邮件）
# mail -s "安全检查报告" root < /var/log/security-daily.log
EOF

chmod +x /etc/cron.daily/security-check

echo "定时检查配置完成"

# 5. 显示安装结果
echo -e "\n========================================="
echo "安装完成！"
echo "========================================="
echo ""
echo "已安装工具："
echo "  ✅ Fail2Ban - 防暴力破解"
echo "  ✅ rkhunter - Rootkit检测"
echo "  ✅ chkrootkit - Rootkit检测"
echo "  ✅ AIDE - 文件完整性检查"
echo ""
echo "定时任务："
echo "  ✅ 每日自动安全检查"
echo ""
echo "手动检查命令："
echo "  Fail2Ban状态: sudo fail2ban-client status"
echo "  Rootkit检测: sudo rkhunter --check"
echo "  文件完整性: sudo aide --check"
echo ""
echo "========================================="
