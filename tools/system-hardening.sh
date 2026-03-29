#!/bin/bash
# 系统加固检查脚本

# 设置环境变量
export HOME="/home/zhaog"
export PATH="/home/zhaog/.npm-global/bin:/usr/local/bin:/usr/bin:/bin"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "系统安全加固检查"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="

# 1. SSH配置检查
echo -e "\n${YELLOW}[1] SSH配置${NC}"
if [ -f /etc/ssh/sshd_config ]; then
    echo "PermitRootLogin: $(grep -E '^PermitRootLogin' /etc/ssh/sshd_config | awk '{print $2}')"
    echo "PasswordAuthentication: $(grep -E '^PasswordAuthentication' /etc/ssh/sshd_config | awk '{print $2}')"
    echo "Port: $(grep -E '^Port' /etc/ssh/sshd_config | awk '{print $2}')"
else
    echo "SSH配置文件不存在"
fi

# 2. 自动更新检查
echo -e "\n${YELLOW}[2] 自动更新${NC}"
if [ -f /etc/apt/apt.conf.d/20auto-upgrades ]; then
    cat /etc/apt/apt.conf.d/20auto-upgrades
else
    echo "未配置自动更新"
fi

# 3. 磁盘加密检查
echo -e "\n${YELLOW}[3] 磁盘加密${NC}"
if command -v cryptsetup &> /dev/null; then
    echo "LUKS工具已安装"
    lsblk -o NAME,TYPE,FSTYPE,MOUNTPOINT | grep -E "crypt|LUKS" || echo "未检测到加密分区"
else
    echo "未安装LUKS工具"
fi

# 4. 失败登录检查
echo -e "\n${YELLOW}[4] 失败登录记录${NC}"
if command -v lastb &> /dev/null; then
    FAILED_LOGINS=$(lastb -n 10 2>/dev/null | wc -l)
    echo "最近失败登录次数: $FAILED_LOGINS"
else
    echo "无法检查失败登录"
fi

# 5. 活跃用户检查
echo -e "\n${YELLOW}[5] 活跃用户${NC}"
who

# 6. 可疑进程检查
echo -e "\n${YELLOW}[6] 可疑进程${NC}"
# 检查监听在0.0.0.0的进程
ss -ltnup | grep "0.0.0.0" | grep -v "127.0.0.1"

# 7. 定时任务检查
echo -e "\n${YELLOW}[7] 用户定时任务${NC}"
crontab -l 2>/dev/null | grep -v "^#" | grep -v "^$" || echo "无定时任务"

echo -e "\n========================================="
echo "检查完成"
echo "========================================="
