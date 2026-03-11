#!/bin/bash
# 安全工具配置 - 第二步

echo "========================================="
echo "安全工具配置 - rkhunter首次扫描 + AIDE安装"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="

# 检查sudo权限
if [ "$EUID" -ne 0 ]; then
    echo "请使用sudo运行此脚本"
    exit 1
fi

# 步骤1: 修复rkhunter配置
echo -e "\n[1/4] 修复rkhunter配置..."
sed -i 's|WEB_CMD=.*|WEB_CMD=""|' /etc/rkhunter.conf
echo "配置已修复"

# 步骤2: 更新rkhunter数据库
echo -e "\n[2/4] 更新rkhunter数据库..."
rkhunter --update
rkhunter --propupd
echo "数据库已更新"

# 步骤3: 首次扫描（约5-10分钟）
echo -e "\n[3/4] 执行rkhunter首次扫描（需要5-10分钟）..."
echo "请耐心等待..."
rkhunter --check --skip-keypress --report-warnings-only

echo -e "\n扫描完成！请查看上方结果"

# 步骤4: 安装AIDE
echo -e "\n[4/4] 安装AIDE（文件完整性检查）..."
apt-get install -y aide

# 初始化AIDE数据库（约10-15分钟）
echo -e "\n初始化AIDE数据库（需要10-15分钟）..."
echo "请耐心等待..."
aideinit

# 激活数据库
if [ -f /var/lib/aide/aide.db.new ]; then
    mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
    echo "AIDE数据库已初始化"
else
    echo "警告：AIDE数据库初始化可能失败"
fi

# 完成提示
echo -e "\n========================================="
echo "配置完成！"
echo "========================================="
echo ""
echo "已完成的操作："
echo "  ✅ rkhunter配置修复"
echo "  ✅ rkhunter数据库更新"
echo "  ✅ rkhunter首次扫描"
echo "  ✅ AIDE安装和初始化"
echo ""
echo "日常使用命令："
echo "  Rootkit检测: sudo rkhunter --check"
echo "  文件完整性: sudo aide --check"
echo ""
echo "========================================="
