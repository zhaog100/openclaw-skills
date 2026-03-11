#!/bin/bash
# Context Monitor v6.0 测试脚本
# 模拟高频活动，测试预警功能

echo "🧪 Context Monitor v6.0 测试开始"
echo "================================"

# 1. 模拟高频工具调用（50次/小时）
echo ""
echo "📊 测试1：模拟高频工具调用..."
for i in {1..55}; do
    echo '["time":"'$(date -Iseconds)'"] ["tools"] "test tool call"' >> /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log
done
echo "✅ 已添加55次工具调用记录"

# 同时模拟用户消息（确保被检测到）
for i in {1..10}; do
    echo '["time":"'$(date -Iseconds)'"] ["message"] "用户消息测试 ROBOT qqbot"' >> /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log
done
echo "✅ 已添加10次用户消息记录"

# 2. 模拟长会话（4小时）
echo ""
echo "📊 测试2：模拟长会话..."
echo "$(date -d '4 hours ago' +%s)" > /tmp/context-session-start
echo "✅ 已设置会话开始时间为4小时前"

# 3. 模拟高频用户活动
echo ""
echo "📊 测试3：模拟高频用户活动..."
echo "60" > /tmp/context-activity-tracker-v6
echo "✅ 已设置活动频率为60次/5分钟"

# 4. 运行监控脚本
echo ""
echo "📊 测试4：运行监控脚本..."
bash ~/.openclaw/workspace/skills/miliger-context-manager/scripts/context-monitor-v6.sh

# 5. 检查日志
echo ""
echo "📊 测试5：检查日志..."
echo "最近10条日志："
tail -10 ~/.openclaw/workspace/logs/context-monitor-v6.log

echo ""
echo "🧪 测试完成！"
echo "预期结果："
echo "1. 工具调用过频提醒（>50次/小时）"
echo "2. 长会话严重提醒（>4小时）"
echo "3. 高活跃度预警（HIGH级别）"
