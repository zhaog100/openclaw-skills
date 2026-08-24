#!/bin/bash
# Gateway systemd 接管修复脚本
# 用法: sudo bash fix-gateway.sh

set -e

echo "=== Step 1: 停 systemd ==="
systemctl stop openclaw-gateway.service 2>&1 || true
sleep 2

echo "=== Step 2: 禁用 systemd 自动启动 ==="
systemctl disable openclaw-gateway.service 2>&1 || true
sleep 1

echo "=== Step 3: 杀掉所有 gateway 进程 ==="
# 先优雅关闭
pkill -f "node.*gateway.*18789" 2>&1 || true
pkill -f "openclaw.*gateway" 2>&1 || true
sleep 3

# 强制杀掉
pkill -9 -f "node.*gateway.*18789" 2>&1 || true
pkill -9 -f "openclaw" 2>&1 || true
sleep 3

echo "=== Step 4: 确认清理 ==="
REMAINING=$(ps aux | grep -E "openclaw|node.*gateway" | grep -v grep | grep -v "systemctl status" | wc -l)
echo "残留进程数: $REMAINING"

PORT_STATUS=$(ss -tlnp | grep 18789 | wc -l)
echo "端口占用: $PORT_STATUS"

if [ "$REMAINING" -gt 0 ]; then
    echo "=== Step 4b: 再次强制杀掉 ==="
    ps aux | grep -E "openclaw|node.*gateway" | grep -v grep | grep -v "systemctl status" | awk '{print $2}' | xargs kill -9 2>&1 || true
    sleep 3
fi

echo "=== Step 5: 等待端口释放 ==="
for i in $(seq 1 10); do
    if ! ss -tlnp | grep -q 18789; then
        echo "✅ 端口已释放 (等待了 ${i} 秒)"
        break
    fi
    sleep 1
done

if ss -tlnp | grep -q 18789; then
    echo "⚠️ 端口仍然被占用"
    ss -tlnp | grep 18789
fi

echo "=== Step 6: 重新启用 systemd ==="
systemctl daemon-reload 2>&1 || true
systemctl enable openclaw-gateway.service 2>&1 || true
sleep 1

echo "=== Step 7: 启动 systemd ==="
systemctl start openclaw-gateway.service 2>&1 || true
sleep 10

echo "=== Step 8: 检查状态 ==="
ACTIVE=$(systemctl is-active openclaw-gateway.service 2>&1)
echo "systemd 状态: $ACTIVE"

MAINPID=$(systemctl show openclaw-gateway.service -p MainPID --value 2>&1)
echo "MainPID: $MAINPID"

NRESTARTS=$(systemctl show openclaw-gateway.service -p NRestarts --value 2>&1)
echo "NRestarts: $NRESTARTS"

echo ""
echo "=== 进程 ==="
ps aux | grep -E "openclaw|node.*gateway" | grep -v grep | grep -v "systemctl status"

echo ""
echo "=== 端口 ==="
ss -tlnp | grep 18789 || echo "端口未监听"

echo ""
echo "=== 最新日志 ==="
journalctl -u openclaw-gateway.service --no-pager --since "5 min ago" 2>&1 | tail -15

echo ""
if [ "$ACTIVE" = "active" ]; then
    echo "✅ Gateway systemd 接管成功！"
else
    echo "❌ Gateway 仍然没有正常启动，请检查上方日志"
fi
