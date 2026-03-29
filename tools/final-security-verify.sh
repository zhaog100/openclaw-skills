#!/bin/bash
# 最终安全验证脚本

echo "========================================="
echo "🔒 系统安全加固 - 最终验证"
echo "========================================="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 检查安全工具
echo "📦 [1/6] 安全工具检查"
echo "-------------------------------------------"
tools=(
    "fail2ban-client:Fail2Ban"
    "rkhunter:Rootkit Hunter"
    "aide:AIDE"
    "chkrootkit:Chkrootkit"
)

for tool in "${tools[@]}"; do
    cmd="${tool%%:*}"
    name="${tool##*:}"
    if command -v "$cmd" &> /dev/null; then
        echo "  ✅ $name"
    else
        echo "  ❌ $name"
    fi
done

# 2. Fail2Ban状态
echo ""
echo "🛡️ [2/6] Fail2Ban状态"
echo "-------------------------------------------"
if systemctl is-active fail2ban &> /dev/null; then
    echo "  ✅ 运行中"
    if [ "$EUID" -eq 0 ]; then
        fail2ban-client status 2>/dev/null | grep -E "Status|Number of jails" || echo "  ⚠️  需要root权限查看详情"
    else
        echo "  ℹ️  需要sudo查看详情"
    fi
else
    echo "  ❌ 未运行"
fi

# 3. UFW防火墙
echo ""
echo "🔥 [3/6] UFW防火墙"
echo "-------------------------------------------"
if command -v ufw &> /dev/null; then
    if [ "$EUID" -eq 0 ]; then
        ufw status verbose 2>/dev/null | head -5
    else
        echo "  ℹ️  需要sudo查看详情"
        echo "  命令: sudo ufw status verbose"
    fi
else
    echo "  ❌ UFW未安装"
fi

# 4. AIDE数据库
echo ""
echo "🔐 [4/6] AIDE文件完整性"
echo "-------------------------------------------"
if [ -f /var/lib/aide/aide.db ]; then
    echo "  ✅ 数据库已初始化"
    ls -lh /var/lib/aide/aide.db 2>/dev/null || echo "  ℹ️  需要sudo查看详情"
else
    echo "  ⏸️  数据库未初始化"
    echo "  执行: sudo aideinit && sudo mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db"
fi

# 5. 定时任务
echo ""
echo "⏰ [5/6] 定时安全任务"
echo "-------------------------------------------"
if command -v openclaw &> /dev/null; then
    cron_count=$(openclaw cron list 2>/dev/null | grep -c "healthcheck\|security" || echo "0")
    echo "  ✅ $cron_count 个安全相关定时任务"
else
    echo "  ℹ️  OpenClaw未配置"
fi

# 6. 插件安全
echo ""
echo "🔌 [6/6] 插件安全配置"
echo "-------------------------------------------"
if [ -f /home/zhaog/.openclaw/openclaw.json ]; then
    whitelist=$(cat /home/zhaog/.openclaw/openclaw.json | jq -r '.plugins.allow[]' 2>/dev/null | tr '\n' ' ')
    if [ -n "$whitelist" ]; then
        echo "  ✅ 白名单: $whitelist"
    else
        echo "  ⚠️  未配置白名单"
    fi
else
    echo "  ℹ️  OpenClaw配置文件不存在"
fi

# 总结
echo ""
echo "========================================="
echo "📊 安全状态总结"
echo "========================================="

# 计算完成度
completed=0
total=6

if command -v fail2ban-client &> /dev/null; then ((completed++)); fi
if command -v rkhunter &> /dev/null; then ((completed++)); fi
if command -v aide &> /dev/null; then ((completed++)); fi
if command -v chkrootkit &> /dev/null; then ((completed++)); fi
if command -v ufw &> /dev/null; then ((completed++)); fi
if [ -f /var/lib/aide/aide.db ]; then ((completed++)); fi

percentage=$((completed * 100 / total))

if [ $percentage -ge 100 ]; then
    echo "✅ 完成度: $percentage%"
    echo "🌟 安全等级: ⭐⭐⭐⭐⭐ 生产级防护"
    echo ""
    echo "🎉 恭喜！系统已达到生产级安全防护！"
else
    echo "⏸️  完成度: $percentage%"
    if [ $percentage -ge 80 ]; then
        echo "🌟 安全等级: ⭐⭐⭐⭐ 优秀"
    elif [ $percentage -ge 60 ]; then
        echo "🌟 安全等级: ⭐⭐⭐ 良好"
    else
        echo "🌟 安全等级: ⭐⭐ 基础"
    fi
fi

echo ""
echo "========================================="
echo "📝 日常维护命令"
echo "========================================="
echo "sudo fail2ban-client status"
echo "sudo rkhunter --check"
echo "sudo aide --check"
echo "sudo ufw status verbose"
echo ""
echo "完整报告:"
echo "  /home/zhaog/.openclaw/workspace/memory/"
echo "  2026-03-09-security-final-report.md"
echo "========================================="
